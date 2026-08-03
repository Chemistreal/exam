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

_NUMERIC_CHOICE = re.compile(
    r'^\s*[−\-]?\d[\d,]*(?:\.\d+)?\s*'          # 수치 본체
    r'(?:×\s*10\s*[-−]?\d+)?\s*'                # 지수 표기(예외적으로 허용)
    r'(?:[%가-힣a-zA-Z°Ω/·\s]{0,4})?\s*$')      # 짧은 단위 꼬리(분·년·배·번·g·% …)

def pnum_choice(s):
    """'수치 보기'일 때만 수를 돌려준다. 서술형이면 None.
       수치 보기 = 보기 전체가 수치 + 4자 이내 단위. 괄호형 튜플도 제외."""
    t=str(s).strip()
    if '(' in t or not _NUMERIC_CHOICE.match(t):
        return None
    return pnum(t)

def ans_len_rank(it):
    """정답 보기의 길이 순위(1=가장 긺). 길이 단서 편중 측정용.

    ★정답과 길이가 같은 보기가 하나라도 있으면 None 을 돌려준다★(T13 P12 발견).
    '몇 번째로 긴 것을 찍는다'가 단서가 되려면 그 순위가 보기 길이만으로 정해져야 하는데,
    동률이 있으면 학생은 어느 쪽이 앞인지 알 수 없다. 종전에는 목록 차례로 순위를 매겨
    ★길이가 넷 다 같은 문항까지 특정 순위로 집계★ 되었고, 그만큼 편중이 부풀려졌다."""
    L=[len(str(c)) for c in it['choices']]
    a=it['answer']
    if L.count(L[a])>1:
        return None
    return sum(1 for x in L if x>L[a])+1

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
    # G6 수치 오름차순 (4개 전부 '수치 보기'일 때만)
    #   ★오탐 수정★ 이전에는 보기에서 한글·기호를 걷어낸 뒤 남은 숫자를 그대로 읽었다.
    #   그래서 "세슘-137은 반감기가 30년이라…" 같은 서술형이 -13730 으로 파싱돼
    #   수치 보기로 오인되었다(M01797). 수치 보기란 "20 분"·"87.5 %"·"4번"처럼
    #   보기 전체가 수치와 짧은 단위뿐인 것을 말하므로, 그 형태일 때만 검사한다.
    #   (batch_template.verify 는 원래 ^\d 로 시작하는 것만 봐서 이 오탐이 없었다.)
    nums=[pnum_choice(x) for x in c]
    if all(n is not None for n in nums) and nums!=sorted(nums):
        errs.append("G6 수치 보기 오름차순 아님")
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
    # G10 평문 위반 — 은행은 평문이다. 마크다운 강조가 그대로 학생에게 노출된다.
    #   ★T12 P1 2차·P3 2차·P3 4차에서 세 번 발생★ 전부 '수정하면서' 들어갔다.
    #   설계 문서를 쓰던 손으로 해설을 고치면 강조 표기가 딸려 온다 — 기계로 막는다.
    #   ★감사36 확장★ '★' 도 막는다. 이 표시는 설계 문서의 내부 강조인데 M01812 자가진단에
    #   "★핵이 아직 없다★" 가 그대로 남아 학생 화면으로 샜다. 은행 전체에서 그 한 건뿐이었으니
    #   관례가 아니라 유출이다. ★검사가 '**' 만 보고 있어서 게이트를 통과했다.★
    for field in ('stem', 'solution'):
        for mark in ('**', '★'):
            if mark in str(it.get(field, '')):
                errs.append(f"G10 {field} 에 강조 표기({mark}) — 은행은 평문")
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
# ★창은 '최근 100제' 가 아니라 '순위가 정의되는 최근 100제' 다★(T13 P12).
# 동률 문항을 창 안에 두면 표본이 열몇 제로 쪼그라들어 편중이 요동친다.
ranked=[]
win=[]
for it in reversed(bank):
    r=ans_len_rank(it)
    if r is None:
        continue
    ranked.append(r); win.append(it)
    if len(ranked)>=WINDOW:
        break
rank_c=Counter(ranked)
nrk=len(ranked) or 1
# ★기대값은 1/4 이 아니라 1/2 이다★(T13 P12 발견).
# G3 가 '정답이 유일 최장/유일 최단' 을 막으므로, 순위가 정의되는 문항에서 정답은
# 구조적으로 2위 아니면 3위뿐이다 — 실측으로도 은행 325제에서 1위·4위가 정확히 0% 다.
# 종전 임계(0.35 ⚠ / 0.50 🔴)는 4분할 가정 위에 세운 값이라, 2분할 실질에서는
# 균등(50:50)조차 경고로 잡는 눈금이었다. 2분할 기준으로 다시 잡는다.
worst_r,worst_n=(rank_c.most_common(1)[0] if rank_c else (0,0))
worst=worst_n/nrk
edge=(rank_c.get(1,0)+rank_c.get(4,0))/nrk
rank_line=" ".join(f"{r}위 {rank_c.get(r,0)/nrk:.0%}" for r in (1,2,3,4)) + f" (동률 제외 {nrk}/{len(bank)}제)"
if worst>=0.80:
    set_errs.append(f"G3c 최근 {nrk}제(동률 제외) 정답 길이순위 {worst_r}위 {worst:.0%} — 2위·3위 두 갈래에서 한쪽으로 쏠림")
if edge>0:
    set_errs.append(f"G3c 정답이 최장 또는 최단인 문항이 {rank_c.get(1,0)+rank_c.get(4,0)}제 — G3 와 어긋남")

print(f"═══ 게이트 v2 · {n}제 ═══")
print(f"  정답분포 {{ {' '.join(f'{CIR[k]}{adist.get(k,0)}' for k in range(4))} }} | 트랙 {dict(Counter(it['track'] for it in bank))} | 난이도 {dict(Counter(it['difficulty'] for it in bank))}")
print(f"  정답 길이순위(최근 {len(win)}제) {rank_line}"
      + ("  ⚠ 편중(2분할 기준)" if worst>=0.70 else "  ✓ 균등(2분할 기준 50:50)"))
if not fails and not set_errs:
    print(f"  ✅ 전 항목 통과 (형식+실체+세트)")
else:
    for fid,errs in fails: print(f"  🔴 {fid}: "+" / ".join(errs))
    for e in set_errs: print(f"  🔴 [세트] {e}")
sys.exit(1 if (fails or set_errs) else 0)
