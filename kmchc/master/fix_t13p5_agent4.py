# -*- coding: utf-8 -*-
"""T13 P5 (M02011~M02020) 층5 4차 조치 — 무지식 배제 경로 하나와 문면 넷.

3차 순회: factchecker 마감 가능(사실 오류 0 · △ 4) · solver 마감 가능 조건부(F5 중 1)

★solver 의 F5 중 — 홀전자 문항의 오답 둘이 물리적 상한을 넘는다★
  2주기 원자의 바닥상태에서 홀전자는 2p 오비탈이 셋이라 ★최대 셋★ 이다. 그런데
  ③ '탄소 4 개' 와 ④ '붕소 5 개' 는 그 상한을 넘는다. 곧 원소별 배치를 하나도
  따지지 않고 "넷도 다섯도 있을 수 없다" 만으로 둘이 날아가, 문항이 ①②의 2 지선다로
  줄어든다. ★크로뮴 문항에서 애써 막은 것과 같은 종류의 축소가 여기서 열려 있었다.★
  → 네 값을 모두 상한 안(3 이하)으로 낮춘다. 그러면 배제하려면 실제로 배치를 그려야
    한다. 값이 겹치더라도 원소가 다르니 짝은 서로 다르다.
      ① 산소(O) — 2 개  ← 정답 (2p⁴ → 2)
      ② 질소(N) — 1 개  : 짝부터 채워 홀전자를 하나로 봄 (실제 3)
      ③ 탄소(C) — 1 개  : 맨 나중에 들어간 전자 하나만 홀전자라고 봄 (실제 2)
      ④ 붕소(B) — 3 개  : 가장 바깥 껍질의 전자 수 3 을 홀전자 수로 읽음 (실제 1)
  ▸ solver 가 낸 ③ '탄소 3 개' 대신 ★'탄소 1 개'★ 로 갔다 — 탄소에서 3 에 닿는
    오독 경로가 마땅치 않은 반면, '맨 나중 전자만 홀전자' 는 실재하는 경로다.
    ④ 는 solver 안(붕소 2)이 아니라 ★붕소 3★ 으로 두어 '최외각 전자 수를 홀전자
    수로' 라는 가장 흔한 경로를 살렸다(3 은 상한 안이다).
  ▸ ★위첨자 지름길 재검산★ — O 4 · N 3 · C 2 · B 1 이 선지값 2 · 1 · 1 · 3 과 넷 다
    어긋난다. 지름길로는 여전히 하나도 고를 수 없다.

★factchecker 의 △ 넷 (표현 — 값이 싸서 받는다)★
  ㉠ M02015 ① — 같은 배치를 쓴 ③ 에는 "실제 바닥상태가 아니야" 가 있는데 ① 에는
     없어 두 오답의 기준선이 어긋난다. 한 구절 붙인다.
  ㉡ M02018 — "둘째 조건만 걸면 아르곤과 칼륨까지" 의 칼륨은 선지 밖 원소다.
     선지를 다시 뒤지게 만들지 않도록 못 박는다.
  ㉢ M02018 — "l = 2 인 전자가 없다 = 3d 가 비어 있다" 는 이 후보군에서만 성립하는
     축약이다. 괄호로 한정한다.
  ㉣ M02019 — 발문에 넣은 '빈 오비탈' 가드가 해설에 메아리치지 않는다. 한 줄 더한다.

★반려한 것★
 · M02013 정답을 `[Ne]` 로 (solver F5 하) — 정답만 [He] 계열이라 "[Ne]" 를 눈으로
   찾는 학생이 ③④ 로 흘러든다는 지적이다. 그러나 ★그 흘러듦은 손해가 아니라 덫★ 이다
   — ③ 은 14, ④ 는 18 전자라 표면 일치로 고르면 틀린다. 심지 계열도 [He] 둘 : [Ne] 둘로
   균형이다. 게다가 `[Ne]` 한 낱말은 네 자라 길이 균일(12 자)이 깨진다.
 · M02011 ↔ M02019 문항 간 누출 (solver·defender 가 각각 지적) — 조판 순서로 갈음한다.
   solver 는 M02019 를 앞에 두라고 했다. watch 에 적어 둔다.
 · M02014 정답이 시각적 이질항(② 만 1s² 로 시작하지 않음) — solver 스스로 "그 이질성이
   곧 출제 개념(파울리 위반)이라 제거하면 문항이 성립하지 않는다" 며 기록만 남겼다.
"""
import json
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2011, 2021)]


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


def setc(it, choices, wrongs):
    assert len(choices) == 4 and len(set(choices)) == 4, it['id']
    it['choices'] = choices
    ds = [{'opt': choices.index(w[0]), 'error': w[1], 'type': w[2]} for w in wrongs]
    assert len(ds) == 3 and all(d['opt'] != it['answer'] for d in ds), it['id']
    it['distractors'] = sorted(ds, key=lambda d: d['opt'])


