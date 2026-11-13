# -*- coding: utf-8 -*-
"""T16 P16 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 7, 'M02613'), ('C16-001', 8, 'M02614'), ('C16-005', 8, 'M02615'),
        ('C16-006', 7, 'M02616'), ('C16-006', 8, 'M02617'), ('C16-008', 7, 'M02618'),
        ('C16-008', 8, 'M02619'), ('C16-011', 6, 'M02620'), ('C16-014', 1, 'M02621'),
        ('C16-014', 5, 'M02622')]

NOTES = {
    'C16-008': (
        "★대장 주의(T16 P16)★ 각도[1](준금속 근처에서는 단정하지 않기)은 ★020[6](세 결합의 잣대가 "
        "어림임)과 같은 자리★ 다 — P11 M02567 의 정답이 곧 '경계에 가까운 자리' 였다. 봉인."),
    'C16-001': (
        "★소진 알림(T16 P16)★ 2차 확장으로 넣은 [7][8] 을 한 배치에서 썼다 — 골짜기의 바닥(결합 "
        "길이)과 그 앞의 오르막(핵끼리의 밀침)이라 서로의 해설이 되지 않는다. 이 개념은 아홉 각도가 "
        "모두 소진됐다."),
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
    print('T16 P16 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
