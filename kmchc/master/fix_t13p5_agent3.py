# -*- coding: utf-8 -*-
"""T13 P5 (M02011~M02020) 층5 3차 조치 — 2차 조치가 낳은 더 강한 F5 를 되돌린다.

2차 순회: factchecker 마감 가능(사실 오류 0 · △ 7) · defender 마감 가능(한 줄 조건)
          · solver 마감 불가(F5 상 하나) · student-sim 은 529 로 죽어 재기동

★2차에 내가 sim 의 안을 받아 만든 구조가 더 강한 우회로를 낳았다.★
  크로뮴 문항의 ③ 을 까닭 축으로 옮겨 ②③④ 가 배치를 공유하게 했더니, 배치가
  4s¹3d⁵ 셋 대 4s²3d⁴ 하나로 ★3 : 1 로 쏠려 그 쏠림 자체가 정답 배치를 누설★한다.
  게다가 남은 둘이 크로뮴을 몰라도 무너진다 — ② 는 s 부껍질 정원이 2 라는 같은
  배치 안(M02012·M02014)의 기초로 거짓이고, ③ 은 발문이 '바닥상태' 를 물었는데
  까닭이 '들뜬 상태' 라 자기모순으로 거짓이다. 곧 실질 2지선다, 메타 단서까지
  넣으면 1지선다다(solver F5 상).
  → solver 가 낸 ★2 : 2 교차★ 로 간다. 배치 둘 × 까닭 둘을 엇갈리게 짝지으면
    배치 다수결도 까닭 다수결도 통하지 않고, ★배치와 까닭을 둘 다 알아야만 갈린다.★
      ① 4s² 3d⁴ + 반채움 까닭  → 까닭은 참이나 3d⁴ 는 반채움이 아니다(짝이 어긋남)
      ② 4s¹ 3d⁵ + 쌓음 까닭    → 배치는 참이나 쌓음대로면 4s² 3d⁴ 다(짝이 어긋남)
      ③ 4s² 3d⁴ + 쌓음 까닭    → ★안으로는 정합한 오답★ = 지배적 오개념의 착지점
      ④ 4s¹ 3d⁵ + 반채움 까닭  ← 정답
    네 선지가 모두 40 자로 같아져 길이 단서도 사라진다.
  ▸ 2차에 쓴 '들뜬 상태' 까닭은 버린다 — defender 는 그것을 "어떤 독법에서도 거짓"
    으로 안전 판정했지만, solver 가 짚었듯 ★발문과의 자기모순은 개념 오답이 아니라
    공짜 배제★ 다. 두 판정은 서로 다른 것을 본 것이라 어긋나지 않는다.

★defender 의 한 줄★
  M02019 발문 — 2차에 넓힌 가드 "빈 오비탈도 모두 센다" 가 반대편을 열었다.
  물음의 세는 대상은 `묶음` 인데 끝문장의 목적어는 `빈 오비탈`, 서술어는 `모두
  센다` 라, 끝문장을 독립 지시문("오비탈을 다 세라")으로 떼어 읽는 독법이 산다.
  그리고 n=3 오비탈 총수는 정확히 9 — ④ 가 바로 그 값이다. ★발문이 오답을 지목한다.★
  → `묶음에 포함한다` 로 대상을 묶음에 재고정한다. 1차의 구멍은 그대로 막힌다.

★factchecker 의 △ 여섯 (모두 표현 다듬기 — 값이 싸서 받는다)★
  ㉠ M02011 — "그 결과" 가 순서까지 반발에서 연역되는 것처럼 읽힌다. 원인과 순서를
     두 문장으로 끊는다.
  ㉡ M02017 ② — "짝은 아직 하나도 없지" 는 문면 그대로면 거짓이다(질소는 1s²·2s² 에
     짝이 있다). '2p 안에는' 으로 한정한다.
  ㉢ M02013 ③④ — ③ 은 중성 원자(12)를, ④ 는 정답 이온(10)을 기준으로 삼아 기준선이
     오간다. 둘 다 정답의 열을 기준으로 통일한다.
  ㉣ M02012 ② — ① 에서는 범위 초과를 짚으면서 ② 의 −3 이 같은 이유로 범위 밖인 점은
     말하지 않는다. 한 구절 더한다.
  ㉤ M02016 ④ — "4s 앞에 3d 와 4p 를 모두 두고" 는 어떤 셈법으로도 4p 가 4s 보다
     앞설 수 없어 부자연스럽다. 무해한 표현으로 바꾼다.
  ㉥ M02019 ④ — "셋씩 다섯씩 묶여" 는 3s 하나가 빠져 읽힌다.

★반려한 것★
 · M02013 ③ 을 10 전자 오답으로 (defender 2순위, '선택 교정') — ③ 은 sim 1차 실측에서
   ★A 와 B 가 함께 앉은 자리★ 다. 셈만으로 지워지는 것은 사실이나, 그 대가로 가장
   강한 유인을 잃는다. defender 도 ④ 는 남길 값어치가 있다고 적었고 ③ 만 바꾸면
   10 전자가 셋이 되어 이번에는 ④ 하나만 셈으로 지워진다 — 이득이 반쪽이다.
 · M02011 ② 의 까닭을 '가리움 효과' 로 (solver F1 하) — ★같은 순회의 factchecker 가
   가리움을 부껍질 갈라짐의 원인으로 쓰면 침투 논거라고 판정했다.★ 두 검증자가 정면으로
   어긋난 자리라 범위 판정을 따른다. factchecker 는 2차에서 현행 문면을 "교과서가 쓰는
   바로 그 문장 — 범위 위반 아님" 으로 확인했다.
 · M02011 ↔ M02019 문항 간 단서 유출 (defender 6순위) — 실재한다. M02011 을 푼 학생은
   M02019 에서 ①(1 개)을 자동 배제한다. 다만 M02019 는 묶음의 ★개수★ 를 묻고 남은
   셋(2·3·9)은 그 대소만으로 갈리지 않는다. 각도를 바꾸는 대신 ★조판 때 두 문항을
   떨어뜨릴 것★ 을 watch 에 적어 둔다.
 · 범위 참고(factchecker △7) — Cr(24) · Sc(21) · Zn(30)이 원자번호 20 을 넘는다.
   개념 대장 C13-020(교재 89 쪽)이 Cr·Cu 예외를, C13-021 이 전이금속 동정을 각각
   교재에서 뽑은 각도이므로 범위 안이다.
"""
import json
from collections import Counter

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']
IDS = ['M%05d' % n for n in range(2011, 2021)]

