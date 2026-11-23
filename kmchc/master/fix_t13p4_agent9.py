# -*- coding: utf-8 -*-
"""T13 P4 (M02001~M02010) 층5 9차 조치 — 마감 조치. 선행사 하나와 문면 셋.

마감 확정 순회: solver 마감 가능 · factchecker 마감 가능 · defender 마감 가능
(단, 비용 0 의 선행사 교정 하나를 조건으로 달았다).

받은 것
 1) M02003 발문 — `그 원소` 의 선행사 (defender · 유일한 실질 지적)
    `[ ] 안의 기호는 그 원소의 전자 수 전부를 뜻한다` 에서 `그 원소` 를 ★문두의
    인(P, 15)★ 으로 받는 독법이 문법상 봉쇄되어 있지 않다. 그 독법에서는 모든
    괄호가 15 가 되어 ① 20 · ② 28 · ③ 20 · ④ 20 — ★네 선지 전부가 "15 가 되지
    않는 것" 이 되어 복수 정답으로 붕괴한다.★ 자연스러운 독법은 아니지만 F2 순회가
    잡으라고 있는 바로 그 종류이고 수정 비용이 0 이다.
    → `그 기호가 나타내는 원소` 로 선행사를 못 박는다. 선지·정답·다른 세 겹 불변.
 2) M02003 해설 두 곳 (factchecker △)
    ㉠ "②는 2 더하기 6+7 곧 13 이라 역시 열다섯" 은 13 이 합계로 오독된다.
    ㉡ "③ 은 아예 성립하지도 않는 표기" 는 엄밀히는 ④ 도 그렇다 — [Ar] 안에 이미
       찬 3s·3p 를 겹쳐 적었으므로 실제 배치로는 성립하지 않는다. 둘을 묶는다.
 3) M02001 ① 해설 (factchecker △) — 발문은 p 오비탈 셋만 규정하는데 해설은 d·f 까지
    같은 방식으로 센다. `같은 이치로` 한 마디로 확장을 명시한다.

★네 겹의 규율 영역★ (defender 가 정리해 준 것 — watch 에 옮겨 적는다)
    옳은지는 따지지 말고 → 배치의 화학적 정오
    하나도 빼지 않고     → **어느 항을** 더할지
    그대로               → 항의 **형태**(위첨자 재해석 차단)
    [ ] 정의 한 줄       → 항의 **값**(괄호 항 한정)
  넷이 서로 다른 축을 잡고 있어 상쇄가 없다. 하나도 빼지 말 것.

반려한 것
 - M02001 잣대를 d·f 까지 일반화 (defender·factchecker·solver 세 검증자가 모두
   '무해·조치 불요' 로 판정) — 부분 확장으로 닿는 값 6 이 어느 선지도 아니다.
 - M02003 의 약한 메타 단서("굳이 단 단서 = ④ 가 수상") — defender 가 "내용 누설이
   아니고 증분이 미미하다, 조치 불요" 로 판정.
 - M02004 도입부가 ① 1 개(조건을 하나 **더** 건 오류)를 포괄하지 않는 점 —
   defender 가 "F2 사안이 아니고 마감 보류 사유도 아니다" 로 올렸다. ① 은 오답해설이
   따로 다루고 있다.
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

# ── 1. M02003 발문 — 선행사를 못 박는다 ──────────────────────────────────
it = D['M02003']
old = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
       '적힌 배치가 옳은지는 따지지 말고 적힌 것을 하나도 빼지 않고 그대로 '
       '더할 때, 전자의 총수가 15 가 되지 않는 것은? '
       '단, [ ] 안의 기호는 그 원소의 전자 수 전부를 뜻한다.')
assert it['stem'] == old, it['stem']
it['stem'] = old.replace('그 원소의 전자 수 전부', '그 기호가 나타내는 원소의 전자 수 전부')

# ── 2. M02003 해설 두 곳 ─────────────────────────────────────────────────
sub(it, '②는 2 더하기 6+7 곧 13 이라 역시 열다섯', '②는 2 더하기 13 으로 열다섯')
sub(it, '넷 다 인의 바닥상태 배치가 아니고 ③ 은 아예 성립하지도 않는 표기이지만',
        '넷 다 인의 바닥상태 배치가 아니고 ③ 과 ④ 는 실제 배치로는 성립하지도 않지만')

# ── 3. M02001 ① 해설 ─────────────────────────────────────────────────────
sub(D['M02001'],
    '발문이 p 오비탈 셋을 각각 따로 세라고 했으니 4s 를 하나,',
    '발문이 p 오비탈 셋을 각각 따로 세라고 했으니, 같은 이치로 4s 를 하나,')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]

assert Counter(i['answer'] for i in items) == {2: 3, 3: 3, 0: 2, 1: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k
    assert D[k]['choices'] == before[k]['choices'], k

touched = {'M02001', 'M02003'}
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

# 문면 검사 — 네 겹이 모두 살아 있어야 한다
s3 = D['M02003']
for keep in ('적힌 배치가 옳은지는 따지지 말고', '하나도 빼지 않고', '그대로 더할 때',
             '[ ] 안의 기호는 그 기호가 나타내는 원소의 전자 수 전부를 뜻한다'):
    assert keep in s3['stem'], keep
for mk in MK:
    assert mk not in s3['stem'], '발문이 선지를 호명하면 안 된다'
assert '③ 과 ④ 는 실제 배치로는 성립하지도 않지만' in s3['solution']
assert '2 더하기 13 으로 열다섯' in s3['solution']
assert '같은 이치로 4s 를 하나,' in D['M02001']['solution']

# 두 독법으로 총수를 다 세어 본다 — 의도한 독법에서만 정답이 하나다
core = {'[He]': 2, '[Ne]': 10, '[Ar]': 18}
sup = {str(i): i for i in range(10)}
sup.update({'⁰': 0, '¹': 1, '²': 2, '³': 3, '⁴': 4, '⁵': 5, '⁶': 6, '⁷': 7, '⁸': 8, '⁹': 9})


def total(c, coreval):
    p = c.split()
    return coreval(p[0]) + sum(sup[t[-1]] for t in p[1:])


ok = [total(c, lambda k: core[k]) for c in s3['choices']]
bad = [total(c, lambda k: 15) for c in s3['choices']]     # '그 원소' = 인 으로 오독했을 때
assert ok == [15, 15, 15, 23] and s3['answer'] == 3, ok
assert bad == [20, 28, 20, 20], bad                       # 넷 다 15 가 아니다 = 붕괴 독법
print('  의도한 독법:', ok, '→ 정답 ④ 하나')
print('  선행사 오독:', bad, '→ 넷 다 15 아님(붕괴) — 이 독법을 막으려 선행사를 못 박았다')

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P4 9차(마감) 조치 완료 — M02003 선행사 + 해설 둘 · M02001 ① 해설')
print(' ', s3['stem'])
