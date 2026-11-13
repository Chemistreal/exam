# -*- coding: utf-8 -*-
"""T13 P3 — 7차 조치 (마감 손질 · 해설 세 문장. 발문·선지·정답 불변).

factchecker 마감 재확인 — ★"판정: 마감해도 좋습니다."★
  · 열 문항 모두 사실 오류 없음 · 번호 어긋남 없음
  · 산술을 값으로 전부 재계산해 일치(전자 수 · 홀전자 수 · n+l · 26 두 번 세기)
  · ★6차의 △ 여덟 곳이 모두 실제로 해소됨★ — 특히 4s < 3d(M01992) ↔ 2p < 3p < 4p
    (M01993) 충돌, 4p 시작점 구멍(M01991), ④ 반박의 오류 지점 미지목(M01994)
  · 새 마찰 셋은 모두 반 줄짜리 문장 다듬기 — 그것을 여기서 닫는다.

㉠ ★M01997 — 6차에 넣은 문장이 스스로 모순을 만들었다★
   "심지는 … 그 배치보다 **앞에 오는** 비활성 기체를 쓰는 것이 관례" 라고 적었는데,
   S²⁻ 은 전자 수가 아르곤과 **꼭 같으므로** 아르곤은 '앞에 오는' 기체가 아니다.
   그 관례를 그대로 적용하면 [Ar] 이 관례 위반이 되어 바로 앞 문장의 "둘 다 옳고" 를
   스스로 깎는다. → '그 배치까지 다 품는 가장 가까운 비활성 기체' 로 고치고, 두 표기가
   어떻게 갈리는지를 이 이온에 맞춰 밝힌다.
   ▸ ★교훈 — 관례를 한 줄 덧붙일 때 그 관례를 그 문항의 사례에 대입해 볼 것.★
     일반론으로는 맞는 문장이 그 문항에서만 어긋나는 일이 있다.
㉡ M01992 — '채움 차례상 5s 가 먼저' 와 '4f 가 더 낮아' 를 애써 갈라 놓고 마지막에
   "순서가 뒤집혀" 로 다시 하나로 묶었다. 무엇의 순서인지 밝힌다.
㉢ M01991 — '비어 있던 4s 자리' 는 구리의 4s 가 4s¹ 이라 반쯤 차 있으므로 오독 소지.
   '하나만 차 있던 4s 의 남은 자리' 로.

받지 않은 것 — M01994 ④ 반박의 인과 방향(factchecker △, 사실 오류 아님).
  본문 ③ 은 '나눠 쓰면 반발이 커서 흩어진다', ④ 반박은 '나란하면 못 들어가 흩어지고
  그래서 덜 겪는다' 로 화살표가 반대라는 지적이다. 둘 다 옳은 서술이고, 6차에 이
  줄을 고친 목적이 **오답의 틀린 대목('끌어당긴다')을 지목하는 것**이었는데 순서를
  본문에 맞추려 다시 손대면 그 지목이 흐려진다. ★여섯 회차 내내 '조치가 다음 회차의
  지적을 만든' 배치다 — 사실 오류가 아닌 곳에서 멈춘다.★
"""
import json
import os
import sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)
import batch_template as T                                    # noqa: E402

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']

bank = json.load(open(BANK, encoding='utf-8'))
by = {x['id']: x for x in bank}
before = {i: (json.dumps(by[f'M0{i}']['choices'], ensure_ascii=False),
              by[f'M0{i}']['stem'], by[f'M0{i}']['answer']) for i in range(1991, 2001)}


def sub(it, old, new, n=1):
    assert it['solution'].count(old) == n, f"{it['id']}: '{old[:40]}' {it['solution'].count(old)}회"
    it['solution'] = it['solution'].replace(old, new)


# ── ㉠ M01997 : 관례를 이 이온에 대입해도 어긋나지 않게 ──────────────────
sub(by['M01997'],
    '다만 심지는 아무거나 고르는 것이 아니라 그 배치보다 앞에 오는 비활성 기체를 쓰는 것이 '
    '관례야.',
    '다만 심지는 아무거나 고르는 것이 아니라 그 배치가 다 품고 있는 가장 가까운 비활성 '
    '기체를 쓰는 것이 관례야. S²⁻ 은 전자 수가 아르곤과 꼭 같아 [Ar] 하나로도 적을 수 있고, '
    '한 단계 앞의 [Ne] 를 심지로 삼아 나머지를 펼친 것이 ④ 야.')

# ── ㉡ M01992 : 무엇의 순서가 뒤집히는지 ─────────────────────────────────
sub(by['M01992'],
    '그래서 다전자 원자에서는 채움 차례상 5s 가 먼저지만, 수소에서는 4f 가 더 낮아 순서가 '
    '뒤집혀.',
    '그래서 다전자 원자에서는 채움 차례상 5s 가 먼저 차지만, 수소에서 에너지만 견주면 4f 가 '
    '아래라 채움 차례와 반대가 돼.')

# ── ㉢ M01991 : 구리의 4s 는 비어 있지 않다 ─────────────────────────────
sub(by['M01991'],
    '아연에서 늘어난 전자는 비어 있던 4s 자리로 들어가.',
    '아연에서 늘어난 전자는 구리에서 하나만 차 있던 4s 의 남은 자리로 들어가.')

# ══ 검사 ═══════════════════════════════════════════════════════════════
seq = [by[f'M0{i}']['answer'] for i in range(1991, 2001)]
assert Counter(seq) == Counter({0: 3, 1: 3, 2: 2, 3: 2}), dict(Counter(seq))
for i in range(1991, 2001):
    z = by[f'M0{i}']
    assert (json.dumps(z['choices'], ensure_ascii=False), z['stem'], z['answer']) == before[i], \
        f'M0{i}: 발문·선지·정답 불변 위반'
    assert len(z['solution']) >= 300, (i, len(z['solution']))
    assert '★' not in z['solution'] and '★' not in z['stem'], f'M0{i}: G10 강조 표기'
    head = z['solution'].split('\n\n')[1]
    a = z['answer']
    assert (MK[a] + '가 옳아' in head) or (MK[a] + '이 옳아' in head), z['id']
    for k in range(4):
        assert (MK[k] + ' ' + z['choices'][k]) in z['solution'], (z['id'], k)

assert '다 품고 있는 가장 가까운 비활성' in by['M01997']['solution']
assert '앞에 오는 비활성' not in by['M01997']['solution']
assert '채움 차례와 반대가 돼' in by['M01992']['solution']
assert '하나만 차 있던 4s 의 남은 자리' in by['M01991']['solution']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('7차 조치 완료 — 해설 3문장. 발문·선지·정답 불변. ★P3 마감★')
