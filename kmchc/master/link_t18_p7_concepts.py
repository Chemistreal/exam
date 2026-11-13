# -*- coding: utf-8 -*-
"""T18 P7 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '분자의 구조'

LINK = [('C18-001', 3, 'M03015'),
        ('C18-002', 3, 'M03016'),
        ('C18-003', 3, 'M03017'),
        ('C18-004', 3, 'M03018'),
        ('C18-005', 3, 'M03019'),
        ('C18-006', 3, 'M03020'),
        ('C18-007', 3, 'M03021'),
        ('C18-008', 3, 'M03022'),
        ('C18-009', 3, 'M03023'),
        ('C18-010', 3, 'M03024')]

NOTES = {}


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
    print('T18 P7 링크 — 각도 %d' % n)
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