def resol(it, lead, cor, wmap, diag):
    a = it['answer']
    body = [lead, '', f"[정답] {MK[a]} {it['choices'][a]} — {cor}", '']
    for k in range(4):
        if k != a:
            body.append(f"{MK[k]} {it['choices'][k]}: {wmap[it['choices'][k]]}")
    body += ['', f"자가진단: {diag}"]
    it['solution'] = '\n'.join(body)


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── 1. M02017 — 네 값을 물리적 상한(3) 안으로 ────────────────────────────
it = D['M02017']
it['calc_check'] = 'O 2p⁴ → 홀 2 / N 2p³ → 홀 3 / C 2p² → 홀 2 / B 2p¹ → 홀 1 (2주기 상한 3)'
setc(it, ['산소(O) — 2 개', '질소(N) — 1 개', '탄소(C) — 1 개', '붕소(B) — 3 개'],
     [('질소(N) — 1 개', '2p³ 를 한 오비탈부터 짝지어 채워 홀전자를 하나로 봄 — 실제로는 3',
       'proc'),
      ('탄소(C) — 1 개', '맨 나중에 들어간 전자 하나만 홀전자라고 봄 — 실제로는 2', 'proc'),
      ('붕소(B) — 3 개', '가장 바깥 껍질의 전자 수 3 을 그대로 홀전자 수로 읽음 — 실제로는 1',
       'proc')])
resol(it, '위첨자를 그대로 홀전자 수로 읽는 지름길은 이 네 짝 가운데 어느 것도 맞히지 못해.',
      '홀전자는 짝을 이루지 못한 전자야. 같은 준위의 오비탈에 전자를 넣을 때는 훈트 '
      '규칙에 따라 먼저 하나씩 고루 넣고, 자리가 다 차야 짝을 짓기 시작해. 2p 부껍질은 '
      '오비탈이 셋이니 셋까지는 모두 홀전자지. 산소는 1s² 2s² 2p⁴ 라 2p 에 넷이 들어가. '
      '셋을 하나씩 넣고 남은 하나가 짝을 지으니 홀전자는 둘이야 — ①이 옳아. 나머지도 '
      '같은 방식으로 세어 보자. 질소는 2p³ 라 셋, 탄소는 2p² 라 둘, 붕소는 2p¹ 이라 '
      '하나지. 여기서 두 가지를 붙들어야 해. 위첨자가 넷이라고 홀전자가 넷인 것이 아니라 '
      '넷째 전자가 오히려 홀전자 하나를 지워 버린다는 것, 그리고 가장 바깥 껍질의 전자 '
      '수는 홀전자 수와 아예 다른 값이라는 것. 참고로 2주기 원자의 바닥상태에서 홀전자는 '
      '2p 오비탈이 셋뿐이라 아무리 많아도 셋을 넘지 못해.',
      {'질소(N) — 1 개': '질소의 2p³ 는 세 오비탈에 하나씩이라 홀전자가 셋이야. 2p 안에는 '
                        '짝이 하나도 없지.',
       '탄소(C) — 1 개': '탄소의 2p² 는 서로 다른 오비탈에 하나씩 들어가. 맨 나중 전자만 '
                        '홀전자인 것이 아니라 둘 다 홀전자야.',
       '붕소(B) — 3 개': '셋은 붕소의 가장 바깥 껍질에 있는 전자 수야. 2s² 는 이미 짝을 '
                        '지었으니 홀전자는 2p¹ 의 하나뿐이지.'},
      'p 부껍질을 만나면 상자 셋을 그리고 하나씩 채워 넣는다.')

# ── 2. M02018 — 둘째 조건에 범위를 못 박는다 (defender 중 · 3중 정답 경로) ─────
#   "n = 4 인 전자가 2 개였고, l = 2 인 전자는 하나도 없었다" 의 둘째 절에 범위
#   한정어가 없어, 앞 절이 도입한 'n = 4 인 전자' 를 선행사로 끌어와
#   ★"그 n = 4 전자들 중 l = 2 인 것은 없다"★ 로 읽을 수 있다. 그 독법에서는
#   3d(n = 3)가 조건 밖으로 빠져 아연도 스칸듐도 두 조건을 다 만족한다 — ②③④
#   3중 정답이다. 두 절이 "…였고, …없었다" 로 완전 평행이라 부분집합 독법이
#   문법적으로 막혀 있지 않았다(defender).
it = D['M02018']
old = ('어떤 중성 원자의 바닥상태를 조사했더니 n = 4 인 전자가 2 개였고, l = 2 인 '
       '전자는 하나도 없었다. 이 원자는 무엇인가?')
