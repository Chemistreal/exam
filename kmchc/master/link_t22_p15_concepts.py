# -*- coding: utf-8 -*-
"""T22 P15 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 4, 'M02767'), ('C22-004', 8, 'M02768'), ('C22-005', 8, 'M02769'),
        ('C22-008', 6, 'M02770'), ('C22-013', 2, 'M02771'), ('C22-014', 5, 'M02772'),
        ('C22-015', 3, 'M02773'), ('C22-017', 2, 'M02774'), ('C22-018', 7, 'M02775'),
        ('C22-019', 5, 'M02776')]

NOTES = {
    'C22-013': (
        "★저작 주의(T22 P15)★ 각도[2](탄소와 수소의 행방)의 정답은 두 원소의 행방을 한 문장에 "
        "담아야 해서 ★혼자 길어진다★. 오답도 두 행방을 적는 꼴로 맞추어 길이를 나란히 했다 "
        "— 짧게 줄이려다 '…탄소로' 처럼 어미를 잃으면 어미 쏠림이 새로 생긴다(M02771)."),
    'C22-010': (
        "★대장 주의(T22 P15)★ 각도[3](분자식이 같아도 구조식이 다를 수 있음)은 001[8]/M02757 이 "
        "이미 물은 자리다 — ★봉인★. C22-012[2]·020[5](가지가 경향을 흔듦)도 012[8]/M02762 와 "
        "겨냥이 같아 봉인한다."),
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
    print('T22 P15 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
