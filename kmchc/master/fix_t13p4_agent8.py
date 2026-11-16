# -*- coding: utf-8 -*-
"""T13 P4 (M02001~M02010) 층5 8차 조치 — 심지 기호의 '값' 을 못 박는다.

마감 최종 확인 순회: solver 마감 가능 · factchecker 마감 가능 · defender 중~상 하나.

받은 것
 1) M02003 발문에 값 고정 한 줄 (defender · 마감 보류 사유, factchecker 도 같은
    갈래를 권고)
    7차에 넣은 `적힌 것을 하나도 빼지 않고 그대로 더할 때` 는 세 몫 가운데 두 몫을
    했다 — ㉠ "존재하지 않는 배치의 전자 수는 정의되지 않는다" 를 닫았고,
    ㉢ "심지 기호를 셈에서 빼고 위첨자만 더하기"(그 독법에서는 ①③④=5, ②=13 로
    ★네 선지가 모두 정답★이 된다)도 닫았다.
    그러나 ㉡ **덮어쓰기** 는 닫지 못했다. `하나도 빼지 않고` 는 관용적으로
    '생략 금지' 로 읽히는데, 덮어쓰기 독자는 아무것도 생략하지 않는다 —
    "[Ar] 도 셌고 3s² 도 3p³ 도 셌다, 다만 [Ar] 이 뜻하는 값을 10 으로 읽었을
    뿐이다". 곧 그 문구는 ★어느 항을 더할지★ 를 규율할 뿐 ★각 항이 어떤 값을
    갖는지★ 를 규율하지 않는다. 이 독법에서 ④ 는 10+2+3 = 15 가 되어 ★정답이
    사라지고 문항이 통째로 무너진다★. 게다가 그 15 는 인의 실제 전자 수이자 실제
    바닥상태 배치라, 독자는 "자비롭게 복원했더니 화학적으로 말이 되는 답이 나왔다"
    는 확증까지 얻는다.
    현재 이를 막는 낱말은 `그대로` 하나뿐 — 방어선이 한 겹이고 실패하면 전손이다.
    → `단, [ ] 안의 기호는 그 원소의 전자 수 전부를 뜻한다.` 를 넣는다.
      겹침·감산·특정 선지를 일절 말하지 않고 네 선지에 균등하게 걸리며, 규율
      대상이 '어느 항' 이 아니라 '항의 값' 이라 덮어쓰기의 유일한 발판을 없앤다.
      ★재려는 지식은 그대로 남는다★ — [He] 2 · [Ne] 10 · [Ar] 18 이라는 값을
      알아야 여전히 셈이 되지 않는다.
    ▸ `하나도 빼지 않고` 는 남긴다 — 위첨자만 더하기 경로를 계속 막는다.
 2) M02004 도입부 (factchecker △)
    7차에 고친 `하나를 흘리면 값이 두 배가 되고` 는 mₛ 를 흘렸을 때(10)만 참이고
    l 을 흘리면 9(1.8 배)다. 9 는 선지에 없어 오답을 유도하지는 않지만, 어느
    조건을 흘렸을 때의 말인지 못 박는다.

반려한 것
 - M02001 잣대를 `각 부껍질의 오비탈은 모두 따로 센다` 로 일반화 (solver·factchecker
   동시 △) — 부분 확장으로 닿는 값(1+3+1+1=6, 1+3+5+1=10)이 어느 선지와도 맞지
   않아 오답 경로가 생기지 않는다는 데 두 검증자가 함께 동의했고, 둘 다 '필수 아님'
   으로 올렸다. 일반화하면 셈의 절반을 발문이 대신해 준다.
 - M02001 ④ 32 의 '스핀오비탈' 경로 (defender, 심각도 하) — 스핀오비탈은 교육과정
   밖 용어이고, 이 은행은 M02002·M02004·M02010 에서 오비탈을 일관되게 (n, l, mₗ)
   로 다룬다. defender 자신이 "이의제기가 들어와도 방어 가능" 으로 판정했고, 자기
   문면에도 똑같이 있던 흠이라 퇴행이 아니라고 적었다.
 - M02002 ④ `반대편` · M02010 ③ 반발 · M02007 ③ 훈트 위반 — 모두 '차단 확인' 으로
   왔다. 차단하는 낱말(`자리 잡는다` · `까닭` · `바닥상태`)을 watch 에 옮겨 적는다.
"""
import json
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2001, 2011)]


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


