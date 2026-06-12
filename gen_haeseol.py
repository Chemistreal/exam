#!/usr/bin/env python3
# 해설 PDF + 문항데이터 → 해설-{id}.html (정답/정답률/개념 요약표 + 문항 네비 + 원본 해설지 이미지)
# 사용: python3 gen_haeseol.py config.json
#   config.json = {"id","title","range","sub","sol_pdf","dpi":130,"quality":72,
#                  "questions":[[n,ans,p,area,type], ...]}
import sys, json, re, subprocess, base64, os, glob, tempfile
cfg=json.load(open(sys.argv[1],encoding='utf-8'))
EID=cfg['id']; CHO=["①","②","③","④"]; CIRC={'①':1,'②':2,'③':3,'④':4}
dpi=cfg.get('dpi',130); q=cfg.get('quality',72)
# 1) 문항→PDF페이지 매핑 (단독 동그라미 줄)
txt=subprocess.run(['pdftotext','-layout',cfg['sol_pdf'],'-'],capture_output=True,text=True).stdout
allpages=txt.split('\f')
if cfg.get('qpage'):
    qpage={int(k):int(v) for k,v in cfg['qpage'].items()}; qn=len(qpage)
else:
    # 1페이지=정답표 가정, 2페이지부터 풀이. 단독 동그라미로 문항 경계.
    qpage={}; qn=0
    for pi,pg in enumerate(allpages[1:]):
        for ln in pg.split('\n'):
            if ln.strip() in CIRC:
                qn+=1; qpage[qn]=pi+2
# PDF 실제 페이지(정답표 포함 1-indexed)에서 문항 페이지 범위
qpages=sorted(set(qpage.values()))
# 2) 해당 페이지만 래스터화
tmp=tempfile.mkdtemp()
lo,hi=min(qpages),max(qpages)
subprocess.run(['pdftoppm','-jpeg','-r',str(dpi),'-jpegopt',f'quality={q}','-f',str(lo),'-l',str(hi),cfg['sol_pdf'],tmp+'/p'],check=True)
def imgb64(pdfpage):
    cands=glob.glob(f'{tmp}/p-*{pdfpage}.jpg')+[f'{tmp}/p-{pdfpage:02d}.jpg',f'{tmp}/p-{pdfpage:03d}.jpg']
    for f in cands:
        if os.path.exists(f): return base64.b64encode(open(f,'rb').read()).decode()
    return None
bypage={}
for qq,pp in qpage.items(): bypage.setdefault(pp,[]).append(qq)
for pp in bypage: bypage[pp].sort()
# 3) 데이터
AC={"--teal-d":["화학의 기초","화학식량","몰","기체","양적관계","액체","고체","용액"],"--cobalt":["원소의 기원","원자모형","전자배치","주기율"],"--brass-d":["분자의 구조","분자의 모양","분자의 극성","반응","화학반응"]}
def acol(area):
    for c,lst in AC.items():
        if area in lst: return c
    return "--ink-3"
rows="".join(f'<tr><td class="mono">{n}</td><td class="ans">{CHO[a-1]}</td><td>{(str(p)+"%") if p is not None else "-"}</td><td><span class="area-pill" style="color:var({acol(ar)})">{ar}</span></td><td class="typ">{ty}</td></tr>' for n,a,p,ar,ty in cfg['questions'])
nav=""  # per-문항 해설 하이퍼링크 제거(요청)
pages_html=""
for pp in sorted(bypage):
    qs=bypage[pp]; bb=imgb64(pp)
    if not bb: continue
    anchors="".join(f'<span id="q{qq}" class="qa"></span>' for qq in qs)
    lab=f"문항 {qs[0]}~{qs[-1]}" if len(qs)>1 else f"문항 {qs[0]}"
    pages_html+=f'<section class="pg">{anchors}<div class="pg__lab"><span class="pg__no">해설지 p.{pp-1}</span>{lab}</div><img class="pg__img" src="data:image/jpeg;base64,{bb}" alt="{lab} 해설" loading="lazy"></section>\n'
# 4) 템플릿(해설.html과 동일 디자인) 로드 후 치환
tpl=open('_haeseol_template.html',encoding='utf-8').read()
html=(tpl.replace('{{TITLE}}',cfg['title']).replace('{{SUB}}',cfg.get('sub',''))
        .replace('{{NAV}}',nav).replace('{{ROWS}}',rows).replace('{{PAGES}}',pages_html))
open(f'해설-{EID}.html','w',encoding='utf-8').write(html)
print(f'해설-{EID}.html 생성: {round(os.path.getsize(f"해설-{EID}.html")/1024/1024,2)}MB · 문항 {qn} · 페이지 {len(bypage)}')
