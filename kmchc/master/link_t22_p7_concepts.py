# -*- coding: utf-8 -*-
"""T22 P7 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 6, 'M02687'), ('C22-003', 3, 'M02688'), ('C22-004', 7, 'M02689'),
        ('C22-005', 6, 'M02690'), ('C22-006', 7, 'M02691'), ('C22-008', 8, 'M02692'),
        ('C22-010', 8, 'M02693'), ('C22-011', 2, 'M02694'), ('C22-013', 6, 'M02695'),
        ('C22-017', 5, 'M02696')]

NOTES = {
    'C22-013': (
        "★저작 주의(T22 P7)★ 각도[6](연소 생성물로 되돌리기)의 정답을 '탄소와 수소가 들어 "
        "있던 물질이다' 로 적으면 발문의 '이산화 탄소와' 를 되받아 ★겹침이 정답에서 최다★ 가 "
        "된다(㉪). '탄소도 수소도 들어 있던 물질이다' 로 적어 비켜 갔다(M02695)."),
    'C22-010': (
        "★저작 주의(T22 P7)★ 각도[8](그림의 각은 실제 각이 아님)은 정답이 '평면에 그린 "
        "것이라…' 처럼 까닭까지 담아 ★혼자 길어진다★. 오답 '잘못 그린 것이다' 를 '잘못 그린 "
        "그림이다' 로 늘려 길이를 맞췄다(㉧ · M02693)."),
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
    print('T22 P7 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
