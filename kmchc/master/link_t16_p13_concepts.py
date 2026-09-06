# -*- coding: utf-8 -*-
"""T16 P13 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-011', 7, 'M02583'), ('C16-011', 8, 'M02584'), ('C16-012', 7, 'M02585'),
        ('C16-012', 8, 'M02586'), ('C16-014', 7, 'M02587'), ('C16-014', 8, 'M02588'),
        ('C16-014', 9, 'M02589'), ('C16-018', 7, 'M02590'), ('C16-019', 7, 'M02591'),
        ('C16-019', 8, 'M02592')]

NOTES = {
    'C16-012': (
        "★저작 주의(T16 P13)★ 각도[7](큰 값에서 작은 값을 뺌)은 오답을 '작은 값에서 큰 값을 빼'·"
        "'큰 값을 작은 값으로 나누어' 처럼 ★같은 낱말을 자리만 바꿔 쓰면 G3g 가 운다★ — 칸별 "
        "최빈값을 이으면 '큰 … 작은 …' 이 되어 정답만 짚힌다. 나눗셈 오답의 차례를 뒤집어 "
        "('작은 값으로 큰 값을 나누어') 첫 칸의 최빈값을 오답 쪽으로 옮겨 풀었다(M02585). "
        "▸ ★뒤집기 오답을 여럿 두면 칸별 최빈값이 정답을 가리키게 된다★"),
    'C16-014': (
        "★소진 알림(T16 P13)★ 2차 확장으로 넣은 [7][8][9] 를 한 배치에서 다 썼다. 셋을 "
        "'부호를 그림으로 확인' · '표에서 값만 골라 오기' · '몰당 단위' 로 갈라 두었으므로 "
        "서로의 해설이 되지 않는다(㉬)."),
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
    print('T16 P13 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