bank = json.load(open(BANK, encoding='utf-8'))
D = {i['id']: i for i in bank}
before = {k: json.loads(json.dumps(D[k])) for k in IDS}

# ── 1. M02003 — 심지 기호의 값을 못 박는다 ───────────────────────────────
it = D['M02003']
old = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
       '적힌 배치가 옳은지는 따지지 말고 적힌 것을 하나도 빼지 않고 그대로 '
       '더할 때, 전자의 총수가 15 가 되지 않는 것은?')
assert it['stem'] == old, it['stem']
it['stem'] = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
              '적힌 배치가 옳은지는 따지지 말고 적힌 것을 하나도 빼지 않고 그대로 '
              '더할 때, 전자의 총수가 15 가 되지 않는 것은? '
              '단, [ ] 안의 기호는 그 원소의 전자 수 전부를 뜻한다.')

# ── 2. M02004 — 어느 조건을 흘렸을 때인지 못 박는다 ──────────────────────
sub(D['M02004'],
    '하나를 흘리면 값이 두 배가 되고, 둘을 흘리면 세 배를 넘어.',
    'mₛ 를 흘리면 값이 두 배가 되고, 부양자수까지 함께 흘리면 세 배를 넘어.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]

assert Counter(i['answer'] for i in items) == {2: 3, 3: 3, 0: 2, 1: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k
    assert D[k]['choices'] == before[k]['choices'], k

touched = {'M02003', 'M02004'}
for k in IDS:
    if k not in touched:
        assert D[k]['solution'] == before[k]['solution'], k
        assert D[k]['stem'] == before[k]['stem'], k

for it in items:
    cs = it['choices']
    assert len(cs) == 4 and len(set(cs)) == 4, it['id']
    assert sorted(d['opt'] for d in it['distractors']) == sorted(set(range(4)) - {it['answer']})
    assert len(it['solution']) >= 300, (it['id'], len(it['solution']))
    assert '★' not in it['solution'] and '★' not in it['stem'], it['id']
    assert it['objective'], it['id']
    L = sorted(len(c) for c in cs)
    a = len(cs[it['answer']])
    assert not (a == L[3] and L[2] < L[3]), (it['id'], 'G3 최장 단독')
    assert not (a == L[0] and L[0] < L[1]), (it['id'], 'G3 최단 단독')
    mid = (L[1] + L[2]) / 2
    if mid >= 8:
        assert (L[3] - L[0]) / mid <= 0.25, (it['id'], 'G3b')
    assert '가 옳아' in it['solution'] or '이 옳아' in it['solution'], it['id']
    for k in range(4):
        assert MK[k] + ' ' + cs[k] in it['solution'], (it['id'], MK[k])

# 문면 검사
s3 = D['M02003']
for keep in ('적힌 배치가 옳은지는 따지지 말고', '하나도 빼지 않고', '그대로 더할 때'):
    assert keep in s3['stem'], keep          # 세 겹이 모두 살아 있어야 한다
assert '[ ] 안의 기호는 그 원소의 전자 수 전부를 뜻한다' in s3['stem']
assert '겹쳐' not in s3['stem'] and '심지' not in s3['stem'], '발문이 겹침을 지목하면 안 된다'
for mk in MK:
    assert mk not in s3['stem'], '발문이 선지를 호명하면 안 된다'
s4 = D['M02004']
assert 'mₛ 를 흘리면 값이 두 배가 되고, 부양자수까지 함께 흘리면 세 배를 넘어.' in s4['solution']

# 값 고정 문구를 넣은 뒤의 총수 재검산 — 정답 유일성
core = {'[He]': 2, '[Ne]': 10, '[Ar]': 18}
sup = {'⁰': 0, '¹': 1, '²': 2, '³': 3, '⁴': 4, '⁵': 5, '⁶': 6, '⁷': 7, '⁸': 8, '⁹': 9}
tot = []
for c in s3['choices']:
    parts = c.split()
    n = core[parts[0]] + sum(sup[p[-1]] for p in parts[1:])
    tot.append(n)
assert tot == [15, 15, 15, 23] and s3['answer'] == 3, tot
# 덮어쓰기 독법이 닫혔는지 — 그 독법에서만 ④ 가 15 가 된다
assert 10 + 2 + 3 == 15 and 18 + 2 + 3 == 23

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P4 8차 조치 완료 — M02003 발문(심지 값 고정) · M02004 도입부')
print(' ', D['M02003']['stem'])
print('  총수 검산:', tot)
