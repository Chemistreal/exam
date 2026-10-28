# -*- coding: utf-8 -*-
"""T13 P4 (M02001~M02010) 층5 6차 조치 — 낱말 하나와 부사 하나.

마감 재확인 순회: solver 마감 가능 · student-sim 마감 가능 · defender 마감 불가(중 하나).

받은 것
 1) M02001 발문에서 낱말 `방향` 을 지운다 (defender · 마감 보류 사유)
    5차에 예시(p_x·p_y·p_z)를 박아 ① 4 개는 확실히 끊었다. 그러나 defender 는
    ★예시 표지는 닫는 힘이 없다★ 고 지적했다 — 「~처럼 … ~도」 는 문법적으로 열린
    집합이라 "방향이 다르면 따로 센다, 예컨대 p 가 그렇다" 로 읽히고, 화살표 ↑↓ 를
    '스핀 방향' 으로 배운 학생에게는 그것도 여전히 허용된다. 애매어를 없앤 것이
    아니라 애매어에 각주를 단 꼴이었다. ④ 32 = 2 × 16 이라 스핀 이배를 허용하는
    독법이 하나라도 살아 있으면 즉시 제2정답이 된다.
    → 낱말을 지우고 셀 대상을 '오비탈' 로 못 박는다. 오비탈은 스핀을 갖지 않으므로
      학생이 항변을 구성할 수 없다(범주 오류가 된다).
    ▸ defender 가 쓴 문장은 `p_x·p_y·p_z 는 서로 다른 오비탈로 각각 센다` 였는데,
      factchecker 가 같은 순회에서 `p_x` 의 밑첨자 조판을 △ 로 올렸고 이 표기는
      은행 어디에도 전례가 없다. `p 오비탈 셋` 은 이미 은행에서 쓰던 말이라
      그쪽을 쓴다. 끊는 힘(오비탈이 셈의 단위)은 같다.
 2) M02003 발문에 `적힌 대로` 를 넣는다 (defender·solver 동시, 선택 사항으로 제시)
    ③ [Ne] 3s⁴ 3p¹ 만 부적법의 종류가 다르다 — ①·② 는 기묘해도 존재할 수 있는
    들뜬 상태이지만 3s⁴ 는 파울리 위반이라 존재 자체가 불가능하다. 그래서
    "없는 것의 전자 수는 정의되지 않는다" 는 항변이 ③ 만 정확히 집어낸다.
    셈이 표기 조작임을 부사 하나로 못 박으면 그 경로가 문법적으로 소멸한다.
    ▸ solver 가 권한 문면은 `적힌 그대로 위첨자를 더할 때` 였는데 ★받지 않았다★ —
      이 문항이 재는 것이 바로 '위첨자만으로는 안 되고 심지를 더해야 한다' 이므로,
      위첨자를 셈의 단위로 지목하면 발문이 틀린 셈법을 지시하게 된다.

반려한 것
 - M02003 ①③ 의 대칭을 깨라 (solver, F5 경미) — ★산술적으로 불가능하다.★
   15 를 심지+위첨자로 가르는 길은 [He]+13 과 [Ne]+5 둘뿐이다([Ar]=18 은 이미
   15 를 넘는다). 15 인 선지가 셋이므로 비둘기집에 따라 둘은 반드시 같은 심지를
   쓴다. 남는 길은 심지 없는 완전 표기 하나를 넣는 것인데, 15 가 되는 완전 표기는
   길이가 16 자로 뛰어 G3b(산포 0.33)에 걸린다 — 3차에 같은 까닭으로 반려한 안이다.
   student-sim 이 이번 순회에서 "동반 소거는 끊겼다" 고 확인했고(③ 이 실제로 표를
   받는다), 넷이 모두 성립하지 않는 배치라 '안 옳은 것 고르기' 우회로가 유일해를
   주지 못한다. 대칭 소거를 하려면 [Ne]=10 을 알아야 하므로 재려는 지식을
   건너뛰지도 못한다. 현행 유지.
 - M02002 ② 교체 — student-sim 이 이번 순회에서 스스로 철회했다("멈춤 규칙에
   걸리고, 제 '에너지 차이' 제안은 제만 갈라짐을 끌어들이므로 철회합니다").
 - M02001 에 '4f 까지 포함' 명시 — defender 가 재확인에서 "받지 않은 판단이
   옳았다" 고 확인했다. 명시하면 계산의 절반을 발문이 대신해 준다.
 - M02010 ③·M02007 ③·M02009 ①·M02002 ④ — defender 가 모두 '유지' 로 판정.
   거짓을 지탱하는 낱말(까닭 · 바닥상태 · 반발이 사라져도 · 자리 잡는다)이
   발문·선지에 명시돼 있어 현재는 막혀 있다. watch 에 옮겨 적는다.
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

# ── 1. M02001 — 낱말 '방향' 을 지운다 ─────────────────────────────────────
it = D['M02001']
old = ('N 껍질(n = 4)에 있는 오비탈은 모두 몇 개인가? '
       '단, p_x·p_y·p_z 처럼 방향이 다른 오비탈도 각각 따로 센다.')
assert it['stem'] == old, it['stem']
it['stem'] = ('N 껍질(n = 4)에 있는 오비탈은 모두 몇 개인가? '
              '단, p 오비탈 셋은 서로 다른 오비탈로 각각 센다.')
sub(it, '발문이 p_x·p_y·p_z 처럼 방향이 다른 것도 따로 세라고 했으니',
        '발문이 p 오비탈 셋을 각각 따로 세라고 했으니')

# ── 2. M02003 — 셈이 표기 조작임을 못 박는다 ─────────────────────────────
it = D['M02003']
old = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
       '적힌 배치가 옳은지는 따지지 말고 전자의 총수만 셀 때, 15 가 되지 않는 것은?')
assert it['stem'] == old, it['stem']
it['stem'] = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
              '적힌 배치가 옳은지는 따지지 말고 적힌 대로 전자의 총수만 셀 때, '
              '15 가 되지 않는 것은?')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]

assert Counter(i['answer'] for i in items) == {2: 3, 3: 3, 0: 2, 1: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k
    assert D[k]['choices'] == before[k]['choices'], k   # 이번 회차는 선지를 건드리지 않는다

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

# 문면 검사 — 애매어가 남지 않았는지
s1 = D['M02001']
assert '방향' not in s1['stem'] and '방향' not in s1['solution'], '방향 잔존'
assert 'p_' not in s1['stem'] and 'p_' not in s1['solution'], '밑첨자 표기 잔존'
assert 'p 오비탈 셋' in s1['stem'] and '오비탈' in s1['stem']
s3 = D['M02003']
assert '적힌 대로 전자의 총수만 셀 때' in s3['stem']
assert '위첨자를 더할' not in s3['stem'], '위첨자를 셈의 단위로 지목하면 안 된다'

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P4 6차 조치 완료 — M02001 발문(방향 삭제) · M02003 발문(적힌 대로)')
for k in ['M02001', 'M02003']:
    print(' ', k, '|', D[k]['stem'])
