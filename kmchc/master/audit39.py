# -*- coding: utf-8 -*-
"""감사39 — T14 2차 (M02215~M02298, 84제) 기계 점검 리포트.

감사38 이 T13 2차에서 걸던 A~Q 를 그대로 다시 걸고, 그 뒤에
★T14 P10~P16 과 마감 4제가 값을 치르고 세운 규약★ 에서 기계로 걸 수 있는 것을 더한다.
판정이 필요한 것은 △ 로만 적고 여기서 고치지 않는다.

거는 검사 (A~Q 는 감사38 과 같다)
  A objective 결손·되풀이 · B ★ 유출 · C 해설 인용 불일치(STALE) · D 정답 확정 어구 ·
  E distractor 결손 · F G3/G3b 길이 단서 · G 선지·해설 형식 · H 수치 선지 3단 ·
  I 축별 최빈값 교차 · J 근거 필드 · K 발문 메아리 · L 극성 홀로서기 ·
  M ★G3g 칸별 최빈값 조합★ · N ★선지 포함관계★ · O ★형태 홀로서기 3:1★ ·
  P ★발문 어미 형식 기대★ · Q ★어미 반향★

  ★T14 마감 4제가 새로 세운 것 — 둘★
  R  ★★잰 값을 기제의 산물로 못 박은 자리★★ — 해설이 '적힌 값 A 와 B 가 그 결과' 꼴로
     ★발문의 수치를 기제의 결과로 귀속★ 하는 자리.
     ▸ ★★첫 판은 버렸다 — 넓게 세웠더니 11/11 오탐이었다★★. 처음에는 '크기를 말하는
       낱말(그만큼·만큼·배·곱)이 네 필드 가운데 일부에만 있는 자리' 로 세웠는데, T14 2차
       84제에서 11건이 울고 ★열한 건 모두 오탐★ 이었다 —
         · 한국어 '그만큼·만큼' 은 대개 ★크기 귀속이 아니라 "그에 따라" 라는 이음말★ 이다
           (M02262·M02277 다섯 곳·M02278·M02279·M02286).
         · 오답 문면을 해설이 인용한 자리(M02226 '차이만큼' · M02252 '잃은 만큼').
         · 발문이 ★배수를 정말로 묻는★ 자리(M02276 '몇 배 더 세게').
         · 수를 견주는 자리(M02219 '같은 수만큼' · M02222 '염소 원자만큼').
       ★검사를 넓히면 오탐이 따라온다 — 넓히기 전에 오탐부터 센다★ 는 규약을 이번에는
       ★세운 뒤에 세었고, 그래서 첫 판을 버렸다.★ 낱말은 신호가 아니었다.
     ▸ 실제 흠은 낱말이 아니라 ★주장의 꼴★ 이었다 — 마감 M02298 해설의 '적힌 값 72 와
       133 이 그 결과야' 가 ★서로 다른 기준으로 잰 두 값의 차(61 pm)를 한 기제에★ 돌렸다.
       그래서 ★'적힌 값 + 수치 + 결과' 라는 꼴★ 로 좁혀 다시 세운다.
     ▸ ★표본이 하나뿐이므로 게이트로 세우지 않는다★ — 이 은행이 절대어 검사에서 세운
       규약을 그대로 따른다(두 테마를 더 재고 정한다).
  S  ★★어휘 반향 — 정답만 발문의 낱말을 되받는 자리★★ — 발문에 있는 두 자 이상 낱말을
     ★정답만★ 되받고 오답 셋은 하나도 되받지 않는 자리. Q(어미 반향)를 꼬리말에서
     낱말 전체로 넓힌다.
     ▸ 마감 1차에 sim 의 A(개념 미형성) 프로필이 ★어휘 대조만으로 정답에 도달했다★ —
       발문·주석이 세 번 되풀이한 낱말을 되받는 선지가 정답 하나뿐이었다. 고친 뒤에는
       그 낱말이 오답으로 옮겨 가 A 가 오답으로 갔다. ★어휘 일치는 오답으로 옮긴다.★
     ▸ 되받는 낱말이 그 문항이 재려는 것과 분리되지 않는 자리(빠진 축 찾기 등)가 있어
       ★차단이 아니라 △ 다.★
"""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
MK = ['①', '②', '③', '④']
LO, HI = 'M02215', 'M02298'

