# -*- coding: utf-8 -*-
"""T16 P2 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '전자친화도·전기음성도'

LINK = [('C16-001', 1, 'M02801'), ('C16-002', 2, 'M02802'), ('C16-005', 0, 'M02803'),
        ('C16-007', 5, 'M02804'), ('C16-013', 0, 'M02805'), ('C16-014', 0, 'M02806'),
        ('C16-015', 0, 'M02807'), ('C16-016', 0, 'M02808'), ('C16-018', 0, 'M02809'),
        ('C16-019', 0, 'M02810')]

NOTES = {
    'C16-013': (
        "★저작 주의(T16 P2)★ 각도[0](무리별 크기)은 선택지가 'N족이 가장 큰 무리가 된다' 로 "
        "★족 번호만 갈아 끼운 네 줄★ 이 되기 쉽다. 그러면 한글 낱말이 같아 오답끼리 자카드가 "
        "1.00 이 된다 — 무리마다 술어를 달리 풀어 갈랐다(M02805). T22 P12 의 분자식 선택지와 "
        "같은 뿌리다."),
    'C16-019': (
        "★저작 주의(T16 P2)★ 각도[0](세 값이 같은 뿌리)은 C16-003(전자 친화도의 뿌리)·"
        "C16-011(전기 음성도 경향의 까닭)과 ★한 배치에 두면 서로의 해설이 된다★(㉬). "
        "P2 는 019[0] 만 두고 003·011 은 뒤 배치로 미뤘다."),
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
