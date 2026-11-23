# -*- coding: utf-8 -*-
"""T15 P11 각도 링크 — 병합과 같은 자리에서 박는다(P10 에서 세운 규약)

  ★그리고 이 배치는 대장 자체를 고친다★ — C15-004[1] 은 실측과 어긋난다.
"""
import json
import os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '이온화에너지'

LINK = [
    ('C15-022', 1, 'M02399'), ('C15-006', 6, 'M02400'), ('C15-016', 1, 'M02401'),
    ('C15-005', 5, 'M02402'), ('C15-017', 2, 'M02403'), ('C15-022', 4, 'M02404'),
    ('C15-022', 5, 'M02405'), ('C15-004', 4, 'M02406'), ('C15-008', 4, 'M02407'),
    ('C15-019', 4, 'M02408'),
]

# ★대장이 틀린 자리★ — 각도를 물리면서 그 까닭을 개념에 적어 둔다.
NOTES = {
    'C15-004': (
        "★대장 정정(T15 P11)★ 각도[1] '같은 족에서 값이 줄어드는 폭이 아래로 갈수록 작아짐' 은 "
        "★실측과 어긋난다★ — 1족 낙폭은 Li→Na 24 · Na→K 77 · K→Rb 16 · Rb→Cs 27, 17족은 "
        "430 · 111 · 132, 18족은 291 · 560 · 170 · 181 로 어느 족에서도 단조가 아니다. "
        "주기가 바뀔 때 새 껍질이 들어오는 폭과 유효 핵전하가 함께 움직이기 때문이다. "
        "★이 각도로는 문항을 짓지 말 것★ — '아래로 갈수록 작아진다' 는 값 자체에만 서고 "
        "낙폭에는 서지 않는다. T12 P10 의 돌턴 별명에 이어 ★대장도 틀린다★ 를 두 번째로 겪었다."),
    'C15-019': (
        "★저작 주의(T15 P11)★ 각도[2] '수소와 헬륨에 급증 자리가 없거나 하나뿐' 은 마감한 "
        "M02335 가 이미 헬륨으로 쓰고 있어 ★겨냥이 겹친다★. 이 각도를 쓰려면 수소 쪽으로만 "
        "묻거나 M02335 와 다른 물음(비를 잴 수 없다는 것과 비가 하나뿐이라는 것의 차이)으로 "
        "가를 것. P11 은 019[4] 로 옮겼다."),
    'C15-022': (
        "★저작 주의(T15 P11)★ 각도[5]('안정하다' 를 '반응하지 않는다' 로 넓히지 않기)를 "
        "★비활성 기체로 물으면 안 된다★ — 교과가 '비활성 기체는 반응하지 않는다' 로 가르치므로 "
        "그 오답이 교과 틀 안에서 참이 되어 F2 가 된다. M02405 는 질소·산소로 물어 그 함정을 "
        "피했다(반응성은 분자의 결합까지 걸린다는 쪽으로 반박한다)."),
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
    print('T15 P11 링크 — 각도 %d · 개념 주의 %d건' % (n, len(NOTES)))
    print('  각도 %d · 소진 %d · 미소진 %d' % (tot, used, tot - used))


if __name__ == '__main__':
    main()
