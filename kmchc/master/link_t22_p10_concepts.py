# -*- coding: utf-8 -*-
"""T22 P10 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-002', 6, 'M02717'), ('C22-004', 1, 'M02718'), ('C22-007', 1, 'M02719'),
        ('C22-008', 3, 'M02720'), ('C22-009', 4, 'M02721'), ('C22-011', 3, 'M02722'),
        ('C22-013', 8, 'M02723'), ('C22-014', 6, 'M02724'), ('C22-016', 5, 'M02725'),
        ('C22-018', 1, 'M02726')]

NOTES = {
    'C22-011': (
        "★저작 주의(T22 P10)★ 각도[3](안 녹는다와 전혀 없다를 가르기)의 정답에 '것은' 이 들어가면 "
        "발문 끝의 '옳은 것은?' 과 맞물려 ★겹침이 정답에서 최다★ 가 된다(㉪). 발문 꼬리말은 모든 "
        "문항에 있으니 정답 문면에서 '것은' 을 걷어낸다(M02722)."),
    'C22-007': (
        "★저작 주의(T22 P10)★ 각도[1](포화의 두 쓰임)은 정답이 '두 포화는 서로 다른 말을 "
        "가리킨다' 처럼 두 낱말을 다 담아 ★혼자 길어진다★. 오답 하나를 '늘' 에서 '언제나' 로 "
        "늘려 맞췄다(㉧ · M02719)."),
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
    print('T22 P10 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
