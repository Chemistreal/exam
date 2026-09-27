# -*- coding: utf-8 -*-
"""labelguard — ★한 배치 안에서 같은 익명 라벨이 서로 다른 원소를 가리키는가★ 를 센다.

■ 왜 세우는가 (T15 P4 3차 · solver)
  M02334 는 '원소 가' 를 E₁ 496 · E₂ 4562 인 원소로 쓰고, M02337 은 같은 '원소 가' 를
  값이 적히지 않은 다른 원소로 쓴다. 두 문항이 나란히 인쇄되면 ★학생이 M02337 의 '가' 에
  M02334 의 496 을 끌어다 쓸 길이 열린다.★

  ▸ ★이 갈래는 내 조치가 열었다★ — M02337 에서 절대값을 지운 것은 값 누출을 끊는
    옳은 조치였는데, 값이 사라지자 그 자리를 ★옆 문항의 값★ 이 채울 수 있게 되었다.
    P3 의 738 사슬과 같은 꼴이다: ★한 문항 안에서 막아도 배치를 가로지르면 길이 생긴다.★

  ▸ valueecho 와 무엇이 다른가 — valueecho 는 ★값★ 이 이어지는 자리를 세고,
    이 검사는 ★이름★ 이 겹치는 자리를 센다. 값을 지워 valueecho 를 통과시키면
    이 검사가 울 수 있다. ★두 검사는 서로의 사각을 본다.★

■ 무엇을 세는가
  한 범위 안에서 익명 라벨(가·나·다·A·B·C)을 쓰는 문항을 모으고, ★같은 라벨을 쓰는
  문항이 둘 이상이면★ 적는다. 그 가운데 한쪽이 값을 인쇄하고 다른 쪽이 인쇄하지 않으면
  ★값이 건너갈 수 있는 자리★ 이므로 위험으로 표시한다.

  · 같은 배치가 아니면 나란히 인쇄될 일이 드무니, 기본은 ★열 문항 단위★ 로 본다.

■ 쓰는 법
      python3 labelguard.py M02329 M02338      # 한 배치
      python3 labelguard.py M02299 M02338      # 테마 전체(여러 배치를 한꺼번에)
      python3 labelguard.py M02329 M02338 --batch 10   # 묶는 크기를 바꾼다
"""
import json
import os
import re
import sys
from collections import defaultdict

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')
LABEL = re.compile(r'원소 (가|나|다|라|A|B|C|D)(?=[의와과는은를이가,·\s]|$)')
NUM = re.compile(r'(?<![\d.])\d{3,5}(?![\d.])')


def load():
    with open(BANK, encoding='utf-8') as f:
        d = json.load(f)
    return d['items'] if isinstance(d, dict) else d


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    size = 10
    if '--batch' in sys.argv:
        size = int(sys.argv[sys.argv.index('--batch') + 1])
    lo, hi = (a + ['M00000', 'M99999'])[:2]

    sel = [x for x in load() if lo <= x['id'] <= hi]
    if not sel:
        sys.exit('범위에 문항이 없다 — %s ~ %s' % (lo, hi))
    sel.sort(key=lambda x: x['id'])

    total = 0
    for s in range(0, len(sel), size):
        chunk = sel[s:s + size]
        used = defaultdict(list)          # 라벨 → [(id, 값들)]
        for x in chunk:
            stem = x.get('stem', '')
            labs = set(LABEL.findall(stem))
            if not labs:
                continue
            vals = sorted(set(NUM.findall(stem)))
            for L in labs:
                used[L].append((x['id'], vals))

        hits = {L: v for L, v in used.items() if len(v) > 1}
        if not hits:
            continue
        print('\n── %s ~ %s' % (chunk[0]['id'], chunk[-1]['id']))
        for L in sorted(hits):
            rows = hits[L]
            withv = [i for i, v in rows if v]
            without = [i for i, v in rows if not v]
            # ★값을 인쇄하는 쪽과 인쇄하지 않는 쪽이 같은 라벨을 나눠 쓰면 값이 건너간다★
            risky = bool(withv) and bool(without)
            mark = '  ★위험 — 값이 건너갈 수 있다' if risky else '  (둘 다 값을 인쇄 — 서로 다른 원소인지 볼 것)'
            print("  '원소 %s' · %s%s" % (L, ' '.join(
                '%s(%s)' % (i, ','.join(v) if v else '값없음') for i, v in rows), mark))
            total += 1

    print('\n%s ~ %s · %d제 · ★라벨이 겹치는 자리 %d★' % (lo, hi, len(sel), total))
    if total:
        print('  ※ 겹친다고 곧 흠은 아니다 — ★두 문항이 같은 원소를 뜻하는지★ 부터 볼 것.')
        print('     서로 다른 원소인데 이름이 같으면 라벨을 갈라 준다(가·나 → A·B).')
        print('     한쪽만 값을 인쇄하면 값이 건너가므로 그쪽을 먼저 본다.')
    else:
        print('  같은 라벨을 나눠 쓰는 자리는 없다')


if __name__ == '__main__':
    main()
