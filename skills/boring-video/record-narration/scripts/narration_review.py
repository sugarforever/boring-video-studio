#!/usr/bin/env python3
"""Repeatable suspicious-window ASR and post-edit attention alignment; no LLM API."""
import argparse
import json
import html
import os
from pathlib import Path
import sys
import numpy as np
from agent_edit import digest, excerpt, save
from audio_evidence import read_pcm, levels, align_text, alignment_issues, coalesce_zero_duration


def inspection_windows(samples,rate,hints,speech=None):
    if speech is not None:
        windows=[]
        for hint in hints:
            for region in speech:
                a,b=region['start']/16000,region['end']/16000
                if b<hint['start']-.35 or a>hint['end']+.35:continue
                for at in np.arange(a,b,20.):
                    windows.append({'start':float(at),'end':min(float(at)+22,b),'hint':hint})
        unique={(round(w['start'],2),round(w['end'],2)):w for w in windows}
        return sorted(unique.values(),key=lambda w:w['start'])
    windows=[]
    for hint in hints:
        start=max(0,hint['start']-.35);end=min(len(samples)/rate,hint['end']+.35)
        db,offset=levels(samples,rate,start,end)
        audible=db[db>-100]
        if not len(audible):continue
        floor,high=np.percentile(audible,[10,90])
        if high-floor<12:continue
        active=db>min(floor+12,high-16)
        spans=[];i=0
        while i<len(active):
            if not active[i]:i+=1;continue
            j=i+1
            while j<len(active) and (active[j] or any(active[j:min(j+16,len(active))])):j+=1
            if j-i>=15:
                a=max(start,offset+i*.01-.18);b=min(end,offset+j*.01+.18)
                if b>hint['start'] and a<hint['end']:spans.append((a,b))
            i=j
        for a,b in spans:
            if b-a>25:
                for at in np.arange(a,b,20.):
                    windows.append({'start':float(at),'end':min(float(at)+22,b),'hint':hint})
            else:windows.append({'start':a,'end':b,'hint':hint})
    unique={}
    for w in windows:unique[(round(w['start'],2),round(w['end'],2))]=w
    return sorted(unique.values(),key=lambda w:w['start'])


def inspect(review,output,model,language='zh',start=0,end=float('inf'),max_windows=24):
    review,output=Path(review),Path(output)
    b=json.loads((review/'bundle.json').read_text())
    for item in b['bindings'].values():
        if digest(item['path'])!=item['sha256']:raise ValueError('Source changed; prepare again')
    hints=json.loads((review/'inspection-hints.json').read_text())
    hints=[h for h in hints if h['end']>start and h['start']<end]
    pcm,rate=read_pcm(b['bindings']['audio']['path'])
    from faster_whisper.audio import decode_audio
    from faster_whisper.vad import get_speech_timestamps, VadOptions
    decoded=decode_audio(b['bindings']['audio']['path'],sampling_rate=16000)
    speech=get_speech_timestamps(decoded,VadOptions(threshold=.35,min_silence_duration_ms=250,speech_pad_ms=150))
    windows=inspection_windows(pcm,rate,hints,speech)
    output.mkdir(parents=True,exist_ok=False)
    evidence={'bundle_id':b['bundle_id'],'scope':[start,min(end,len(pcm)/rate)],
              'model':model.model_size_or_path if hasattr(model,'model_size_or_path') else 'faster-whisper (see CLI invocation)',
              'vad':'bundled Silero ONNX, threshold .35, silence 250ms, padding 150ms',
              'status':'asr_evidence_only','windows':[],'unprocessed_windows':windows[max_windows:],
              'limitations':'Energy proposes windows, not speech identity; repeated ASR is correlated, not listening. Never auto-patch source words.'}
    for i,w in enumerate(windows[:max_windows]):
        target=output/f'window-{i+1:03d}.wav'
        excerpt(b['bindings']['audio']['path'],target,w['start'],w['end'])
        segments,_=model.transcribe(str(target),language=language,word_timestamps=True,
                                    vad_filter=False,condition_on_previous_text=False)
        words=[{'word':v.word,'start':float(v.start)+w['start'],'end':float(v.end)+w['start'],
                'probability':float(v.probability)} for s in segments for v in s.words or []]
        evidence['windows'].append(dict(w,file=str(target),words=words,text=''.join(v['word'] for v in words)))
        save(output/'inspection.json',evidence)
        print(f'Inspected {i+1}/{min(len(windows),max_windows)}: {w["start"]:.2f}..{w["end"]:.2f}',flush=True)
    save(output/'inspection.json',evidence)
    return evidence


def alignment_groups(words,duration):
    chunks=[];group=[]
    for w in words:
        if group and (w['end']-group[0]['start']>20 or w['start']-group[-1]['end']>.65):
            chunks.append(group);group=[]
        group.append(w)
    if group:chunks.append(group)
    result=[]
    for i,g in enumerate(chunks):
        a=max(0,g[0]['start']-.25);b=min(duration,g[-1]['end']+.3)
        if i:a=max(a,(chunks[i-1][-1]['end']+g[0]['start'])/2)
        if i+1<len(chunks):b=min(b,(g[-1]['end']+chunks[i+1][0]['start'])/2)
        if not a<b or b-a>25:raise ValueError('Alignment window invalid/too long; inspect word spans')
        result.append({'start':a,'end':b,'text':''.join(w['text'] for w in g)})
    return result


