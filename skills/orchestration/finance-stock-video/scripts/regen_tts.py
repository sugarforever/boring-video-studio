#!/usr/bin/env python3
# Per-sentence ListenHub TTS regen -> exact-timed SRT + concatenated audio (1.2x)
import json, os, sys, subprocess, urllib.request, tempfile
from concurrent.futures import ThreadPoolExecutor

KEY = os.environ["LISTENHUB_API_KEY"]
# 音色/速度可配（默认财经系列：灵依 1.2x）；通用/克隆音色用 env 覆盖：
#   TTS_SPEAKER=voice-clone-6a29dd635b88331426c4ecbc TTS_TEMPO=1.0（VerySmallWoods 克隆，自然速）
SPEAKER = os.environ.get("TTS_SPEAKER", "zh-female-wanwanxiaohe-moon-bigtts-fa851a51")
BASE = "https://api.marswave.ai/openapi/v1/speech"
SR = 44100
TEMPO = float(os.environ.get("TTS_TEMPO", "1.2"))
OUTDIR = sys.argv[1]  # episode dir to write narration-full.mp3 + narration.srt
CLIPS = "/tmp/tts_clips"; os.makedirs(CLIPS, exist_ok=True)

segs = [s["content"] for s in json.load(open("/tmp/req.json"))["scripts"]]
print(f"segments: {len(segs)}")

# 停顿：{after_cue(1-based): 成片里的停顿秒数}。由 srt_helper.py buildreq --pause-map 产出。
# 逐句合成是 1.0x 域，最后整段 atempo=TEMPO，所以插 dur*TEMPO 的静音、成片里正好是 dur 秒。
PAUSES = {}
_pf = os.environ.get("PAUSE_MAP", "/tmp/pauses.json")
if os.path.exists(_pf):
    for _p in json.load(open(_pf, encoding="utf-8")):
        PAUSES[int(_p["after_cue"])] = float(_p["dur"])
    print(f"pauses: {len(PAUSES)} 处 (成片域秒数)")

def _silence_wav(dur_raw, tag):
    w = f"{CLIPS}/sil-{tag}.wav"
    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono",
                    "-t", f"{dur_raw:.3f}", w], check=True, stderr=subprocess.DEVNULL)
    return w

def synth(i_text):
    i, text = i_text
    body = json.dumps({"scripts":[{"content":text,"speakerId":SPEAKER}]}).encode()
    req = urllib.request.Request(BASE, data=body, method="POST",
        headers={"Authorization":f"Bearer {KEY}","Content-Type":"application/json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            # recursively find audioUrl
            url=None
            def find(o):
                nonlocal url
                if url: return
                if isinstance(o,dict):
                    for k,v in o.items():
                        if k=="audioUrl" and isinstance(v,str): url=v; return
                        find(v)
                elif isinstance(o,list):
                    for v in o: find(v)
            find(d)
            if not url: raise RuntimeError(f"no audioUrl: {json.dumps(d)[:200]}")
            mp3=f"{CLIPS}/{i:02d}.mp3"; wav=f"{CLIPS}/{i:02d}.wav"
            urllib.request.urlretrieve(url, mp3)
            subprocess.run(["ffmpeg","-y","-i",mp3,"-ar",str(SR),"-ac","1",wav],
                           check=True, stderr=subprocess.DEVNULL)
            dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                "-of","default=noprint_wrappers=1:nokey=1",wav],capture_output=True,text=True).stdout.strip())
            print(f"  [{i:02d}] {dur:6.3f}s  {text[:24]}")
            return i,wav,dur
        except Exception as e:
            print(f"  [{i:02d}] retry {attempt}: {e}")
    raise RuntimeError(f"failed seg {i}")

with ThreadPoolExecutor(max_workers=4) as ex:
    results = list(ex.map(synth, list(enumerate(segs))))
results.sort(key=lambda x:x[0])

# concat wavs (1.0x)，在 pause map 指定的段后插一段静音（1.0x 域 = dur*TEMPO）
listf=f"{CLIPS}/list.txt"
_lines=[]
for _i,(_,w,_) in enumerate(results):
    _lines.append(f"file '{w}'\n")
    _cue=_i+1
    if _cue in PAUSES:
        _lines.append(f"file '{_silence_wav(PAUSES[_cue]*TEMPO, f'{_cue:02d}')}'\n")
open(listf,"w").write("".join(_lines))
full10=f"{CLIPS}/full-1.0x.wav"
subprocess.run(["ffmpeg","-y","-f","concat","-safe","0","-i",listf,"-c","copy",full10],check=True,stderr=subprocess.DEVNULL)

# cumulative cue times at 1.0x, then /TEMPO for final 1.2x（cue 末尾若有停顿，累加 dur*TEMPO）
def fmt(t):
    if t<0:t=0
    h=int(t//3600);t-=h*3600;m=int(t//60);t-=m*60;s=int(t);ms=int(round((t-s)*1000))
    if ms==1000:s+=1;ms=0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
cues=[]; t=0.0
for i,(_,_,dur) in enumerate(results):
    start=t/TEMPO; end=(t+dur)/TEMPO
    cues.append((start,end,segs[i])); t+=dur
    if (i+1) in PAUSES:
        t += PAUSES[i+1]*TEMPO      # 停顿也进累计时长，后续 cue 自动顺延（/TEMPO 后正好 +dur）
# write starts for scene mapping
json.dump([{"i":i,"start":round(c[0],3),"end":round(c[1],3),"text":c[2]} for i,c in enumerate(cues)],
          open(f"{OUTDIR}/cue-starts.json","w"),ensure_ascii=False,indent=1)
# write SRT
with open(f"{OUTDIR}/narration.srt","w",encoding="utf-8") as f:
    for i,(s,e,txt) in enumerate(cues,1):
        f.write(f"{i}\n{fmt(s)} --> {fmt(e)}\n{txt}\n\n")

# final mp3 at 1.2x
subprocess.run(["ffmpeg","-y","-i",full10,"-filter:a",f"atempo={TEMPO}","-c:a","libmp3lame","-q:a","2",
                f"{OUTDIR}/narration-full.mp3"],check=True,stderr=subprocess.DEVNULL)
total=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
    "-of","default=noprint_wrappers=1:nokey=1",f"{OUTDIR}/narration-full.mp3"],capture_output=True,text=True).stdout.strip())
print(f"\nDONE. final audio {total:.2f}s ({len(cues)} cues). last cue end {cues[-1][1]:.2f}s")
