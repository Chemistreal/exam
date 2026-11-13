# -*- coding: utf-8 -*-
"""소급 조치 — 조사 앞 빈칸 열한 자리 (T13 P9 · T14 P3 · P4 · P5).

T14 P6 1차에 factchecker 가 확신도 90% 로 짚은 자국이다. P6 안의 열한 자리는 그때
붙였고, ★같은 꼴이 앞 배치에 그대로 남아 은행에 들어가 있었다★ — P3 4건 · P4 3건 ·
P5 3건 · T13 P9 1건. 그때 소급 부채로 적어 두었던 것을 여기서 갚는다.

★① 오탐부터 센다.★
  은행 전체를 `[가-힣] (를|을|도|이지) ` 로 훑으면 스무 자리가 울리는데 ★아홉이
  오탐★ 이다.
    · '몇 ★도★ 올릴 때의 열량'(M00496·M00576·M00577×2·M00607·M00611) — 여기서 '도' 는
      조사가 아니라 ★온도의 단위 명사★ 다.
    · '전하량만 보면 ★을★ 3 · 병 2 · 갑 1'(M01838×3) — '갑·을·병' 은 그 문항 자료의
      ★이름★ 이다.
  → 정규식으로 걸지 않고 ★낱말 목록을 명시★ 해 열한 자리만 고친다. 기계 검사는
    '고친 뒤 그 열한 문면이 0 인가' 로 세운다.

★② 자국의 정체 — 강조를 지우면서 남은 빈칸.★
  열한 자리가 모두 ★해설 마무리 격언★ 이거나 ★요령을 적는 줄★ 이다. 저작할 때 강조할
  구절을 띄어 두었다가 평문 검사(국소검사 ⑨) 때문에 표시만 지우고 빈칸을 남긴 것이다.
  ▸ ★평문으로 바꾸라는 검사는 표시를 지우게 할 뿐 자국까지 지워 주지는 않는다.★

은행과 저작 파일을 함께 고친다 — ★한쪽만 고치면 다음 재빌드에서 되살아난다.★
"""
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(BASE, 'master_bank.json')

# (파일, 옛 문면, 새 문면, 문항)  — 저작 파일의 줄바꿈과 무관하게 한 줄 안에 있는 것만
R = [
    ('build_t13_p9.py', '먼저 출발점 을 보고', '먼저 출발점을 보고', 'M02058'),
    ('build_t14_p3.py', '어디에 있었는지 를 봐야', '어디에 있었는지를 봐야', 'M02157'),
    ('build_t14_p3.py', '어떻게 얻는지 를 되짚는', '어떻게 얻는지를 되짚는', 'M02160'),
    ('build_t14_p3.py', '무엇이 묶였는지 를 먼저', '무엇이 묶였는지를 먼저', 'M02161'),
    ('build_t14_p3.py', '숫자가 있는지 를 먼저', '숫자가 있는지를 먼저', 'M02164'),
    ('build_t14_p4.py', '손에 있는지 를 먼저 묻는다', '손에 있는지를 먼저 묻는다', 'M02169'),
    ('build_t14_p4.py', '받치는 조건인지 를 함께', '받치는 조건인지를 함께', 'M02171'),
    ('build_t14_p4.py', '누가 위인지 를 적어', '누가 위인지를 적어', 'M02174'),
    ('build_t14_p5.py', '볼 수 있는지 를 세어', '볼 수 있는지를 세어', 'M02176'),
    ('build_t14_p5.py', '한 몸으로 움직이는지 를 적어', '한 몸으로 움직이는지를 적어', 'M02181'),
    ('build_t14_p5.py', '방향인지 대소인지 를 먼저', '방향인지 대소인지를 먼저', 'M02182'),
]


def main():
    # ── ① 저작 파일 ────────────────────────────────────────────────────────────
    for f in sorted({r[0] for r in R}):
        p = os.path.join(BASE, f)
        s = open(p, encoding='utf-8').read()
        for fn, old, new, _ in R:
            if fn != f:
                continue
            assert s.count(old) == 1, f'{f}: {s.count(old)}곳 — {old!r}'
            s = s.replace(old, new)
        open(p, 'w', encoding='utf-8').write(s)

    # ── ② 은행 ────────────────────────────────────────────────────────────────
    b = json.load(open(BANK, encoding='utf-8'))
    items = b['items'] if isinstance(b, dict) else b
    idx = {i['id']: i for i in items}
    n = 0
    for _, old, new, mid in R:
        it = idx[mid]
        assert it['solution'].count(old) == 1, f'{mid}: {old!r} 가 해설에 1곳이 아니다'
        it['solution'] = it['solution'].replace(old, new)
        n += 1
    assert n == 11
    json.dump(b, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # ── ③ ★기계로 센다★ — 고친 열한 문면이 은행과 저작 파일 어디에도 없는가 ────
    b2 = json.load(open(BANK, encoding='utf-8'))
    items2 = b2['items'] if isinstance(b2, dict) else b2
    blob = '\n'.join((i.get('solution') or '') for i in items2)
    for f in sorted({r[0] for r in R}):
        blob += open(os.path.join(BASE, f), encoding='utf-8').read()
    for _, old, _, mid in R:
        assert old not in blob, f'{mid}: 옛 문면이 남았다 — {old!r}'

    print(f'조사 앞 빈칸 소급 조치 — {n}자리 (은행 + 저작 파일 4개)')
    print('  오탐 아홉은 손대지 않음: 몇 "도"(온도 단위) 6건 · 갑을병의 "을" 3건')


if __name__ == '__main__':
    main()
