# -*- coding: utf-8 -*-
"""T22 P8 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-002', 4, 'M02697'), ('C22-004', 2, 'M02698'), ('C22-007', 5, 'M02699'),
        ('C22-009', 3, 'M02700'), ('C22-012', 1, 'M02701'), ('C22-014', 1, 'M02702'),
        ('C22-015', 1, 'M02703'), ('C22-016', 1, 'M02704'), ('C22-018', 6, 'M02705'),
        ('C22-019', 2, 'M02706')]

NOTES = {
    'C22-009': (
        "★저작 주의(T22 P8)★ 각도[3](이름에서 분자식 세우기)의 오답을 '탄소 셋에 수소 여덟' "
        "'탄소 셋에 수소 여섯' 처럼 ★숫자만 갈아 끼우면★ 두 오답의 자카드가 0.67 로 붙는다. "
        "한쪽을 '끝소리만 보고 알켄이라 읽는다' 는 절차 오답으로 돌려 갈랐다(M02700)."),
    'C22-018': (
        "★저작 주의(T22 P8)★ 각도[6](분자식에서 수소 수 세기)은 발문에 '탄소 여섯' 을 적으면 "
        "정답의 '여섯이 된다' 가 발문을 되받아 ★겹침이 정답에서 최다★ 가 된다(㉪). 발문에서 "
        "수를 걷어내고 '고리를 이루고 있다' 까지만 적었다(M02705)."),
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
    print('T22 P8 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
