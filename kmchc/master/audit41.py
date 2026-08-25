# -*- coding: utf-8 -*-
"""감사41 — T22 탄화수소 (M02627~M02790, 164제) 기계 점검 리포트.

  A~S 는 ★auditlib★ 에 있다. 여기에는 T22 검증 순회가 값을 치르고 세운 것만 더한다.

  ★X 계산 줄이 정답을 오답처럼 적은 자리★
    ▸ M02723 은 calc_check 의 번호가 한 칸 밀려 ★정답 번호에 물리는 까닭★ 이 적혀 있었다.
      calc 는 '① 방향이 반대 / ② 관례에 맞음' 처럼 오답을 번호로 짚는 자리라서, 정답
      번호 뒤에 물리는 말이 붙으면 셈 줄과 판정이 어긋난 것이다. 손으로는 잘 안 보인다.

  ★Y 로마자 화학식 표기★
    ▸ 이 은행은 화학식을 ★이름으로 적는다★(CH₄ 대신 메테인). 아래 첨자를 쓸 수 없는 자리가
      많아 세운 규약이다. 로마자 화학식이 남은 자리를 범위별로 센다.
    ▸ ★원소 기호 하나(C·H)와 이름 없는 약칭은 흠이 아니다★ — 첫 판이 'C' 한 글자까지
      울려 오탐이 쏟아졌다. 그래서 ★로마자 뒤에 숫자가 붙은 꼴★(CH4·C2H6)만 짚는다.

  ★Z 절대어 단정★
    ▸ M02715 의 '첨가와 치환은 함께 일어나지 않는다' 는 ★사실이 아니었다★ — 조건에 따라
      함께 일어난다. 이런 자리는 '결코·절대·항상·반드시·언제나·함께 …않는다' 꼴로 나타난다.
    ▸ ★첫 판은 14/14 오탐이었다★ — 오답에서 세었기 때문이다. 오답은 ★거짓이어야 하고★,
      거짓을 만드는 가장 흔한 길이 지나친 단정이다('섞기만 하면 언제나 일어난다').
      오답이 절대어를 쓰는 것은 흠이 아니라 ★설계★ 다. 해설의 '탄소는 언제나 손이 넷' 도
      참인 단정이다.
    ▸ 그래서 정답 쪽(정답 선지·answer_proof·해설의 정답 마디)에서 다시 세었다.
      ★둘째 판도 17/17 오탐이었다★ — 걸린 것은 죄다 참인 단정이었다:
      '탄소는 언제나 결합 넷' · '벤젠 여섯 결합의 길이가 모두 같다' · '벤젠은 평면' ·
      '알켄은 알케인보다 수소가 둘 적다'. 화학Ⅰ 범위에서 예외가 없는 말들이다.
    ▸ ★그래서 이 검사를 버린다.★ 절대어는 ★거짓의 표지가 아니다★ — 참인 단정도 절대어로
      적히고, 거짓인 단정도 절대어 없이 적힌다(M02715 의 '함께 일어나지 않는다' 는
      절대어 목록에 넣어야 걸리는데, 그러면 참인 '함께 일어나지 않는' 자리까지 물린다).
      ★사실의 참거짓은 기계가 아니라 factchecker 검증자가 가린다★ — 감사는 꼴을 보고
      검증자는 사실을 본다. 이 갈림을 흐리면 감사 리포트가 판정 대기 목록이 된다.
      두 판 모두 남겨 적는 까닭은, 다음 테마에서 같은 검사를 다시 세우지 않게 하려는 것이다.
"""
import re
import sys
from collections import Counter

import auditlib

LO = sys.argv[1] if len(sys.argv) > 1 else 'M02627'
HI = sys.argv[2] if len(sys.argv) > 2 else 'M02790'

items = auditlib.load(LO, HI)
F = []


def rep(it, cls, msg):
    F.append((it['id'], cls, msg))


auditlib.core(items, rep)

MK = auditlib.MK
REJ = re.compile(r'(아니|틀|반대|잘못|어긋|빠뜨|뒤집|헷갈|넘겨|무너)')
FORM = re.compile(r'\b[A-Z][a-z]?\d')
#   ABS 는 남겨 둔다 — 버린 검사의 잣대다(위 Z 머리글).
ABS = re.compile(r'(결코|절대로|언제나|항상|반드시|모두 (?:다|같)|함께 일어나지 않|'
                 r'하나도 없|예외가 없)')

for it in items:
    cs, a = it['choices'], it['answer']

    # ── X ★계산 줄이 정답을 오답처럼 적은 자리★ ────────────────────────
    calc = it.get('calc_check') or ''
    for m in re.finditer(re.escape(MK[a]) + r'[^①②③④/]*', calc):
        seg = m.group(0)
        if REJ.search(seg):
            rep(it, 'X', '계산 줄이 정답 %s 를 물리는 말로 적었다 — %s'
                % (MK[a], seg.strip()[:40]))
            break

    # ── Y ★로마자 화학식 표기★ ──────────────────────────────────────────
    for fld in ('stem', 'solution'):
        for m in FORM.finditer(it[fld]):
            rep(it, 'Y', '%s 에 로마자 화학식 — %s' % (fld, m.group(0)))
            break
    for k, c in enumerate(cs):
        if FORM.search(c):
            rep(it, 'Y', '선지 %s 에 로마자 화학식 — 「%s」' % (MK[k], c))

    # ── Z ★절대어 단정★ — ★버린 검사★ (첫 판 14/14 · 둘째 판 17/17 오탐)
    #   위 머리글에 까닭을 적어 두었다. 절대어는 거짓의 표지가 아니다.
    #   이 자리는 ★비워 둔다★ — 지우면 다음 테마에서 같은 검사를 다시 세운다.

CLS = dict(auditlib.CLS)
CLS.update({'X': '★계산 줄이 정답을 물린다★', 'Y': '★로마자 화학식 표기★'})

print('감사41 — T22 탄화수소 %s~%s · %d제' % (LO, HI, len(items)))
print('=' * 74)
c = Counter(x[1] for x in F)
for k in sorted(CLS):
    print('  %s %-24s %3d 건' % (k, CLS[k], c.get(k, 0)))
print('-' * 74)
print('  합계 %d 건 · 깨끗한 문항 %d/%d'
      % (len(F), len(items) - len({x[0] for x in F}), len(items)))
print('=' * 74)
for k in sorted(CLS):
    rows = [x for x in F if x[1] == k]
    if not rows:
        continue
    print('\n■ %s %s — %d 건' % (k, CLS[k], len(rows)))
    for fid, _, msg in rows[:40]:
        print('  %s  %s' % (fid, msg))
    if len(rows) > 40:
        print('  … %d 건 더' % (len(rows) - 40))
