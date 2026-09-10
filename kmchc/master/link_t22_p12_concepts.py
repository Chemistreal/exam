# -*- coding: utf-8 -*-
"""T22 P12 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-002', 2, 'M02737'), ('C22-004', 6, 'M02738'), ('C22-006', 6, 'M02739'),
        ('C22-009', 5, 'M02740'), ('C22-012', 4, 'M02741'), ('C22-013', 7, 'M02742'),
        ('C22-016', 4, 'M02743'), ('C22-018', 3, 'M02744'), ('C22-019', 6, 'M02745'),
        ('C22-020', 8, 'M02746')]

NOTES = {
    'C22-016': (
        "★저작 주의(T22 P12)★ 각도[4](치환 앞뒤의 분자식 맞대기)를 CH4·CH3Cl 처럼 ★분자식만 "
        "갈아 끼운 선택지★ 로 쓰면 한글 낱말이 '에서·바뀐다' 뿐이라 네 선택지의 자카드가 1.0 "
        "이 된다. 무엇이 빠지고 무엇이 앉는지를 말로 풀어 갈랐다(M02743)."),
    'C22-019': (
        "★저작 주의(T22 P12)★ 각도[6](한 번에 갈리지 않음)의 정답에 '함께' 를 쓰면 발문의 "
        "'여러 물질이 함께 들어 있었다' 를 되받아 ★겹침이 정답에서 최다★ 가 된다(㉪). "
        "'같이' 로 바꿔 비켜 갔다(M02745)."),
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
    print('T22 P12 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