A_CFG = '[Ar] 4s² 3d⁴'      # 쌓음원리의 예측 — 크로뮴의 실제 바닥상태가 아니다
B_CFG = '[Ar] 4s¹ 3d⁵'      # 실제 바닥상태
R_BUILD = '쌓음원리에 따라 4s 부터 차례로 채우기 때문'
R_HALF = '3d 가 반만 채워진 배치가 더 안정하기 때문'


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

# ── 1. M02015 — 배치 둘 × 까닭 둘을 2 : 2 로 엇갈린다 ─────────────────────
it = D['M02015']
c1 = f'{A_CFG} — {R_HALF}'
c2 = f'{B_CFG} — {R_BUILD}'
c3 = f'{A_CFG} — {R_BUILD}'
c4 = f'{B_CFG} — {R_HALF}'
setc(it, [c1, c2, c3, c4],
     [(c1, '까닭은 옳으나 3d⁴ 는 반채움이 아니다 — 까닭이 그 배치를 낳지 않는다', 'proc'),
      (c2, '배치는 옳으나 쌓음원리대로면 4s² 3d⁴ 가 나온다 — 까닭이 그 배치를 낳지 않는다',
       'proc'),
      (c3, '쌓음원리를 그대로 적용한 정합적 오답 — 크로뮴이 바로 그 예외다', 'proc')])
it['answer_proof'] = ('₂₄Cr 은 4s 의 전자 하나를 3d 로 올려 반채움을 만든 [Ar] 4s¹ 3d⁵ 이 '
                      '바닥상태 — 배치와 까닭이 서로 맞물려야 옳다')
it['calc_check'] = 'Cr 24 = [Ar](18) + 4s¹ + 3d⁵ / 홀전자 1+5 = 6 (4s²3d⁴ 이면 4)'
it['objective'] = ('크로뮴의 예외 배치와 그 까닭(반채움 안정화)을 짝지어, 어느 한쪽만 알아서는 '
                   '고를 수 없게 확인')
resol(it, '배치 둘과 까닭 둘을 엇갈려 놓았어. 어느 한쪽만 알아서는 고를 수 없어.',
      '먼저 쌓음원리대로만 채워 보자. 아르곤까지 열여덟을 채우고 남은 여섯을 4s 부터 '
      '넣으면 4s² 3d⁴ 가 나와. 그런데 실제 크로뮴의 바닥상태는 4s¹ 3d⁵ 야. 4s 에 있던 '
      '전자 하나가 3d 로 올라가 있지. 까닭은 3d 부껍질의 오비탈 다섯 개에 전자가 하나씩 '
      '고루 들어간 반채움 상태가 유난히 안정하기 때문이야. 그렇게 하면 홀전자 수가 '
      '여섯으로 가장 많아져 — ④가 옳아. 여기서 확인해 둘 것이 둘 있어. 첫째, 전자의 '
      '총수는 변하지 않아. 4s¹ 과 3d⁵ 를 더하면 여섯이고 아르곤의 열여덟을 더해 스물넷, '
      '곧 원자 번호와 같지. 둘째, 이 배치는 들뜬 상태가 아니라 바닥상태야. 예외라는 말은 '
      '쌓음원리의 예측과 다르다는 뜻이지 불안정하다는 뜻이 아니거든. 배치와 까닭이 서로 '
      '맞물리는지를 한 짝씩 대 보는 것이 이 유형의 전부야.',
      {c1: '까닭은 옳은 말이야. 그런데 3d 에 넷이 든 것은 반채움이 아니야. 3d 의 오비탈은 '
           '다섯이니 반채움은 다섯이 하나씩 들어간 상태지. 까닭이 이 배치를 낳지 않아.',
       c2: '배치는 옳아. 그런데 쌓음원리를 그대로 따랐다면 4s 가 먼저 꽉 차 4s² 3d⁴ 가 '
           '나왔을 거야. 이 배치는 오히려 그 예측을 벗어난 것이라 까닭이 어긋나.',
       c3: '쌓음원리를 그대로 적용하면 정말 이 배치가 나와. 까닭과 배치가 서로 맞기는 해. '
           '그런데 크로뮴이 바로 그 예외라 실제 바닥상태가 아니야.'},
      '배치와 까닭을 한 짝씩 떼어 서로 맞물리는지 대 본다.')

