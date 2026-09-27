# -*- coding: utf-8 -*-
"""감사40 — T16 전자친화도·전기음성도 (M02791~M02954, 164제) 기계 점검 리포트.

  A~S 는 ★auditlib★ 에 옮겨 두었다(감사37~39 가 세 벌 베껴 적던 자리다).
  여기에는 ★이번 테마의 검증 순회가 값을 치르고 세운 것★ 만 더한다 — T·U·V·W.
  판정이 필요한 것은 △ 로만 적고 여기서 고치지 않는다.

  ★T 축과 방향이 어긋난 단정★
    ▸ ★첫 판은 버렸다 — 11 건이 울고 열한 건 모두 오탐이었다.★ 처음에는 '성질어와
      방향어가 함께 있는데 축어가 없는 문장' 으로 세웠는데, 걸린 것은 죄다
      '밀치는 힘이 커지므로 반지름이 커진다' 같은 ★기제 설명★ 이었다. 기제를 적는
      문장에 축을 달라고 요구하는 검사였던 셈이다.
    ▸ 더 나쁜 것은 ★정작 잡아야 할 자리를 놓쳤다★ 는 점이다. M02852 의 흠은
      '2주기에서 3주기로 가면 값이 커진다' 였고, 이 문장에는 축어(주기)가 ★있다★.
      흠은 축이 없는 것이 아니라 ★축과 방향이 어긋난★ 것이었다.
    ▸ 그래서 표로 다시 세운다 — 같은 족에서 아래로(주기 번호가 커지는 쪽)는
      전기 음성도·이온화 에너지·전자친화도가 ★작아지고★ 반지름은 커진다.
      같은 주기에서 오른쪽으로는 그 반대다. 문장이 이 표와 어긋나면 짚는다.
      ★기제 설명은 축어가 없어 애초에 걸리지 않는다★ — 오탐이 사라진 까닭이다.

  ★U 정의 그 자체인 오답★
    ▸ M02851③ 은 오답으로 지정했는데 ★정의 그 자체★ 라 참이었다. 오답이 정의문 꼴
      ('…란 …이다' · '…를 말한다' · '…로 정의한다')이면 그 자체로 참일 위험이 크다.
      정의를 오답으로 쓰려면 ★정의를 비틀어야★ 하고, 비틀면 정의문 꼴이 남지 않는다.

  ★V 갈라 적힌 용어 표기★
    ▸ M02856 과 M02859 가 같은 것을 '재는 값' 과 다른 말로 불러 부딪쳤다. 그래서 범위
      안의 표기 혼용을 세려 했는데, ★첫 판은 뜻이 아니라 말투를 세었다★ —
      '재는 값 ↔ 잰 값'(시제) · '내주는 ↔ 내놓는'(같은 뜻의 두 말) 두 건이 걸렸고
      둘 다 오탐이었다. 한국어는 같은 뜻을 여러 말로 적는 것이 흠이 아니다.
    ▸ 기계로 셀 수 있는 것은 ★못 박은 용어의 표기가 갈리는 자리★ 뿐이다(띄어쓰기·붙여쓰기).
      뜻이 부딪치는 자리는 사람이 읽어야 보인다 — 그 몫은 검증자 순회에 남긴다.

  ★W 규약을 밝히지 않고 쓴 음수 표기★
    ▸ M02863④ 는 '그 배치가 세운 음수 규약' 안에서 참이 되어 버렸다. 그래서 음수 규약과
      크기 규약이 한 범위에 섞이는지를 세었더니 3제 ↔ 11제로 울렸는데, ★세 제는 모두
      발문이 스스로 규약을 밝힌 문항★ 이었다('나오는 쪽을 음수로 적은 표에서…').
      규약을 다루는 문항이 규약을 쓰는 것은 흠이 아니다 — 오탐이다.
    ▸ 흠은 ★밝히지 않고 쓰는★ 자리다. 그래서 선지·근거·해설이 음수 표기에 기대는데
      ★발문에 규약을 세우는 말이 없는★ 문항만 짚는다. 문항 하나로 서지 못하는 자리다.
"""
import re
import sys
from collections import Counter

import auditlib

LO = sys.argv[1] if len(sys.argv) > 1 else 'M02791'
HI = sys.argv[2] if len(sys.argv) > 2 else 'M02954'

items = auditlib.load(LO, HI)
F = []


def rep(it, cls, msg):
    F.append((it['id'], cls, msg))


auditlib.core(items, rep)

MK = auditlib.MK
FIELDS = ('answer_proof', 'calc_check', 'solution', 'device')
#   ★축과 방향의 표★ — 아래로(주기 번호가 커지는 쪽) / 오른쪽으로(족 번호가 커지는 쪽)
#     교재가 한 줄로 적는 것을 그대로 옮긴다. 반지름만 방향이 뒤집힌다.
TABLE = {'아래': {'전기음성도': -1, '이온화': -1, '전자친화도': -1, '반지름': +1},
         '오른쪽': {'전기음성도': +1, '이온화': +1, '전자친화도': +1, '반지름': -1}}
PROPK = [('전기음성도', re.compile(r'전기\s?음성도')),
         ('이온화', re.compile(r'이온화\s?에너지')),
         ('전자친화도', re.compile(r'전자\s?친화도')),
         ('반지름', re.compile(r'(원자\s?)?반지름'))]
DOWN = re.compile(r'(같은 족에서 아래|아래로 (갈|내려)|주기가 커지|주기 번호가 커지'
                  r'|\d주기에서 \d주기로|껍질 수가 늘)')
RIGHT = re.compile(r'(같은 주기에서 오른쪽|오른쪽으로 (갈|가)|족 번호가 커지'
                   r'|원자 번호가 커질수록.{0,12}같은 주기)')
