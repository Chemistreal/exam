# -*- coding: utf-8 -*-
"""T15 P10 각도 링크 — ★병합과 같은 자리에서 박는다★

  P5~P9 는 다섯 배치를 미룬 끝에 link_t15_p5top9.py 로 한꺼번에 박았고, 그 사이에
  ★대장이 비어 보여 P10 이 같은 각도를 다시 고를 뻔했다★. 그 값을 치렀으니 P10 부터는
  병합 직후에 박는다 — ★소진 표시는 마감의 결과가 아니라 저작의 전제다★.
  ※ 개념 주의(NOTES)는 순회를 마칠 때 회차의 값과 함께 적는다. 여기서는 링크만 박는다.
"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-002', 1, 'M02389'), ('C15-003', 2, 'M02390'), ('C15-005', 3, 'M02391'),
    ('C15-007', 3, 'M02392'), ('C15-008', 3, 'M02393'), ('C15-010', 1, 'M02394'),
    ('C15-013', 1, 'M02395'), ('C15-017', 1, 'M02396'), ('C15-018', 2, 'M02397'),
    ('C15-019', 1, 'M02398'),
]


def main():
    cj = json.load(open(CJ, encoding='utf-8'))
    cs = {c['id']: c for c in cj[THEME]}
    n = 0
    for cid, idx, mid in LINK:
        a = cs[cid]['angles'][idx]
        a.setdefault('by', [])
        if mid not in a['by']:
            a['by'].append(mid)
            n += 1
    json.dump(cj, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = sum(len(c['angles']) for c in cj[THEME])
    used = sum(1 for c in cj[THEME] for a in c['angles'] if a.get('by'))
    print('T15 P10 링크 — 각도 %d' % n)
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
