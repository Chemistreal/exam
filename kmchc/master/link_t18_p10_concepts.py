# -*- coding: utf-8 -*-
"""T18 P10 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '분자의 구조'

LINK = [('C18-011', 4, 'M03045'),
        ('C18-012', 4, 'M03046'),
        ('C18-013', 4, 'M03047'),
        ('C18-014', 4, 'M03048'),
        ('C18-015', 4, 'M03049'),
        ('C18-016', 4, 'M03050'),
        ('C18-017', 4, 'M03051'),
        ('C18-018', 4, 'M03052'),
        ('C18-019', 4, 'M03053'),
        ('C18-020', 4, 'M03054')]

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
    print('T18 P10 링크 — 각도 %d' % n)
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
