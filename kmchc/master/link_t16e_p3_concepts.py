# -*- coding: utf-8 -*-
"""T16 P3 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-001', 3, 'M02811'), ('C16-003', 0, 'M02812'), ('C16-004', 1, 'M02813'),
        ('C16-005', 7, 'M02814'), ('C16-009', 4, 'M02815'), ('C16-010', 1, 'M02816'),
        ('C16-013', 2, 'M02817'), ('C16-014', 2, 'M02818'), ('C16-016', 2, 'M02819'),
        ('C16-020', 0, 'M02820')]

NOTES = {
    'C16-014': (
        "★저작 주의(T16 P3)★ 각도[2](두 축이 어긋나면 멈추기)의 오답을 '오른쪽에 있는 쪽이 "
        "반드시 더 크다'·'아래쪽에 있는 쪽이 반드시 더 크다' 로 ★방향만 갈아 끼우면★ 자카드가 "
        "0.67 로 붙는다. 한쪽을 '아래에 놓인 원소를 골라 적는다' 는 다른 꼴로 돌렸다(M02818)."),
    'C16-016': (
        "★저작 주의(T16 P3)★ 각도[2](값과 성질 사이의 걸음)는 발문에 '값과 성질 사이에' 를 적으면 "
        "정답이 그 세 낱말을 그대로 되받아 ★겹침이 정답에서 최다★ 가 된다(㉪). 발문을 '이 사실이 "
        "말해 주는 것으로' 로 돌렸다. 오답 셋이 '…것이다' 로 끝나 어미도 3:1 이었다(M02819)."),
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
