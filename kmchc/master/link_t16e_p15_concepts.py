# -*- coding: utf-8 -*-
"""T16 P15 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-013', 6, 'M02931'),
        ('C16-014', 4, 'M02932'),
        ('C16-015', 2, 'M02933'),
        ('C16-016', 1, 'M02934'),
        ('C16-017', 3, 'M02935'),
        ('C16-018', 2, 'M02936'),
        ('C16-019', 1, 'M02937'),
        ('C16-020', 1, 'M02938'),
        ('C16-004', 5, 'M02939'),
        ('C16-006', 5, 'M02940')]

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
    print('T16 P15 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
