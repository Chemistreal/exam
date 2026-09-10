# -*- coding: utf-8 -*-
"""T22 P2 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-005', 0, 'M02637'), ('C22-003', 1, 'M02638'), ('C22-002', 3, 'M02639'),
        ('C22-006', 1, 'M02640'), ('C22-007', 2, 'M02641'), ('C22-009', 1, 'M02642'),
        ('C22-010', 0, 'M02643'), ('C22-011', 0, 'M02644'), ('C22-013', 0, 'M02645'),
        ('C22-012', 0, 'M02646')]

NOTES = {
    'C22-005': (
        "★저작 주의(T22 P2)★ 각도[0](알카인의 정의)은 004[0] 과 나란한 짝이라 ★발문의 꼴을 "
        "일부러 다르게 두었다★ — P1 M02633 은 '이중 결합이 하나 있다 → 어느 무리인가', "
        "P2 M02637 은 '일반식이 이렇게 적힌다 → 그 무리는 어떠한가'. 나란한 각도를 다른 배치에 "
        "두는 것만으로는 모자라고 ★묻는 방향까지 돌려야 한다★."),
    'C22-013': (
        "★저작 주의(T22 P2)★ 각도[0](완전 연소의 생성물)에서 오답을 '일산화 탄소와 물' · "
        "'이산화 탄소와 물' 처럼 앞말만 바꿔 늘어놓으면 ★칸별 최빈값이 정답을 유일하게 짚는다★"
        "(㉯). 오답 하나의 첫 마디를 '물과' 로 돌려 첫 칸의 최빈값을 흩었다(M02645)."),
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
    print('T22 P2 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
