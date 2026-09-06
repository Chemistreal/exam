# -*- coding: utf-8 -*-
"""T13 P1 — 9차 조치 (서술 1건 · 화학 주장·선지·발문 불변).

8차의 서술 두 손질을 확인하러 보낸 factchecker 가 **두 손질은 깨끗하다고
확인하면서, 6차부터 남아 있던 내적 모순 하나를 새로 짚었다.**

  M01975 ③ 반박: "나중에 채운 3d 부터 빼다가 **모자라니** 4s 로 넘어간 셈이지."

  Mn 은 [Ar] 4s² 3d⁵ 라 3d 에 다섯이 있다. 채운 역순으로 3d 부터 빼면 셋을
  다 뺄 수 있어 **모자랄 일이 없다.** 그 경로가 실제로 낳는 값은 ①(3d 에서
  셋)이지 ③ 이 아니다. 게다가 같은 해설의 ① 반박이 "셋을 다 3d 에서 빼면
  4s² 가 그대로 남는데" 라고 **스스로 3d 에 여유가 있음을 확인해 놓아**
  두 반박이 서로 어긋났다.

★이 지적이 6차 순회에서는 나오지 않았다★ — 6차 factchecker 는 M01975 를
"문제없음" 으로 넘겼다. 그 회차의 사실 검증이 정원·양자수·홀전자 같은
수치 대조에 무게를 실었기 때문으로 보인다. **닫는 회차에 '이 두 자리를
특히 보라' 고 좁혀 준 것이 오히려 전체를 다시 훑게 만들었다.**

  ▸ 규칙: 마감 확인 패스는 **바뀐 자리를 지목하되 전체를 다시 훑으라고 함께
    적을 것.** 이번에 그렇게 적어 하나를 더 건졌다.

→ 경로를 **두 규칙의 혼용**으로 다시 적는다. 채운 역순으로 3d 에 손을 대다가
도중에 바깥 껍질 우선이 떠올라 남은 하나를 4s 에서 뺀 것이고, 잘못은 '모자라서'
가 아니라 **3d 를 먼저 건드린 것 자체**다.
"""
import json

BANK = 'master/master_bank.json'
MK = ['①', '②', '③', '④']

bank = json.load(open(BANK, encoding='utf-8'))
by = {x['id']: x for x in bank}
before = {i: (json.dumps(by[f'M0{i}']['choices'], ensure_ascii=False),
              by[f'M0{i}']['stem'], by[f'M0{i}']['answer'])
          for i in range(1971, 1981)}

it = by['M01975']
old = ('③ 3d 에서 둘을 빼고 4s 에서 하나: 채운 역순이라는 생각을 절반만 쓴 거야. 나중에 채운 '
       '3d 부터 빼다가 모자라니 4s 로 넘어간 셈이지. 그런데 제거는 채운 역순이 아니라 바깥 '
       '껍질부터야. 4s 에 전자가 남아 있는 한 그것이 가장 바깥이니 먼저 나가고, 4s 가 완전히 '
       '빈 다음에야 3d 차례지.')
new = ('③ 3d 에서 둘을 빼고 4s 에서 하나: 두 생각을 섞어 쓴 값이야. 채운 역순이라는 생각으로 '
       '나중에 채운 3d 에 먼저 손을 대다가, 도중에 바깥 껍질부터라는 규칙이 떠올라 남은 하나를 '
       '4s 에서 뺀 셈이지. 그런데 3d 를 먼저 건드린 것부터가 잘못이야. 4s 에 전자가 남아 있는 '
       '한 그것이 가장 바깥이니 먼저 나가고, 4s 가 완전히 빈 다음에야 3d 차례지.')
assert it['solution'].count(old) == 1, it['solution'].count(old)
it['solution'] = it['solution'].replace(old, new)

for d in it['distractors']:
    if d['opt'] == 2:
        d['error'] = '채운 역순과 바깥 껍질 우선을 섞어 씀 — 3d 를 먼저 건드린 것부터가 잘못'

for i in range(1971, 1981):
    x = by[f'M0{i}']
    now = (json.dumps(x['choices'], ensure_ascii=False), x['stem'], x['answer'])
    assert now == before[i], f'M0{i}: 서술만 고치는 회차인데 구조가 바뀌었다'
    assert len(x['solution']) >= 300, (i, len(x['solution']))
    head = x['solution'].split('\n\n')[1]
    a = x['answer']
    assert (MK[a] + '가 옳아' in head) or (MK[a] + '이 옳아' in head), x['id']
    for k in range(4):
        assert (MK[k] + ' ' + x['choices'][k]) in x['solution'], x['id']

json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('9차 조치 완료 — M01975 ③ 반박을 두 규칙의 혼용으로 다시 적음. 구조 불변 확인.')
