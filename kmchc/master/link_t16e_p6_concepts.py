# -*- coding: utf-8 -*-
"""T16 P6 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-001', 4, 'M02841'), ('C16-002', 7, 'M02842'), ('C16-003', 2, 'M02843'),
        ('C16-006', 4, 'M02844'), ('C16-007', 3, 'M02845'), ('C16-011', 7, 'M02846'),
        ('C16-012', 4, 'M02847'), ('C16-015', 3, 'M02848'), ('C16-016', 4, 'M02849'),
        ('C16-018', 5, 'M02850')]

NOTES = {
    'C16-004': (
        "★대장 봉인(T16 P6)★ 각도[2]·[3]·[4]·[5]·[7] 은 다른 개념이 이미 물었다 — [2]≡013[2]/"
        "M02817(18족) · [3]≡004[1]/M02813(2족 까닭) · [4]≡020[0]/M02820(단정형) · [5]≡014[0]/"
        "M02806(견주는 차례) · [7]≡013[0]/M02805(17족). C16-004 는 [6] 하나만 남는다."),
    'C16-009': (
        "★대장 봉인(T16 P6)★ 각도[2](밀치는 힘)·[6](한 값을 두 번 쓰지 않기)·[8](둘을 더해 "
        "전체를 셈)은 [0]/M02797 · [1]/M02836 · [4]/M02815 가 이미 물은 자리다 — 개념이 "
        "작아 각도끼리 겹친다. C16-009 는 소진으로 본다."),
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
    print('T16 P6 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
