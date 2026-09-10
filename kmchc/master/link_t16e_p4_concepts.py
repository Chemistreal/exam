# -*- coding: utf-8 -*-
"""T16 P4 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-001', 7, 'M02821'), ('C16-002', 3, 'M02822'), ('C16-003', 1, 'M02823'),
        ('C16-006', 2, 'M02824'), ('C16-007', 7, 'M02825'), ('C16-008', 2, 'M02826'),
        ('C16-011', 0, 'M02827'), ('C16-012', 2, 'M02828'), ('C16-015', 5, 'M02829'),
        ('C16-018', 4, 'M02830')]

NOTES = {
    'C16-015': (
        "★저작 주의(T16 P4)★ 각도[5](부분 전하가 어느 쪽에)는 정답을 '값이 큰 쪽에 생긴다' 로 "
        "짧게 적으면 ★혼자 유난히 짧아★ 산포가 0.56 까지 튄다. 오답이 '…부분 음전하가 생긴다' 로 "
        "길어지기 때문이다. 정답도 같은 꼴로 풀어 적어 맞췄다(M02829)."),
    'C16-011': (
        "★저작 주의(T16 P4)★ 각도[0](전기 음성도 경향의 까닭)은 C16-003[0]·[1](전자 친화도의 "
        "뿌리)과 ★한 배치에 두면 서로의 해설이 된다★(㉬). P4 는 003[1](반지름)과 011[0](유효 "
        "핵전하)로 요인을 갈라 두어 겨냥이 겹치지 않게 했다."),
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
    print('T16 P4 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
