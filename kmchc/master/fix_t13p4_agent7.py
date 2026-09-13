# -*- coding: utf-8 -*-
"""T13 P4 (M02001~M02010) 층5 7차 조치 — factchecker 가 잡은 배수 귀속 오류.

★내가 5차에 넣은 문장이 틀렸다.★ factchecker 의 경미 △ 를 받아 M02004 도입부를
'두 배나 세 배로 커져' 에서 '두 배, 세 배 넘게 커져' 로 고쳤는데, 실제 값을 세어
보면 ★조건을 하나만 흘려서는 세 배가 나오지 않는다.★

  조건 {n=3, l=2, mₛ=+1/2} → 5
   · mₛ 만 흘림  → 3d 열 개                    = 10  (정확히 두 배)
   · l 만 흘림   → M 껍질 9 오비탈 × +1/2 하나 =  9  (1.8 배)
   · 둘 다 흘림  → M 껍질 정원                 = 18  (3.6 배)

곧 18 은 두 조건을 함께 흘려야 나오는 값이다. 도입부가 "하나라도 흘리면 세 배 넘게"
라고 말하면 ④ 오답해설("부양자수가 2 라는 조건이 3d 로 좁혀 줬어")과도 어긋난다.
두 곳을 함께 고친다.

같이 받는 것 — M02003 발문의 겹침 셈 규칙 (factchecker 강한 권고)
  정답 ④ [Ar] 3s² 3p³ 는 심지 안에 이미 든 3s·3p 를 뒤에 겹쳐 적은 표기다.
  학생이 "겹친 것은 덮어쓴 것" 으로 읽으면 ④ 도 15 가 되어 ★네 선지가 모두 같아지고
  문항이 무너진다★. 6차에 넣은 '적힌 대로' 는 유효성 면제를 좁혔을 뿐 이 셈 규칙까지
  말하지는 않는다.
  ▸ factchecker 가 쓴 문면("심지 안의 부껍질이 뒤에 다시 적혀 있어도 …")은 ★받지
    않았다★ — 그 문장은 겹침이 있는 선지가 있다는 사실을 발문이 알려 주는 셈이라
    ④ 를 곧장 지목한다. 어느 선지도 가리키지 않으면서 덮어쓰기 독법만 닫는
    '적힌 것을 하나도 빼지 않고' 로 간다.

같이 받는 것 — M02003 해설 첫 마디 (factchecker △)
  "위첨자만 더해서는 갈리지 않게 짜여 있어" 는 문자 그대로는 부정확하다. ② 의
  위첨자 합은 13 이라 갈린다. 함정의 실제 모양은 '위첨자만 더하면 ② 로 끌려간다' 다.

반려한 것
 - M02001 의 p_x 표기 조판 △ — 6차에 낱말 '방향' 을 지우면서 표기 자체가 사라졌다.
   (factchecker 는 6차 이전 판본을 보고 있었다.)
 - 범위 △(4d·4f·3d·Cr/Cu 예외·3d/4s 역전이 통상 화학I 본문보다 깊다) — 비차단으로
   올렸고 사실은 모두 정확하다는 판정이 함께 왔다. 이 은행은 심화 트랙을 함께
   싣고, 해당 문항들은 개념 대장이 교재 86~94 쪽에서 뽑은 각도다. 현행 유지.
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

# ── 1. M02004 — 배수 귀속을 실제 값에 맞춘다 ─────────────────────────────
it = D['M02004']
sub(it, '조건이 셋이면 셋을 다 걸어야 해. 하나라도 흘리면 값이 두 배, 세 배 넘게 커져.',
        '조건이 셋이면 셋을 다 걸어야 해. 하나를 흘리면 값이 두 배가 되고, '
        '둘을 흘리면 세 배를 넘어.')
sub(it, '④ 18 개: 열여덟은 M 껍질 전체의 정원이야. 부양자수가 2 라는 조건이 3d 로 좁혀 줬어.',
        '④ 18 개: 열여덟은 M 껍질 전체의 정원이라, 부양자수와 mₛ 두 조건을 함께 '
        '흘려야 나오는 값이야. 부양자수가 2 라는 조건이 3d 로 좁혀 주고, 거기서 '
        'mₛ 조건이 다시 절반으로 줄여.')

# ── 2. M02003 — 덮어쓰기 독법을 닫는다 (선지를 지목하지 않고) ────────────
it = D['M02003']
old = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
       '적힌 배치가 옳은지는 따지지 말고 적힌 대로 전자의 총수만 셀 때, '
       '15 가 되지 않는 것은?')
assert it['stem'] == old, it['stem']
it['stem'] = ('다음은 인(P, 원자 번호 15)의 전자배치를 축약 표기로 적어 본 것이다. '
              '적힌 배치가 옳은지는 따지지 말고 적힌 것을 하나도 빼지 않고 그대로 '
              '더할 때, 전자의 총수가 15 가 되지 않는 것은?')
sub(it, '위첨자만 더해서는 갈리지 않게 짜여 있어.',
        '위첨자만 더하면 혼자 튀어 보이는 ② 로 끌려가게 짜여 있어.')

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
s4 = D['M02004']
assert '하나를 흘리면 값이 두 배가 되고, 둘을 흘리면 세 배를 넘어.' in s4['solution']
assert '두 조건을 함께 흘려야 나오는 값' in s4['solution']
assert '세 배 넘게 커져' not in s4['solution']
s3 = D['M02003']
assert '하나도 빼지 않고 그대로 더할 때' in s3['stem']
assert '심지' not in s3['stem'] and '겹쳐' not in s3['stem'], '발문이 겹침을 알려 주면 안 된다'
assert '② 로 끌려가게' in s3['solution']

# 배수 귀속 검산 — 조건을 하나씩 흘렸을 때의 실제 값
assert 2 * (2 * 2 + 1) == 10                 # mₛ 만 흘림 → 3d 정원
assert 3 ** 2 == 9                           # l 만 흘림 → M 껍질 오비탈 수 × +1/2
assert 2 * 3 ** 2 == 18                      # 둘 다 흘림 → M 껍질 정원
assert (2 * 2 + 1) == 5                      # 세 조건 다 걸었을 때

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P4 7차 조치 완료 — M02004 배수 귀속 · M02003 발문(덮어쓰기 차단) + 해설 첫 마디')
print(' ', D['M02003']['stem'])
print(' ', D['M02004']['solution'].split('\n')[0])
