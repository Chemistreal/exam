#!/usr/bin/env python3
"""
selfaudit.py — 기계적 자기복제 감사기 (Opus 단독 체제 보완 도구)

배경: 감사 14호(Fable)가 Opus 자기감사의 구조적 약점을 실증함 —
계산·경계·파서층은 무결하나, '자기복제 판정층'에서 체계적으로 관대(거울/보완값/소재교체 승인).
편향은 같은 모델의 결심으로 교정 불가 → 판단 대신 기계적 신호로 대체한다.

이 도구는 신규 문항 각각에 대해 '이전 전체 문항' 중 구조적 충돌을 탐지하고,
충돌 시 기본값을 △(review)로 강제한다. 통과하려면 명시적 근거가 있어야 한다(hostile-reviewer 기본값).

탐지 규칙(모두 객관적, 판단 배제):
  R1 동일 scenario(정확)                         → 강한 충돌
  R2 동일 skill(정확)                             → 강한 충돌
  R3 동일 계산 골격 + 동일 linked + 동일 정답값    → ★거울/원소·프레임 교체 후보★ (M785/M864형)
  R4 동일 계산 골격 + 동일 linked (값 무관)        → 워크호스 반복 후보
  R5 보완값 짝: 동일 골격 + 정답값 a,b가 a+b∈{1,10,100,...} → ★보완값 후보★ (M810/M780형)
사용: python3 selfaudit.py <lo_id> <hi_id>   (예: python3 selfaudit.py M00823 M00887)
"""
import json, re, sys, os

HERE=os.path.dirname(os.path.abspath(__file__))

def load():
    return json.load(open(os.path.join(HERE,'master_bank.json'),encoding='utf-8'))

def skeleton(it):
    """계산 골격: 수를 #로 치환한 연산 패턴. 개념형은 '' 반환."""
    e=it.get('answer_expr') or ''
    if not e: return ''
    e=e.replace('×','*')
    sk=re.sub(r'[0-9]+\.?[0-9]*(e-?[0-9]+)?','#',e)
    sk=re.sub(r'\s+','',sk)
    return sk

def ans_val(it):
    """정답 보기의 수치(대표 1개). 없으면 None."""
    c=it['choices'][it['answer']]
    c2=c.replace('×10','e').replace('−','-')
    m=re.search(r'-?[0-9]+\.?[0-9]*(e-?[0-9]+)?',c2)
    if not m: return None
    try: return float(m.group())
    except: return None

def concept_key(it):
    """개념형 근사 키: skill + linked (계산 골격이 없을 때)."""
    return (it['skill'], tuple(it.get('linked_concepts',[])))

def is_round_complement(a,b):
    if a is None or b is None: return False
    for total in [1,10,100,1000]:
        if abs((a+b)-total)<1e-6 and a>0 and b>0 and a!=b: return True
    return False

def audit(lo,hi):
    bank=load()
    idx={it['id']:i for i,it in enumerate(bank)}
    # ★대조 대상 = 자기 자신을 뺀 은행 전체★
    #   이전에는 prior = (id < lo) 였다. 그래서 ①같은 배치 안 10제끼리는 서로 대조되지
    #   않았고 ②이미 등재된 구간을 소급 감사할 수도 없었다(뒤 문항이 안 보임).
    #   자기 자신만 빼면 두 사각지대가 함께 사라진다.
    targets=[it for it in bank if lo<=it['id']<=hi]
    # 문항 특징 인덱스 — 전체를 담고, 대조 시점에 자기 자신만 제외한다
    by_scn=dict(); by_skill=dict()
    skel_map=dict()   # (skel, linked) -> list of (id, ans_val)
    for it in bank:
        by_scn.setdefault(it['scenario'],[]).append(it['id'])
        by_skill.setdefault(it['skill'],[]).append(it['id'])
        sk=skeleton(it)
        if sk:
            key=(sk,tuple(it.get('linked_concepts',[])))
            skel_map.setdefault(key,[]).append((it['id'],ans_val(it)))
    flags=[]
    for it in targets:
        hits=[]; me=it['id']
        r1=[p for p in by_scn.get(it['scenario'],[]) if p!=me]
        if r1: hits.append(('R1 동일 scenario',r1[:3]))
        r2=[p for p in by_skill.get(it['skill'],[]) if p!=me]
        if r2: hits.append(('R2 동일 skill',r2[:3]))
        sk=skeleton(it)
        if sk:
            key=(sk,tuple(it.get('linked_concepts',[])))
            av=ans_val(it)
            same=[(p,v) for p,v in skel_map.get(key,[]) if p!=me]
            if same:
                eqval=[pid for pid,pv in same if pv is not None and av is not None and abs(pv-av)<1e-6]
                if eqval: hits.append(('R3 골격+정답값 동일(거울/교체 후보)',eqval[:3]))
                comp=[pid for pid,pv in same if is_round_complement(av,pv)]
                if comp: hits.append(('R5 보완값 짝(complement)',comp[:3]))
                other=[pid for pid,pv in same if pid not in eqval and pid not in comp]
                if other: hits.append(('R4 골격+linked 동일(워크호스)',other[:3]))
        if hits:
            flags.append((it['id'],it['skill'],hits))
    return flags,len(targets)

if __name__=='__main__':
    lo=sys.argv[1] if len(sys.argv)>1 else 'M00001'
    hi=sys.argv[2] if len(sys.argv)>2 else 'M99999'
    flags,n=audit(lo,hi)
    print(f"═══ selfaudit: {lo}~{hi} ({n}제) 대상, 이전 전체와 구조 충돌 검사 ═══")
    strong=[f for f in flags if any(r[0].startswith(('R1','R2','R3','R5')) for r in f[2])]
    workhorse=[f for f in flags if f not in strong]
    print(f"★강한 충돌(R1/R2/R3/R5 — 기본 △, 근거 없으면 교체): {len(strong)}건★")
    for fid,sk,hits in strong:
        print(f"  {fid} [{sk}]")
        for r,ids in hits:
            if r.startswith(('R1','R2','R3','R5')): print(f"      ⚠ {r} ← {ids}")
    print(f"\n워크호스 반복(R4 — 사다리 허용, 창당 1회 권고): {len(workhorse)}건")
    for fid,sk,hits in workhorse:
        r4=[h for h in hits if h[0].startswith('R4')]
        print(f"  {fid} [{sk}] ← {r4[0][1] if r4 else ''}")
    print(f"\n판정: 강한 충돌 {len(strong)}건 = 기계적 △ 후보 · 클린 {n-len(flags)}제")
