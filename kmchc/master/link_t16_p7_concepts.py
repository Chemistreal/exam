# -*- coding: utf-8 -*-
"""T16 P7 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-013', 4, 'M02523'), ('C16-013', 5, 'M02524'), ('C16-014', 0, 'M02525'), ('C16-014', 2, 'M02526'), ('C16-014', 4, 'M02527'), ('C16-015', 0, 'M02528'), ('C16-015', 3, 'M02529'), ('C16-016', 2, 'M02530'), ('C16-012', 1, 'M02531'), ('C16-017', 2, 'M02532')]

NOTES = {
    'C16-013': (
        "★대장 주의(T16 P7)★ 각도[0][2][3] 은 C16-001[5]·005[2] 와 ★겨냥이 그대로 겹친다★ — "
        "결합 에너지와 세기, 끊는 일의 흡열, 쌍과 길이·세기는 이미 앞 개념이 가져갔다. "
        "★대장을 세울 때 개념 사이의 겹침을 다 걸러 내지 못했다★ 는 뜻이므로, 이 개념은 "
        "[4](길이의 두 끝)·[5](반지름의 합과의 차이)·[6] 만 쓴다. 마감 때 남은 각도를 다시 볼 것."),
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
    print('T16 P7 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
