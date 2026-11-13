# -*- coding: utf-8 -*-
"""T16 P8 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-016', 0, 'M02533'), ('C16-016', 3, 'M02534'), ('C16-016', 4, 'M02535'), ('C16-017', 0, 'M02536'), ('C16-017', 3, 'M02537'), ('C16-018', 0, 'M02538'), ('C16-018', 2, 'M02539'), ('C16-019', 0, 'M02540'), ('C16-011', 4, 'M02541'), ('C16-012', 2, 'M02542')]

NOTES = {
    'C16-018': (
        "★저작 주의(T16 P8)★ 각도[0](세 원소에 직접 붙은 수소만)의 정답에 '수소' 와 '분자' 를 "
        "쓰면 ★발문과의 어휘 겹침이 정답에서 최다★ 가 된다 — 발문이 그 두 낱말을 쓸 수밖에 "
        "없기 때문이다. 정답을 '플루오린·산소·질소에 곧바로 붙어 있어야' 처럼 ★원소 이름만으로 "
        "적으면 겹침이 사라진다★(M02538)."),
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
    print('T16 P8 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
