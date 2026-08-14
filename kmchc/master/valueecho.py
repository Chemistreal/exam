# -*- coding: utf-8 -*-
"""valueecho — 한 테마 안에서 ★같은 값이 여러 문항의 발문에 인쇄되는 자리★ 를 센다.

■ 왜 세우는가
  T15 P3 순회에서 solver 가 짚었다: M02325 의 익명 원소 '다' 는 순차값이 738 로 시작하는데,
  같은 배치의 M02323 이 '마그네슘 738' 을 이름과 함께 인쇄한다. 그래서 두 발문을 맞대면
  ★익명 원소의 정체가 값 대조만으로 드러난다.★
  ▸ 나는 그 지적을 ★차단으로는 받지 않았다★ — '다 = 마그네슘' 에서 '껍질 셋' 으로 가는 걸음은
    마그네슘의 전자 배치를 아는 것이므로 화학 없이 닿는 길이 아니다. 그러나 ★익명으로 가리려던
    것이 값으로 드러나는 것 자체는 부채★ 이고, 눈으로는 못 센다. 그래서 검사로 세운다.

■ 무엇을 세는가
  발문에 인쇄된 ★세 자리 이상의 수★ 를 문항마다 모으고, 둘 이상의 문항이 같은 수를 인쇄하면
  적는다. 그 가운데 ★한쪽이 익명 원소(가·나·다·A·B·C)를 쓰고 다른 쪽이 원소 이름을 쓰면★
  익명이 값으로 풀리는 자리이므로 ★위험★ 으로 표시한다.

  · 값이 되풀이되는 것 자체는 흠이 아니다 — 같은 원소를 여러 각도에서 묻는 것은 정상이다.
    ★익명과 실명이 같은 값으로 이어질 때만★ 부채다.

■ 쓰는 법
    python3 valueecho.py                 # 기본 테마(이온화에너지) 전체
    python3 valueecho.py 원자반지름       # 다른 테마
    python3 valueecho.py 이온화에너지 M02319 M02328   # 범위만
"""
import json
import os
import re
import sys
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(BASE, 'master_bank.json')

ANON = re.compile(r'원소 (?:가|나|다|A|B|C)(?=의|와|과|는|은|를|이|가|,|·|\s|$)')
NAMED = re.compile(r'(리튬|베릴륨|붕소|탄소|질소|산소|플루오린|네온|나트륨|마그네슘|알루미늄'
                   r'|규소|인|황|염소|아르곤|칼륨|칼슘|헬륨|수소|브로민|아이오딘|세슘|루비듐'
                   r'|스트론튬|바륨)')
NUM = re.compile(r'(?<![0-9.])([0-9]{3,6})(?![0-9.])')


def main():
    theme = sys.argv[1] if len(sys.argv) > 1 else '이온화에너지'
    lo = sys.argv[2] if len(sys.argv) > 3 else None
    hi = sys.argv[3] if len(sys.argv) > 3 else None

    with open(BANK, encoding='utf-8') as f:
        d = json.load(f)
    items = d['items'] if isinstance(d, dict) else d
    sel = [x for x in items if x.get('theme') == theme
           and (lo is None or lo <= x['id'] <= hi)]
    if not sel:
        print(f'테마 {theme!r} 에 해당하는 문항이 없다 — theme 값을 확인할 것')
        return

    where = defaultdict(list)
    kind = {}
    for x in sel:
        s = x['stem']
        kind[x['id']] = ('익명' if ANON.search(s) else '') + ('실명' if NAMED.search(s) else '')
        for v in set(NUM.findall(s)):
            where[v].append(x['id'])

    shared = {v: ids for v, ids in where.items() if len(ids) > 1}
    risky = []
    for v, ids in sorted(shared.items(), key=lambda kv: -len(kv[1])):
        ks = {i: kind[i] for i in ids}
        anon = [i for i in ids if '익명' in ks[i]]
        named = [i for i in ids if '실명' in ks[i]]
        mark = ''
        if anon and named:
            mark = '  ★위험 — 익명이 값으로 풀린다'
            risky.append((v, anon, named))
        tag = ' '.join('%s(%s)' % (i, ks[i] or '무명') for i in ids)
        print('  %7s · %s%s' % (v, tag, mark))

    print(f'\n{theme} {len(sel)}제 · 되풀이된 값 {len(shared)} · '
          f'★익명이 값으로 풀리는 자리 {len(risky)}★')
    for v, anon, named in risky:
        print(f"  ▸ {v} — 익명 {','.join(anon)} 과 실명 {','.join(named)} 이 같은 값을 인쇄한다")
    if not risky:
        print('  익명과 실명이 값으로 이어지는 자리는 없다')


if __name__ == '__main__':
    main()
