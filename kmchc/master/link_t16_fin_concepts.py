# -*- coding: utf-8 -*-
"""T16 마감 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-018', 8, 'M02623'), ('C16-020', 8, 'M02624'), ('C16-016', 7, 'M02625'),
        ('C16-017', 8, 'M02626')]

NOTES = {
    'C16-016': (
        "★마감 알림(T16)★ 아홉 각도가 모두 소진됐다. [5](극성 결합의 개수만으로 정하지 않기)와 "
        "010[5]·012[6] 이 한 자리였다는 것을 P12 에서 찾아 뒤 둘을 봉인했다."),
    'C16-018': (
        "★마감 알림(T16)★ 열 각도 가운데 아홉이 소진되고 [9](수소 결합과 다른 분자 사이 힘의 "
        "세기를 견주기)만 남았다 — 164 를 채우고 남은 것이라 다음 테마의 재료가 아니다."),
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
    print('T16 마감 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
