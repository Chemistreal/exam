# -*- coding: utf-8 -*-
"""감사37 — T12 2차 (M01887~M01970, 84제) 기계 점검 리포트.

감사36 이 T12 1차(M01807~M01886, 80제)에서 잡은 세 부류를 그대로 다시 걸고,
그 뒤에 층5 순회가 새로 세운 규약(패리티·2×2 교차·교과서 관용·주어 닫기)에서
기계로 걸 수 있는 것을 더한다. 판정이 필요한 것은 △ 로만 적고 고치지 않는다.

거는 검사
  A  objective 결손 / skill 의 되풀이
  B  ★ 유출 (stem·solution)
  C  해설의 오답 인용이 선지 문면과 글자 그대로 맞는가 (STALE)
  D  해설에 '① …' 꼴로 네 선지가 모두 인용됐는가 · '가/이 옳아' 가 있는가
  E  distractor 가 정답 아닌 세 자리를 빠짐없이 덮는가 · error/type 결손
  F  G3(정답이 단독 최장·최단) · G3b(길이 산포 0.25)
  G  선지 중복 · 해설 300자 하한
  H  ★수치 선지 검사 3단★ — 앞자리 숫자 오름차순(G6) · 값의 패리티가 한쪽으로
     쏠려 정답만 남는지 · 선지들이 공유하는 관계식을 어기는 선지가 하나뿐인지
  I  ★축별 최빈값 교차★ — 선지가 'X Y' 두 마디로 갈리는 문항에서 두 축의
     최빈값이 만나는 칸이 정답인가
  J  answer_expr / calc_check / answer_proof 결손
  K  ★발문 메아리★ — 수치 정답이 발문에 그대로 적힌 수인가 (T13 P6 규약 소급)
  L  ★극성 홀로서기★ — 부정 표지를 가진 선지가 하나뿐인가 (T13 P6 규약 소급)
"""
import json, os, re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(HERE, 'master_bank.json')
MK = ['①', '②', '③', '④']
LO, HI = 'M01887', 'M01970'

bank = json.load(open(BANK, encoding='utf-8'))
items = [i for i in bank if LO <= i['id'] <= HI]
assert items, '범위에 문항이 없다'

F = []                                   # (문항, 부류, 내용)
def rep(it, cls, msg):
    F.append((it['id'], cls, msg))


NUM = re.compile(r'^\s*[-−]?\d')

