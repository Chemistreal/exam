# -*- coding: utf-8 -*-
"""선지 넷을 쓰기 전에 미리 재는 자 — 길이 판·자카드·표면 축.

★왜 만드는가★
  조치 회차마다 새 선지를 손으로 세었고 ★거의 매번 한 번은 틀렸다★.
  T14 P8 에서만 네 번이다 — factchecker 안 18자를 그대로 쓰면 산포 0.26 · defender 의
  M02208 선지 넷은 정답이 유일 최단 · M02211 ① 25자로 산포 0.56 · M02210 ④ 를 갈면서
  '더' 축을 놓아 정답만 홀로 남음. P9 첫 빌드에서도 둘이 걸렸다.
  ★검증자가 준 문면은 그 문항의 길이 판까지 보고 고른다★ 를 손으로 지키는 대신 여기서 센다.

★쓰는 법★
  python3 choiceprobe.py            # 예시(자기 시험)
  또는 다른 스크립트에서:
      from choiceprobe import probe
      probe(['...', '...', '...', '...'], ans=2, mid='M02220')

★재는 것 여섯★ — build_t14_p3.local_checks 의 ③⑫⑬⑮ 및 batch_template 의 G3b·G6
  ① 길이 판   정답이 유일 최장·최단이면 차단(동률은 통과)              ← 국소검사 ③
  ② 산포      (최대−최소)/중앙값 ≤ 0.25                                ← G3b
  ③ 자카드    오답 두 칸이 낱말을 크게 겹치면 차단(≥ 0.62)             ← 국소검사 ⑫
  ④ 부정형    넷 가운데 정답만 부정형이면 차단                         ← 국소검사 ⑬
  ⑤ '더' 축   3:1 로 갈리며 정답을 홀로 남기면 차단                    ← 국소검사 ⑮
  ⑥ 개시 축   개시 두 어절이 3:1 로 갈리며 정답을 홀로 남기면 차단     ← 국소검사 ⑮
  덧붙여 ★수치 선지 오름차순★(G6)은 선지가 모두 수로 시작할 때만 잰다.

★한계를 적어 둔다★ — 이 자는 ★선지 넷만★ 본다. 발문·해설과 맞물리는 검사(수치 봉인 ④ ·
  이온 규칙 봉인 ⑤ · 그래프 봉인 ⑥ · 테마2 봉인 ⑦ · 척도 봉인 ⑰ · 조사 앞 빈칸 ⑱)는
  여기서 재지 못한다. ★이 자를 통과했다는 것은 빌드를 돌리지 않아도 된다는 뜻이 아니다.★
"""
import re
import statistics


def _tk(s):
    return {t for t in re.findall(r'[가-힣]{2,}', s)}


NEG = re.compile(r'(없다|않는다|않다|못한다|불가능하다|아니다)$')
NUMHEAD = re.compile(r'^\s*(\d+)')


def probe(choices, ans, mid='?', verbose=True):
    """선지 넷과 0-based 정답 자리를 받아 걸리는 것을 목록으로 돌려준다."""
    cs = [c.strip() for c in choices]
    assert len(cs) == 4, f'선지가 넷이 아니다: {len(cs)}'
    assert 0 <= ans < 4, f'정답 자리가 0~3 이 아니다: {ans}'
    bad = []
    ls = [len(c) for c in cs]

    # ① 길이 판 — 정답이 유일 최장·최단
    if ls.count(ls[ans]) == 1 and (ls[ans] == max(ls) or ls[ans] == min(ls)):
        which = '최장' if ls[ans] == max(ls) else '최단'
        bad.append(f'정답이 유일 {which} {ls} (정답 {ans + 1})')

    # ② 산포
    med = statistics.median(ls)
    spread = (max(ls) - min(ls)) / med if med else 0
    if spread > 0.25:
        bad.append(f'보기 길이 산포 {spread:.2f} > 0.25 — {ls}')

    # ③ 오답끼리 자카드
    for i in range(4):
        for j in range(i + 1, 4):
            if ans in (i, j):
                continue
            a, b = _tk(cs[i]), _tk(cs[j])
            if a and b:
                jac = len(a & b) / len(a | b)
                if jac >= 0.62:
                    bad.append(f'오답 {i+1}·{j+1} 자카드 {jac:.2f} ≥ 0.62')

    # ④ 정답만 부정형
    ns = [bool(NEG.search(c)) for c in cs]
    if sum(ns) == 1 and ns[ans]:
        bad.append(f'넷 가운데 정답만 부정형 — {ns}')

    # ⑤⑥ 표면 축 둘 (국소검사 ⑮ 와 같은 판정식)
    for name, v in (("'더' 포함", [('더' in c) for c in cs]),
                    ('개시 두 어절', [' '.join(c.split()[:2]) for c in cs])):
        uniq = [k for k in set(v) if v.count(k) == 1]
        if len(set(v)) == 2 and uniq and v.index(uniq[0]) == ans:
            bad.append(f"'{name}' 이 3:1 로 갈리며 정답을 홀로 남김: {v}")

    # G6 — 선지가 모두 수로 시작하면 오름차순이어야 한다
    heads = [NUMHEAD.match(c) for c in cs]
    if all(heads):
        ns2 = [int(h.group(1)) for h in heads]
        if ns2 != sorted(ns2):
            bad.append(f'수치 선지가 오름차순이 아님 — {ns2}')

    if verbose:
        print(f'── {mid} · 정답 {ans + 1} · 길이 {ls} · 산포 {spread:.3f}')
        for i, c in enumerate(cs):
            mark = '←' if i == ans else ' '
            print(f'   {i+1}{mark} [{ls[i]:2d}] {c}')
        if bad:
            for b in bad:
                print(f'   ❌ {b}')
        else:
            print('   ✅ 선지 넷 — 걸리는 것 없음')
    return bad


if __name__ == '__main__':
    # ★자기 시험★ — P8 에서 실제로 걸렸던 두 자리를 넣어 자가 걸리는지 본다.
    print('◆ 걸려야 하는 것 둘 (P8 에서 실제로 걸린 자리)')
    b1 = probe(['목록의 알갱이가 모두 원자 번호 20 이하인지',
                '목록의 원소가 모두 금속인지',
                '목록이 원자 번호 차례로 놓였는지',
                '목록이 중성 원자로만 이루어졌는지'], 3, 'M02211 옛 안')
    assert any('산포' in x for x in b1), '산포를 잡지 못했다'
    b2 = probe(['모든 전자가 똑같은 세기로 끌린다',
                '유효 핵전하가 커지면 껍질 수가 준다',
                '바깥 껍질 전자가 더 세게 끌린다',
                '끌리는 세기는 껍질 수만으로 정해진다'], 2, 'M02210 옛 안')
    assert any("'더' 포함" in x for x in b2), "'더' 축을 잡지 못했다"

    print('\n◆ 통과해야 하는 것 (현재 은행에 실린 문면)')
    b3 = probe(['가장 먼 두 핵 사이 거리의 절반이다',
                '이웃 수가 많은 쪽만 절반을 취한다',
                '이웃이 많은 쪽은 반지름을 작게 잡는다',
                '이웃 수가 달라도 절반 취하기는 같다'], 3, 'M02208 현재')
    assert not b3, f'통과해야 하는데 걸렸다: {b3}'
    print('\n자기 시험 통과 — 걸려야 할 둘을 잡고 통과해야 할 하나를 통과시켰다.')
