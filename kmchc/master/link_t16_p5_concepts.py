# -*- coding: utf-8 -*-
"""T16 P5 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 5, 'M02503'), ('C16-002', 5, 'M02504'), ('C16-003', 5, 'M02505'), ('C16-004', 2, 'M02506'), ('C16-005', 5, 'M02507'), ('C16-006', 4, 'M02508'), ('C16-007', 5, 'M02509'), ('C16-008', 4, 'M02510'), ('C16-009', 3, 'M02511'), ('C16-011', 2, 'M02512')]

NOTES = {
    'C16-006': (
        "★저작 주의(T16 P5)★ 각도[4](녹는 것과 끊어지는 것)의 선지를 쓸 때 ★'물 분자' 와 "
        "'끊어진다' 두 마디가 정답에만 함께 모이면 G3g 가 운다★ — 칸별 최빈값 조합이 정답을 "
        "유일하게 짚기 때문이다. 오답 하나에도 두 마디를 함께 주어 풀었다(M02508)."),
    'C16-008': (
        "★저작 주의(T16 P5)★ 각도[4](이온과 공유가 함께 있는 물질)의 오답 '이온 결합만 있다' "
        "와 '공유 결합만 있다' 는 ★낱말 집합이 똑같아 자카드 1.00 이 된다★. 한쪽을 "
        "'전자쌍을 함께 쓰는 결합만 있다' 처럼 틀 자체를 바꿔 적는다(M02510)."),
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
