# -*- coding: utf-8 -*-
"""T16 P9 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-012', 1, 'M02871'), ('C16-012', 6, 'M02872'), ('C16-018', 1, 'M02873'),
        ('C16-018', 3, 'M02874'), ('C16-010', 5, 'M02875'), ('C16-006', 6, 'M02876'),
        ('C16-009', 6, 'M02877'), ('C16-015', 1, 'M02878'), ('C16-017', 5, 'M02879'),
        ('C16-020', 3, 'M02880')]

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
    print('T16 P9 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
