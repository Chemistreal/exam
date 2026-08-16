# -*- coding: utf-8 -*-
"""T16 P12 각도 링크 — 병합과 같은 자리에서 박는다(T15 P10 에서 세운 규약)"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '화학결합'

LINK = [('C16-002', 6, 'M02573'), ('C16-003', 2, 'M02574'), ('C16-003', 4, 'M02575'),
        ('C16-004', 6, 'M02576'), ('C16-005', 3, 'M02577'), ('C16-006', 0, 'M02578'),
        ('C16-009', 2, 'M02579'), ('C16-010', 4, 'M02580'), ('C16-010', 6, 'M02581'),
        ('C16-012', 5, 'M02582')]

NOTES = {
    'C16-006': (
        "★대장 주의(T16 P12)★ 각도[5](분자 안의 결합과 분자 사이의 힘을 갈라 세기)는 "
        "★020[1] 과 겨냥이 그대로 겹친다★ — P11 M02563 이 이미 가져갔다. 마감 때 겹침을 풀어 "
        "다시 적기 전에는 쓰지 않는다."),
    'C16-009': (
        "★대장 주의(T16 P12)★ 각도[5](수소는 둘로 끝남을 따로 세기)는 ★020[2] 의 옥텟 예외와 "
        "같은 자리★ 다 — P11 M02564 의 정답이 곧 '수소와 헬륨은 둘로 끝난다' 였다. 봉인."),
    'C16-010': (
        "★대장 주의(T16 P12)★ 각도[5](극성 결합이 있어도 무극성 분자가 될 수 있음)는 "
        "★012[6] · 016[5] 와 셋이 한 자리★ 이고 P10 M02550 · P11 M02571 이 이미 두 번 물었다. "
        "셋 다 봉인. ▸ 쓸 수 있게 남은 것은 [4](차로 어림)와 [6](이온을 치우침의 끝으로)뿐이었고 "
        "이 배치가 둘 다 소진했다."),
    'C16-011': (
        "★대장 주의(T16 P12)★ 각도[5](두 값의 차로 결합의 성격을 어림하기)는 ★010[4] 와 "
        "같은 물음★ 이다 — 010[4] 만 쓰기로 하고(M02580) 이쪽은 봉인. 남은 [6](값이 클수록 "
        "부분 음전하 쪽)은 아직 쓸 수 있다."),
    'C16-008': (
        "★대장 주의(T16 P12)★ 각도[6](성질에서 결합의 종류를 되돌리기)와 007[4](고체에서도 "
        "통한다는 점을 이온과 가르기)는 ★019 계열과 겨냥이 겹친다★ — P10 여섯 문항이 019 의 "
        "일곱 각도를 다 가져갔다. 두 자리 모두 봉인."),
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
    print('T16 P12 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
