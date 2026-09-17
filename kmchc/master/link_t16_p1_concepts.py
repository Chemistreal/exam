# -*- coding: utf-8 -*-
"""T16 P1 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 0, 'M02463'), ('C16-001', 3, 'M02464'), ('C16-002', 0, 'M02465'), ('C16-002', 3, 'M02466'), ('C16-003', 0, 'M02467'), ('C16-003', 3, 'M02468'), ('C16-005', 0, 'M02469'), ('C16-007', 0, 'M02470'), ('C16-008', 0, 'M02471'), ('C16-011', 0, 'M02472')]

NOTES = {
    'C16-005': (
        "★저작 주의(T16 P1)★ 각도[0](쌍의 개수로 결합 가르기)의 오답을 '쌍이 둘이므로 …' 로 "
        "나란히 쓰면 ★자카드가 0.67 로 뛴다★ — 세 선지가 같은 틀을 나눠 갖기 때문이다. "
        "한 오답은 틀을 바꿔 '함께 쓴 쌍이 셋인 …' 으로 적었다(M02469)."),
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
    print('T16 P1 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
