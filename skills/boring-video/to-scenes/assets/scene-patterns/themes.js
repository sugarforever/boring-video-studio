(function(){
const F={archivo:"'Archivo','Noto Sans SC',sans-serif",inst:"'Instrument Sans','Noto Sans SC',sans-serif",geist:"'Geist','Noto Sans SC',sans-serif",news:"'Newsreader','Noto Sans SC',serif",gm:"'Geist Mono','Noto Sans SC',monospace",sm:"'Space Mono','Noto Sans SC',monospace"};
function TH(s,m){const L=m==='light';
if(s==='bf'){const ink=L?'#111111':'#F5F0E4',sd=L?'#111111':'#000000',ac=L?'#F04414':'#FF6A3D',ac2=L?'#2448FF':'#6B86FF',g=L?'#0A8A50':'#2BD38A',bg=L?'#F2EEE3':'#1F1C16',sf=L?'#FFFFFF':'#2A261E';
return {bg,sf,s2:L?'#E7E0CF':'#353026',ink,mu:L?'#4A463E':'#C2BAA8',ln:ink,hair:L?'rgba(17,17,17,.16)':'rgba(245,240,228,.16)',hi:'#FFD21F',onHi:'#111111',ac,on:L?'#FFFFFF':'#111111',ac2,on2:L?'#FFFFFF':'#111111',ac3:g,
bd:'3px solid '+ink,bdT:'2px solid '+ink,r:'6px',rS:'4px',sh:'8px 8px 0 '+sd,shS:'4px 4px 0 '+sd,fd:F.archivo,dw:900,tls:'-0.02em',fb:F.archivo,fn:F.archivo,nw:900,fm:F.sm,
kBg:L?'#111111':'#FFD21F',kInk:L?'#FFD21F':'#111111',kBd:'none',kR:'4px',kPad:'10px 18px',kF:F.archivo,kSt:'normal',kW:800,kMark:'#FF4A1C',kMW:'14px',kMH:'14px',kMR:'2px',
deco:'none',dots:'none',grid:'transparent',track:L?'#E3DCCB':'#38322A',b1:'#FFD21F',bN:L?'#111111':'#F5F0E4',barBd:'3px solid '+ink,dotR:'50%',c1:ac,c2:ac2,c3:'#FFD21F',c4:g,
tm:L?'#111111':'#0E0D0A',tmInk:'#F2EEE3',tmMu:'#9A9384',tmBar:'#FFD21F',tmBarInk:'#111111',tmOk:'#2BD38A',leaf:'#18B26B',svgSt:'#111111',svgSw:5,svgSwS:'5',ptBd:'3px solid #111111',rule:'3px solid '+ink};}
if(s==='sw'){const ink=L?'#0D0D0D':'#F1F1EC',red=L?'#E8210F':'#FF3B24',on=L?'#FFFFFF':'#0E0E0D';
return {bg:L?'#F3F3EF':'#0E0E0D',sf:'transparent',s2:L?'#E7E7E2':'#1B1B19',ink,mu:L?'#57574F':'#A5A59E',ln:ink,hair:L?'rgba(13,13,13,.16)':'rgba(241,241,236,.16)',hi:red,onHi:on,ac:red,on,ac2:ink,on2:L?'#F3F3EF':'#0E0E0D',ac3:ink,
bd:'none',bdT:'2px solid '+ink,r:'0px',rS:'0px',sh:'inset 0 5px 0 '+ink,shS:'none',fd:F.inst,dw:700,tls:'-0.04em',fb:F.inst,fn:F.inst,nw:600,fm:F.gm,
kBg:'transparent',kInk:ink,kBd:'none',kR:'0px',kPad:'0px',kF:F.inst,kSt:'normal',kW:600,kMark:red,kMW:'18px',kMH:'18px',kMR:'0px',
deco:'none',dots:'none',grid:L?'rgba(13,13,13,.055)':'rgba(241,241,236,.05)',track:L?'#E2E2DC':'#232321',b1:red,bN:ink,barBd:'none',dotR:'0px',c1:red,c2:ink,c3:L?'#8C8C85':'#7A7A74',c4:L?'#C9C9C2':'#3E3E3A',
tm:L?'#0D0D0D':'#1A1A18',tmInk:'#F1F1EC',tmMu:'#8C8C85',tmBar:red,tmBarInk:'#FFFFFF',tmOk:'#FF5A45',leaf:ink,svgSt:'none',svgSw:0,svgSwS:'0',ptBd:'none',rule:'2px solid '+ink};}
if(s==='rc'){const ink=L?'#16161A':'#EDEDF2',red=L?'#EE2B47':'#FF4D63',sf=L?'#FFFFFF':'#141417',line=L?'rgba(20,20,30,.10)':'rgba(255,255,255,.09)',bd='1px solid '+line,ac2=L?'#5B5BF0':'#8080FF',ac3=L?'#0F9F7F':'#2FD9A9';
return {bg:L?'#F3F3F5':'#0A0A0C',sf,s2:L?'#F7F7F9':'#1B1B1F',ink,mu:L?'#62626D':'#8F8F9A',ln:line,hair:L?'rgba(20,20,30,.08)':'rgba(255,255,255,.07)',hi:red,onHi:'#FFFFFF',ac:red,on:'#FFFFFF',ac2,on2:'#FFFFFF',ac3,
bd,bdT:bd,r:'20px',rS:'10px',sh:L?'inset 0 1px 0 rgba(255,255,255,.9), 0 1px 2px rgba(20,20,30,.05), 0 18px 44px -14px rgba(20,20,40,.18)':'inset 0 1px 0 rgba(255,255,255,.06), 0 28px 64px -22px rgba(0,0,0,.8)',shS:L?'0 1px 2px rgba(20,20,30,.06)':'inset 0 1px 0 rgba(255,255,255,.05)',
fd:F.geist,dw:600,tls:'-0.04em',fb:F.geist,fn:F.geist,nw:600,fm:F.gm,
kBg:sf,kInk:ink,kBd:bd,kR:'999px',kPad:'10px 22px 10px 18px',kF:F.geist,kSt:'normal',kW:500,kMark:red,kMW:'10px',kMH:'10px',kMR:'50%',
deco:L?'radial-gradient(900px 420px at 80% -8%, rgba(238,43,71,.09), rgba(238,43,71,0) 70%)':'radial-gradient(1000px 460px at 80% -10%, rgba(255,77,99,.16), rgba(255,77,99,0) 70%)',dots:L?'radial-gradient(rgba(20,20,30,.06) 1px, transparent 1.4px)':'radial-gradient(rgba(255,255,255,.05) 1px, transparent 1.4px)',
grid:'transparent',track:L?'#EDEDF1':'#1F1F24',b1:red,bN:L?'#CFCFD8':'#3A3A44',barBd:'none',dotR:'50%',c1:red,c2:ac2,c3:ac3,c4:L?'#E8930C':'#FFB224',
tm:L?'#FFFFFF':'#0F0F12',tmInk:L?'#16161A':'#E6E6EC',tmMu:L?'#8A8A95':'#6E6E79',tmBar:L?'#F7F7F9':'#16161A',tmBarInk:L?'#62626D':'#8F8F9A',tmOk:ac3,leaf:ac3,svgSt:'none',svgSw:0,svgSwS:'0',ptBd:'4px solid '+sf,rule:'1px solid '+line};}
const ink=L?'#1F1A14':'#F2E9DB',ac=L?'#D4532A':'#EC7148',ac2=L?'#2F6B5A':'#74B8A0',bg=L?'#F3EDE2':'#1D1915',ln=L?'#D3C5AE':'#463D31',bd='1px solid '+(L?'#D8CBB5':'#3E362C'),on=L?'#FFF8F0':'#1D1915';
return {bg,sf:L?'#FBF7EF':'#27221C',s2:L?'#ECE3D3':'#302921',ink,mu:L?'#6B6153':'#B7A994',ln,hair:L?'rgba(31,26,20,.13)':'rgba(242,233,219,.12)',hi:ac,onHi:on,ac,on,ac2,on2:on,ac3:ac2,
bd,bdT:bd,r:'12px',rS:'8px',sh:L?'inset 0 1px 0 rgba(255,255,255,.8), 0 16px 36px -22px rgba(80,50,20,.35)':'inset 0 1px 0 rgba(255,235,210,.04), 0 24px 48px -24px rgba(0,0,0,.7)',shS:'none',
fd:F.news,dw:500,tls:'-0.02em',fb:F.news,fn:F.news,nw:500,fm:F.gm,
kBg:'transparent',kInk:ac,kBd:'none',kR:'0px',kPad:'0px',kF:F.news,kSt:'italic',kW:500,kMark:ac,kMW:'40px',kMH:'2px',kMR:'0px',
dots:'none',deco:L?'radial-gradient(1600px 900px at 15% -10%, rgba(255,255,255,.6), transparent 60%)':'radial-gradient(1600px 900px at 15% -10%, rgba(236,113,72,.07), transparent 60%)',
grid:'transparent',track:L?'#E6DCCB':'#352E26',b1:ac,bN:L?'#BCAE97':'#5E5346',barBd:'none',dotR:'50%',c1:ac,c2:ac2,c3:L?'#D9982A':'#E8B54E',c4:L?'#7A68A6':'#A99BD0',
tm:L?'#2A241D':'#14110E',tmInk:'#EFE6D8',tmMu:'#9C8F7C',tmBar:L?'#352E25':'#1F1A15',tmBarInk:'#B7A994',tmOk:'#8CC7A8',leaf:ac2,svgSt:'none',svgSw:0,svgSwS:'0',ptBd:'3px solid '+bg,rule:'1px solid '+ln};}
window.SceneThemes={resolve:TH,ids:["blockframe","swiss-minimalism","raycast-dark","claude-warm"],keys:{"blockframe":"bf","swiss-minimalism":"sw","raycast-dark":"rc","claude-warm":"cw"}};
})();
