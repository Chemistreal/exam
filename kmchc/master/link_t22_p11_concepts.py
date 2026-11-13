# -*- coding: utf-8 -*-
"""T22 P11 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 5, 'M02727'), ('C22-003', 4, 'M02728'), ('C22-008', 2, 'M02729'),
        ('C22-010', 7, 'M02730'), ('C22-011', 6, 'M02731'), ('C22-012', 6, 'M02732'),
        ('C22-014', 3, 'M02733'), ('C22-015', 4, 'M02734'), ('C22-017', 3, 'M02735'),
        ('C22-019', 1, 'M02736')]

NOTES = {
    'C22-017': (
        "★저작 주의(T22 P11)★ 각도[3](포화가 잘 반응하지 않는 까닭)의 정답은 '풀릴 겹이 없다' "
        "로 흘러 ★정답만 부정형★ 이 되기 쉽다(㉣). '자리가 모두 차 있기 때문이다' 로 돌려 "
        "긍정으로 적었다(M02735)."),
    'C22-008': (
        "★저작 주의(T22 P11)★ 각도[2](삼중의 몫은 두 배)를 각도[6](수소 수에서 결합을 어림)이나 "
        "C22-015[6](삼중에 두 번 더하기)과 ★한 배치에 두면 서로의 해설이 된다★(㉬) — 둘 다 "
        "'삼중은 두 번' 이 열쇠다. P11 은 [2] 만 두고 015 는 [4] 로 갈랐다."),
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
    print('T22 P11 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
