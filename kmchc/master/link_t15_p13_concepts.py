# -*- coding: utf-8 -*-
"""T15 P13 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-015', 1, 'M02419'), ('C15-015', 7, 'M02420'), ('C15-007', 4, 'M02421'),
    ('C15-013', 4, 'M02422'), ('C15-007', 7, 'M02423'), ('C15-020', 1, 'M02424'),
    ('C15-020', 2, 'M02425'), ('C15-008', 7, 'M02426'), ('C15-017', 7, 'M02427'),
    ('C15-012', 7, 'M02428'),
]

NOTES = {
    'C15-020': (
        "★저작 주의(T15 P13)★ 각도[1](빠진 값의 범위 좁히기)를 2주기에서 물을 때 ★어느 자리를 지우느냐가 답을 바꾼다★ — 질소(15족)를 지우면 15족·16족이 뒤집히는 자리라 '이웃 사이' 로 못 박을 수 없고, 탄소를 지우면 사이로 좁혀진다. M02424 는 앞의 자리를 골라 '예외인지 먼저 보라' 를 열쇠로 삼았다."),
    'C15-015': (
        "★저작 주의(T15 P13)★ 발문에 '톱니' 를 쓰면 local_checks 가 ★'세로축' 을 함께 적으라고 운다★. 각도[7](세로축 이름이 빠진 그림)은 그 낱말이 물음의 초점이라 자연히 걸리지 않지만, [1](톱니 하나가 한 주기)은 세로축을 일부러 적어 두어야 한다(M02419)."),
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
    print('T15 P13 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