for it in items:
    cs, a, sol = it['choices'], it['answer'], it['solution']

    # A ── objective
    if not it.get('objective'):
        rep(it, 'A', 'objective 결손')
    elif it['objective'].strip() == it.get('skill', '').strip():
        rep(it, 'A', f"objective 가 skill 의 되풀이 — {it['objective']}")

    # B ── ★ 유출
    for fld in ('stem', 'solution'):
        if '★' in it[fld]:
            rep(it, 'B', f'{fld} 에 ★ 유출')

    # C·D ── 해설의 선지 인용
    for k in range(4):
        if MK[k] + ' ' + cs[k] not in sol:
            rep(it, 'C', f'해설의 {MK[k]} 인용이 선지 문면과 다르다 — 선지 「{cs[k]}」')
    # ▸ 부정 발문('…없는 것은?' · '…아닌 것은?')에서는 "①이 옳아" 가 오히려 어긋난다.
    #   M01938 이 '그래서 답이 ①이야' 로 적은 것은 결함이 아니라 올바른 처리다.
    #   확정 어구는 꼴을 넓혀 본다.
    if not any(t in sol for t in ('가 옳아', '이 옳아', f'답이 {MK[a]}', f'{MK[a]}이야')):
        rep(it, 'D', '해설에 정답 확정 어구가 없다')

    # E ── distractor
    ds = it.get('distractors', [])
    if sorted(d['opt'] for d in ds) != sorted(set(range(4)) - {a}):
        rep(it, 'E', f"distractor 자리가 어긋난다 — {[d['opt'] for d in ds]}, 정답 {a}")
    for d in ds:
        if not d.get('error') or not d.get('type'):
            rep(it, 'E', f"distractor opt{d['opt']} 의 error/type 결손")

    # F·G ── 길이·중복
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

    # H ── 수치 선지 3단
    if all(NUM.match(c) for c in cs):
        head = [int(re.match(r'\s*[-−]?(\d+)', c).group(1)) for c in cs]
        if head != sorted(head):
            rep(it, 'H', f'G6 앞자리 숫자가 오름차순이 아니다 — {head}')
        par = [h % 2 for h in head]
        if Counter(par)[par[a]] == 1:
            rep(it, 'H', f'패리티로 정답만 남는다 — 앞자리 {head}')
        # 두 수를 짝지은 꼴이면 관계식 이상치를 센다
        pr = [re.findall(r'\d+', c) for c in cs]
        if all(len(p) == 2 for p in pr):
            v = [(int(x), int(y)) for x, y in pr]
            for r, name in ((lambda p: p[1] == 2 * p[0], '뒤 = 2 × 앞'),
                            (lambda p: p[1] == p[0] ** 2, '뒤 = 앞²')):
                ok = [i for i, p in enumerate(v) if r(p)]
                if len(ok) == 3 and a in ok:
                    bad = (set(range(4)) - set(ok)).pop()
                    rep(it, 'H', f'관계식 「{name}」 을 어기는 선지가 {MK[bad]} 하나뿐 — '
                                 f'이상치로 지워지고 정답이 좁혀진다 {v}')

    # I ── 축별 최빈값 교차
    parts = [c.split(' ') for c in cs]
    if all(len(p) == 2 for p in parts) and len({p[0] for p in parts}) < 4 \
                                       and len({p[1] for p in parts}) < 4:
        x = [p[0] for p in parts]
        y = [p[1] for p in parts]
        cx, cy = Counter(x), Counter(y)
        tx, ty = cx.most_common(1)[0], cy.most_common(1)[0]
        if tx[1] > 1 and ty[1] > 1:
            cross = [i for i in range(4) if x[i] == tx[0] and y[i] == ty[0]]
            if cross == [a]:
                rep(it, 'I', f'축별 최빈값 교차가 정답을 가리킨다 — '
                             f'{tx[0]}({tx[1]}) × {ty[0]}({ty[1]}) → {MK[a]}')

    # J ── 근거 필드
    for fld in ('answer_proof', 'calc_check', 'device', 'scenario'):
        if not it.get(fld):
            rep(it, 'J', f'{fld} 결손')

    # K ── ★발문 메아리★ (T13 P6 에서 새로 세운 규약을 소급 적용)
    #   정답이 수치일 때 그 수가 발문에 그대로 적혀 있으면, 아무것도 모르는 학생의
    #   첫 반사(발문에 나온 수 고르기)가 정답에 착지한다.
    #   ▸ ★메아리는 정답에만 있을 때 단서다.★ 네 선지의 수가 모두 발문에 적혀 있으면
    #     (자료를 표로 준 문항) 발문에 있다는 사실이 아무것도 좁혀 주지 않는다.
    def inste(c):
        m = NUM.match(c) and re.match(r'\s*[-−]?(\d+)', c)
        return bool(m) and bool(re.search(r'(?<!\d)' + m.group(1) + r'(?!\d)', it['stem']))
    if NUM.match(cs[a]) and inste(cs[a]) and not any(inste(c) for i, c in enumerate(cs) if i != a):
        rep(it, 'K', f'정답값 「{cs[a]}」 만 발문에 그대로 있다 — 나머지 셋은 발문에 없다')

    # L ── ★극성 홀로서기★ (같은 규약)
    #   부정 표지를 가진 선지가 하나뿐이면 그 하나가 형태로 도드라진다.
    #   ▸ 오답 하나만 부정형인 경우(18 → 13 건)는 걸지 않는다. 실측에서 걸린 것은
    #     ★정답★ 이 홀로 부정형일 때뿐이고, 오답 쪽은 뜻을 담느라 자연히 생긴다.
    neg = [i for i, c in enumerate(cs) if any(t in c for t in ('않', '없', '아니', '못'))]
    if neg == [a]:
        rep(it, 'L', f'정답만 부정형 — 극성으로 홀로 선다 「{cs[a]}」')

# ── 출력 ──────────────────────────────────────────────────────────────────
CLS = {'A': 'objective', 'B': '★ 유출', 'C': '해설 인용 불일치(STALE)',
       'D': '정답 확정 어구', 'E': 'distractor', 'F': '길이 단서(G3/G3b)',
       'G': '선지·해설 형식', 'H': '수치 선지 3단', 'I': '축별 최빈값 교차',
       'J': '근거 필드', 'K': '발문 메아리(P6 규약 소급)', 'L': '극성 홀로서기(P6 규약 소급)'}
print(f'감사37 — T12 2차 {LO}~{HI} · {len(items)}제')
print('=' * 74)
c = Counter(x[1] for x in F)
for k in sorted(CLS):
    print(f'  {k} {CLS[k]:<22} {c.get(k, 0):>3} 건')
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
