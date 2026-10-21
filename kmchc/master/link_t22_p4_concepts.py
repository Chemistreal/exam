# -*- coding: utf-8 -*-
"""T22 P4 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-002', 7, 'M02657'), ('C22-005', 3, 'M02658'), ('C22-006', 4, 'M02659'),
        ('C22-008', 5, 'M02660'), ('C22-009', 2, 'M02661'), ('C22-010', 2, 'M02662'),
        ('C22-012', 3, 'M02663'), ('C22-014', 2, 'M02664'), ('C22-016', 0, 'M02665'),
        ('C22-018', 0, 'M02666')]

NOTES = {
    'C22-018': (
        "★저작 주의(T22 P4)★ 각도[0](탄소 여섯이 고리를 이룸)의 오답을 '탄소 다섯이 고리를 "
        "이룬다' 처럼 수만 바꿔 늘어놓으면 ★'탄소|여섯이|…|이룬다' 가 칸별 최빈값으로 정답만 "
        "짚는다★(㉯). 오답 하나를 '별 모양으로 놓인다' 로 돌려 마지막 칸의 최빈값을 흩었다"
        "(M02666)."),
    'C22-008': (
        "★저작 주의(T22 P4)★ 각도[5](셈한 값을 되짚어 확인하기)의 열쇠는 ★처음과 다른 길로 "
        "같은 값에 닿는 것★ 이다 — '같은 식에 한 번 더 넣는다' 는 같은 길이라 잘못이 그대로 "
        "따라온다. 오답을 이 축으로 지으면 셈형 문항에서 근거절이 참이 되는 일을 피할 수 "
        "있다(M02660)."),
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
    print('T22 P4 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
