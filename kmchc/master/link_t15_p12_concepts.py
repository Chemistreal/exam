# -*- coding: utf-8 -*-
"""T15 P12 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-018', 4, 'M02409'), ('C15-024', 3, 'M02410'), ('C15-023', 1, 'M02411'),
    ('C15-023', 4, 'M02412'), ('C15-024', 7, 'M02413'), ('C15-013', 3, 'M02414'),
    ('C15-013', 7, 'M02415'), ('C15-010', 4, 'M02416'), ('C15-003', 3, 'M02417'),
    ('C15-018', 3, 'M02418'),
]

NOTES = {
    'C15-010': (
        "★저작 주의(T15 P12)★ 각도[4](족 번호에서 원자가전자 수를 되돌리기)를 물을 때 발문에 "
        "'급증' 이나 '크게 뛰는' 을 쓰면 ★local_checks 가 급증의 셈법을 발문에 적으라고 운다★. "
        "이 각도는 셈법이 물음의 초점이 아니므로 '바깥 껍질의 전자를 다 뗀 다음으로 넘어가는 "
        "자리' 로 물어 피했다(M02416)."),
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
    print('T15 P12 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
