# -*- coding: utf-8 -*-
"""T22 P3 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 3, 'M02647'), ('C22-002', 5, 'M02648'), ('C22-003', 6, 'M02649'),
        ('C22-004', 3, 'M02650'), ('C22-007', 4, 'M02651'), ('C22-011', 1, 'M02652'),
        ('C22-013', 1, 'M02653'), ('C22-014', 0, 'M02654'), ('C22-015', 0, 'M02655'),
        ('C22-019', 0, 'M02656')]

NOTES = {
    'C22-011': (
        "★저작 주의(T22 P3)★ 각도[1](물에 잘 녹지 않는 까닭)의 정답을 '붙들 부분 전하가 없다' "
        "로 적으면 ★정답만 부정형★ 이 된다(㉣). '붙들릴 부분 전하가 아주 적다' 로 돌려 극성을 "
        "맞췄고, ▸ ★무극성 분자에도 순간 쌍극자는 있으므로 '없다' 보다 '아주 적다' 가 사실에도 "
        "더 맞다★ — 형식을 고치다 사실이 함께 좋아진 자리다(M02652)."),
    'C22-014': (
        "★저작 주의(T22 P3)★ 각도[0](맞추는 차례)의 오답으로 '어느 것부터 맞추든 결과는 "
        "같아진다' 를 두면 ★그 오답이 참이 된다★(㉥) — 차례는 손이 덜 가는 길일 뿐 결과를 "
        "바꾸지 않는다. '세 원소를 한 번에 함께 맞춘다' 로 갈았다(M02654)."),
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
    print('T22 P3 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
