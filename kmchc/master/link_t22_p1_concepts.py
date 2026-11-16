# -*- coding: utf-8 -*-
"""T22 P1 각도 링크 — 병합과 같은 자리에서 박는다"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '탄화수소'

LINK = [('C22-001', 0, 'M02627'), ('C22-001', 2, 'M02628'), ('C22-002', 0, 'M02629'),
        ('C22-002', 1, 'M02630'), ('C22-003', 0, 'M02631'), ('C22-003', 2, 'M02632'),
        ('C22-004', 0, 'M02633'), ('C22-006', 0, 'M02634'), ('C22-007', 0, 'M02635'),
        ('C22-009', 0, 'M02636')]

NOTES = {
    'C22-004': (
        "★저작 주의(T22 P1)★ 각도[0](알켄의 정의)과 005[0](알카인의 정의)은 대장에서 ALLOW 로 "
        "면제한 나란한 짝이다 — 나란한 것이 옳지만 ★한 배치에 함께 두면 서로의 해설이 된다★(㉬). "
        "P1 은 004[0] 만 넣었고 005[0] 은 뒤 배치로 미뤘다."),
    'C22-006': (
        "★저작 주의(T22 P1)★ 각도[0] 을 물을 때 발문에 '끝과 끝이 이어져' 라고 쓰면 정답이 "
        "'끝이 이어진 쪽' 이라 말할 수밖에 없어 ★겹침이 정답에서 최다★ 가 된다(㉪). 정답을 "
        "'맞붙어 닫힌 쪽' 으로 적어 비켜 두었다(M02634)."),
    'C22-003': (
        "★저작 주의(T22 P1)★ 각도[2](탄소 수에서 수소 수 셈하기)는 이 테마의 첫 셈형 자리다. "
        "오답 셋을 ★일반식의 두 걸음 가운데 어느 걸음이 빠졌는가★ 로 지었다 — 두 걸음 다 빠짐 · "
        "둘 더하기가 빠짐 · 두 배 하기가 빠짐. ▸ 셈형 오답은 근거절이 참이 되기 쉬우니(㉡) "
        "★어긋난 걸음을 문면에 적는다★."),
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
    print('T22 P1 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
