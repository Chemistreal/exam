# -*- coding: utf-8 -*-
"""T22 P16 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-005', 7, 'M02777'), ('C22-008', 1, 'M02778'), ('C22-015', 7, 'M02779'),
        ('C22-016', 2, 'M02780'), ('C22-016', 6, 'M02781'), ('C22-017', 5, 'M02782'),
        ('C22-017', 8, 'M02783'), ('C22-018', 8, 'M02784'), ('C22-019', 7, 'M02785'),
        ('C22-019', 8, 'M02786')]

NOTES = {
    'C22-008': (
        "★저작 주의(T22 P16)★ 각도[1](겹 하나가 수소 둘을 줄임)은 선택지가 '둘/넷 × 줄어든/"
        "늘어난' 의 ★두 칸 격자★ 로 짜이기 쉽다. 그러면 칸별 최빈값을 이으면 곧 정답이 되어 "
        "G3g 가 운다(㉯). 정답의 첫 마디만 '수소는' 으로 돌려 최빈값과 어긋나게 했다(M02778)."),
    'C22-018': (
        "★저작 주의(T22 P16)★ 각도[8](전자가 고루 퍼짐)의 오답을 '여섯 결합이 모두 단일/이중' "
        "처럼 한 낱말만 갈아 쓰면 자카드가 0.67 로 붙고, 셋이 '…때문이다' 로 끝나 어미가 3:1 로 "
        "갈린다. 한쪽을 '겹이 여섯 자리에…' 로, 다른 쪽 어미를 '…탓이다' 로 돌렸다(M02784)."),
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
    print('T22 P16 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
