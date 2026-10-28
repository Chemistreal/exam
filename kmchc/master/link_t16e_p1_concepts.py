# -*- coding: utf-8 -*-
"""T16 P1 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-001', 0, 'M02791'), ('C16-002', 0, 'M02792'), ('C16-004', 0, 'M02793'),
        ('C16-006', 0, 'M02794'), ('C16-007', 0, 'M02795'), ('C16-008', 0, 'M02796'),
        ('C16-009', 0, 'M02797'), ('C16-010', 0, 'M02798'), ('C16-012', 0, 'M02799'),
        ('C16-017', 0, 'M02800')]

NOTES = {
    'C16-001': (
        "★저작 주의(T16 P1)★ 각도[0](정의)은 선택지가 '떼다/얻다 × 들다/나오다' 의 ★두 칸 "
        "격자★ 로 짜인다. 격자의 두 칸을 그대로 쓰면 오답끼리 자카드가 0.75 로 붙는다 — "
        "한 오답을 '전자를 받으면서 에너지를 쓴다' 처럼 다른 꼴로 풀어 갈랐다(M02791). "
        "T22 P16 의 G3g 와 같은 뿌리다."),
    'C16-012': (
        "★저작 주의(T16 P1)★ 각도[0](두 값의 첫째가 다름)의 정답을 '…염소 쪽이 더 크다' 로 "
        "적으면 발문의 '가장 크다' 를 되받아 ★겹침이 정답에서 최다★ 가 된다(㉪). '더 높다' 로 "
        "낱말을 바꿔 비켜 갔다(M02799)."),
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
