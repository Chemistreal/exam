# -*- coding: utf-8 -*-
"""T13 P1 — 10차 조치 (어구 하나 · 마감 직전).

마감 재확인에서 defender 는 **F2 실패 후보 없음**(오답 서른 전부 '변호 궁색'),
factchecker 는 **사실 오류 없음** 을 보고했다. factchecker 가 남긴 △ 는 하나다.

  M01980 ③ 반박: "거기에 전이금속 중성 원자에는 4s² 가 있다는 **사실**까지
  말없이 얹으면 …"

  오류 경로 자체는 정확히 30 을 낳는다(3d 에서 빠졌다고 보면 중성 3d¹⁰ → 28,
  4s² 를 얹으면 Zn 30). 문제는 **학생이 잘못 얹은 전제를 '사실' 이라 부른 것**
  이다. Cr(4s¹3d⁵)·Cu(4s¹3d¹⁰)는 예외이고, 무엇보다 ★같은 배치의 M01978 이
  바로 그 Cr 의 4s¹3d⁵ 를 정면으로 다룬다.★ M01978 을 푼 학생이 여기서
  "전이금속은 4s²" 를 사실로 읽으면 잘못 일반화한다.

→ factchecker 가 제안한 표현을 그대로 쓴다 — '어림' 으로 낮추고 예외를 한 마디
  붙인다. ★단정을 약화시키는 방향뿐이라 새 사실 주장을 만들지 않는다.★

  (덤으로 아연은 IUPAC 기준으로 전이금속에 넣지 않는다 — 그 점에서도 '전이금속
  중성 원자' 라는 단정은 이 자리에 맞지 않았다.)

이로써 P1 을 닫는다. 선지·발문·정답·오답 메타는 8차 이후 한 글자도 바뀌지
않았고, 9·10차는 해설의 서술만 손댔다.
"""
import json

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']

bank = json.load(open(BANK, encoding='utf-8'))
by = {x['id']: x for x in bank}
before = {i: (json.dumps(by[f'M0{i}']['choices'], ensure_ascii=False),
              by[f'M0{i}']['stem'], by[f'M0{i}']['answer']) for i in range(1971, 1981)}

it = by['M01980']
old = '거기에 전이금속 중성 원자에는 4s² 가 있다는 사실까지 말없이 얹으면'
new = ('거기에 전이금속은 대개 4s² 를 갖는다는 어림까지 말없이 얹으면 — Cr 과 Cu 처럼 '
       '4s¹ 인 예외도 있는데 말이지 —')
assert it['solution'].count(old) == 1
it['solution'] = it['solution'].replace(old, new)

for i in range(1971, 1981):
    x = by[f'M0{i}']
    assert (json.dumps(x['choices'], ensure_ascii=False), x['stem'], x['answer']) == before[i], i
    assert len(x['solution']) >= 300, (i, len(x['solution']))
    head = x['solution'].split('\n\n')[1]
    a = x['answer']
    assert (MK[a] + '가 옳아' in head) or (MK[a] + '이 옳아' in head), x['id']
    for k in range(4):
        assert (MK[k] + ' ' + x['choices'][k]) in x['solution'], x['id']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('10차 조치 완료 — M01980 ③ 반박의 단정을 어림으로 낮추고 예외를 밝힘. 구조 불변 확인.')
