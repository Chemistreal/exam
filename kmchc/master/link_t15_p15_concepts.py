# -*- coding: utf-8 -*-
"""T15 P15 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-017', 3, 'M02439'), ('C15-017', 5, 'M02440'), ('C15-004', 6, 'M02441'),
    ('C15-010', 2, 'M02442'), ('C15-022', 3, 'M02443'), ('C15-023', 2, 'M02444'),
    ('C15-014', 7, 'M02445'), ('C15-019', 6, 'M02446'), ('C15-003', 6, 'M02447'),
    ('C15-013', 2, 'M02448'),
]

NOTES = {
    'C15-017': (
        "★저작 주의(T15 P15)★ 각도[5](세 원소 가운데 판정되는 쌍 세기)와 [6](주기가 다르고 "
        "족이 같으면 판정 가능)은 ★서로의 해설이 된다★ — [5] 를 풀면 '같은 족이면 걸린다' 가 "
        "곧바로 드러난다. 한 배치에 함께 두지 말 것. P15 는 [3] 과 [5] 만 썼다."),
    'C15-004': (
        "★저작 주의(T15 P15)★ 각도[6](족 경향으로 다른 족과 못 견줌)의 정답은 부정형이 되기 "
        "쉬워 ★정답만 부정형★ 검사에 걸린다. '…걸리지 않는다' 대신 '이 잣대가 걸리는 것은 "
        "한 족 안뿐' 처럼 ★범위를 긍정으로 적는다★(M02441)."),
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
    print('T15 P15 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
