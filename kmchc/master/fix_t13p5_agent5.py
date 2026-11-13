# -*- coding: utf-8 -*-
"""T13 P5 (M02011~M02020) 층5 5차(마감) 조치 — 패리티 지름길 하나와 근거 어구 하나.

4차 마감 확인 순회: solver 마감 가능 · factchecker 마감 가능(사실 오류 0) ·
student-sim 마감 가능(A 0/B 0/C 8/D 10 · 죽은 선지 문항당 최대 1)

★solver 의 경미 지적 — '탄소 1 개' 가 패리티로 배제된다★
  홀전자 수의 홀짝은 전자 총수의 홀짝과 같아야 한다. 탄소는 전자가 여섯(짝수)이라
  홀전자도 짝수여야 하는데 '1' 은 홀수다. 곧 ★배치를 그리지 않고도 지워진다.★
  게다가 4차 조치에서 '탄소 3' 을 물린 까닭("탄소에서 3 에 닿는 오독 경로가 마땅치
  않다")이 '탄소 1' 에도 그대로 적용된다 — 2p² 를 한 오비탈에 몰아넣는 가장 흔한
  오독은 0 을 낳지 1 을 낳지 않는다.
  → solver 의 안대로 ★'탄소 0 개'★ 로 간다. 상한(3) 안이고, 패리티가 맞고,
    훈트를 어겨 짝부터 채우는 교과서적 오독 경로를 그대로 얻는다.
  ▸ 다른 셋의 패리티도 확인했다 — 산소 8/2 · 질소 7/1 · 붕소 5/3 모두 정합이라
    이 지름길로는 넷 가운데 하나도 지워지지 않는다.

★factchecker 의 △ 하나 — 새 문장의 근거 어구가 헐겁다★
  "홀전자는 2p 오비탈이 셋뿐이라 아무리 많아도 셋을 넘지 못해" 는 결론은 참이지만
  근거가 헐겁다. 리튬(2s¹)처럼 2p 가 아닌 홀전자도 있다. "홀전자가 가장 많아지는
  경우가 2p 세 오비탈에 하나씩 들어갈 때" 로 고친다.

★반려한 것★
 · M02011 ↔ M02019 교차 단서 (solver F5 중하 · defender 도 3차에 지적) — 실재한다.
   M02011 을 푼 학생은 M02019 에서 ①(1 개)을 자동 배제한다. 다만 M02019 는 묶음의
   ★개수★ 를 묻고 남은 셋(2·3·9)은 그 사실만으로 갈리지 않는다. ★각도를 바꾸는 대신
   조판 때 M02019 를 앞에 두거나 두 문항을 떨어뜨릴 것★ 을 watch 에 적었다.
 · M02012 ③ 만 0 대칭이라는 F5 하 (solver 가 2·4차 두 번) — ★원리적으로 닫히지
   않는다.★ 값 개수를 고정하면 0 을 가운데 둔 대칭 목록은 정답 하나뿐이고, 대칭
   오답을 두려면 개수를 달리해야 하는데 그러면 길이 산포가 G3b 를 넘는다. solver 도
   "전형적 수준이라 허용 가능" 으로 적었다. 개념 대장에 남겼다.
 · M02018 아연의 축약 표기 순서 (factchecker △) — [Ar] 4s² 3d¹⁰ 는 채움 순서 표기다.
   껍질 순 정식 표기는 [Ar] 3d¹⁰ 4s² 이지만 ★이 배치와 이 테마 전체가 채움 순서로
   통일돼 있어★ 그대로 둔다(factchecker 도 "배치 내부 통일성은 지켜져 있으므로
   그대로 두어도 무방" 으로 적었다).
 · 세트 균형 — 파울리가 두 자리(M02014 수용 한계 · M02020 스핀), l 갈라짐이 두
   자리(M02011 · M02019)다(solver F5 하). 서로 다른 국면을 묻고 한도(3회) 안이다.
"""
import json
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2011, 2021)]