# ── 2. M02019 — 가드의 대상을 묶음으로 재고정한다 ─────────────────────────
it = D['M02019']
old = ('산소(O) 원자에서 주양자수가 3 인 오비탈들을 에너지가 같은 것끼리 묶으면 '
       '묶음은 모두 몇 개가 되는가? 전자가 들어 있지 않은 빈 오비탈도 모두 센다.')
assert it['stem'] == old, it['stem']
it['stem'] = ('산소(O) 원자에서 주양자수가 3 인 오비탈들을 에너지가 같은 것끼리 묶으면 '
              '묶음은 모두 몇 개가 되는가? 전자가 들어 있지 않은 빈 오비탈도 묶음에 '
              '포함한다.')
sub(it, '그 아홉이 셋씩 다섯씩 묶여 세 준위를 이루지.',
        '그 아홉이 하나·셋·다섯으로 묶여 세 준위를 이루지.')

# ── 3. factchecker △ 다섯 ────────────────────────────────────────────────
sub(D['M02011'],
    '그 반발이 같은 껍질 안에서도 준위를 갈라 놓아 부껍질마다 에너지가 달라지지. '
    '그 결과 부양자수가 작은 쪽이 낮아져서 3s < 3p < 3d 가 돼',
    '그 반발이 같은 껍질 안에서도 준위를 갈라 놓아 부껍질마다 에너지가 달라지지. '
    '갈라진 뒤의 순서는 부양자수가 작은 쪽부터라서 3s < 3p < 3d 가 돼')
sub(D['M02017'], '홀전자가 셋이야. 짝은 아직 하나도 없지.',
                 '홀전자가 셋이야. 2p 안에는 짝이 하나도 없지.')
sub(D['M02013'], '전자를 오히려 둘 더했어. 열넷이 되니',
                 '전자를 오히려 넷 더했어. 열넷이 되니')
sub(D['M02013'], '옥텟을 채우려고 전자를 여덟이나 더했어.',
                 '옥텟을 채우려고 전자를 여덟이나 더했어. 정답보다 여덟이 많지.')
sub(D['M02012'], '개수는 다섯이 맞지만 가운데가 0 이 아니야.',
                 '개수는 다섯이 맞지만 −3 은 l = 2 의 범위 밖이고 가운데도 0 이 아니야.')
sub(D['M02016'], '여덟째는 4p 야. 4s 앞에 3d 와 4p 를 모두 두고 센 셈이지.',
                 '여덟째는 4p 야. 4s 앞에 두 자리를 더 끼워 넣고 센 셈이지.')

# ── 검사 ──────────────────────────────────────────────────────────────────
items = [D[k] for k in IDS]
assert Counter(i['answer'] for i in items) == {1: 3, 2: 2, 0: 3, 3: 2}
for k in IDS:
    assert D[k]['answer'] == before[k]['answer'], k
untouched = set(IDS) - {'M02011', 'M02012', 'M02013', 'M02015', 'M02016', 'M02017', 'M02019'}
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

# 이번 회차 구조 검사 — 배치도 까닭도 다수결이 통하지 않아야 한다
cfg = [c.split(' — ')[0] for c in D['M02015']['choices']]
rsn = [c.split(' — ')[1] for c in D['M02015']['choices']]
assert Counter(cfg) == {A_CFG: 2, B_CFG: 2}, Counter(cfg)
assert Counter(rsn) == {R_BUILD: 2, R_HALF: 2}, Counter(rsn)
assert D['M02015']['choices'][3] == f'{B_CFG} — {R_HALF}'
assert len({len(c) for c in D['M02015']['choices']}) == 1, '네 선지 길이가 같아야 한다'
assert '들뜬 상태이기 때문' not in ''.join(D['M02015']['choices'])
assert '묶음에 포함한다' in D['M02019']['stem'] and '모두 센다' not in D['M02019']['stem']
assert '갈라진 뒤의 순서는' in D['M02011']['solution']
assert 18 + 1 + 5 == 24 and 1 + 5 == 6          # Cr 검산

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('T13 P5 3차 조치 완료 — M02015 2:2 교차 · M02019 가드 재고정 · 표현 △ 다섯')
for i, c in enumerate(D['M02015']['choices']):
    print(f'  {MK[i]} {c}  ({len(c)}자)')
print(' ', D['M02019']['stem'][-40:])
