"""T12 P9 마감 — 개념 대장에 P9 10제 링크 + ★대장에 남은 거짓 전제 하나 정정★

대장은 '무엇을 이미 썼나'와 '무엇을 쓰면 안 되나'를 함께 담는 자리다.
P9 를 링크하면서, 순회에서 드러난 ★각도 자체의 결함★ 도 함께 새긴다.

★C12-026[3] — 각도의 전제가 거짓이다★
  "축이 400·500·600·700 nm 네 눈금뿐이다 — 이 축에서 410과 434를 구별할 수 있는가(없다)"
  이 각도를 그대로 받아 M01892 를 만들었고, 1차 순회에서 ★정답이 거짓★ 임이 드러났다.
  24 nm 는 300 nm 폭의 8% 라 인쇄된 띠에서 두 선은 또렷이 갈라져 보인다(교재 75쪽 도판이 그렇다).
  눈금 개수가 제한하는 것은 ★선의 분리 관찰이 아니라 값 읽기★ 다.
  ▸ 각도를 정정하고 note 에 사유를 남긴다. 그대로 두면 다음 배치가 같은 함정에 다시 빠진다.
"""
import json, os

CJ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'concepts.json')
THEME = '원자 모형'

# (개념 id, 각도 index, 문항 id)
LINK = [
    ('C12-011', 3, 'M01887'),   # 논증 사슬 4단계 배열
    ('C12-013', 5, 'M01888'),   # 헬륨 3배 반사실
    ('C12-017', 3, 'M01889'),   # 식의 단위가 kJ/mol — 원자 1개가 아니라 1몰
    ('C12-018', 7, 'M01890'),   # 세 묶음의 색은 계열을 나눈 것
    ('C12-019', 3, 'M01891'),   # hν 칸만 비어 있다
    ('C12-030', 2, 'M01893'),   # 적외선(진동)과 마이크로파(회전) 가르기
    ('C12-032', 0, 'M01894'),   # 유추 불가능한 서술 고르기(부정 발문)
    ('C12-N05', 1, 'M01895'),   # n 이 커질수록 0 에 붙는 거동
    ('C12-N02', 0, 'M01896'),   # 두 수치로 전자 1개의 질량 산출
]

# C12-026[3] 을 통째로 갈아 끼운다 (전제가 거짓이었다)
FIX_ANGLE = ('C12-026', 3,
             '축이 400·500·600·700 nm 네 눈금뿐이다 — 이 축에서 410과 434를 구별할 수 있는가(없다) [경계]',
             '눈금이 성긴 축이 막는 것은 선의 분리 관찰이 아니라 값 읽기다 — 무엇까지 읽을 수 있는지 [경계]')

# M01892 가 실제로 선 자리 — 새 각도로 추가하고 링크한다
NEW_ANGLE = ('C12-026',
             '보이는 선은 준위가 아니라 전이다 — 이 그림으로 준위의 개수를 셀 수 없는 까닭 [경계]',
             ['M01892'])

NOTE_ADD = ("★저작 금지 정정(P9)★ 옛 각도 [3]('410과 434를 구별할 수 없다')은 ★전제가 거짓★ 이었다. "
            "24 nm 는 300 nm 폭의 8% 라 인쇄된 띠에서 두 선은 또렷이 갈라져 보인다(75쪽 도판 실사 확인). "
            "그 각도로 만든 M01892 는 1차 순회에서 정답이 거짓임이 드러나 축을 두 번 옮겼다 — "
            "'값 읽기'로 옮기니 정답이 화학이 아니라 그래프 상식이 되어 네 프로필 전원이 맞혔고(죽은 선지 3개), "
            "'선은 준위가 아니라 전이'로 다시 옮겨서야 개념 위에 섰다. "
            "★눈금 개수는 값 읽기를 막지 관찰을 막지 않는다.★")


def main():
    obj = json.load(open(CJ, encoding='utf-8'))
    C = obj[THEME]
    d = {c['id']: c for c in C}

    # 1. 거짓 전제 각도 정정
    cid, idx, old, new = FIX_ANGLE
    a = d[cid]['angles'][idx]
    assert a['a'] == old, f'{cid}[{idx}]: 대상 각도 어긋남 -> {a["a"]}'
    assert not a['by'], f'{cid}[{idx}]: 이미 소진된 각도라 함부로 못 고침 -> {a["by"]}'
    a['a'] = new
    d[cid]['note'] = (d[cid].get('note', '') + ' ' + NOTE_ADD).strip()

    # 2. 새 각도 추가 + 링크
    ncid, ntext, nby = NEW_ANGLE
    assert all(x['a'] != ntext for x in d[ncid]['angles']), '이미 있는 각도'
    d[ncid]['angles'].append({'a': ntext, 'by': list(nby)})

    # 3. 나머지 링크
    n = 0
    for cid, idx, mid in LINK:
        a = d[cid]['angles'][idx]
        assert mid not in a['by'], f'{cid}[{idx}]: {mid} 이미 링크됨'
        a['by'].append(mid)
        n += 1

    # ── 검증 ────────────────────────────────────────────────
    have = {b for c in C for x in c['angles'] for b in x['by']}
    p9 = [f'M0{i}' for i in range(1887, 1897)]
    missing = [m for m in p9 if m not in have]
    assert not missing, f'대장 미링크 잔존: {missing}'
    dup = [m for m in p9 if sum(1 for c in C for x in c['angles'] for b in x['by'] if b == m) != 1]
    assert not dup, f'중복 링크: {dup}'
    free = sum(1 for c in C for x in c['angles'] if not x['by'])
    total = sum(len(c['angles']) for c in C)

    json.dump(obj, open(CJ, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'P9 대장 링크 {n + 1}건 (새 각도 1 포함) · 거짓 전제 각도 1건 정정')
    print(f'  개념 {len(C)}개 · 각도 {total}개 · 미소진 {free}개 (잔여 74제)')


if __name__ == '__main__':
    main()
