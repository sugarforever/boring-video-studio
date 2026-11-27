#!/usr/bin/env python3
"""Compare source-clock edits and export matched listening windows; no quality claims."""
import argparse
import html
import json
from pathlib import Path
import numpy as np
from agent_edit import digest,excerpt,save
from audio_evidence import read_pcm


def map_time(t,report):
    for k in report['kept']:
        if k['source_start']-1e-8<=t<=k['source_end']+1e-8:
            return k['output_start']+t-k['source_start']
    raise ValueError('Comparison anchor lies in removed source audio')


def interior_identity(source,output,report,rate):
    mismatches=count=0
    for k in report['kept']:
        first,last=round(k['source_start']*rate),round(k['source_end']*rate)
        at=round(k['output_start']*rate);length=last-first
        if length<=600:continue
        a=source[first+300:last-300];b=output[at+300:at+length-300]
        if len(a)!=len(b):raise ValueError('Output sample count differs from edit mapping')
        mismatches+=int(np.count_nonzero(a!=b));count+=len(a)
    return {'interior_samples_compared':count,'mismatched_samples':mismatches,'edge_exclusion_samples':300}


def compare(baseline,candidate,output,previous=None):
    paths={'baseline':Path(baseline),'candidate':Path(candidate)}
    if previous:paths['previous']=Path(previous)
    reports={k:json.loads(p.read_text()) for k,p in paths.items()}
    reference=reports['candidate'];source=Path(reference['source'])
    if any(r['source_sha256']!=digest(source) for r in reports.values()):
        raise ValueError('Comparison requires unchanged identical source audio')
    data,rate=read_pcm(source)
    result={'source_sha256':digest(source),'durations':{'source':len(data)/rate},
            'interior_identity':{},'rows':[],'status':'listening_pending'}
    for k,r in reports.items():
        samples,sr=read_pcm(r['audio'])
        if sr!=rate:raise ValueError('Sample rates differ')
        if len(samples)!=round(r['duration_after']*rate):raise ValueError('Stale output duration')
        result['durations'][k]=len(samples)/rate
        result['interior_identity'][k]=interior_identity(data,samples,r,rate)
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    parts=[]
    for i,c in enumerate(reference['cuts'],1):
        a=max(0,c['start']-3);b=min(len(data)/rate,c['end']+3)
        row={'id':i,'reason':c['reason'],'source_window':[a,b],'versions':{}}
        section=f'<section><h2>{i}. {html.escape(c["reason"])}</h2>'
        for k in ['source',*reports]:
            start,end=(a,b) if k=='source' else (map_time(a,reports[k]),map_time(b,reports[k]))
            audio=source if k=='source' else reports[k]['audio']
            file=f'{i}-{k}.wav';excerpt(audio,output/file,start,end)
            cuts=[] if k=='source' else [x for x in reports[k]['cuts'] if x['start']<b and x['end']>a]
            edges=[]
            for cut in cuts:
                values=[]
                for t in [cut['start'],cut['end']]:
                    n=round(t*rate);x=data[max(0,n-480):min(len(data),n+480)].astype(float)
                    values.append(float(20*np.log10(max(np.sqrt(np.mean(x*x))/32768,1e-10))))
                edges.append({'start':cut['start'],'end':cut['end'],'rms_20ms_dbfs':values})
            row['versions'][k]={'file':file,'window':[start,end],'cuts':edges}
            section+=f'<h3>{k}</h3><audio controls src="{file}"></audio><pre>{html.escape(json.dumps(edges,ensure_ascii=False,indent=2))}</pre>'
        result['rows'].append(row);parts.append(section+'</section>')
    save(output/'comparison.json',result)
    (output/'review.html').write_text('<meta charset="utf-8"><title>Audio edit comparison</title><style>body{max-width:980px;margin:32px auto;font:18px system-ui}audio{width:100%}section{border-top:1px solid #ccc;margin:32px 0}</style><h1>同源音频剪辑比较</h1><p>source 原录音；baseline 旧成品；previous 第一版草稿；candidate 当前声学切点版。能量、ASR、字节一致都不能代替试听。</p>'+''.join(parts),encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ['baseline','candidate','output']:p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--previous',type=Path);a=p.parse_args()
    compare(a.baseline,a.candidate,a.output,a.previous)
    print(a.output/'review.html')

if __name__=='__main__':main()
