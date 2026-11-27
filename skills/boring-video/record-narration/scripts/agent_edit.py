#!/usr/bin/env python3
"""Export narration evidence for the current agent; validate and execute its decisions.

No LLM client. Inputs and all decisions are retained; outputs require listening approval.
"""
import argparse
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import sys
import wave
from edit_audio import edit


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def prepare(audio, transcript, script, output):
    paths = {k:Path(v).resolve() for k,v in [('audio',audio),('transcript',transcript),('script',script)]}
    bindings = {k:{'path':str(p),'sha256':digest(p)} for k,p in paths.items()}
    with wave.open(str(paths['audio'])) as f:
        if (f.getnchannels(),f.getsampwidth(),f.getframerate()) != (1,2,48000):
            raise ValueError('Expected mono 48 kHz PCM16 WAV')
        duration=f.getnframes()/f.getframerate()
    data=json.loads(paths['transcript'].read_text(encoding='utf-8'))
    from audio_evidence import coalesce_zero_duration
    input_words,timing_notes=coalesce_zero_duration(data['words'])
    words=[]; previous=0.
    for i,w in enumerate(input_words):
        start,end=float(w['start']),float(w['end'])
        if not all(math.isfinite(v) for v in (start,end)) or not previous <= start < end <= duration:
            raise ValueError(f'Invalid/overlapping word timing at index {i}; repair alignment first')
        words.append({'id':f'w{i:06d}','start':start,'end':end,'raw_text':w['word'],'text':w['word'],
                      'source_word_indices':w['source_word_indices']})
        previous=end
    if not words: raise ValueError('Word-level transcript is empty')
    bundle={'version':1,'bindings':bindings,'duration':duration,'words':words,'input_timing_notes':timing_notes,
            'alignment_status':'input timestamps; source association must be verified by agent'}
    bundle['bundle_id']=hashlib.sha256(json.dumps(bundle,sort_keys=True).encode()).hexdigest()
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    save(output/'bundle.json',bundle)
    save(output/'decisions.template.json',{'bundle_id':bundle['bundle_id'],'corrections':[],'cuts':[]})
    hints=[]; previous=0.
    for w in words:
        if w['start']-previous>=1.2:
            hints.append({'kind':'long_gap','start':previous,'end':w['start'],
                          'next_word':w['id'],'interpretation':'possible silence OR omitted speech; inspect audio'})
        if w['end']-w['start']>=max(1.2,len(w['raw_text'].strip())*.4):
            hints.append({'kind':'long_word_span','start':w['start'],'end':w['end'],'word':w['id'],
                          'interpretation':'possible pause/restart absorbed into ASR word timing'})
        previous=w['end']
    save(output/'inspection-hints.json',hints)
    lines=['# Agent review input','', 'Reference script (context, not spoken-word authority):',
           paths['script'].read_text(encoding='utf-8'),'',
           'Review ALL words. Preserve raw repeats/residual syllables. Correct recognition only.',
           'For each cut supply first/last and replacement_first/replacement_last word IDs and reason.',
           'Keep emphasis and unique improvisation; retain ambiguous passages. No shortening quota.',
           'An empty plan is valid only after reviewing all text. Text review is not audio listening.',
           'Corrections: id, text, reason; one replacement text per existing word ID. Do not invent times.',
           '', '## Inspection hints (not cut decisions)', json.dumps(hints,ensure_ascii=False), '', '## Timed words']
    lines += [f"{w['id']} [{w['start']:.3f}–{w['end']:.3f}] {w['raw_text']}" for w in words]
    (output/'agent-input.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return bundle


def srt(words):
    groups=[]; group=[]
    for w in words:
        if group and (w['start']-group[-1]['end']>.6 or w['end']-group[0]['start']>4 or
                      sum(len(x['text']) for x in group)+len(w['text'])>24):
            groups.append(group);group=[]
        group.append(w)
    if group: groups.append(group)
    def stamp(t):
        ms=round(t*1000);sec,ms=divmod(ms,1000);minute,sec=divmod(sec,60);hour,minute=divmod(minute,60)
        return f'{hour:02}:{minute:02}:{sec:02},{ms:03}'
    return '\n\n'.join(f"{i}\n{stamp(g[0]['start'])} --> {stamp(g[-1]['end'])}\n{''.join(w['text'] for w in g).strip()}" for i,g in enumerate(groups,1))+'\n'


def apply(review, decisions, output, boundary_mode='acoustic'):
    review,output=Path(review),Path(output)
    bundle=json.loads((review/'bundle.json').read_text(encoding='utf-8'))
    expected=bundle.copy(); identity=expected.pop('bundle_id')
    if hashlib.sha256(json.dumps(expected,sort_keys=True).encode()).hexdigest()!=identity:
        raise ValueError('Bundle changed; prepare again')
    if decisions['bundle_id']!=identity: raise ValueError('Wrong bundle version')
    for binding in bundle['bindings'].values():
        if digest(binding['path'])!=binding['sha256']: raise ValueError('Source changed; prepare again')
    words=copy.deepcopy(bundle['words']); lookup={w['id']:i for i,w in enumerate(words)}
    seen=set()
    for c in decisions.get('corrections',[]):
        if c['id'] in seen or not c['text'].strip() or not c['reason'].strip():
            raise ValueError('Corrections need unique IDs, nonempty text and reason')
        seen.add(c['id']);words[lookup[c['id']]]['text']=c['text']
    cuts=[]; ranges=[]; replacements=[]
    for c in decisions['cuts']:
        a,b=lookup[c['first']],lookup[c['last']]
        r,t=lookup[c['replacement_first']],lookup[c['replacement_last']]
        if a>b or r>t or not c['reason'].strip(): raise ValueError('Invalid cut/replacement range')
        if ranges and a<=ranges[-1][1]: raise ValueError('Cuts must be ordered and nonoverlapping')
        ranges.append((a,b));replacements.append((r,t))
        cuts.append({'start':words[a]['start'],'end':words[b]['end'],'reason':c['reason']})
    for r,t in replacements:
        if any(a<=t and r<=b for a,b in ranges): raise ValueError('A replacement would be deleted')
    if boundary_mode not in ('acoustic','word'): raise ValueError('Unknown boundary mode')
    from audio_evidence import read_pcm, refine_cut
    pcm,rate=read_pcm(bundle['bindings']['audio']['path'])
    boundary_report=[]; approved=[]; approved_ranges=[]
    for cut,(a,b) in zip(cuts,ranges):
        if boundary_mode=='word':
            boundary=dict(cut,status='unverified',reason='diagnostic raw word edges; acoustic validation skipped')
        else:
            previous=words[a-1]['start'] if a else 0.
            following=words[b+1]['start'] if b+1<len(words) else bundle['duration']
            boundary=refine_cut(pcm,rate,cut['start'],cut['end'],previous,following)
        boundary['first']=words[a]['id'];boundary['last']=words[b]['id']
        if boundary['status'] in ('ready','unverified'):
            proposal=dict(cut,start=boundary['start'],end=boundary['end'])
            if approved and proposal['start']<approved[-1]['end']:
                boundary.update(status='unresolved',reason='refined cuts overlap')
            else:
                approved.append(proposal);approved_ranges.append((a,b))
        boundary_report.append(boundary)
    cuts,ranges=approved,approved_ranges
    result_audio=edit(bundle['bindings']['audio']['path'],cuts,output)
    report=json.loads((output/'edit-report.json').read_text())
    final=[]; mapping_issues=[]
    for i,w in enumerate(words):
        if any(a<=i<=b for a,b in ranges): continue
        overlaps=[(max(w['start'],k['source_start']),min(w['end'],k['source_end']),k)
                  for k in report['kept'] if w['start']<k['source_end'] and w['end']>k['source_start']]
        if not overlaps: raise ValueError('Retained word has no surviving audio; inspect cut')
        start,end,kept=max(overlaps,key=lambda item:item[1]-item[0])
        if abs(start-w['start'])>1e-5 or abs(end-w['end'])>1e-5:
            mapping_issues.append({'id':w['id'],'reason':'source timestamp intersects acoustic edge; realignment required'})
        shift=kept['source_start']-kept['output_start']
        final.append(dict(w,source_start=w['start'],source_end=w['end'],
                          start=start-shift,end=end-shift))
    result={'audio':str(result_audio),'bundle_id':identity,'words':final,
            'status':'draft_review_required','boundary_mode':boundary_mode,
            'unresolved_cuts':sum(x['status']=='unresolved' for x in boundary_report),
            'mapping_issues':mapping_issues,'alignment':'mapped source ASR times; not retranscribed',
            'review':'text-based edit draft; full speech and cut-boundary listening pending'}
    review_tasks=[{'kind':'boundary','status':'pending','word':x['first'],'reason':x['reason']}
                  for x in boundary_report if x['status']!='ready']
    review_tasks.extend({'kind':'recognition_correction','status':'pending','word':c['id'],
                         'reason':c['reason']} for c in decisions.get('corrections',[]))
    review_tasks.extend({'kind':'input_shared_timing','status':'pending','evidence':note}
                         for note in bundle.get('input_timing_notes',[]))
    review_tasks.extend([{'kind':'final_alignment','status':'pending'},
                         {'kind':'full_speech_listening','status':'pending'},
                         {'kind':'user_acceptance','status':'pending'}])
    save(output/'review-tasks.json',review_tasks)
    save(output/'boundary-report.json',boundary_report)
    save(output/'transcript.draft.json',result);save(output/'decisions.json',decisions)
    save(output/'source-bundle.json',bundle);save(output/'retake-cuts.json',cuts)
    (output/'subtitles.draft.srt').write_text(srt(final),encoding='utf-8')
    rows=[]
    for i,c in enumerate(cuts):
        start=max(0,c['start']-3);end=min(bundle['duration'],c['end']+3)
        source=f'before-{i+1}.wav'
        excerpt(bundle['bindings']['audio']['path'], output/source, start, end)
        seam=c['start']-sum(x['end']-x['start'] for x in cuts[:i])
        edited=f'after-{i+1}.wav'
        excerpt(result_audio, output/edited, max(0,seam-3), min(report['duration_after'],seam+3))
        rows.append(f'<section><h2>{i+1}. {html.escape(c["reason"])}</h2><p>Source {c["start"]:.3f}–{c["end"]:.3f}s</p>Before <audio controls src="{html.escape(source)}"></audio> After <audio controls src="{html.escape(edited)}"></audio></section>')
    page='<meta charset="utf-8"><title>Narration edit review</title><style>body{max-width:960px;margin:40px auto;font:18px system-ui}section{border-top:1px solid #ccc;padding:20px 0}audio{display:block;width:100%}</style><h1>待试听的剪辑草稿</h1><p>当前 agent 基于文字决策；未声称完成全片听审。字幕使用映射后的原始词时间。请检查是否漏剪、误删、伤字或接缝不自然。</p><p><a href="boundary-report.json">切点证据</a> · <a href="review-tasks.json">未完成检查</a></p><p><a href="subtitles.draft.srt">草稿字幕</a> · <a href="REVIEW.md">处理报告</a> · <a href="decisions.json">剪辑决策</a></p><h2>完整处理版本</h2><audio controls src="'+html.escape(result_audio.name)+'"></audio>'+''.join(rows)
    (output/'review.html').write_text(page,encoding='utf-8')
    (output/'REVIEW.md').write_text(f'# Audio processing review\n\nStatus: draft_review_required\n\n{len(cuts)} text-supported cuts; removed {sum(c["end"]-c["start"] for c in cuts):.3f}s.\n\nOriginal: {bundle["bindings"]["audio"]["path"]}\n\nOutput: {result_audio}\n\nNoise treatment: inherited from input, not performed by this command.\n\nAll original files retained. Text corrections preserve raw_text. Full speech review, boundary listening and fresh subtitle alignment remain pending. Source/transcript correspondence is supplied by caller; hashes prevent later changes, not wrong initial pairing.\n',encoding='utf-8')
    return result


def excerpt(source, target, start, end):
    with wave.open(str(source), 'rb') as src:
        rate=src.getframerate()
        src.setpos(min(src.getnframes(),round(start*rate)))
        data=src.readframes(max(0,round(end*rate)-round(start*rate)))
        with wave.open(str(target), 'wb') as dst:
            dst.setparams(src.getparams());dst.writeframes(data)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    init=sub.add_parser('prepare')
    for key in ('audio','transcript','script','output'):init.add_argument('--'+key,type=Path,required=True)
    run=sub.add_parser('apply')
    for key in ('review','decisions','output'):run.add_argument('--'+key,type=Path,required=True)
    run.add_argument('--boundary-mode',choices=['acoustic','word'],default='acoustic')
    a=p.parse_args()
    try:
        if a.command=='prepare': result=prepare(a.audio,a.transcript,a.script,a.output)
        else: result=apply(a.review,json.loads(a.decisions.read_text(encoding='utf-8')),a.output,a.boundary_mode)
        print(json.dumps({'bundle_id':result['bundle_id'],'output':str(a.output)},ensure_ascii=False))
    except (ValueError,KeyError,OSError,TypeError,wave.Error) as e:
        print(f'Error: {e}',file=sys.stderr);return 1
    return 0

if __name__=='__main__':sys.exit(main())
