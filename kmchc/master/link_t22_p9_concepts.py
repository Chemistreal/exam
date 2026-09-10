# -*- coding: utf-8 -*-
"""T22 P9 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 1, 'M02707'), ('C22-003', 7, 'M02708'), ('C22-005', 4, 'M02709'),
        ('C22-006', 3, 'M02710'), ('C22-008', 0, 'M02711'), ('C22-010', 4, 'M02712'),
        ('C22-011', 5, 'M02713'), ('C22-013', 4, 'M02714'), ('C22-015', 8, 'M02715'),
        ('C22-019', 4, 'M02716')]

NOTES = {
    'C22-001': (
        "★저작 주의(T22 P9)★ 각도[1](다른 원소가 끼면 탄화수소가 아님)은 정답이 "
        "'…가 아니다' 로 흘러 ★정답만 부정형★ 이 되기 쉽다(㉣). "
        "'원소가 셋이라 다른 무리에 든다' 로 돌려 긍정으로 적었다(M02707)."),
    'C22-003': (
        "★저작 주의(T22 P9)★ 각도[7](이름을 차례로 적기)을 다섯 이름을 통째로 늘어놓는 선택지로 "
        "물으면 ★네 선택지의 낱말 집합이 같아져 자카드가 1.0★ 이 된다. '세 번째에 오는 것' 하나만 "
        "묻고 선택지마다 탄소 수를 붙여 갈랐다(M02708)."),
}


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
    for cid, note in NOTES.items():
        old = cs[cid].get('note') or ''
        if note not in old:
            cs[cid]['note'] = (old + ' ' + note).strip()
    json.dump(cj, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    tot = sum(len(c['angles']) for c in cj[THEME])
    used = sum(1 for c in cj[THEME] for a in c['angles'] if a.get('by'))
    print('T22 P9 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
