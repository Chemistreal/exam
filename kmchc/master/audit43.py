# -*- coding: utf-8 -*-
"""감사43 — T15 이온화 에너지 (M02299~M02462, 164제) 기계 점검 리포트.

  A~S 와 X 는 ★auditlib★ 에 있다. 여기에는 이 테마의 자료가 숫자라서 기계로 잴 수 있는 것만 더한다.

  ★EE 순차 이온화 값이 오름차순인가★
    ▸ 순차 값은 ★어느 원소에서나 E₁ < E₂ < E₃★ 다(M02303 이 그것을 묻는 문항이다). 발문이
      순차 값을 늘어놓으면 그 줄은 오름차순이어야 한다 — 손으로 적은 표에서 한 자리만 뒤집혀도
      문항 전체가 거짓이 되고, 학생은 그 표로 급증 자리를 센다.

  ★FF 급증 자리와 원자가 전자 수의 짝★
    ▸ 급증 앞까지의 개수가 원자가 전자 수다. 발문의 값 줄에서 ★비가 가장 큰 자리★ 를 기계로 세어
      해설이 말하는 원자가 전자 수와 맞대면, 표를 고칠 때 생기는 어긋남이 드러난다.
    ▸ ★비로 재는지 차로 재는지가 문항마다 다르다★(M02306 은 비를 발문에 못 박았다). 둘 가운데
      어느 쪽으로 재도 같은 자리가 나오는 문항만 짚는다 — 갈리는 문항은 사람이 읽어야 한다.

  ★GG 값에 단위가 붙어 있는가★
    ▸ 이 은행은 이온화 에너지 값을 kJ/mol 로 적는다. 발문이 값을 주면서 단위를 한 번도 적지
      않으면 학생이 알갱이 하나당으로 읽는다(M02301 이 바로 그 오독을 묻는 문항이다).
"""
import re
import sys
from collections import Counter

import auditlib

LO = sys.argv[1] if len(sys.argv) > 1 else 'M02299'
HI = sys.argv[2] if len(sys.argv) > 2 else 'M02462'

items = auditlib.load(LO, HI)
MK = auditlib.MK
F = []


def rep(it, cls, msg):
    F.append((it['id'], cls, msg))


auditlib.core(items, rep)

NUM = re.compile(r'(?<![\d.])(\d{2,3}(?:,\d{3})*|\d{3,6})(?![\d.])')
SEQ_MARK = re.compile(r'(순차|제1|제2|E₁|E₂|차례로)')
VAL_N = re.compile(r'원자가\s*전자\s*(?:수(?:가|는)?\s*)?(하나|둘|셋|넷|다섯|여섯|일곱|여덟|[1-8])')
WORD = {'하나': 1, '둘': 2, '셋': 3, '넷': 4, '다섯': 5, '여섯': 6, '일곱': 7, '여덟': 8}


def nums(s):
    return [int(m.group(1).replace(',', '')) for m in NUM.finditer(s)]


def jumps(v):
    """★비가 두 배를 넘는 자리를 모두★ 돌려준다(1부터).

      ★가장 큰 비 하나를 급증으로 보면 안 된다★ — 알루미늄의 순차값은 578·1817·2745·11577 …
      42655·201266 이고 가장 큰 비는 ★안쪽 껍질로 넘어가는 열한째 자리★ 다(M02432 가 그 자리를
      묻는 문항이다). 족을 정하는 급증은 그 앞에 따로 있으므로, 두 배를 넘는 자리를 모두 세어
      그 가운데 원자가 전자 수가 있는지만 본다.
    """
    return [i + 1 for i in range(len(v) - 1) if v[i + 1] / v[i] >= 2]


def one_atom(stem):
    """★한 원자의 순차 값을 늘어놓은 발문인가★ — 여러 원소의 값이면 오름차순일 까닭이 없다.
      족·주기를 말하거나 원소 이름·기호가 둘 이상 나오거나 단위가 둘이면 넘긴다
      (첫 판이 다섯 건을 울렸고 다섯이 다 그런 발문이었다)."""
    if '족' in stem or '주기' in stem or '두 원소' in stem:
        return False
    #  ★익명 원소가 둘이면 표가 둘이다★ — '가는 496, 4562 … 이고 나는 419, 3052 …' 꼴이
    #  이 테마에 흔하다(첫 판 일곱 건이 모두 이런 발문이었다).
    if len(set(re.findall(r'(?:원소\s*)?([가나다])(?:는|의|와|에서)', stem))) >= 2:
        return False
    if len(re.findall(r'(?:단위|pm|피코미터)', stem)) >= 2:
        return False
    names = re.findall(r'(수소|리튬|나트륨|칼륨|베릴륨|붕소|탄소|질소|산소|플루오린|네온|'
                       r'마그네슘|알루미늄|규소|인|황|염소|아르곤|칼슘|브로민)', stem)
    if len(set(names)) >= 2:
        return False
    return len(re.findall(r'\b(?:H|Li|Na|K|Be|B|C|N|O|F|Ne|Mg|Al|Si|P|S|Cl|Ar|Ca|Br)\b', stem)) < 2


for it in items:
    stem = it['stem']
    sol = it.get('solution') or ''
    calc = it.get('calc_check') or ''
    v = [x for x in nums(stem) if x >= 100]

    # ── EE ★순차 값 오름차순★ ────────────────────────────────────────
    if SEQ_MARK.search(stem) and len(v) >= 3 and v != sorted(v) and one_atom(stem):
        rep(it, 'EE', '발문의 순차 값이 오름차순이 아니다 — %s' % v)

    # ── FF ★급증 자리 ↔ 원자가 전자 수★ ──────────────────────────────
    m = VAL_N.search(sol) or VAL_N.search(calc)
    if m and len(v) >= 4 and SEQ_MARK.search(stem + calc) and one_atom(stem):
        want = WORD[m.group(1)] if m.group(1) in WORD else int(m.group(1))
        js = jumps(v)
        if want and js and want not in js:
            rep(it, 'FF', '비가 2 배를 넘는 자리는 %s 인데 원자가 전자 %d 로 적혀 있다 — %s'
                % (js, want, v))

    # ── GG ★값에 단위★ ──────────────────────────────────────────────
    if len(v) >= 2 and 'kJ' not in stem and '단위' not in stem:
        if any(x >= 300 for x in v) and '피코미터' not in stem and 'pm' not in stem:
            rep(it, 'GG', '발문이 값을 주면서 kJ/mol 을 한 번도 적지 않았다 — %s' % v[:6])

CLS = dict(auditlib.CLS)
CLS.update({'EE': '★순차 값 오름차순★', 'FF': '★급증 자리 ↔ 원자가 전자★',
            'GG': '★값에 단위 없음★'})

print('감사43 — T15 이온화 에너지 %s~%s · %d제' % (LO, HI, len(items)))
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