# 2주기 원소: (전자 총수, 바닥상태 홀전자 수)
Z2 = {'Li': (3, 1), 'Be': (4, 0), 'B': (5, 1), 'C': (6, 2),
      'N': (7, 3), 'O': (8, 2), 'F': (9, 1), 'Ne': (10, 0)}


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── 1. M02017 ③ — 패리티가 맞는 값으로 ──────────────────────────────────
it = D['M02017']
old_c, new_c = '탄소(C) — 1 개', '탄소(C) — 0 개'
assert it['choices'][2] == old_c, it['choices']
assert len(new_c) == len(old_c)
it['choices'][2] = new_c
for d in it['distractors']:
    if d['opt'] == 2:
        d['error'] = '2p² 를 한 오비탈에 짝지어 넣어 홀전자가 없다고 봄 — 실제로는 2'
it['solution'] = it['solution'].replace(old_c, new_c)
sub(it, '탄소의 2p² 는 서로 다른 오비탈에 하나씩 들어가. 맨 나중 전자만 '
        '홀전자인 것이 아니라 둘 다 홀전자야.',
        '탄소의 2p² 는 짝을 짓지 않아. 오비탈이 셋이나 비어 있으니 훈트 규칙에 따라 '
        '서로 다른 오비탈에 하나씩 들어가 둘 다 홀전자가 되지.')

# ── 2. M02017 — 상한의 근거 어구를 조인다 ────────────────────────────────
sub(it, '참고로 2주기 원자의 바닥상태에서 홀전자는 '
        '2p 오비탈이 셋뿐이라 아무리 많아도 셋을 넘지 못해.',
        '참고로 2주기 원자의 바닥상태에서 홀전자가 가장 많아지는 경우는 2p 세 오비탈에 '
        '하나씩 들어갈 때라, 아무리 많아도 셋을 넘지 못해.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]
assert Counter(i['answer'] for i in items) == {1: 3, 2: 2, 0: 3, 3: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k
for k in set(IDS) - {'M02017'}:
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

# ── 홀전자 문항 전용 검사 — 네 지름길이 모두 막혔는지 ─────────────────────
said = {}
for c in D['M02017']['choices']:
    el = c[c.index('(') + 1:c.index(')')]
    said[el] = int(c.split('—')[1].strip().split()[0])
assert said == {'O': 2, 'N': 1, 'C': 0, 'B': 3}, said
# ㉠ 참인 짝은 정답 하나뿐
assert [el for el in said if said[el] == Z2[el][1]] == ['O'], said
# ㉡ 물리적 상한(2주기 바닥상태 최댓값 3) 안
assert max(Z2[e][1] for e in Z2) == 3
assert all(v <= 3 for v in said.values()), '상한 초과 값이 있다'
# ㉢ 패리티 — 홀전자 수의 홀짝은 전자 총수의 홀짝과 같아야 한다
for el, v in said.items():
    assert v % 2 == Z2[el][0] % 2, f'{el}: 패리티로 지워진다 (전자 {Z2[el][0]}, 값 {v})'
# ㉣ 2p 위첨자 직독 지름길
p2 = {'O': 4, 'N': 3, 'C': 2, 'B': 1}
assert all(said[el] != p2[el] for el in said), '위첨자 직독으로 맞는 선지가 있다'
# ㉤ 전자 총수 직독 · 최외각 전자 수 직독 — 정답에 닿지 않아야 한다
tot = {el: Z2[el][0] for el in said}
outer = {'O': 6, 'N': 5, 'C': 4, 'B': 3}
assert said['O'] != tot['O'] and said['O'] != outer['O'], '정답이 직독으로 풀린다'
assert '홀전자가 가장 많아지는 경우는' in D['M02017']['solution']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P5 5차(마감) 조치 완료 — M02017 ③ 패리티 정합 · 상한 근거 어구')
print('  선지값', said)
print('  실제  ', {e: Z2[e][1] for e in said}, '| 전자 총수', tot)
print('  지름길 차단: 위첨자', p2, '· 최외각', outer, '· 패리티 정합 4/4')