UP = re.compile(r'(커진|늘어난|증가|더 크|세진)')
DN = re.compile(r'(작아진|줄어든|감소|더 작|약해진)')
DEFN = re.compile(r'(이란|라 한다|라고 한다|를 말한다|로 정의|이라 부른|라 부른)')
SIGNM = re.compile(r'(음수|음의 값|[-−]\s?\d|부호가 음)')
SIGNP = re.compile(r'(양수|양의 값|값이 크|크게 적|절댓값)')

for it in items:
    cs, a = it['choices'], it['answer']

    # ── T ★축과 방향이 어긋난 단정★ (첫 판은 11/11 오탐으로 버렸다) ─────
    #   ▸ ★둘째 판도 두 건 다 오탐이었다★ — '오른쪽으로 갈수록 유효 핵전하가 커지고
    #     반지름이 작아진다' 를 한 문장으로 보아 '커진'을 반지름에 붙였다. 한 문장이
    #     성질마다 다른 방향을 말한다. 그래서 ★성질어 뒤 한 마디만★ 본다.
    for fld in FIELDS:
        t = it.get(fld) or ''
        for sent in re.split(r'(?<=[.!?…야어다])\s+', t):
            ax = '아래' if DOWN.search(sent) else ('오른쪽' if RIGHT.search(sent) else None)
            if not ax:
                continue
            for key, pat in PROPK:
                for m in pat.finditer(sent):
                    seg = re.split(r'(?:고 |며 |지만|, |\. )', sent[m.end():], 1)[0]
                    d = (+1 if UP.search(seg) else 0) or (-1 if DN.search(seg) else 0)
                    if d and TABLE[ax][key] != d:
                        rep(it, 'T', '%s — %s 쪽인데 %s 가 %s 고 적었다 · %s'
                            % (fld, ax, key, '커진다' if d > 0 else '작아진다',
                               (sent[max(0, m.start() - 14):m.end() + 24]).strip()))
                        break

    # ── U ★정의 그 자체인 오답★ ────────────────────────────────────────
    for k in range(4):
        if k != a and DEFN.search(cs[k]):
            rep(it, 'U', '오답 %s 가 정의문 꼴이다 — 「%s」' % (MK[k], cs[k]))

    # ── W ★부호 규약의 갈림★ (범위별로 모아 아래에서 센다) ──────────────
    blob = ' '.join([it['stem']] + list(cs) + [it.get(f) or '' for f in FIELDS])
    if re.search(r'전자\s?친화도', blob):
        it['_sign'] = ('음' if SIGNM.search(blob) else '') + ('양' if SIGNP.search(blob) else '')

# ── V ★갈라 적힌 용어 표기★ (첫 판은 2/2 오탐 — 말투를 세고 있었다) ───────
#   못 박은 용어의 띄어쓰기만 본다. 같은 뜻의 두 낱말은 흠이 아니다.
PAIRS = [('전기음성도', '전기 음성도'), ('전자친화도', '전자 친화도'),
         ('이온화에너지', '이온화 에너지'), ('유효핵전하', '유효 핵전하'),
         ('원자반지름', '원자 반지름')]
RANGE_F = []


def blob(i):
    return ' '.join([i['stem']] + list(i['choices'])
                    + [i.get(f) or '' for f in FIELDS])


for x, y in PAIRS:
    hx = [i['id'] for i in items if re.search(x + r'(?!\s)', blob(i).replace(y, '·'))]
    hy = [i['id'] for i in items if y in blob(i)]
    if hx and hy:
        RANGE_F.append(('V', '「%s」 %d제 ↔ 「%s」 %d제 — %s / %s'
                        % (x, len(hx), y, len(hy), ' '.join(hx[:4]), ' '.join(hy[:4]))))

# ── W ★규약을 밝히지 않고 쓴 음수 표기★ (첫 판은 3/3 오탐) ────────────────
DECL = re.compile(r'(음수로 적|나오는 쪽을 음수|부호|음의 값으로)')
for it in items:
    rest = ' '.join(list(it['choices']) + [it.get(f) or '' for f in FIELDS])
    if re.search(r'전자\s?친화도', rest) and SIGNM.search(rest) and not DECL.search(it['stem']):
        rep(it, 'W', '음수 표기에 기대는데 발문이 규약을 세우지 않는다')

CLS = dict(auditlib.CLS)
CLS.update({'T': '★축과 방향이 어긋난 단정★', 'U': '★정의 그 자체인 오답★',
            'V': '★갈라 적힌 용어 표기(범위)★', 'W': '★밝히지 않은 음수 표기★'})

print('감사40 — T16 전자친화도·전기음성도 %s~%s · %d제' % (LO, HI, len(items)))
print('=' * 74)
c = Counter(x[1] for x in F)
c.update(Counter(k for k, _ in RANGE_F))
for k in sorted(CLS):
    print('  %s %-24s %3d 건' % (k, CLS[k], c.get(k, 0)))
print('-' * 74)
print('  합계 %d 건 · 깨끗한 문항 %d/%d'
      % (len(F) + len(RANGE_F), len(items) - len({x[0] for x in F}), len(items)))
print('=' * 74)
for k in sorted(CLS):
    rows = [x for x in F if x[1] == k]
    rrow = [x for x in RANGE_F if x[0] == k]
    if not rows and not rrow:
        continue
    print('\n■ %s %s — %d 건' % (k, CLS[k], len(rows) + len(rrow)))
    for fid, _, msg in rows:
        print('  %s  %s' % (fid, msg))
    for _, msg in rrow:
        print('  (범위)   %s' % msg)
