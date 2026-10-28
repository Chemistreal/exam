# -*- coding: utf-8 -*-
"""T16 P15 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-002', 7, 'M02603'), ('C16-002', 8, 'M02604'), ('C16-003', 7, 'M02605'),
        ('C16-003', 8, 'M02606'), ('C16-004', 7, 'M02607'), ('C16-004', 8, 'M02608'),
        ('C16-004', 9, 'M02609'), ('C16-007', 7, 'M02610'), ('C16-007', 8, 'M02611'),
        ('C16-007', 9, 'M02612')]

NOTES = {
    'C16-020': (
        "★대장 주의(T16 P15)★ 각도[7](화학식량과 분자량을 갈라 적기)은 ★004[8] 과 같은 자리★ 다 "
        "— M02608 이 004[8] 로 물었으므로 봉인. 2차 확장에서 새 각도 44 개를 서로 맞대었는데도 "
        "★새 각도와 다른 개념의 새 각도 사이에서 한 자리가 새어 나갔다★. ▸ 남은 [8]('결합' 이라는 "
        "말이 가리키는 것을 자리마다 갈라 적기)은 아직 쓸 수 있다."),
    'C16-007': (
        "★소진 알림(T16 P15)★ 2차 확장으로 넣은 [7][8][9] 를 한 배치에서 다 썼다(녹는점이 "
        "물질마다 다름 · 내놓은 전자 수와 세기 · 늘여서 실 만들기). 남은 것은 [4] 하나인데 "
        "★019[3](금속만 고체에서 통함)과 겨냥이 겹쳐 봉인★ 이다.")
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
    print('T16 P15 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
