"""Acoustic evidence, conservative boundary planning and local attention alignment.

Pause-search design informed by MakeMyClip/editor pauses.ts and Developh/resolve-cut
cut_list.py. Original implementation; thresholds require per-recording validation.
Energy is not a speech recognizer. Alignment is not independent listening.
"""
import math
from pathlib import Path
import wave
import numpy as np


def read_pcm(path):
    with wave.open(str(path), 'rb') as f:
        if (f.getnchannels(), f.getsampwidth(), f.getframerate()) != (1, 2, 48000):
            raise ValueError('Expected mono 48 kHz PCM16 WAV')
        return np.frombuffer(f.readframes(f.getnframes()), dtype='<i2'), f.getframerate()


def levels(samples, rate, start, end):
    hop=round(rate*.01)
    first=max(0,round(start*rate));last=min(len(samples),round(end*rate))
    data=samples[first:last];n=len(data)//hop
    if not n: return np.array([]), first/rate
    data=data[:n*hop].reshape(n,hop).astype(float)/32768
    return 20*np.log10(np.maximum(np.sqrt(np.mean(data*data,axis=1)),1e-10)), first/rate


def quiet_runs(db, offset, threshold):
    # Bridge <=40 ms room clicks, never bridge a sustained voiced interval.
    mask=db<=threshold
    for i in range(1,len(mask)-1):
        if mask[i]:continue
        j=i
        while j<len(mask) and not mask[j]:j+=1
        if j-i<=4 and mask[i-1] and j<len(mask):mask[i:j]=True
    runs=[];i=0
    while i<len(db):
        if not mask[i]: i+=1;continue
        j=i+1
        while j<len(db) and mask[j]:j+=1
        if j-i>=8:runs.append((offset+i*.01,offset+j*.01))
        i=j
    return runs


def refine_cut(samples, rate, start, end, previous_word_start, next_word_start):
    """Keep cuts in unambiguous quiet runs bounded by neighbouring kept speech.

    previous_word_start bounds the search, not a claim about its actual end.
    No valid run -> leave the proposed deletion unresolved, never force a cut.
    """
    duration=len(samples)/rate
    if not 0<=previous_word_start<=start<end<=next_word_start<=duration:
        return {'status':'unresolved','reason':'invalid neighbour bounds'}
    db,offset=levels(samples,rate,max(0,start-1.5),min(duration,next_word_start+.7))
    if not len(db):return {'status':'unresolved','reason':'no samples'}
    audible=db[db>-100]
    if not len(audible) or np.percentile(audible,90)-np.percentile(audible,10)<12:
        return {'status':'unresolved','reason':'insufficient speech/room contrast'}
    threshold=float(min(np.percentile(audible,20)+10,np.percentile(audible,95)-20))
    runs=quiet_runs(db,offset,threshold)
    before=[(max(a,previous_word_start+.02,start-.65),min(b,start+.45))
            for a,b in runs if b>max(previous_word_start+.02,start-.65) and a<start+.45]
    before=[(a,b) for a,b in before if b-a>=.08-1e-8]
    after=[(max(a,end-.65,next_word_start-.65),min(b,next_word_start+.05))
           for a,b in runs if b>max(end-.65,next_word_start-.65) and a<next_word_start+.05]
    after=[(a,b) for a,b in after if b-a>=.08-1e-8]
    evidence={'threshold_dbfs':threshold,'quiet_runs':runs,'proposed_start':start,'proposed_end':end}
    if not before or not after:
        return dict(evidence,status='unresolved',reason='no protected quiet boundary')
    if len(before)>1 or len(after)>1:
        return dict(evidence,status='unresolved',reason='ambiguous competing quiet runs')
    a,b=before[0];cut_start=min(max(start,a+min(.1,(b-a)/2)),b-min(.1,(b-a)/2))
    a,b=after[0];cut_end=min(b-min(.12,(b-a)/2),next_word_start-.02)
    if not a<=cut_end<=b:
        return dict(evidence,status='unresolved',reason='quiet boundary would cross kept-word onset')
    if cut_start>=cut_end:
        return dict(evidence,status='unresolved',reason='boundary order invalid')
    return dict(evidence,status='ready',start=round(cut_start,5),end=round(cut_end,5),
                reason='continuous quiet boundaries; kept neighbours constrain search')


def alignment_issues(words, duration):
    issues=[];previous=0.
    for i,w in enumerate(words):
        start,end=float(w['start']),float(w['end'])
        if not all(math.isfinite(v) for v in (start,end)) or not previous<=start<end<=duration:
            issues.append({'word':i,'reason':'invalid, overlapping or zero-duration alignment'})
        if end-start>max(1.2,len(w['word'].strip())*.4):
            issues.append({'word':i,'reason':'long aligned span'})
        if float(w.get('probability',1))<.35:
            issues.append({'word':i,'reason':'low alignment-conditioned token probability'})
        previous=max(previous,end)
    return issues


def align_text(audio, groups, model, language='zh'):
    """Recompute timestamps for supplied text, in <=25s local audio windows.

    Uses installed faster-whisper/CT2 attention alignment (not phoneme CTC).
    No new recognition words are substituted; all input text must survive exactly.
    """
    from faster_whisper.audio import pad_or_trim
    from faster_whisper.tokenizer import Tokenizer
    pcm,rate=read_pcm(audio)
    tokenizer=Tokenizer(model.hf_tokenizer,model.model.is_multilingual,task='transcribe',language=language)
    aligned=[];windows=[]
    for group in groups:
        begin,end=group['start'],group['end'];text=group['text']
        from faster_whisper.audio import decode_audio
        # decode_audio resamples the source once; cached below across windows.
        if not windows: decoded=decode_audio(str(audio),sampling_rate=16000)
        sample=decoded[round(begin*16000):round(end*16000)]
        features=model.feature_extractor(sample)
        num_frames=min(features.shape[-1],3000)
        encoded=model.encode(pad_or_trim(features))
        tokens=tokenizer.encode(text)
        values=model.find_alignment(tokenizer,[tokens],encoded,num_frames)[0]
        words=[{'word':w['word'],'start':float(w['start'])+begin,
                'end':min(float(w['end'])+begin,end),'probability':float(w['probability'])} for w in values]
        if ''.join(w['word'] for w in words)!=text:
            raise ValueError('Alignment changed text; retain source and inspect tokenization')
        aligned.extend(words);windows.append(dict(group))
    return aligned,windows


def coalesce_zero_duration(words):
    """Keep zero-duration tokens as shared timed units; never invent their boundaries."""
    result=[];notes=[];prefix=''
    for i,original in enumerate(words):
        w=dict(original)
        if w['end']==w['start']:
            notes.append({'word':i,'reason':'zero-duration token coalesced; no individual timing claimed'})
            if result:result[-1]['word']+=w['word']
            else:prefix+=w['word']
        else:
            if prefix:w['word']=prefix+w['word'];prefix=''
            result.append(w)
    if prefix:raise ValueError('No timed unit for zero-duration text')
    return result,notes
