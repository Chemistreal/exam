# -*- coding: utf-8 -*-
"""T22 P13 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-008', 4, 'M02747'), ('C22-009', 7, 'M02748'), ('C22-010', 1, 'M02749'),
        ('C22-011', 7, 'M02750'), ('C22-012', 7, 'M02751'), ('C22-013', 5, 'M02752'),
        ('C22-014', 8, 'M02753'), ('C22-015', 6, 'M02755'), ('C22-016', 8, 'M02754'),
        ('C22-018', 4, 'M02756')]

NOTES = {
    'C22-010': (
        "★저작 주의(T22 P13)★ 각도[1](분자식에서 구조식으로 갈 때)은 발문이 '…그리려 한다' 로 "
        "끝나기 쉬운데, 정답도 '…알아야 한다' 로 맺으면 ★정답 꼬리말이 발문에만 있는 낱말★ 이 "
        "된다(㉮). 발문을 '…그리려는 사람이 있다' 로 돌려 비켜 갔다(M02749)."),
    'C22-014': (
        "★저작 주의(T22 P13)★ 각도[8](어긋난 자리 짚기)의 정답을 '산소 계수를 다시 맞춘다' 로 "
        "적으면 발문의 '산소·계수를' 를 두 번 되받아 ★겹침이 정답에서 최다★ 가 된다(㉪). "
        "'넘치는 쪽 계수를 다시 맞춘다' 로 원소 이름을 빼고 적었다(M02753)."),
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
    print('T22 P13 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
