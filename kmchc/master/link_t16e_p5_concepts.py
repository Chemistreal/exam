# -*- coding: utf-8 -*-
"""T16 P5 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-001', 8, 'M02831'), ('C16-002', 6, 'M02832'), ('C16-003', 4, 'M02833'),
        ('C16-004', 8, 'M02834'), ('C16-005', 5, 'M02835'), ('C16-009', 1, 'M02836'),
        ('C16-010', 2, 'M02837'), ('C16-013', 8, 'M02838'), ('C16-017', 2, 'M02839'),
        ('C16-019', 8, 'M02840')]

NOTES = {
    'C16-019': (
        "★저작 주의(T16 P5)★ 각도[8](이온의 값과 원자의 값을 섞지 않기)은 정답이 '…섞지 "
        "못한다' 로 흘러 ★정답만 부정형★ 이 되기 쉽다(㉣). '두 표는 잰 자리가 서로 다른 "
        "값이다' 로 돌려 긍정으로 적었다(M02840)."),
    'C16-005': (
        "★대장 주의(T16 P5)★ 각도[3](둘째 주기가 좁아 서로 밀침)은 012[2]/M02828 이 이미 "
        "물은 자리다 — ★봉인★. 불소가 염소보다 작은 까닭은 한 자리에서만 묻는다."),
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
    print('T16 P5 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
