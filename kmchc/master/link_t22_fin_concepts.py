# -*- coding: utf-8 -*-
"""T22 마감 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-007', 3, 'M02787'), ('C22-015', 5, 'M02788'),
        ('C22-017', 6, 'M02789'), ('C22-020', 2, 'M02790')]

NOTES = {
    'C22-015': (
        "★저작 주의(T22 마감)★ 각도[5](첨가로 불포화 가려내기)를 브로민 물로 쓰면 015[2]/M02675 "
        "와 017[5]/M02782 와 겹친다. 수소 첨가로 ★기체 부피가 주는지★ 를 보는 실험으로 옮겨 "
        "갈랐다(M02788) — 같은 겨냥이라도 자리를 바꾸면 새 문항이 선다."),
    'C22-020': (
        "★대장 마감(T22)★ C22-020 아홉 각도 가운데 실제로 쓴 것은 [2]·[6]·[8] 셋뿐이고 나머지 "
        "여섯은 다른 개념이 먼저 물어 봉인했다. '자주 어긋나는 자리' 를 모은 개념은 대장을 세울 "
        "때부터 ★다른 개념의 그림자★ 로 잡는 편이 낫다 — 다음 테마에 옮겨 적을 것."),
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
    print('T22 마감 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
