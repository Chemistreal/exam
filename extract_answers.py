#!/usr/bin/env python3
# 해설/답 PDF에서 정답(①②③④)·정답률(%)·문항→페이지 매핑을 자동 추출 → JSON
# 사용: python3 extract_answers.py <해설.pdf> [out.json]
# 출력: {"ans":{n:정답}, "rate":{n:정답률}, "qpage":{n:PDF페이지}, "n":문항수, "multi":[복수정답],
#        "blocks":{n:풀이텍스트}, "method":"label|circle"}
# 정답은 1페이지 정답표에서 직접 파싱(가장 신뢰도 높음).
# 본문은 '문제 N' 라벨이 있으면 라벨 기준, 없으면 단독 동그라미 기준으로 페이지·정답률·풀이 추출.
import sys, re, subprocess, json
CIRC={'①':1,'②':2,'③':3,'④':4}
pdf=sys.argv[1]; outp=sys.argv[2] if len(sys.argv)>2 else None
txt=subprocess.run(['pdftotext','-layout',pdf,'-'],capture_output=True,text=True).stdout
pages=txt.split('\f')

# 1) 정답표(1페이지): (번호, 정답) 모두. 복수정답(②,③) 지원.
ans={}; multi=[]
for ln in pages[0].split('\n'):
    for m in re.finditer(r'(\d+)\s+([①②③④])(?:\s*,\s*([①②③④]))?', ln):
        n=int(m.group(1))
        if m.group(3): ans[n]=CIRC[m.group(2)]; multi.append({'n':n,'answers':[CIRC[m.group(2)],CIRC[m.group(3)]]})
        else: ans[n]=CIRC[m.group(2)]

# 2) 본문 라벨/동그라미 판별
body_pages=pages[1:]
all_lines=[]
for pi,pg in enumerate(body_pages):
    for ln in pg.split('\n'): all_lines.append((pi+2,ln))  # PDF page = pi+2
label_idx=[(i,int(m.group(1))) for i,(pp,ln) in enumerate(all_lines) for m in [re.match(r'\s*문제\s*(\d+)\b',ln)] if m]
method='label' if len(label_idx)>=len(ans)*0.8 else 'circle'

qpage={}; rate={}; blocks={}
def clean(seg):
    out=[]
    for _,l in seg:
        s=re.sub(r'^\s*문제\s*\d+\s*','',l).strip()
        if not s or '조준모의고사' in s or '테스트' in s or '【' in s or re.match(r'^[━─\-\s]+$',s) or s in CIRC: continue
        out.append(s)
    return ' '.join(out)

if method=='label':
    for k,(idx,n) in enumerate(label_idx):
        qpage[n]=all_lines[idx][0]
        end=label_idx[k+1][0] if k+1<len(label_idx) else len(all_lines)
        blocks[n]=clean(all_lines[idx:end])
        for j in range(idx,min(idx+4,end)):
            m=re.search(r'정답률\s*:\s*(\d+)%',all_lines[j][1])
            if m: rate[n]=int(m.group(1)); break
else:
    marks=[(i,pp) for i,(pp,ln) in enumerate(all_lines) if ln.strip() in CIRC]
    for k,(idx,pp) in enumerate(marks):
        n=k+1
        qpage[n]=pp
        end=marks[k+1][0] if k+1<len(marks) else len(all_lines)
        blocks[n]=clean(all_lines[idx+1:end])
        for j in range(idx-1,max(0,idx-6),-1):
            m=re.search(r'정답률\s*:\s*(\d+)%',all_lines[j][1])
            if m: rate[n]=int(m.group(1)); break

out={'ans':ans,'rate':rate,'qpage':qpage,'n':len(ans),'multi':multi,'blocks':blocks,'method':method}
js=json.dumps(out,ensure_ascii=False)
if outp: open(outp,'w',encoding='utf-8').write(js)
else: print(js)
sys.stderr.write(f"정답 {len(ans)} | 방식 {method} | 정답률 {len(rate)} | 페이지매핑 {len(qpage)} | 복수정답 {[x['n'] for x in multi]}\n")