assert it['stem'] == old, it['stem']
it['stem'] = ('어떤 중성 원자의 바닥상태를 조사했더니 n = 4 인 전자가 2 개였고, 이 원자 '
              '전체에서 l = 2 인 전자는 하나도 없었다. 이 원자는 무엇인가?')

# ── 2. factchecker △ 넷 ──────────────────────────────────────────────────
sub(D['M02015'], '반채움은 다섯이 하나씩 들어간 상태지. 까닭이 이 배치를 낳지 않아.',
                 '반채움은 다섯이 하나씩 들어간 상태지. 까닭이 이 배치를 낳지 않고, '
                 '이 배치는 실제 바닥상태도 아니야.')
sub(D['M02018'], '거꾸로 둘째 조건만 걸면 아르곤과 칼륨까지 살아남아.',
                 '거꾸로 둘째 조건만 걸면 아르곤은 물론 선지에 없는 칼륨까지 살아남아.')
sub(D['M02018'], 'l = 2 인 전자가 하나도 없다는 것은 3d 가 통째로 비어 있다는 말이야.',
                 'l = 2 인 전자가 하나도 없다는 것은, 여기 후보에서 l = 2 인 자리는 3d '
                 '하나뿐이니 3d 가 통째로 비어 있다는 말이야.')
sub(D['M02019'], '산소는 전자가 여덟인 다전자 원자야.',
                 '산소는 전자가 여덟인 다전자 원자야. 그 여덟은 모두 안쪽 두 껍질에 들어가 '
                 'n = 3 인 오비탈은 죄다 비어 있지만, 준위가 갈라져 있는 것은 전자가 들어 '
                 '있느냐와 상관이 없어.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]
assert Counter(i['answer'] for i in items) == {1: 3, 2: 2, 0: 3, 3: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k
untouched = set(IDS) - {'M02015', 'M02017', 'M02018', 'M02019'}
for k in untouched:
    assert D[k] == before[k], k

for it in items:
    cs = it['choices']
    assert len(cs) == 4 and len(set(cs)) == 4, it['id']
    assert sorted(d['opt'] for d in it['distractors']) == sorted(set(range(4)) - {it['answer']}), it['id']
    assert len(it['solution']) >= 300, (it['id'], len(it['solution']))
    assert '★' not in it['stem'] and '★' not in it['solution'], it['id']
    assert it['objective'], it['id']
    L = sorted(len(c) for c in cs)
    a = len(cs[it['answer']])
    assert not (a == L[3] and L[2] < L[3]), (it['id'], 'G3 최장 단독', cs)
    assert not (a == L[0] and L[0] < L[1]), (it['id'], 'G3 최단 단독', cs)
    mid = (L[1] + L[2]) / 2
    if mid >= 8:
        assert (L[3] - L[0]) / mid <= 0.25, (it['id'], 'G3b', cs)
    assert '가 옳아' in it['solution'] or '이 옳아' in it['solution'], it['id']
    for k in range(4):
        assert MK[k] + ' ' + cs[k] in it['solution'], (it['id'], MK[k], cs[k])

# 이번 회차 검사 — 물리적 상한과 지름길
real = {'O': 2, 'N': 3, 'C': 2, 'B': 1}          # 2주기 바닥상태 홀전자 수
supr = {'O': 4, 'N': 3, 'C': 2, 'B': 1}          # 2p 위첨자(지름길이 내놓는 값)
said = {}
for c in D['M02017']['choices']:
    el = c[c.index('(') + 1:c.index(')')]
    said[el] = int(c.split('—')[1].strip().split()[0])
assert said == {'O': 2, 'N': 1, 'C': 1, 'B': 3}, said
assert all(v <= 3 for v in said.values()), '2주기 상한 3 을 넘는 값이 있다'
assert sum(1 for el in said if said[el] == real[el]) == 1, '참인 짝은 정답 하나뿐이어야 한다'
assert all(said[el] != supr[el] for el in said), '위첨자 지름길이 맞는 선지가 있다'
assert D['M02017']['choices'][0] == '산소(O) — 2 개'
assert '이 배치는 실제 바닥상태도 아니야' in D['M02015']['solution']
assert '선지에 없는 칼륨까지' in D['M02018']['solution']
assert '여기 후보에서 l = 2 인 자리는 3d 하나뿐' in D['M02018']['solution']
assert 'n = 3 인 오비탈은 죄다 비어 있지만' in D['M02019']['solution']
assert '이 원자 전체에서 l = 2 인 전자는 하나도 없었다' in D['M02018']['stem']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P5 4차 조치 완료 — M02017 상한 안으로 · 문면 △ 넷')
print('  선지값', said, '/ 실제', real, '/ 위첨자', supr)
