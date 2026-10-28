# -*- coding: utf-8 -*-
"""T16 P14 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-009', 7, 'M02593'), ('C16-009', 8, 'M02594'), ('C16-005', 7, 'M02595'),
        ('C16-015', 1, 'M02596'), ('C16-015', 7, 'M02597'), ('C16-015', 5, 'M02598'),
        ('C16-015', 8, 'M02599'), ('C16-010', 7, 'M02600'), ('C16-010', 8, 'M02601'),
        ('C16-016', 8, 'M02602')]

NOTES = {
    'C16-015': (
        "★대장 주의(T16 P14)★ 각도[6](전자점식만으로 모양을 정하지 않기)은 ★009[6](전자점식으로는 "
        "모양을 정할 수 없음을 적기)과 같은 문장★ 이다 — 009[6] 이 이미 소진됐으므로 봉인. "
        "2차 확장에서 새 각도끼리는 걸렀지만 ★원래 있던 140 개 사이의 겹침은 아직 다 훑지 "
        "못했다★ 는 뜻이다. ▸ 남은 [9](모양이 정해지면 결합각이 따라 정해짐)는 M02544(비공유 "
        "쌍이 각을 좁힘)와 겨냥이 가까우니 쓸 때 물음의 꼴을 멀리 둘 것."),
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
    print('T16 P14 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