bank = json.load(open(BANK, encoding='utf-8'))
items = [i for i in bank if LO <= i['id'] <= HI]
assert items, '범위에 문항이 없다'

F = []
def rep(it, cls, msg):
    F.append((it['id'], cls, msg))


NUM = re.compile(r'^\s*[-−]?\d')
SYM = re.compile(r'[A-Za-z()\[\]<>=+ₗ₁₂]')

for it in items:
    cs, a, sol = it['choices'], it['answer'], it['solution']

    if not it.get('objective'):
        rep(it, 'A', 'objective 결손')
    elif it['objective'].strip() == it.get('skill', '').strip():
        rep(it, 'A', f"objective 가 skill 의 되풀이 — {it['objective']}")

    for fld in ('stem', 'solution'):
        if '★' in it[fld]:
            rep(it, 'B', f'{fld} 에 ★ 유출')

    for k in range(4):
        if MK[k] + ' ' + cs[k] not in sol:
            rep(it, 'C', f'해설의 {MK[k]} 인용이 선지 문면과 다르다 — 선지 「{cs[k]}」')
    #   ▸ ★확정 어구는 꼴이 여럿이다★ — '①이 옳아' 말고도 '①이 답이야' · '②가
    #     바닥상태야' 처럼 물음에 맞춘 말로 닫는다. 감사37 의 좁은 꼴을 넓혔다.
    if not (any(t in sol for t in ('가 옳아', '이 옳아', f'답이 {MK[a]}'))
            or re.search(re.escape(MK[a]) + r'[이가]\s*[^.]{0,12}(답|옳|맞|이야|야)', sol)):
        rep(it, 'D', '해설에 정답 확정 어구가 없다')

    ds = it.get('distractors', [])
    if sorted(d['opt'] for d in ds) != sorted(set(range(4)) - {a}):
        rep(it, 'E', f"distractor 자리가 어긋난다 — {[d['opt'] for d in ds]}, 정답 {a}")
    for d in ds:
        if not d.get('error') or not d.get('type'):
            rep(it, 'E', f"distractor opt{d['opt']} 의 error/type 결손")

    if len(set(cs)) != 4:
        rep(it, 'G', f'선지 중복 — {cs}')
    if len(sol) < 300:
        rep(it, 'G', f'해설 {len(sol)}자 (하한 300)')
    L = sorted(len(c) for c in cs)
    la = len(cs[a])
    if la == L[3] and L[2] < L[3]:
        rep(it, 'F', f'G3 정답이 단독 최장 — {[len(c) for c in cs]}')
    if la == L[0] and L[0] < L[1]:
        rep(it, 'F', f'G3 정답이 단독 최단 — {[len(c) for c in cs]}')
    mid = (L[1] + L[2]) / 2
    if mid >= 8 and (L[3] - L[0]) / mid > 0.25:
        rep(it, 'F', f'G3b 산포 {(L[3]-L[0])/mid:.3f} — {[len(c) for c in cs]}')

    if all(NUM.match(c) for c in cs):
        head = [int(re.match(r'\s*[-−]?(\d+)', c).group(1)) for c in cs]
        if head != sorted(head):
            rep(it, 'H', f'G6 앞자리 숫자가 오름차순이 아니다 — {head}')
        par = [h % 2 for h in head]
        if Counter(par)[par[a]] == 1:
            rep(it, 'H', f'패리티로 정답만 남는다 — 앞자리 {head}')

    parts = [c.split(' ') for c in cs]
    if all(len(p) == 2 for p in parts) and len({p[0] for p in parts}) < 4 \
                                       and len({p[1] for p in parts}) < 4:
        x = [p[0] for p in parts]; y = [p[1] for p in parts]
        tx = Counter(x).most_common(1)[0]; ty = Counter(y).most_common(1)[0]
        if tx[1] > 1 and ty[1] > 1 and [i for i in range(4)
                                        if x[i] == tx[0] and y[i] == ty[0]] == [a]:
            rep(it, 'I', f'축별 최빈값 교차가 정답을 가리킨다 — {tx[0]} × {ty[0]}')

    for fld in ('answer_proof', 'calc_check', 'device', 'scenario'):
        if not it.get(fld):
            rep(it, 'J', f'{fld} 결손')

    def inste(c):
        m = NUM.match(c) and re.match(r'\s*[-−]?(\d+)', c)
        return bool(m) and bool(re.search(r'(?<!\d)' + m.group(1) + r'(?!\d)', it['stem']))
    if NUM.match(cs[a]) and inste(cs[a]) and not any(inste(c) for i, c in enumerate(cs) if i != a):
        rep(it, 'K', f'정답값 「{cs[a]}」 만 발문에 그대로 있다')

    neg = [i for i, c in enumerate(cs) if any(t in c for t in ('않', '없', '아니', '못'))]
    if neg == [a]:
        rep(it, 'L', f'정답만 부정형 — 극성으로 홀로 선다 「{cs[a]}」')

    # ── M ★G3g 칸별 최빈값 조합★ ────────────────────────────────────────
    toks = [c.split() for c in cs]
    if len(toks[0]) >= 2 and all(len(t) == len(toks[0]) for t in toks):
        picks = []
        for col in zip(*toks):
            cc = Counter(col).most_common()
            win = [v for v, k in cc if k == cc[0][1]]
            picks.append(win[0] if len(win) == 1 else None)
        if any(p is not None for p in picks):
            surv = [i for i, t in enumerate(toks)
                    if all(p is None or t[k] == p for k, p in enumerate(picks))]
            if surv == [a]:
                rep(it, 'M', f'칸별 최빈값 조합이 정답만 남긴다 — {" ".join(p or "·" for p in picks)}')

    # ── N ★선지 사이 포함관계★ ─────────────────────────────────────────
    #   낱말 집합으로 본다. 정답의 낱말이 다른 선지의 낱말에 모두 들어 있으면,
    #   그 선지가 참일 때 정답도 참이 되기 쉬워 소거의 실마리가 된다.
    #   ▸ ★낱말 집합으로 보면 오탐만 나온다★ — '황(원자 번호 16)' 과 '염소(원자 번호 17)'
    #     처럼 한 글자 낱말이 빠져 서로를 품는 것으로 보인다(감사38 초판이 5건 모두 오탐).
    #     문자열이 통째로 들어 있을 때만 짚는다 — 뜻의 포함관계는 손으로 볼 일이다.
    for i, c in enumerate(cs):
        if i == a:
            continue
        if len(cs[a]) >= 6 and cs[a] in c:
            rep(it, 'N', f'정답이 {MK[i]} 안에 통째로 들어 있다 — 「{cs[a]}」 ⊂ 「{c}」')
        elif len(c) >= 6 and c in cs[a]:
            rep(it, 'N', f'{MK[i]} 가 정답 안에 통째로 들어 있다 — 「{c}」 ⊂ 「{cs[a]}」')

    # ── O ★형태 홀로서기 3 : 1★ ────────────────────────────────────────
    has = [bool(SYM.search(c)) for c in cs]
    if Counter(has)[has[a]] == 1:
        rep(it, 'O', f'기호 유무로 정답만 홀로 선다 — {["기호" if h else "순우리말" for h in has]}')

    # ── P ★발문 어미의 형식 기대★ ──────────────────────────────────────
    #   ▸ ★'짝지은 것은?' 은 빼야 한다★ — 두 마디('X — Y')로 된 선지의 표준 어미이고
    #     〈보기〉를 예고하지 않는다(감사38 초판이 4건 모두 이 꼴로 오탐).
    if re.search(r'(묶은|고른)\s*것은', it['stem']) and '—' not in ''.join(cs) and \
            not any(t in ''.join(cs) for t in ('ㄱ', 'ㄴ', 'ㄷ')):
        rep(it, 'P', '발문이 〈보기〉 조합형을 예고하는데 선지에 ㄱ·ㄴ·ㄷ 이 없다')

    # ── Q ★어미 반향★ ──────────────────────────────────────────────────
    tails = [c.strip()[-3:] for c in cs]
    if len(tails[a]) == 3 and tails[a] in it['stem'] and \
            not any(t in it['stem'] for i, t in enumerate(tails) if i != a):
        rep(it, 'Q', f'정답의 꼬리말 「{tails[a]}」 만 발문에 있다')

    # ── R ★★잰 값을 기제의 산물로 못 박은 자리★★ (T14 마감 · 첫 판은 11/11 오탐으로 버렸다)
    #   ▸ '적힌 값 …이 그 결과' 꼴 — 발문의 수치를 기제의 결과로 귀속하는 주장.
    #     서로 다른 기준으로 잰 값이 섞여 있으면 그 귀속이 과잉이 된다.
    for _f in ('answer_proof', 'calc_check', 'solution'):
        _t = it.get(_f) or ''
        for _m in re.finditer(r'(적힌|주어진) 값[^.\n]{0,40}', _t):
            if re.search(r'\d', _m.group(0)) and '결과' in _m.group(0):
                rep(it, 'R', f'{_f} 가 잰 값을 기제의 산물로 못 박는다 — {_m.group(0)[:34]}')

    # ── S ★★어휘 반향 — 정답만 발문의 낱말을 되받는다★★ (T14 마감) ────────
    #   ▸ 두 자 이상 한글 낱말만 센다. 조사·어미가 붙는 자리를 피해 어간 2자로 자른다.
    def _w(s):
        return {t[:2] for t in re.findall(r'[가-힣]{2,}', s)}

    stw = _w(it['stem'])
    echo = [len(_w(c) & stw) for c in cs]
    if echo[a] >= 2 and all(echo[i] == 0 for i in range(4) if i != a):
        shared = sorted(_w(cs[a]) & stw)[:4]
        rep(it, 'S', f"정답만 발문의 낱말을 되받는다 — {'·'.join(shared)}")

