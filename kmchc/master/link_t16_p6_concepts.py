# -*- coding: utf-8 -*-
"""T16 P6 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 6, 'M02513'), ('C16-005', 6, 'M02514'), ('C16-006', 6, 'M02515'), ('C16-007', 6, 'M02516'), ('C16-008', 5, 'M02517'), ('C16-009', 4, 'M02518'), ('C16-010', 2, 'M02519'), ('C16-010', 3, 'M02520'), ('C16-011', 3, 'M02521'), ('C16-012', 0, 'M02522')]

NOTES = {
    'C16-005': (
        "★저작 주의(T16 P6)★ 각도[6](삼중이 늘 안정한 것은 아님)의 정답은 부정형이 되기 쉽다 "
        "— '…정하지 않는다' 대신 ★'분자 전체는 결합 전체와 모양이 함께 정한다' 처럼 무엇이 "
        "정하는지를 긍정으로 적는다★(M02514). T15 P15 에서 얻은 규약과 같은 자리다."),
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
