# -*- coding: utf-8 -*-
"""T15 P14 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-002', 2, 'M02429'), ('C15-002', 7, 'M02430'), ('C15-008', 6, 'M02431'),
    ('C15-009', 2, 'M02432'), ('C15-010', 3, 'M02433'), ('C15-021', 7, 'M02434'),
    ('C15-023', 3, 'M02435'), ('C15-016', 7, 'M02436'), ('C15-005', 7, 'M02437'),
    ('C15-024', 2, 'M02438'),
]

NOTES = {
    'C15-008': (
        "★저작 주의(T15 P14)★ 각도[6](제1 의 주기 경향을 E₂ 에 옮기지 않기)의 반례로는 "
        "★나트륨과 마그네슘★ 이 가장 깨끗하다 — 제1 은 Na < Mg 인데 제2 는 Na 가 안쪽 껍질을 "
        "건드려 훨씬 커진다. 같은 주기에서 껍질 경계가 둘 사이에 놓이는 짝을 고를 것."),
    'C15-009': (
        "★저작 주의(T15 P14)★ 각도[2](급증이 두 곳인 원소에서 첫 자리 고르기)는 순차값을 "
        "★열 개 넘게★ 인쇄해야 두 급증이 모두 보인다(M02432 는 알루미늄의 열셋). 값이 길어지면 "
        "발문이 무거워지므로 이 각도는 심화에서만 쓴다."),
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
    print('T15 P14 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
