# -*- coding: utf-8 -*-
"""T15 P2 7차 조치 — defender 확인 순회 RC-A·RC-B (M02315 한 문항).

RC-A: 6차의 완화가 해설 본문에만 닿아, 같은 문항의 근거와 ② 단평에는 절대
      문면이 그대로 남았다. defender 가 지목한 대로 낱말 하나씩만 얹는다.
RC-B: '둘 다 주로 유효 핵전하와 …' 는 '주로' 의 수식 범위가 '둘 다' 로도
      읽힌다. 부사를 서술어 쪽으로 옮겨 관형절에 묶는다.
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


# RC-A ① 근거(cor) — '정하는 양이므로' 앞에 '주로'
rep("'수가 정하는 양이므로, 한쪽이 다른 쪽의 원인이 아니라 같은 원인에서 나온 두 결과로서 '",
    "'수가 주로 정하는 양이므로, 한쪽이 다른 쪽의 원인이 아니라 같은 원인에서 나온 두 결과로서 '")

# RC-A ② 단평(wmap) — '같은 원인' 앞에 '주된'
rep("'같은 원인의 두 결과야.',", "'주된 원인이 같은 두 결과야.',")

# RC-B 해설 ② 반박 — 부사를 서술어 쪽으로
rep("'인과가 없어 — 둘 다 주로 유효 핵전하와 껍질 수가 정하는 결과지. 결과 하나를 다른 결과의 '",
    "'인과가 없어 — 둘 다 유효 핵전하와 껍질 수가 주로 정하는 결과지. 결과 하나를 다른 결과의 '")

KEEP = [
    "'이온화 에너지를 정하는 것도 주로 그 둘이지. 두 양의 주된 원인이 같으니 한쪽이 다른 쪽의 '",
    "'두 양은 유효 핵전하와 껍질 수라는 같은 원인에서 나온 두 결과다'], 3,",
    "'두 양이 함께 움직이면 공통 원인을 먼저 찾는다.'",
]
for k in KEEP:
    assert k in body, 'KEEP 사라짐: %r' % k[:50]

GONE = ["'수가 정하는 양이므로", "둘 다 주로 유효", "'같은 원인의 두 결과야.',"]
for g in GONE:
    assert g not in body, 'GONE 남음: %r' % g

WANT = ['수가 주로 정하는 양이므로', '껍질 수가 주로 정하는 결과지', '주된 원인이 같은 두 결과야']
for w in WANT:
    assert w in body, 'WANT 없음: %r' % w

try:
    ast.parse(body)
except SyntaxError as e:
    sys.stderr.write('문법 오류 %s — 원본 복구\n' % e)
    io.open(SRC, 'w', encoding='utf-8').write(BEFORE)
    raise

io.open(SRC, 'w', encoding='utf-8').write(body)
print('조치 3곳 기록 — M02315 근거·② 단평·해설 ② 반박')