CLS = {'A': 'objective', 'B': '★ 유출', 'C': '해설 인용 불일치(STALE)',
       'D': '정답 확정 어구', 'E': 'distractor', 'F': '길이 단서(G3/G3b)',
       'G': '선지·해설 형식', 'H': '수치 선지 3단', 'I': '축별 최빈값 교차',
       'J': '근거 필드', 'K': '발문 메아리', 'L': '극성 홀로서기',
       'M': '★G3g 칸별 최빈값 조합★', 'N': '★선지 포함관계★',
       'O': '★형태 홀로서기 3:1★', 'P': '★발문 어미 형식 기대★', 'Q': '★어미 반향★',
       'R': '★잰 값을 기제의 산물로★', 'S': '★어휘 반향(정답만)★'}
print(f'감사39 — T14 2차 {LO}~{HI} · {len(items)}제')
print('=' * 74)
c = Counter(x[1] for x in F)
for k in sorted(CLS):
    print(f'  {k} {CLS[k]:<24} {c.get(k, 0):>3} 건')
print('-' * 74)
print(f'  합계 {len(F)} 건 · 깨끗한 문항 {len(items) - len({x[0] for x in F})}/{len(items)}')
print('=' * 74)
for k in sorted(CLS):
    rows = [x for x in F if x[1] == k]
    if not rows:
        continue
    print(f'\n■ {k} {CLS[k]} — {len(rows)} 건')
    for fid, _, msg in rows:
        print(f'  {fid}  {msg}')
