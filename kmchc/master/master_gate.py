#!/usr/bin/env python3
"""명작 검수 게이트 v2 — 형식(v1) + 실체 검증. 하나라도 실패하면 등재 불가."""
import json, sys, re
from collections import Counter

bank = json.load(open('master/master_bank.json', encoding='utf-8'))
CIR='①②③④'
REQUIRED=['id','skill','unit','theme','textbook_theme','track','dok','difficulty',
          'expected_solve_rate','stem','choices','answer','answer_proof','distractors',
          'device','calc_check','scenario','linked_concepts','source','solution']

# ── 해설 하한 ─────────────────────────────────────────────────────
# 문서·batch_template 기준은 300자인데 게이트만 250자였다(28건이 미달인 채 통과 중이었음).
# 300으로 통일하되, 이미 봉인된 T1·T4의 초기 문항 28건은 명시적 동결 목록으로 예외 처리한다.
# ★목록은 리터럴이라 늘어나지 않는다 — 신규 문항이 300자 미만이면 반드시 실패한다★
SOLUTION_MIN = 300
LEGACY_SHORT_SOLUTION = frozenset("""
M00011 M00012 M00017 M00044 M00060 M00065 M00069 M00073 M00074 M00090
M00092 M00095 M00109 M00116 M00129 M00141 M00146 M00156 M00157 M00161
M00175 M00214 M00237 M00247 M00251 M00278 M00302 M00326
""".split())

# ── 오답 유형 허용 집합 ────────────────────────────────────────────
# 게이트가 'type 값이 비어 있지 않은지'만 봐서 오타로 새 유형이 생겨도 통과했다.
ALLOWED_TYPES = frozenset(['proc','sign','surface','conserv','unit',
                           'scale','overgen','causal'])

# ── G3b 보기 길이 산포 ─────────────────────────────────────────────
# 실측: 산포 (max−min)/median 이 0.15 이하이면 정답 길이순위 분포가 균등(2위 29.8%)해지고,
# 0.15를 넘으면 2위로 41~43% 몰린다 = '두 번째로 긴 걸 찍는' 요령이 통한다.
# 원인은 G3(유일 최장 금지)를 오답 패딩으로 해소해 온 관행이므로, 보기 길이를 애초에
# 나란히 맞추는 쪽으로 규칙을 바꾼다. ★소급 적용 불가 — 신규 생산분에만 강제★
G3B_MAX_SPREAD = 0.25
G3B_MIN_MEDIAN = 8          # 이보다 짧은 보기(수치형)는 면제 — 길이가 단서가 될 수 없음
G3B_FROM_ID = 'M01753'      # 이 ID 이상부터 강제

def spread(choices):
    L=sorted(len(str(c)) for c in choices)
    med=(L[1]+L[2])/2 or 1
    return (L[3]-L[0])/med

def g3b_applies(choices):
    L=sorted(len(str(c)) for c in choices)
    return (L[1]+L[2])/2 >= G3B_MIN_MEDIAN

def ans_len_rank(it):
    """정답 보기의 길이 순위(1=가장 긺). 길이 단서 편중 측정용."""
    L=[len(str(c)) for c in it['choices']]
    return sorted(range(4), key=lambda i:-L[i]).index(it['answer'])+1

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
        if x.get('type') and x['type'] not in ALLOWED_TYPES:
            errs.append(f"G3 opt{x.get('opt')} 미등록 오답 유형 '{x['type']}'")
    # G3 단서
    if len(c)==4 and isinstance(a,int):
        Lc=[len(str(x)) for x in c]
        if Lc[a]==max(Lc) and Lc.count(max(Lc))==1: errs.append("G3 정답=유일 최장")
        if Lc[a]==min(Lc) and Lc.count(min(Lc))==1: errs.append("G3 정답=유일 최단")
        # G3b 보기 길이 산포(신규 생산분 강제)
        if fid>=G3B_FROM_ID and g3b_applies(c):
            sp=spread(c)
            if sp>G3B_MAX_SPREAD:
                errs.append(f"G3b 보기 길이 산포 {sp:.2f}>{G3B_MAX_SPREAD} (길이가 단서가 됨 — 보기를 나란히)")
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
    if len(sol)<SOLUTION_MIN and fid not in LEGACY_SHORT_SOLUTION:
        errs.append(f"G9 해설 부족({len(sol)}자 < {SOLUTION_MIN})")
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

# ★G3c 세트 수준: 정답 길이순위 편중 = '몇 번째로 긴 보기를 찍는다'가 통하는지
# 문항 단위로는 전부 결백해도 집합에서 새는 유형이라 세트 검사로만 잡힌다.
WINDOW=100
win=bank[-WINDOW:] if n>=WINDOW else bank
rank_c=Counter(ans_len_rank(it) for it in win)
worst_r,worst_n=rank_c.most_common(1)[0]
worst=worst_n/len(win)
rank_line=" ".join(f"{r}위 {rank_c.get(r,0)/len(win):.0%}" for r in (1,2,3,4))
if worst>=0.50:
    set_errs.append(f"G3c 최근 {len(win)}제 정답 길이순위 {worst_r}위 {worst:.0%} — 길이로 정답을 찍을 수 있음")

print(f"═══ 게이트 v2 · {n}제 ═══")
print(f"  정답분포 {{ {' '.join(f'{CIR[k]}{adist.get(k,0)}' for k in range(4))} }} | 트랙 {dict(Counter(it['track'] for it in bank))} | 난이도 {dict(Counter(it['difficulty'] for it in bank))}")
print(f"  정답 길이순위(최근 {len(win)}제) {rank_line}"
      + ("  ⚠ 편중" if worst>=0.35 else "  ✓ 균등"))
if not fails and not set_errs:
    print(f"  ✅ 전 항목 통과 (형식+실체+세트)")
else:
    for fid,errs in fails: print(f"  🔴 {fid}: "+" / ".join(errs))
    for e in set_errs: print(f"  🔴 [세트] {e}")
sys.exit(1 if (fails or set_errs) else 0)
