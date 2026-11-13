# -*- coding: utf-8 -*-
"""T16 P2 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-001', 1, 'M02473'), ('C16-002', 1, 'M02474'), ('C16-004', 0, 'M02475'), ('C16-004', 3, 'M02476'), ('C16-005', 1, 'M02477'), ('C16-006', 2, 'M02478'), ('C16-006', 1, 'M02479'), ('C16-007', 1, 'M02480'), ('C16-009', 0, 'M02481'), ('C16-010', 0, 'M02482')]

NOTES = {
    'C16-004': (
        "★저작 주의(T16 P2)★ 전도를 묻는 문항은 이온·공유·금속 셋이 ★같은 물음에 서로 다른 "
        "답을 내는 자리★ 라 한 배치에 함께 두어도 서로의 해설이 되지 않는다(이온은 상태가 "
        "가르고, 공유는 나를 전하가 없고, 금속은 고체에서도 통한다). 다만 ★까닭을 적을 때 "
        "'움직임' 이라는 한 낱말로 셋을 다 적으면 겨냥이 겹친다★ — 이온은 붙들림, 공유는 "
        "갈라지지 않음, 금속은 자유 전자로 갈라 적었다(M02475·M02478·M02480)."),
    'C16-006': (
        "★저작 주의(T16 P2)★ 각도[0]('분자 사이의 힘이 약해 녹는점이 낮다')과 [1](그물 구조 "
        "예외)을 ★한 배치에 두면 앞이 뒤의 반례가 되어 어긋나 보인다★. P2 는 [1] 만 쓰고 [0] 은 "
        "뒤 배치로 미뤘다. [1] 을 쓸 때는 '규칙을 버린다' 가 아니라 ★범위를 좁힌다★ 가 정답이다."),
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
    print('T16 P2 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
