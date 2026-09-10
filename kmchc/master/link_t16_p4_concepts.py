# -*- coding: utf-8 -*-
"""T16 P4 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 4, 'M02493'), ('C16-002', 4, 'M02494'), ('C16-004', 1, 'M02495'), ('C16-004', 5, 'M02496'), ('C16-005', 4, 'M02497'), ('C16-006', 3, 'M02498'), ('C16-007', 3, 'M02499'), ('C16-008', 3, 'M02500'), ('C16-009', 6, 'M02501'), ('C16-010', 1, 'M02502')]

NOTES = {
    'C16-008': (
        "★저작 주의(T16 P4)★ 각도[3](화학식만으로의 한계)의 정답은 ★'대체로 정하되 예외를 "
        "남긴다' 꼴★ 이라야 한다 — '언제나 정한다' 도 '아무것도 못 정한다' 도 둘 다 거짓이다. "
        "이 테마에서 잣대의 세기를 묻는 자리는 모두 같은 꼴이 되므로 한 배치에 하나만 둔다."),
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
    print('T16 P4 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
