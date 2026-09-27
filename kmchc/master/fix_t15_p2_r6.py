# -*- coding: utf-8 -*-
"""T15 P2 6차 조치 — defender 3차 RC-1: M02315 해설의 절대 표현 두 곳.

블로커는 아니나 학생이 읽는 문면이 자기 ③ 반박과 엄밀히 어긋난다.
"이온화 에너지를 정하는 것도 똑같이 그 둘이지" 는 두 양이 늘 같은 짝으로
정해진다고 읽히는데, 바로 아래 ③ 반박은 15족→16족 에서 두 양이 같은 방향으로
간다고 적는다(2주기 껍질 수는 둘로 고정, Zeff N 3.834 → O 4.453 인데
IE 1402 → 1314 로 감소 — 짝지음 전자 반발이라는 셋째 몫이 있다).
문장 신설 없이 '주로' 두 낱말만 얹어 절대 표현을 눅인다.
"""
import ast, io, sys

SRC = 'build_t15_p2.py'
BEFORE = io.open(SRC, encoding='utf-8').read()
body = BEFORE


def rep(old, new, n=1):
    global body
    c = body.count(old)
    assert c == n, '%d곳 (기대 %d): %r' % (c, n, old[:60])
    body = body.replace(old, new)


# (A) 정답 근거 문장 — 두 양의 원인이 같다는 절대 표현
rep("'이온화 에너지를 정하는 것도 똑같이 그 둘이지. 두 양의 원인이 같으니 한쪽이 다른 쪽의 '",
    "'이온화 에너지를 정하는 것도 주로 그 둘이지. 두 양의 주된 원인이 같으니 한쪽이 다른 쪽의 '")

# (B) ② 반박 문장 — 같은 절대 표현
rep("'인과가 없어 — 둘 다 유효 핵전하와 껍질 수가 정하는 결과지. 결과 하나를 다른 결과의 '",
    "'인과가 없어 — 둘 다 주로 유효 핵전하와 껍질 수가 정하는 결과지. 결과 하나를 다른 결과의 '")

# 불변 확인 — 선지 문면·정답 지표·단평은 손대지 않는다
KEEP = [
    "'반지름은 껍질 수가, 이온화 에너지는 유효 핵전하가 따로 정한다'",
    "'이온화 에너지가 커지는 것이 반지름을 작게 만드는 원인이다'",
    "'두 양은 늘 정확히 반대로 움직이므로 하나로 다른 하나를 대신할 수 있다'",
    "'두 양이 함께 움직이면 공통 원인을 먼저 찾는다.'",
]
for k in KEEP:
    assert k in body, 'KEEP 사라짐: %r' % k[:50]

GONE = ['똑같이 그 둘이지', '둘 다 유효 핵전하와 껍질 수가 정하는 결과지']
for g in GONE:
    assert g not in body, 'GONE 남음: %r' % g

WANT = ['주로 그 둘이지', '두 양의 주된 원인이 같으니', '둘 다 주로 유효 핵전하와']
for w in WANT:
    assert w in body, 'WANT 없음: %r' % w

try:
    ast.parse(body)
except SyntaxError as e:
    sys.stderr.write('문법 오류 %s — 원본 복구\n' % e)
    io.open(SRC, 'w', encoding='utf-8').write(BEFORE)
    raise

io.open(SRC, 'w', encoding='utf-8').write(body)
print('조치 2곳 기록 — M02315 해설 (A) 정답 근거 (B) ② 반박')