def realign(result,output,model,language='zh'):
    result,output=Path(result),Path(output)
    tx=json.loads((result/'transcript.draft.json').read_text())
    report=json.loads((result/'edit-report.json').read_text())
    audio=Path(tx['audio'])
    output.mkdir(parents=True,exist_ok=False)
    input_bindings={str(p.resolve()):digest(p) for p in [audio,result/'transcript.draft.json',result/'edit-report.json']}
    groups=alignment_groups(tx['words'],report['duration_after'])
    words,windows=align_text(audio,groups,model,language)
    issues=alignment_issues(words,report['duration_after'])
    aligned={'audio':str(audio),'language':language,'method':'faster-whisper attention/DTW text alignment; not phoneme CTC or independent listening',
             'source_bundle':tx['bundle_id'],'bindings':input_bindings,'words':words,'windows':windows,
             'issues':issues,'status':'alignment_review_required' if issues else 'awaiting_audio_review',
             'unresolved_cuts':tx.get('unresolved_cuts',0),'provisional_corrections':'retained unchanged; require audio evidence'}
    if aligned['unresolved_cuts']:aligned['status']='draft_review_required'
    save(output/'transcript.aligned.json',aligned)
    # Retain raw alignment, including failures; shared timed units avoid fabricating zero-token times.
    layout_words,coalesced=coalesce_zero_duration(words)
    structural=[x for x in alignment_issues(layout_words,report['duration_after']) if x['reason'].startswith('invalid')]
    aligned['coalesced_units']=coalesced
    aligned['subtitle_status']='review_draft'
    if not structural:
        from process_audio import word_cues,srt
        segments=word_cues(layout_words,max_chars=16,max_duration=5.,pause_gap=.45)
        aligned['segments']=segments
        save(output/'transcript.aligned.json',aligned)
        (output/'subtitles.aligned.srt').write_text(srt(aligned),encoding='utf-8')
    if any(digest(path)!=value for path,value in input_bindings.items()):
        raise ValueError('Alignment inputs changed while processing')
    save(output/'QC.json',{'status':aligned['status'],'alignment_issues':issues,
         'unresolved_cuts':aligned['unresolved_cuts'],'listening':'pending','user_acceptance':'pending',
         'input_bindings':input_bindings,'subtitle_exported':not structural,'shared_timing_units':coalesced})
    links=f'<p><a href="{html.escape(os.path.relpath(result/"review.html",output))}">剪辑对比与原始证据</a></p>'
    if not structural:links+='<p><a href="subtitles.aligned.srt">重新对齐的草稿字幕</a></p>'
    page='<meta charset="utf-8"><title>Alignment review</title><style>body{max-width:960px;margin:32px auto;font:18px system-ui}audio{width:100%}</style><h1>对齐后待审版本</h1>'
    page+=f'<p>状态：{aligned["status"]}。{len(issues)} 条对齐提示；音频听审、文本校正和用户确认仍待完成。</p>'
    page+=f'<audio controls src="{html.escape(os.path.relpath(audio,output))}"></audio>'+links
    page+='<p><a href="QC.json">检查报告</a> · <a href="transcript.aligned.json">完整对齐数据与异常</a></p>'
    (output/'review.html').write_text(page,encoding='utf-8')
    return aligned


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    scan=sub.add_parser('inspect');scan.add_argument('--review',type=Path,required=True)
    scan.add_argument('--start',type=float,default=0);scan.add_argument('--end',type=float,default=float('inf'))
    scan.add_argument('--max-windows',type=int,default=24)
    align=sub.add_parser('align');align.add_argument('--result',type=Path,required=True)
    for parser in (scan,align):
        parser.add_argument('--output',type=Path,required=True);parser.add_argument('--model',default='small')
        parser.add_argument('--language',default='zh')
    a=p.parse_args()
    if a.command=='inspect' and (a.max_windows<1 or a.start<0 or a.end<=a.start):p.error('Invalid inspection scope')
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel(a.model,device='cpu',compute_type='int8')
        if a.command=='inspect':result=inspect(a.review,a.output,model,a.language,a.start,a.end,a.max_windows)
        else:result=realign(a.result,a.output,model,a.language)
        from importlib.metadata import version
        save(a.output/'invocation.json',{'command':a.command,'model':a.model,'language':a.language,
              'engine':'faster-whisper CPU int8','faster_whisper_version':version('faster-whisper'),
              'ctranslate2_version':version('ctranslate2'),'status':result['status']})
        print(json.dumps({'output':str(a.output),'status':result['status']},ensure_ascii=False))
    except (OSError,ValueError,RuntimeError,KeyError) as e:
        print(f'Error: {e}',file=sys.stderr);return 1
    return 0

if __name__=='__main__':sys.exit(main())
