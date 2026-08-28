# -*- coding: utf-8 -*-
"""T18 P13 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '분자의 구조'

LINK = [('C18-001', 7, 'M03075'),
        ('C18-002', 7, 'M03076'),
        ('C18-003', 7, 'M03077'),
        ('C18-004', 7, 'M03078'),
        ('C18-005', 7, 'M03079'),
        ('C18-006', 7, 'M03080'),
        ('C18-007', 7, 'M03081'),
        ('C18-008', 7, 'M03082'),
        ('C18-009', 7, 'M03083'),
        ('C18-010', 7, 'M03084')]

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
    print('T18 P13 링크 — 각도 %d' % n)
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
