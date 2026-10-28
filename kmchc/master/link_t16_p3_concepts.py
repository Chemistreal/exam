# -*- coding: utf-8 -*-
"""T16 P3 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 2, 'M02483'), ('C16-002', 2, 'M02484'), ('C16-003', 1, 'M02485'), ('C16-003', 6, 'M02486'), ('C16-004', 4, 'M02487'), ('C16-005', 2, 'M02488'), ('C16-007', 2, 'M02489'), ('C16-008', 2, 'M02490'), ('C16-009', 1, 'M02491'), ('C16-011', 1, 'M02492')]

NOTES = {
    'C16-007': (
        "★저작 주의(T16 P3)★ 각도[2](두드려 펴짐)와 C16-004[4](이온 결정은 부스러짐)는 "
        "★같은 물음에 반대 답이 나오는 짝★ 이라 한 배치에 나란히 두어도 좋다. 다만 까닭을 "
        "'단단하다/무르다' 로 적으면 겨냥이 겹치므로, 한쪽은 ★같은 전하가 마주쳐 밀친다★, "
        "다른 쪽은 ★자유 전자가 다시 묶는다★ 로 갈라 적는다(M02487·M02489)."),
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
    print('T16 P3 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
