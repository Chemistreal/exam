# -*- coding: utf-8 -*-
"""audit_core — ★테마 검사가 필요 없는 범위★ 를 auditlib 의 A~S·X 로만 훑는다

  쓰임:  python3 audit_core.py M02463 M02626        (한 범위)
         python3 audit_core.py --all                (테마마다 한 줄로)

  ★왜 세우는가★ — 감사40(T16)·41(T22)·42(T18)·43(T15)은 그 테마의 자료를 기계로 재는 검사를
  따로 세울 값이 있었다. 그런데 T17(화학 결합)은 ★세울 자리가 없었다★:
    · '이온 결합 물질을 분자라 부른 자리' 는 여섯 건이 걸렸고 ★여섯이 다 옳은 문면★ 이었다
      ('이온 결정에는 떼어 낼 분자가 없다' 처럼 스스로 부인하는 문장이다).
    · '(결합쌍 + 비공유쌍) × 2 = 둘레 전자' 셈은 T17 의 계산 줄 문면에 그 꼴로 적히지 않는다.
  ▸ ★검사를 세울 자리가 없으면 세우지 않는다★ — 그 대신 A~S 를 돌려 옛 규약 부채만 센다.
    감사 파일을 테마마다 새로 베껴 적는 것이 그 자체로 드리프트의 원인이다(감사37~39 가 값을 치렀다).
"""
import sys
from collections import Counter

import auditlib

SPAN = [('T1~T13 앞', 'M00001', 'M01970'), ('T13 양자수', 'M01971', 'M02134'),
        ('T14', 'M02135', 'M02298'), ('T15 이온화', 'M02299', 'M02462'),
        ('T17 화학결합', 'M02463', 'M02626'), ('T22 탄화수소', 'M02627', 'M02790'),
        ('T16 전자친화도', 'M02791', 'M02954'), ('T18 분자의 구조', 'M02955', 'M03999')]


def run(lo, hi, quiet=False):
    items = auditlib.load(lo, hi)
    F = []
    auditlib.core(items, lambda it, cls, msg: F.append((it['id'], cls, msg)))
    c = Counter(x[1] for x in F)
    if not quiet:
        print('audit_core — %s~%s · %d제' % (lo, hi, len(items)))
        print('=' * 74)
        for k in sorted(auditlib.CLS):
            if c.get(k):
                print('  %s %-24s %3d 건' % (k, auditlib.CLS[k], c[k]))
        print('-' * 74)
        print('  합계 %d 건 · 깨끗한 문항 %d/%d'
              % (len(F), len(items) - len({x[0] for x in F}), len(items)))
        for k in sorted(auditlib.CLS):
            rows = [x for x in F if x[1] == k]
            if not rows:
                continue
            print('\n■ %s %s — %d 건' % (k, auditlib.CLS[k], len(rows)))
            for fid, _, msg in rows[:30]:
                print('  %s  %s' % (fid, msg))
            if len(rows) > 30:
                print('  … %d 건 더' % (len(rows) - 30))
    return len(items), F, c


def main():
    if '--all' in sys.argv:
        print('%-16s %6s %6s  %s' % ('범위', '문항', '지적', '갈래'))
        print('-' * 74)
        for name, lo, hi in SPAN:
            n, F, c = run(lo, hi, quiet=True)
            kinds = ' '.join('%s%d' % (k, v) for k, v in sorted(c.items()))
            print('%-16s %6d %6d  %s' % (name, n, len(F), kinds or '—'))
        return
    lo = sys.argv[1] if len(sys.argv) > 1 else 'M02463'
    hi = sys.argv[2] if len(sys.argv) > 2 else 'M02626'
    run(lo, hi)


if __name__ == '__main__':
    main()
