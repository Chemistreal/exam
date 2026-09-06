# -*- coding: utf-8 -*-
"""감사38 — T13 2차 (M02051~M02134, 84제) 기계 점검 리포트.

감사37 이 T12 2차에서 걸던 A~L 을 그대로 다시 걸고, 그 뒤에
★T13 P14~P16 과 마감 4제가 값을 치르고 세운 규약★ 에서 기계로 걸 수 있는 것을 더한다.
판정이 필요한 것은 △ 로만 적고 여기서 고치지 않는다.

거는 검사 (A~L 은 감사37 과 같다)
  A  objective 결손 / skill 의 되풀이
  B  ★ 유출 (stem·solution)
  C  해설의 오답 인용이 선지 문면과 글자 그대로 맞는가 (STALE)
  D  해설에 정답 확정 어구가 있는가
  E  distractor 가 정답 아닌 세 자리를 빠짐없이 덮는가 · error/type 결손
  F  G3(정답이 단독 최장·최단) · G3b(길이 산포 0.25)
  G  선지 중복 · 해설 300자 하한
  H  수치 선지 3단 — 오름차순(G6) · 패리티 홀로서기 · 관계식 이상치
  I  축별 최빈값 교차 (두 마디 선지)
  J  answer_expr / calc_check / answer_proof 결손
  K  발문 메아리 (P6 규약)
  L  극성 홀로서기 (P6 규약)

  ★T13 마감 4제가 새로 세운 것★
  M  ★G3g 칸별 최빈값 조합★ — I 를 마디 수와 무관하게 넓힌다. 네 선지가 같은 개수의
     마디로 나뉠 때 마디마다 최빈값을 집어 이으면 정답만 남는가.
     ▸ 살아남는 것이 둘 이상이면 결함이 아니다.
  N  ★선지 사이 포함관계★ — 정답의 낱말 집합이 다른 선지의 부분집합이면, 그 선지가
     참일 때 정답도 참이 되어 화학 없이 지워진다(뒤집어 정답이 남는다).
  O  ★형태 홀로서기 3 : 1★ — 기호(라틴 문자·수식 기호·괄호) 유무로 넷이 3 : 1 로
     갈리고 ★정답이 홀로 있는 쪽★ 이면 소거가 열린다.
  P  ★발문 어미의 형식 기대★ — '묶은 것은? · 고른 것은?' 은 ㄱ·ㄴ·ㄷ 〈보기〉 조합형을
     예고하는데 선지에 그 표지가 없는 자리.
  Q  ★어미 반향★ — 정답 선지의 꼬리말이 발문에 그대로 있고 나머지 셋은 아닌 자리.
"""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
MK = ['①', '②', '③', '④']
LO, HI = 'M02051', 'M02134'

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

CLS = {'A': 'objective', 'B': '★ 유출', 'C': '해설 인용 불일치(STALE)',
       'D': '정답 확정 어구', 'E': 'distractor', 'F': '길이 단서(G3/G3b)',
       'G': '선지·해설 형식', 'H': '수치 선지 3단', 'I': '축별 최빈값 교차',
       'J': '근거 필드', 'K': '발문 메아리', 'L': '극성 홀로서기',
       'M': '★G3g 칸별 최빈값 조합★', 'N': '★선지 포함관계★',
       'O': '★형태 홀로서기 3:1★', 'P': '★발문 어미 형식 기대★', 'Q': '★어미 반향★'}
print(f'감사38 — T13 2차 {LO}~{HI} · {len(items)}제')
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
