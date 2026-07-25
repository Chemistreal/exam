#!/usr/bin/env python3
"""명작 검수 게이트 v2 — 형식(v1) + 실체 검증. 하나라도 실패하면 등재 불가."""
import json, sys, re
from collections import Counter

bank = json.load(open('master/master_bank.json', encoding='utf-8'))
CIR='①②③④'
REQUIRED=['id','skill','unit','theme','textbook_theme','track','dok','difficulty',
          'expected_solve_rate','stem','choices','answer','answer_proof','distractors',
          'device','calc_check','scenario','linked_concepts','source','solution']

def pnum(s):
    s=str(s).replace('\u2212','-')
    s=re.sub(r'[%가-힣a-zA-Z\s()]','',str(s)).replace('×10','e')
    m=re.search(r'-?\d+\.?\d*(?:e-?\d+)?',s)
    try: return float(m.group()) if m else None
    except: return None

fails=[]; skill_cnt=Counter()
for it in bank:
    fid=it.get('id','?'); errs=[]
    # 스키마
    miss=[f for f in REQUIRED if f not in it or it[f] in (None,'',[])]
    if miss: errs.append(f"스키마 누락 {miss}")
    c=it.get('choices',[]); a=it.get('answer')
    if len(c)!=4: errs.append("G6 선지 4개 아님")
    if not isinstance(a,int) or not(0<=a<4): errs.append("G2 정답 인덱스 오류")
    if len(set(c))!=len(c): errs.append("G2 선지 중복")
    # G3 형식
    d=it.get('distractors',[])
    if len(d)!=3: errs.append(f"G3 오답 메타 {len(d)}개")
    for x in d:
        if not x.get('error') or not x.get('type'): errs.append(f"G3 opt{x.get('opt')} 라벨/유형 없음")
        if x.get('opt')==a: errs.append("G3 오답이 정답 지목")
    # G3 단서
    if len(c)==4 and isinstance(a,int):
        Lc=[len(str(x)) for x in c]
        if Lc[a]==max(Lc) and Lc.count(max(Lc))==1: errs.append("G3 정답=유일 최장")
        if Lc[a]==min(Lc) and Lc.count(min(Lc))==1: errs.append("G3 정답=유일 최단")
    # G6 수치 오름차순 (4개 전부 수치 파싱될 때)
    nums=[pnum(x) for x in c]
    if all(n is not None for n in nums) and nums!=sorted(nums):
        # 튜플형 "(a, b, c)"은 첫 수만 잡혀 오탐 → 괄호 포함 보기는 제외
        if not any('(' in str(x) for x in c): errs.append("G6 수치 보기 오름차순 아님")
    # ★실체: expr 재계산
    ae=it.get('answer_expr')
    if ae:
        try:
            v=eval(ae,{"__builtins__":{}})
            cv=pnum(c[a])
            if cv is None or abs(v-cv)>0.01*max(1,abs(cv)): errs.append(f"G1 answer_expr={v:.4g} ≠ 보기 {c[a]}")
        except Exception as e: errs.append(f"G1 expr 오류 {e}")
    for x in d:
        if x.get('expr'):
            try:
                v=eval(x['expr'],{"__builtins__":{}})
                cv=pnum(c[x['opt']])
                if cv is None or abs(v-cv)>0.02*max(1,abs(cv)): errs.append(f"G3 opt{x['opt']} expr={v:.4g} ≠ 보기 {c[x['opt']]}")
            except Exception as e: errs.append(f"G3 opt{x['opt']} expr 오류 {e}")
    # G9 해설
    sol=it.get('solution','')
    if len(sol)<250: errs.append(f"G9 해설 부족({len(sol)}자)")
    else:
        wrong_mention=sum(1 for i in range(4) if i!=a and CIR[i] in sol)
        if wrong_mention<3: errs.append("G9 해설에 오답 3개 미언급")
    # 필수 의도서
    if not it.get('answer_proof'): errs.append("G1 증명 없음")
    if not it.get('device'): errs.append("G4 장치 없음")
    skill_cnt[it.get('skill','')]+=1
    if errs: fails.append((fid,errs))

# 세트 수준 검사
n=len(bank)
adist=Counter(it['answer'] for it in bank)
set_errs=[]
if n>=12:
    for pos in range(4):
        share=adist.get(pos,0)/n
        if share==0: set_errs.append(f"정답 {CIR[pos]} 0% — 세트 뚫림")
        elif share>0.45: set_errs.append(f"정답 {CIR[pos]} {share:.0%} 편중")
over=[(s,c) for s,c in skill_cnt.items() if c>20]
for s,c in over: set_errs.append(f"G7 스킬 상한 초과 '{s}' {c}/20")

print(f"═══ 게이트 v2 · {n}제 ═══")
print(f"  정답분포 {{ {' '.join(f'{CIR[k]}{adist.get(k,0)}' for k in range(4))} }} | 트랙 {dict(Counter(it['track'] for it in bank))} | 난이도 {dict(Counter(it['difficulty'] for it in bank))}")
if not fails and not set_errs:
    print(f"  ✅ 전 항목 통과 (형식+실체+세트)")
else:
    for fid,errs in fails: print(f"  🔴 {fid}: "+" / ".join(errs))
    for e in set_errs: print(f"  🔴 [세트] {e}")
sys.exit(1 if (fails or set_errs) else 0)
