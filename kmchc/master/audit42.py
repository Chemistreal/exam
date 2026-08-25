# -*- coding: utf-8 -*-
"""감사42 — T18 분자의 구조 (M02955~, 저작된 만큼) 기계 점검 리포트.

  A~S 와 X 는 ★auditlib★ 에 있다. 여기에는 ★T18 이 값을 치른 것만★ 더한다.

  ★AA 화학Ⅰ 범위를 벗어난 자리 수·모양★
    ▸ C18-007 의 stmt 가 '2·3·4·5·6쌍' 을 안고 있어 M03001 이 ★삼각쌍뿔·정팔면체★ 를 물었다.
      각도를 세우는 자리에서 범위를 못 박지 않으면 저작 단계에서 그대로 문항이 된다.
    ▸ 그래서 자리 5·6 의 이름과 '자리가 다섯·여섯' 을 범위 전체에서 센다.

  ★BB 결합각 값이 은행 표준과 어긋난 자리★
    ▸ 이 테마의 값은 손에 꼽는다 — 180 · 120 · 109.5 · 107 · 104.5 · 약 119(이산화 황) ·
      92(황화 수소) · 93.5(포스핀) · 90(평면 십자의 헛값). ★109도·105도처럼 반올림된 값★ 이
      한 자리라도 섞이면 문항끼리 어긋난다(M02991 이 '120도에 조금 못 미쳐' 와 '약 120도' 로 갈렸다).

  ★CC 모양 이름과 대표 분자의 짝이 정답 쪽에서 어긋난 자리★
    ▸ ★오답 쪽에서는 세지 않는다★ — 오답은 일부러 짝을 틀리게 맞춘다(감사41 의 Z 가 가르쳐 준 것:
      감사는 꼴을 보고 검증자는 사실을 본다). 그래서 ★정답 선지와 근거 줄에서만★ 센다.
    ▸ 한 문장에 여러 분자가 함께 나오는 자리가 많아, ★그 모양에 맞는 분자가 함께 있으면 넘긴다★.

  ★DD 자리 수·비공유 수와 각의 짝이 계산 줄에서 어긋난 자리★
    ▸ 표는 (자리, 비공유) → 각 이다: (2,0)=180 · (3,0)=120 · (3,1)≈119 · (4,0)=109.5 ·
      (4,1)=107 · (4,2)=104.5. 계산 줄은 이 셋을 한 줄에 적으므로 기계로 맞댈 수 있다.
"""
import re
import sys
from collections import Counter

import auditlib

LO = sys.argv[1] if len(sys.argv) > 1 else 'M02955'
HI = sys.argv[2] if len(sys.argv) > 2 else 'M03034'

items = auditlib.load(LO, HI)
MK = auditlib.MK
F = []


def rep(it, cls, msg):
    F.append((it['id'], cls, msg))


auditlib.core(items, rep)

OUT = re.compile(r'(삼각쌍뿔|정팔면체|사각뿔|오각|자리가 다섯|자리가 여섯|자리 5개|자리 6개)')
ANG = re.compile(r'(\d+(?:\.\d+)?)\s*도')
OK = {180, 120, 109.5, 107, 104.5, 119, 119.5, 92, 93.5, 90, 360, 60, 100, 0}
SHAPE = {'직선형': ('이산화 탄소', '이플루오린화 베릴륨', '사이안화 수소', '질소'),
         '평면 삼각형': ('삼플루오린화 붕소', '폼알데하이드'),
         '정사면체형': ('메테인',),
         '삼각뿔형': ('암모니아',),
         '굽은형': ('물', '이산화 황', '황화 수소')}
MOLS = {m: s for s, ms in SHAPE.items() for m in ms}
PAIR = re.compile(r'자리\s*(\d)\s*(?:개)?[^/]{0,24}비공유\s*(\d)')
TABLE = {(2, 0): 180.0, (3, 0): 120.0, (3, 1): 119.0, (4, 0): 109.5, (4, 1): 107.0,
         (4, 2): 104.5}

for it in items:
    cs, a = it['choices'], it['answer']
    sol = it.get('solution') or ''
    proof = it.get('answer_proof') or ''
    calc = it.get('calc_check') or ''

    # ── AA ★범위 밖 자리 수·모양★ ────────────────────────────────────
    for fld, txt in (('stem', it['stem']), ('근거', proof), ('해설', sol), ('계산 줄', calc)):
        m = OUT.search(txt)
        if m:
            rep(it, 'AA', '%s 에 범위 밖 자리 — %s' % (fld, m.group(0)))
    for k, c in enumerate(cs):
        if OUT.search(c):
            rep(it, 'AA', '선지 %s 에 범위 밖 자리 — 「%s」' % (MK[k], c))

    # ── BB ★결합각 값★ ──────────────────────────────────────────────
    for fld, txt in (('stem', it['stem']), ('근거', proof), ('해설', sol), ('계산 줄', calc)):
        for m in ANG.finditer(txt):
            v = float(m.group(1))
            #  ★85도 미만은 이 테마에서 결합각이 아니다★ — 2.5도씩·5도 차이 같은 ★간격★ 이다.
            #  첫 판이 17건을 울렸고 열일곱이 다 간격이었다(M02988·M03008·M03024·M03028).
            #  ★85도 미만은 간격이고 180도를 넘는 값은 셈의 결과다★ — 이 테마의 결합각은
            #  85~180도 사이에만 있다(가장 큰 값이 직선형 180도다). 아래는 '2.5도씩·5도 차이'
            #  같은 간격이고 위는 '109.5도 셋은 328.5도' 처럼 더한 값이다.
            if v < 85 or v > 180:
                continue
            #  ★셈의 결과는 결합각이 아니다★ — '109.5도 × 3 = 328.5도' 처럼 더하고 곱한 값이
            #  섞인다(M03052 는 한 바퀴 360도를 채우는지 세는 문항이다). 앞자리에 셈의 표가
            #  있으면 넘긴다 — 첫 판이 이 자리에서 두 건을 울렸다.
            if any(t in txt[max(0, m.start() - 16):m.start()] for t in ('=', '×', '합', '더하')):
                continue
            if v not in OK:
                rep(it, 'BB', '%s 의 각 %s도 — 표준값이 아니다' % (fld, m.group(1)))

    # ── CC ★모양 이름과 대표 분자의 짝(정답 쪽에서만)★ ─────────────────
    for fld, txt in (('정답 선지', cs[a]), ('근거', proof)):
        #  ★모양 이름이 둘 이상이면 이름을 늘어놓은 목록이다★ — 짝을 맞댈 자리가 아니다.
        #  M02972 의 근거가 넷을 늘어놓아 첫 판에서 네 건이 울렸다(4/4 오탐).
        if sum(1 for sh in SHAPE if sh in txt) > 1:
            continue
        for shape, good in SHAPE.items():
            if shape not in txt:
                continue
            if any(g in txt for g in good):
                continue                      # ★맞는 분자가 함께 있으면 넘긴다★
            bad = [m for m in MOLS if m in txt and MOLS[m] != shape]
            #  '물' 은 '물질·물음' 안에도 있다 — 앞뒤를 보고 낱말로만 센다
            bad = [m for m in bad if m != '물' or re.search(r'물[은이에과의]|물\s', txt)]
            if bad:
                rep(it, 'CC', '%s 에서 %s 에 %s 를 짝지었다' % (fld, shape, '·'.join(bad)))

    # ── DD ★자리 수·비공유 수와 각의 짝★ ─────────────────────────────
    for seg in calc.split('/'):
        m = PAIR.search(seg)
        if not m:
            continue
        key = (int(m.group(1)), int(m.group(2)))
        want = TABLE.get(key)
        if want is None:
            continue
        #  ★짝 뒤에 처음 오는 값 하나만 본다★ — 한 마디가 '… → 104.5도 → 104.5도 < 107도'
        #  처럼 견줌까지 담으면 뒤의 값이 다른 짝의 것이다(M03031 이 그렇게 울렸다).
        for g in list(ANG.finditer(seg, m.end()))[:1]:
            v = float(g.group(1))
            if v in OK and abs(v - want) > 1.2:
                rep(it, 'DD', '계산 줄에서 자리 %d·비공유 %d 에 %s도 — 표는 %s도'
                    % (key[0], key[1], g.group(1), want))

CLS = dict(auditlib.CLS)
CLS.update({'AA': '★범위 밖 자리 수·모양★', 'BB': '★결합각 표준값 어긋남★',
            'CC': '★모양·분자 짝(정답 쪽)★', 'DD': '★자리·비공유·각의 짝★'})

print('감사42 — T18 분자의 구조 %s~%s · %d제' % (LO, HI, len(items)))
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
