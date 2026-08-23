#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""단원별 여덟 회차에서 그림이 소실된 문항의 그림을 다시 그린다.

exam_*.json 은 .hwp 에서 **글만** 캔 것이라 원본의 그림·표가 없다. 원본
PDF 를 구하려 공식 사이트(olympiad.kchem.org)를 뒤졌지만 2010년 이후만
공개되어 있고, 2003~2008 화올은 유료 기출문제집에만 있다. 비공식 스캔을
긁어 **공개 저장소**에 올릴 수는 없다.

다행히 줄기·해설에 그림의 내용이 전부 적혀 있다 — 「Ne 1.5기압·1.0L」,
「A와 E 기울기는 C의 2배」, 「꼭짓점에 Ti 8개·중심에 1개」. 그래서 그림을
**서술에서 다시 그린다.** 원본을 흉내 낸 위조가 아니라, 문항이 요구하는
정보를 담은 재작도다. 각 그림 아래에 「재작도」 라고 밝힌다.

수치가 해설에 없는 자리는 지어내지 않는다 — 풀이에 안 쓰이는 값은 기호로
남긴다(예: 플라스크 셋 중 Ne 아닌 두 개의 압력).

다시 그릴 수 **없는** 문항 둘은 그리지 않고 남긴다:
    kch1to3 31    본문 자체가 .hwp 에서 소실 — 원본이 있어야 한다
    chem2-1 42    해설의 개수 서술이 스스로 모순 — 원본 확인 전에는 못 그린다

사용: from legacy_figs import FIGS, NOFIG   # (회차id, 문항번호) → html
"""

# ── 공통 ─────────────────────────────────────────────────────────────────
INK = '#16181d'
MUT = '#5b6270'
ACC = '#2E6E63'
RED = '#B04A5A'
BLU = '#3B5BA5'


def _svg(w, h, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" '
            'width="%d" role="img">%s</svg>' % (w, h, w, body))


def _redrawn(inner, cap=''):
    """그림 + 「재작도」 꼬리표. 원본이 아님을 학생에게 숨기지 않는다."""
    tail = ('<figcaption style="font-family:\'Noto Sans KR\',sans-serif;'
            'font-size:12px;color:%s;margin-top:4px">%s%s재작도 — 원본 그림의 '
            '내용을 글 서술에서 다시 그린 것입니다</figcaption>' %
            (MUT, cap, ' · ' if cap else ''))
    return '<figure style="margin:.6em 0">%s%s</figure>' % (inner, tail)


def _table(headers, rows, widths=None):
    th = ''.join('<th style="border:1px solid #9aa0ad;padding:5px 10px;'
                 'background:#f2efe8;font-size:14.5px">%s</th>' % h for h in headers)
    trs = ''
    for r in rows:
        tds = ''.join('<td style="border:1px solid #9aa0ad;padding:5px 10px;'
                      'text-align:center;font-size:14.5px">%s</td>' % c for c in r)
        trs += '<tr>%s</tr>' % tds
    return ('<table style="border-collapse:collapse;margin:.5em 0;'
            'font-family:\'Noto Sans KR\',sans-serif"><tr>%s</tr>%s</table>' % (th, trs))


def _txt(x, y, s, size=13, fill=INK, anchor='middle', bold=False, family="'Noto Sans KR',sans-serif"):
    return ('<text x="%g" y="%g" font-size="%g" fill="%s" text-anchor="%s" '
            'font-family="%s"%s>%s</text>' %
            (x, y, size, fill, anchor, family, ' font-weight="700"' if bold else '', s))


def _line(x1, y1, x2, y2, stroke=INK, w=1.4, dash=''):
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g"%s/>' %
            (x1, y1, x2, y2, stroke, w, (' stroke-dasharray="%s"' % dash) if dash else ''))


def _poly(pts, stroke=INK, w=2, fill='none', dash=''):
    p = ' '.join('%g,%g' % xy for xy in pts)
    return ('<polyline points="%s" fill="%s" stroke="%s" stroke-width="%g" '
            'stroke-linejoin="round" stroke-linecap="round"%s/>' %
            (p, fill, stroke, w, (' stroke-dasharray="%s"' % dash) if dash else ''))


def _circ(x, y, r, fill, stroke=INK, sw=1.2):
    return '<circle cx="%g" cy="%g" r="%g" fill="%s" stroke="%s" stroke-width="%g"/>' % (x, y, r, fill, stroke, sw)


def _arrow(x1, y1, x2, y2, stroke=INK, w=1.6):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    h = 7
    p1 = (x2 - h * math.cos(a - .42), y2 - h * math.sin(a - .42))
    p2 = (x2 - h * math.cos(a + .42), y2 - h * math.sin(a + .42))
    return (_line(x1, y1, x2, y2, stroke, w) +
            '<polygon points="%g,%g %g,%g %g,%g" fill="%s"/>' %
            (x2, y2, p1[0], p1[1], p2[0], p2[1], stroke))


# ── 개별 그림 ────────────────────────────────────────────────────────────
def fig_ion_table():
    return _redrawn(_table(
        ['', '양성자 수', '중성자 수', '전자 수', '전하'],
        [['원자 X', '20', '20', '(가)', '+2'],
         ['이온 Y', '23', '28', '20', '(나)'],
         ['⁵⁶Fe²⁺', '26', '(다)', '24', '+2']]), '표')


def fig_gas_can():
    dots = ''
    import random
    rnd = random.Random(7)
    for _ in range(26):
        dots += _circ(30 + rnd.random() * 160, 26 + rnd.random() * 120, 2.6, INK, INK, 0)
    body = ('<rect x="22" y="18" width="176" height="136" fill="none" stroke="%s" stroke-width="3"/>' % INK
            + dots + _txt(110, 172, '20 °C · 3기압 (냉각 전)', 13, MUT))
    return _redrawn(_svg(230, 182, body), '금속 통 단면 · 점 = 수소 분자')


def fig_liebig():
    b = []
    b.append('<rect x="14" y="52" width="128" height="40" rx="6" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append(_txt(78, 76, '시료 연소관', 13))
    b.append(_txt(78, 40, 'O₂ →', 13, MUT))
    # ⚠ 흡수제 이름을 적지 않는다 — 「(가)(나)에 들어갈 흡수제 고르기」 가 이
    #    문항의 과제다. 게다가 처음 적었던 이름(염화칼슘·KOH)은 답지의 정답
    #    (실리카겔·수산화나트륨)과 어긋나기까지 했다. 중립으로 둔다.
    for i, (x, lab, sub) in enumerate([(170, '(가)', '흡수관 1'), (300, '(나)', '흡수관 2')]):
        b.append('<rect x="%d" y="40" width="104" height="64" rx="10" fill="none" stroke="%s" stroke-width="2"/>' % (x, INK))
        b.append(_txt(x + 52, 66, lab, 15, INK, 'middle', True))
        b.append(_txt(x + 52, 86, sub, 12, MUT))
        b.append(_arrow((142 if i == 0 else 274), 72, x, 72))
    b.append(_arrow(404, 72, 434, 72))
    return _redrawn(_svg(450, 116, ''.join(b)), '리비히 원소 분석 장치')


def fig_decay_nz():
    b = []
    b.append(_arrow(40, 200, 40, 20))
    b.append(_arrow(40, 200, 320, 200))
    b.append(_txt(24, 30, '중성자 수', 12, MUT, 'start'))
    b.append(_txt(318, 216, '양성자 수', 12, MUT, 'end'))
    x0, y0 = 170, 110
    b.append(_circ(x0, y0, 4, INK))
    # (가) γ: 제자리(굽은 화살)
    b.append('<path d="M %g %g q 26 -30 0 -44" fill="none" stroke="%s" stroke-width="1.8"/>' % (x0 + 4, y0 - 4, ACC))
    b.append('<polygon points="%g,%g %g,%g %g,%g" fill="%s"/>' % (x0 + 2, y0 - 46, x0 + 10, y0 - 50, x0 + 8, y0 - 40, ACC))
    b.append(_txt(x0 + 34, y0 - 40, '(가)', 14, ACC, 'start', True))
    # (나) α: 양성자 −2, 중성자 −2 (왼쪽 아래)
    b.append(_arrow(x0 - 6, y0 + 6, x0 - 66, y0 + 66, RED))
    b.append(_txt(x0 - 74, y0 + 82, '(나)', 14, RED, 'middle', True))
    # (다) β⁺/EC: 양성자 −1, 중성자 +1 (왼쪽 위)
    b.append(_arrow(x0 - 6, y0 - 6, x0 - 36, y0 - 36, BLU))
    b.append(_txt(x0 - 46, y0 - 44, '(다)', 14, BLU, 'middle', True))
    return _redrawn(_svg(340, 232, ''.join(b)), 'N–Z 도표 위의 세 변환')


def fig_rutherford():
    b = []
    b.append('<rect x="196" y="24" width="8" height="150" fill="#d9c87a" stroke="%s"/>' % INK)
    b.append(_txt(200, 192, '금박', 12, MUT))
    for y in (60, 100, 140):
        b.append(_arrow(30, y, 192, y, MUT, 1.4))
    b.append(_txt(30, 44, 'α 입자살', 12, MUT, 'start'))
    b.append(_arrow(204, 60, 360, 58, INK, 1.6))
    b.append(_arrow(204, 100, 360, 100, INK, 1.6))
    b.append(_arrow(204, 140, 330, 190, RED, 1.6))
    b.append(_arrow(199, 100, 60, 30, RED, 1.6))
    b.append(_txt(366, 82, '대부분 통과', 12.5, INK, 'start'))
    b.append(_txt(300, 208, '일부 휘어짐', 12.5, RED, 'start'))
    b.append(_txt(46, 20, '극히 일부 튕김', 12.5, RED, 'start'))
    return _redrawn(_svg(470, 220, ''.join(b)), '알파 입자 산란 실험')


_BALMER = [('w', 410, '#7b5bd6'), ('x', 434, '#4b62d8'), ('y', 486, '#2E8B8B'), ('z', 656, '#c0392b')]


def _spectrum(labels=True):
    b = []
    b.append('<rect x="30" y="30" width="420" height="64" fill="#0d0f14"/>')
    for lab, nm, col in _BALMER:
        x = 30 + (nm - 380) * 420.0 / (700 - 380)
        b.append(_line(x, 30, x, 94, col, 3))
        if labels:
            b.append(_txt(x, 22, lab, 14, INK, 'middle', True))
        b.append(_txt(x, 112, str(nm), 11.5, MUT))
    b.append(_txt(30, 130, '380', 11, MUT, 'start'))
    b.append(_txt(450, 130, '700 (nm)', 11, MUT, 'end'))
    b.append(_line(30, 118, 450, 118, MUT, 1))
    return _svg(470, 140, ''.join(b))


def fig_spectrum_only():
    return _redrawn(_spectrum(labels=False), '수소 방전관 선 스펙트럼 (발머 계열)')


def fig_bohr_levels():
    b = []
    # 왼쪽: 준위도. e=n∞, a=n6, b=n5, (무표기 n4), c=n3, d=n2
    ys = {'e': 34, 'a': 52, 'b': 66, '': 86, 'c': 118, 'd': 190}
    ns = {'e': 'n=∞', 'a': 'n=6', 'b': 'n=5', '': 'n=4', 'c': 'n=3', 'd': 'n=2'}
    for lab, y in ys.items():
        b.append(_line(40, y, 200, y, INK, 1.6 if lab else 1.2))
        if lab:
            b.append(_txt(30, y + 4, lab, 13.5, INK, 'end', True))
        b.append(_txt(208, y + 4, ns[lab], 12, MUT, 'start'))
    for i, (lab, src) in enumerate([('w', 'a'), ('x', 'b'), ('y', ''), ('z', 'c')]):
        x = 66 + i * 34
        b.append(_arrow(x, ys[src], x, ys['d'] - 3, ACC, 1.5))
        b.append(_txt(x, ys['d'] + 16, lab, 12.5, ACC, 'middle', True))
    b.append(_txt(140, 228, '에너지 준위와 전이', 12, MUT))
    left = ''.join(b)
    right = ('<g transform="translate(268,44)">'
             + _spectrum() .replace('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 470 140" width="470" role="img">', '')
             .replace('</svg>', '') + '</g>')
    # 스펙트럼을 축소해 오른쪽에 앉힌다
    right = '<g transform="translate(252,50) scale(0.62)">' + _spectrum().split('>', 1)[1].rsplit('<', 1)[0] + '</g>'
    return _redrawn(_svg(560, 240, left + right), '왼쪽 준위도 · 오른쪽 선 스펙트럼')


def fig_periodic_abc():
    import math
    b = []
    panels = [('A', [1, 2, 3, 4, 5, 6, 7, 0], '계단형 증가 · Ne에서 0'),
              ('B', [10, 8.6, 7.6, 6.9, 6.4, 6.0, 5.7, 5.4], '단조 감소'),
              ('C', [2.5, 6.5, 9.5, 10, 1.2, 0.9, 0.6, 0.4], 'C에서 최고 · 비금속에서 급락')]
    for pi, (name, vals, cap) in enumerate(panels):
        ox = 20 + pi * 180
        b.append(_arrow(ox + 18, 128, ox + 18, 20))
        b.append(_arrow(ox + 18, 128, ox + 168, 128))
        vmax = max(vals)
        pts = [(ox + 30 + i * 18, 124 - v * 92.0 / vmax) for i, v in enumerate(vals)]
        b.append(_poly(pts, ACC, 2))
        for p in pts:
            b.append(_circ(p[0], p[1], 2.4, ACC, ACC, 0))
        b.append(_txt(ox + 92, 16, name, 15, INK, 'middle', True))
        b.append(_txt(ox + 92, 144, '원자 번호 (Li→Ne)', 10.5, MUT))
    return _redrawn(_svg(560, 156, ''.join(b)), '2주기 원소의 성질 A·B·C')


def fig_lif_borne():
    b = []
    lv = [('Li⁺(g) + e⁻ + F(g)', 30, 758),
          ('Li⁺(g) + e⁻ + ½F₂(g)', 58, 681),
          ('Li⁺(g) + F⁻(g)', 96, 353),
          ('Li(g) + ½F₂(g)', 208, 161),
          ('Li(s) + ½F₂(g)', 252, 0),
          ('LiF(s)', 388, -694)]
    for name, y, kj in lv:
        b.append(_line(150, y, 330, y, INK, 1.6))
        b.append(_txt(142, y + 4, name, 12, INK, 'end'))
    # ⚠ 단계 이름을 적지 않는다 — 「+520 (이온화)」 라고 쓰면 「이온화 에너지는
    #    얼마인가」 의 답이 그림에 적힌 꼴이 된다. 원본처럼 수치만 준다.
    b.append(_arrow(240, 252, 240, 210, ACC)); b.append(_txt(248, 236, '+161', 11.5, ACC, 'start'))
    b.append(_arrow(240, 208, 240, 60, ACC)); b.append(_txt(248, 140, '+520', 11.5, ACC, 'start'))
    b.append(_arrow(262, 58, 262, 33, ACC)); b.append(_txt(268, 50, '+77', 11.5, ACC, 'start'))
    b.append(_arrow(300, 30, 300, 93, BLU)); b.append(_txt(306, 68, '−328', 11.5, BLU, 'start'))
    b.append(_arrow(318, 96, 318, 385, BLU)); b.append(_txt(324, 250, '−1047', 11.5, BLU, 'start'))
    b.append(_arrow(176, 252, 176, 385, RED)); b.append(_txt(170, 320, '−617', 11.5, RED, 'end'))
    b.append(_txt(40, 416, '단위: kJ/mol', 11, MUT, 'start'))
    return _redrawn(_svg(470, 430, ''.join(b)), 'LiF 생성 에너지 준위도')


def fig_kf_cycle():
    b = []
    lv = [('K(s) + ½F₂(g)', 250), ('K(g) + ½F₂(g)', 205), ('K⁺(g) + e⁻ + ½F₂(g)', 90),
          ('K⁺(g) + e⁻ + F(g)', 55), ('K⁺(g) + F⁻(g)', 120), ('KF(s)', 330)]
    xs = [(30, 170), (30, 170), (30, 170), (206, 356), (206, 356), (206, 356)]
    for (name, y), (x1, x2) in zip(lv, xs):
        b.append(_line(x1, y, x2, y, INK, 1.6))
        b.append(_txt((x1 + x2) / 2, y - 6, name, 11.5, INK))
    b.append(_arrow(100, 250, 100, 208, ACC)); b.append(_txt(108, 234, '1', 13, ACC, 'start', True))
    b.append(_arrow(100, 205, 100, 93, ACC)); b.append(_txt(108, 152, '3', 13, ACC, 'start', True))
    b.append(_arrow(184, 90, 216, 58, ACC)); b.append(_txt(196, 62, '2', 13, ACC, 'start', True))
    b.append(_arrow(280, 55, 280, 117, BLU)); b.append(_txt(288, 90, '4', 13, BLU, 'start', True))
    b.append(_arrow(280, 120, 280, 327, BLU)); b.append(_txt(288, 230, '5', 13, BLU, 'start', True))
    b.append(_arrow(60, 250, 60, 327, RED)); b.append(_line(60, 330, 206, 330, RED, 1.6))
    b.append(_txt(52, 292, 'ΔH_f', 12, RED, 'end'))
    return _redrawn(_svg(400, 350, ''.join(b)), 'KF Born–Haber 순환 · 단계 1~5')


def fig_air_table():
    return _redrawn(_table(
        ['성분', '부피비(%)', '정상 끓는점(°C)', '정상 녹는점(°C)'],
        [['N₂', '78', '−196', '−210'],
         ['O₂', '21', '−183', '−218'],
         ['Ar', '1', '−186', '−189']]), '공기의 조성')


def fig_three_flasks():
    b = []
    spec = [('A 기체', '1.0 L', 40), ('Ne · 1.5기압', '1.0 L', 180), ('B 기체', '0.5 L', 320)]
    for name, vol, x in spec:
        w = 96 if vol == '1.0 L' else 72
        b.append('<rect x="%d" y="60" width="%d" height="76" rx="14" fill="none" stroke="%s" stroke-width="2"/>' % (x, w, INK))
        b.append(_txt(x + w / 2, 96, name, 12.5, INK, 'middle', True))
        b.append(_txt(x + w / 2, 116, vol, 12, MUT))
    for x1, x2 in ((136, 180), (276, 320)):
        b.append(_line(x1, 84, x2, 84, INK, 2))
        m = (x1 + x2) / 2
        b.append(_circ(m, 84, 6, '#fff', INK, 1.6))
        b.append(_txt(m, 72, '밸브', 10.5, MUT))
    return _redrawn(_svg(440, 150, ''.join(b)), '연결관 부피는 무시')


def fig_o_config():
    def box_row(ox, oy, occ):
        out = []
        labels = ['1s', '2s', '2p', '3s']
        xi = 0
        for li, (lab, boxes) in enumerate(zip(labels, [1, 1, 3, 1])):
            for bi in range(boxes):
                x = ox + xi * 26
                out.append('<rect x="%d" y="%d" width="24" height="24" fill="none" stroke="%s" stroke-width="1.4"/>' % (x, oy, INK))
                spins = occ[li][bi] if bi < len(occ[li]) else ''
                if spins == 'ud':
                    out.append(_txt(x + 8, oy + 18, '↑', 15)); out.append(_txt(x + 17, oy + 18, '↓', 15))
                elif spins == 'u':
                    out.append(_txt(x + 12, oy + 18, '↑', 15))
                xi += 1
            out.append(_txt(ox + (xi - boxes / 2.0) * 26 - 13 * boxes + 13, oy + 40, lab, 11.5, MUT))
        return out
    b = []
    states = [
        ('①', [['ud'], ['ud'], ['ud', 'u', 'u'], ['']]),
        ('②', [['ud'], ['ud'], ['ud', 'u', ''], ['u']]),
        ('③', [['ud'], ['ud'], ['ud', 'ud', ''], ['']]),
        ('④', [['ud'], ['u'], ['ud', 'ud', 'u'], ['']]),
    ]
    for i, (lab, occ) in enumerate(states):
        ox, oy = 56 + (i % 2) * 260, 24 + (i // 2) * 92
        b.append(_txt(ox - 22, oy + 18, lab, 15, INK, 'middle', True))
        b += box_row(ox, oy, occ)
    return _redrawn(_svg(560, 208, ''.join(b)), '산소 원자의 네 가지 전자 배치')


def fig_stern_gerlach():
    b = []
    b.append('<rect x="20" y="78" width="66" height="40" rx="6" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append(_txt(53, 102, '오븐', 12.5))
    b.append(_line(100, 88, 100, 108, INK, 2)); b.append(_txt(100, 126, '슬릿', 11, MUT))
    b.append(_arrow(86, 98, 176, 98, MUT, 1.4))
    b.append('<path d="M180 40 h96 v22 h-96 z" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append(_txt(228, 56, 'N', 14, INK, 'middle', True))
    b.append('<path d="M180 134 h96 v22 h-96 z" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append(_txt(228, 150, 'S', 14, INK, 'middle', True))
    b.append(_txt(228, 26, '비균일 자기장', 11.5, MUT))
    b.append('<path d="M276 98 q 44 -20 84 -26" fill="none" stroke="%s" stroke-width="1.8"/>' % ACC)
    b.append('<path d="M276 98 q 44 20 84 26" fill="none" stroke="%s" stroke-width="1.8"/>' % ACC)
    b.append(_line(372, 40, 372, 156, INK, 2.4))
    b.append(_circ(366, 71, 3.4, ACC, ACC, 0))
    b.append(_circ(366, 125, 3.4, ACC, ACC, 0))
    b.append(_txt(384, 74, '두 갈래', 11.5, MUT, 'start'))
    b.append(_txt(372, 174, '검출판', 11, MUT))
    return _redrawn(_svg(470, 186, ''.join(b)), '수소 원자살(1s)의 자기장 통과')


def fig_three_cans():
    b = []
    for i, (lab, gas) in enumerate([('(가)', 'H₂ · 2기압'), ('(나)', 'He · 2기압'), ('(다)', 'O₂ · 4기압')]):
        x = 26 + i * 150
        b.append('<rect x="%d" y="34" width="118" height="86" rx="8" fill="none" stroke="%s" stroke-width="2.4"/>' % (x, INK))
        b.append(_txt(x + 59, 22, lab, 14, INK, 'middle', True))
        b.append(_txt(x + 59, 72, gas, 13))
        b.append(_txt(x + 59, 94, '5 L', 12, MUT))
        b.append(_circ(x + 118, 62, 3.2, '#fff', INK, 1.6))
        b.append(_txt(x + 128, 56, '구멍', 10.5, MUT, 'start'))
    return _redrawn(_svg(510, 134, ''.join(b)), '진공 실내의 금속 용기 셋')


def _maxwell_pts(ox, oy, w, h, m):
    import math
    pts = []
    for i in range(61):
        v = i / 60.0 * 3.4
        f = (m ** 1.5) * v * v * math.exp(-m * v * v)
        pts.append((ox + v / 3.4 * w, oy - f * h * 3.2))
    return pts


def fig_boltzmann():
    b = []
    ox, oy = 46, 168
    b.append(_arrow(ox, oy, ox, 22)); b.append(_arrow(ox, oy, 430, oy))
    b.append(_txt(30, 20, '분자 수 비율', 11, MUT, 'start'))
    b.append(_txt(428, 184, '분자 속력', 11, MUT, 'end'))
    # 무거운 기체일수록 봉우리가 낮은 속력에서 높게 선다 — 각 곡선을 제
    # 최고점 기준으로 그려 봉우리가 그림 밖으로 나가지 않게 한다.
    for m, col, lab, peak_h in [(3.2, RED, '(가)', 128), (1.5, ACC, '(나)', 104), (0.7, BLU, '(다)', 78)]:
        pts = _maxwell_pts(ox, oy, 370, 120, m)
        top = min(p[1] for p in pts)
        scale = peak_h / (oy - top)
        pts = [(x, oy - (oy - y) * scale) for x, y in pts]
        b.append(_poly(pts, col, 2))
        px, py = min(pts, key=lambda p: p[1])
        b.append(_txt(px + 14, py - 8, lab, 13, col, 'middle', True))
    return _redrawn(_svg(450, 196, ''.join(b)), '같은 온도 · 세 기체의 속력 분포')


def fig_compressibility():
    import math
    b = []
    ox, oy = 60, 190
    b.append(_arrow(ox, oy, ox, 22)); b.append(_arrow(ox, oy, 440, oy))
    b.append(_txt(36, 18, 'PV/RT', 12, MUT, 'start'))
    b.append(_txt(438, 206, 'P (atm)', 11.5, MUT, 'end'))
    y1 = oy - 78
    b.append(_line(ox, y1, 440, y1, MUT, 1, '5,4'))
    b.append(_txt(52, y1 + 4, '1', 12, MUT, 'end'))
    pts = []
    for i in range(81):
        p = i / 80.0 * 1000
        z = 1 - 0.55 * math.exp(-((p - 170) / 150.0) ** 2) * (p / (p + 60)) + max(0.0, (p - 400)) ** 1.35 / 3800.0
        pts.append((ox + p / 1000.0 * 380, oy - z * 78))
    b.append(_poly(pts, INK, 2.2))
    x400 = ox + 400 / 1000.0 * 380
    b.append(_line(x400, oy, x400, 30, MUT, 1, '4,4'))
    b.append(_txt(x400, oy + 16, '400', 11.5, MUT))
    b.append(_txt((ox + x400) / 2, 210, 'A', 14, ACC, 'middle', True))
    b.append(_txt((x400 + 440) / 2, 210, 'B', 14, RED, 'middle', True))
    return _redrawn(_svg(460, 224, ''.join(b)), '압축률 인자 Z = PV/RT')


def fig_vapor_curves():
    import math
    b = []
    ox, oy = 56, 190
    b.append(_arrow(ox, oy, ox, 22)); b.append(_arrow(ox, oy, 440, oy))
    b.append(_txt(30, 18, '증기 압력', 12, MUT, 'start'))
    b.append(_txt(452, 178, '온도\n(°C)'.split('\n')[0] + ' (°C)', 11.5, MUT, 'end'))
    yatm = oy - 118
    b.append(_line(ox, yatm, 440, yatm, MUT, 1, '5,4'))
    b.append(_txt(50, yatm + 4, '1기압', 11.5, MUT, 'end'))
    for bp, col, lab in [(34.6, ACC, '다이에틸에테르'), (78.4, BLU, '에탄올'), (100.0, RED, '물')]:
        pts = []
        for i in range(61):
            t = -20 + i / 60.0 * 140
            pv = math.exp(0.045 * (t - bp)) * 1.0
            if pv > 1.55:
                break
            pts.append((ox + (t + 20) / 140.0 * 380, oy - pv * 118))
        b.append(_poly(pts, col, 2))
        b.append(_txt(pts[-1][0] - 4, max(16, pts[-1][1] - 8), lab, 11.5, col, 'end'))
    return _redrawn(_svg(460, 224, ''.join(b)), '세 액체의 증기 압력 곡선')


def _closed_box(inner, w=420, h=206):
    return ('<rect x="14" y="14" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2.6"/>' % (w - 28, h - 28, INK)) + inner


def _beaker(x, y, w, h, level, lab, sub, col='#cfe3ff'):
    b = []
    b.append('<path d="M%d %d v%d h%d v-%d" fill="none" stroke="%s" stroke-width="2"/>' % (x, y, h, w, h, INK))
    lv = y + h - level
    b.append('<rect x="%d" y="%g" width="%d" height="%g" fill="%s" opacity="0.85"/>' % (x + 1, lv, w - 2, y + h - lv - 1, col))
    b.append(_txt(x + w / 2, y + h + 18, lab, 12.5, INK, 'middle', True))
    if sub:
        b.append(_txt(x + w / 2, y + h + 34, sub, 11, MUT))
    return ''.join(b)


def fig_two_beakers_sea():
    inner = (_beaker(70, 50, 110, 96, 60, '증류수', '50 mL') +
             _beaker(240, 50, 110, 96, 60, '바닷물', '50 mL', '#bcd8cf') +
             _txt(210, 40, '밀폐 용기', 11.5, MUT))
    return _redrawn(_svg(420, 226, _closed_box(inner)), '')


def fig_two_beakers_glc():
    inner = (_beaker(70, 50, 110, 96, 60, '1 M NaCl', '수용액', '#bcd8cf') +
             _beaker(240, 50, 110, 96, 60, '1 M 포도당', '수용액') +
             _txt(210, 40, '밀폐 용기 · 온도 일정', 11.5, MUT))
    return _redrawn(_svg(420, 226, _closed_box(inner)), '')


def fig_capillary():
    b = []
    for x0, lab, up, convex, col in [(40, '물', True, False, '#cfe3ff'), (250, '수은', False, True, '#aeb0ba')]:
        b.append('<path d="M%d 150 h150 v46 h-150 z" fill="%s" stroke="%s" stroke-width="1.6"/>' % (x0, col, INK))
        cx = x0 + 75
        lv = 108 if up else 176
        b.append(_line(cx - 9, 60, cx - 9, 196, INK, 1.8))
        b.append(_line(cx + 9, 60, cx + 9, 196, INK, 1.8))
        b.append('<rect x="%g" y="%g" width="16" height="%g" fill="%s"/>' % (cx - 8, lv, 195 - lv, col))
        if convex:
            b.append('<path d="M%g %g q 8 -10 16 0" fill="%s" stroke="%s" stroke-width="1.2"/>' % (cx - 8, lv, col, INK))
        else:
            b.append('<path d="M%g %g q 8 10 16 0" fill="#fff" stroke="%s" stroke-width="1.2"/>' % (cx - 8, lv, INK))
        b.append(_txt(cx, 224, lab, 13, INK, 'middle', True))
    return _redrawn(_svg(470, 238, ''.join(b)), '모세관 속 메니스커스')


def fig_heating_curve():
    b = []
    ox, oy = 50, 196
    b.append(_arrow(ox, oy, ox, 22)); b.append(_arrow(ox, oy, 452, oy))
    b.append(_txt(28, 18, '온도', 12, MUT, 'start'))
    b.append(_txt(450, 212, '가열 시간', 11.5, MUT, 'end'))
    # 기울기 A=E=2k, C=k. 구간 시간: A=1, B=1, C=2, D=7, E=1  (D=7B)
    total = 12.0
    segs = [('A', 1, 2), ('B', 1, 0), ('C', 2, 1), ('D', 7, 0), ('E', 1, 2)]
    x, y = ox, oy - 8
    k = 22
    for lab, dt, slope in segs:
        x2 = x + dt / total * 392
        y2 = y - slope * k * (dt / total * 392) / 60
        b.append(_line(x, y, x2, y2, INK, 2.2))
        b.append(_txt((x + x2) / 2, (y + y2) / 2 - 10, lab, 13, ACC, 'middle', True))
        x, y = x2, y2
    b.append(_line(ox, oy - 8 - 2 * k * (1 / total * 392) / 60, ox + 8, oy - 8 - 2 * k * (1 / total * 392) / 60, MUT, 1))
    b.append(_txt(46, oy - 4, '0', 11, MUT, 'end'))
    return _redrawn(_svg(470, 226, ''.join(b)), '얼음의 가열 곡선 (일정한 열 공급)')


def _cube(ox, oy, s, depth=0.42):
    d = s * depth
    f = [(ox, oy), (ox + s, oy), (ox + s, oy + s), (ox, oy + s)]
    bk = [(x + d, y - d) for x, y in f]
    b = []
    for i in range(4):
        b.append(_line(*f[i], *f[(i + 1) % 4], INK, 1.5))
        b.append(_line(*bk[i], *bk[(i + 1) % 4], MUT, 1.1))
        b.append(_line(*f[i], *bk[i], MUT, 1.1))
    return b, f, bk


def _cube_pts(ox, oy, s, depth=0.42):
    d = s * depth
    P = {}
    for xi in (0, 1):
        for yi in (0, 1):
            for zi in (0, 1):
                P[(xi, yi, zi)] = (ox + xi * s + zi * d, oy + (1 - yi) * s - zi * d)
    return P


FACES = [[(0,0,0),(1,0,0),(1,1,0),(0,1,0)], [(0,0,1),(1,0,1),(1,1,1),(0,1,1)],
         [(0,0,0),(0,1,0),(0,1,1),(0,0,1)], [(1,0,0),(1,1,0),(1,1,1),(1,0,1)],
         [(0,0,0),(1,0,0),(1,0,1),(0,0,1)], [(0,1,0),(1,1,0),(1,1,1),(0,1,1)]]
EDGES = [(a, c) for a in [(0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,1,1)]
         for c in [(0,0,0),(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1),(0,1,1),(1,1,1)]
         if sum(abs(a[i] - c[i]) for i in range(3)) == 1 and a < c]


def fig_nacl_cscl():
    b = []
    # NaCl: 꼭짓점 8 + 면심 6 = Cl, 모서리 12 + 중심 1 = Na.
    # ⚠ 이 문항의 평가 목표가 «격자점 세기» 다 — 절반만 그리면 그림대로 센
    #    학생이 정확히 틀린다. 여섯 면·열두 모서리를 **전부** 그린다.
    box, f, bk = _cube(40, 74, 130)
    b += box
    P = _cube_pts(40, 74, 130)
    for k, (x, y) in P.items():
        b.append(_circ(x, y, 7, '#cfe3ff'))
    for (a, c) in EDGES:
        x = (P[a][0] + P[c][0]) / 2; y = (P[a][1] + P[c][1]) / 2
        b.append(_circ(x, y, 4.5, '#e5b8be'))
    for face in FACES:
        xs = sum(P[p][0] for p in face) / 4; ys = sum(P[p][1] for p in face) / 4
        b.append(_circ(xs, ys, 7, '#cfe3ff'))
    cx = sum(P[p][0] for p in P) / 8; cy = sum(P[p][1] for p in P) / 8
    b.append(_circ(cx, cy, 4.5, '#e5b8be'))
    b.append(_txt(140, 256, 'NaCl', 13.5, INK, 'middle', True))
    b.append(_txt(140, 274, '○ Cl⁻ (꼭짓점 8 · 면심 6) · ● Na⁺ (모서리 12 · 중심 1)', 10, MUT))
    # CsCl
    box2, _, _ = _cube(330, 74, 130)
    b += box2
    P2 = _cube_pts(330, 74, 130)
    for k, (x, y) in P2.items():
        b.append(_circ(x, y, 7, '#cfe3ff'))
    cx = sum(P2[p][0] for p in P2) / 8; cy = sum(P2[p][1] for p in P2) / 8
    b.append(_circ(cx, cy, 8.5, '#e5b8be'))
    b.append(_txt(395, 256, 'CsCl', 13.5, INK, 'middle', True))
    b.append(_txt(395, 274, '○ Cl⁻ (꼭짓점 8) · ● Cs⁺ (중심 1)', 10, MUT))
    return _redrawn(_svg(560, 288, ''.join(b)), '두 이온 결정의 단위세포')


def fig_cu3au():
    b = []
    box, _, _ = _cube(120, 74, 150)
    b += box
    P = _cube_pts(120, 74, 150)
    for k, (x, y) in P.items():
        b.append(_circ(x, y, 8, '#f2d98c'))
    for face in FACES:
        xs = sum(P[p][0] for p in face) / 4; ys = sum(P[p][1] for p in face) / 4
        b.append(_circ(xs, ys, 6, '#d99a63'))
    b.append(_txt(195, 266, '꼭짓점 ○ Au · 면심 ● Cu', 12, MUT))
    return _redrawn(_svg(400, 280, ''.join(b)), 'Cu–Au 합금의 단위세포')


def fig_nias():
    b = []
    box, _, _ = _cube(120, 74, 150)
    b += box
    P = _cube_pts(120, 74, 150)
    for k, (x, y) in P.items():
        b.append(_circ(x, y, 7.5, '#cfd8e8'))
    for e in [((0,0,0),(0,1,0)), ((1,0,0),(1,1,0)), ((0,0,1),(0,1,1)), ((1,0,1),(1,1,1))]:
        x = (P[e[0]][0] + P[e[1]][0]) / 2; y = (P[e[0]][1] + P[e[1]][1]) / 2
        b.append(_circ(x, y, 7.5, '#cfd8e8'))
    cx = sum(P[p][0] for p in P) / 8; cy = sum(P[p][1] for p in P) / 8
    b.append(_circ(cx - 22, cy + 16, 6.5, '#e0a8a8'))
    b.append(_circ(cx + 24, cy - 14, 6.5, '#e0a8a8'))
    b.append(_txt(195, 266, '○ Ni (꼭짓점 8 · 수직 모서리 중앙 4) · ● As (내부 2)', 11.5, MUT))
    return _redrawn(_svg(430, 280, ''.join(b)), 'NiAs 의 단위세포')


def fig_fcc_352():
    b = []
    box, _, _ = _cube(120, 74, 150)
    b += box
    P = _cube_pts(120, 74, 150)
    for k, (x, y) in P.items():
        b.append(_circ(x, y, 8, '#cfe3ff'))
    for face in FACES:
        xs = sum(P[p][0] for p in face) / 4; ys = sum(P[p][1] for p in face) / 4
        b.append(_circ(xs, ys, 6.5, '#9fc3ef'))
    b.append(_line(120, 240, 270, 240, INK, 1.4))
    b.append(_txt(195, 258, 'a = 352 pm', 12.5, INK))
    return _redrawn(_svg(400, 274, ''.join(b)), '면심입방(fcc) 단위세포')


def fig_bcc_fe():
    b = []
    box, _, _ = _cube(120, 74, 150)
    b += box
    P = _cube_pts(120, 74, 150)
    for k, (x, y) in P.items():
        b.append(_circ(x, y, 8, '#d8d8dc'))
    cx = sum(P[p][0] for p in P) / 8; cy = sum(P[p][1] for p in P) / 8
    b.append(_circ(cx, cy, 9, '#b8b8c2'))
    b.append(_line(120, 240, 270, 240, INK, 1.4))
    b.append(_txt(195, 258, '한 변 a', 12.5, INK))
    b.append(_txt(195, 276, '꼭짓점 8 + 중심 1 (Fe)', 11.5, MUT))
    return _redrawn(_svg(400, 288, ''.join(b)), '체심입방(bcc) 단위세포')


def fig_tio2():
    b = []
    box, _, _ = _cube(120, 74, 150)
    b += box
    P = _cube_pts(120, 74, 150)
    for k, (x, y) in P.items():
        b.append(_circ(x, y, 7.5, '#cfd8e8'))
    cx = sum(P[p][0] for p in P) / 8; cy = sum(P[p][1] for p in P) / 8
    b.append(_circ(cx, cy, 7.5, '#cfd8e8'))
    top = [[(0,1,0),(1,1,0),(1,1,1),(0,1,1)]][0]
    bot = [[(0,0,0),(1,0,0),(1,0,1),(0,0,1)]][0]
    for face, offs in ((top, ((-24, 6), (26, -8))), (bot, ((-24, 6), (26, -8)))):
        xs = sum(P[p][0] for p in face) / 4; ys = sum(P[p][1] for p in face) / 4
        for dx, dy in offs:
            b.append(_circ(xs + dx, ys + dy, 5.5, '#e0a8a8'))
    b.append(_circ(cx - 30, cy + 22, 5.5, '#e0a8a8'))
    b.append(_circ(cx + 30, cy - 20, 5.5, '#e0a8a8'))
    b.append(_txt(195, 266, '○ Ti (꼭짓점 8 · 중심 1) · ● O (윗면 2 · 밑면 2 · 내부 2)', 11.5, MUT))
    return _redrawn(_svg(470, 280, ''.join(b)), '단위세포 (루틸형)')


def fig_osmosis_u():
    b = []
    b.append('<path d="M60 40 v150 h90 v-150" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append('<path d="M180 40 v150 h90 v-150" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append('<rect x="150" y="150" width="15" height="40" fill="#cfe3ff" opacity="0.8"/>')
    b.append('<rect x="165" y="150" width="15" height="40" fill="#bcd8cf" opacity="0.8"/>')
    b.append('<rect x="150" y="150" width="30" height="40" fill="none" stroke="%s" stroke-width="2"/>' % INK)
    b.append(_line(165, 148, 165, 192, RED, 2.4, '5,3'))
    b.append(_txt(165, 210, '반투막', 11.5, RED))
    b.append('<rect x="62" y="90" width="86" height="98" fill="#cfe3ff" opacity="0.8"/>')
    b.append('<rect x="182" y="90" width="86" height="98" fill="#bcd8cf" opacity="0.8"/>')
    b.append(_txt(105, 82, 'a', 13, INK, 'middle', True))
    b.append(_txt(225, 82, 'b', 13, INK, 'middle', True))
    b.append(_txt(105, 232, '순수한 물', 12))
    b.append(_txt(225, 232, '1.0 M 포도당', 12))
    return _redrawn(_svg(330, 246, ''.join(b)), '반투막을 둔 두 액체')


def fig_first_order():
    import math
    b = []
    ox, oy = 56, 180
    b.append(_arrow(ox, oy, ox, 22)); b.append(_arrow(ox, oy, 440, oy))
    b.append(_txt(30, 18, '[A]', 12, MUT, 'start'))
    b.append(_txt(438, 196, '시간', 11.5, MUT, 'end'))
    for c0, col, lab in [(1.0, ACC, '실험 1'), (0.5, BLU, '실험 2')]:
        pts = []
        for i in range(61):
            t = i / 60.0 * 5
            pts.append((ox + t / 5.0 * 370, oy - c0 * math.exp(-0.9 * t) * 140))
        b.append(_poly(pts, col, 2.2))
        b.append(_txt(pts[2][0] + 8, pts[0][1] - 6, lab + ' ([A]₀=%.1f)' % c0, 11.5, col, 'start'))
    # ⚠ t½ 보조선을 긋지 않는다 — 「초기 농도가 달라도 반감기가 같다」 는
    #    관찰이 곧 이 문항의 정답 근거다. 그림이 그 관찰을 대신해 주면 안 된다.
    return _redrawn(_svg(460, 212, ''.join(b)), '두 실험의 시간에 따른 [A]')


def fig_water_desc():
    body = ('<div style="border:1.5px solid #B8912E;background:#FBF6EA;border-radius:8px;'
            'padding:11px 14px;font-family:\'Noto Serif KR\',serif;font-size:15.5px;'
            'line-height:1.7;word-break:keep-all">'
            '분자 <b>A</b>는 수소 원자 2개와 (다) 원자 1개로 이루어진 <b>(가)</b> 분자이며 '
            '<b>(나)</b> 구조이다. 분자 <b>B</b>는 탄소 원자 1개와 (다) 원자 2개로 이루어진 '
            '직선형 분자이다. <b>(다)</b>는 인체 질량 기준으로 가장 큰 비율을 차지하는 원소이다.'
            '</div>'
            '<div style="font-family:\'Noto Sans KR\',sans-serif;font-size:12px;color:%s;'
            'margin-top:4px">재작도 — 원본 제시문의 내용을 해설에서 재구성한 것입니다</div>' % MUT)
    return body


# ── 매핑 ─────────────────────────────────────────────────────────────────
def _build():
    F = {}
    F[('kch1u1', 3)] = fig_ion_table()
    F[('kch1u1', 51)] = fig_gas_can()
    for e in ('kch1to2', 'kch1to2-b'):
        F[(e, 15)] = fig_liebig()
        F[(e, 30)] = fig_decay_nz()
        F[(e, 33)] = fig_rutherford()
        F[(e, 39)] = fig_spectrum_only()
        F[(e, 40)] = fig_bohr_levels()
    for e in ('kch1to3', 'kch1to3-b'):
        F[(e, 43)] = fig_periodic_abc()
        F[(e, 44)] = fig_lif_borne()
    F[('kch1to3-b', 45)] = fig_kf_cycle()
    F[('kch1to3-b', 11)] = fig_air_table()
    F[('kch1to3-b', 19)] = fig_three_flasks()
    F[('kch1to3-b', 30)] = fig_stern_gerlach()
    F[('kch1to3-b', 33)] = fig_o_config()
    F[('kch1to3-b', 60)] = fig_water_desc()
    F[('chem2-1', 17)] = fig_three_cans()
    F[('chem2-1', 19)] = fig_boltzmann()
    F[('chem2-1', 30)] = fig_vapor_curves()
    F[('chem2-1', 33)] = fig_capillary()
    F[('chem2-1', 36)] = fig_heating_curve()
    F[('chem2-1', 41)] = fig_nacl_cscl()
    F[('chem2-1', 43)] = fig_cu3au()
    F[('chem2-1', 44)] = fig_nias()
    F[('chem2-1', 46)] = fig_fcc_352()
    F[('chem2-1', 51)] = fig_bcc_fe()
    for e in ('chem2-1', 'kch2to3', 'kch2final'):
        F[(e, 26 if e == 'chem2-1' else 11)] = fig_compressibility()
        F[(e, 31 if e == 'chem2-1' else 13)] = fig_two_beakers_sea()
    for e in ('kch2to3', 'kch2final'):
        F[(e, 20)] = fig_tio2()
        F[(e, 25)] = fig_two_beakers_glc()
        F[(e, 30)] = fig_osmosis_u()
    F[('kch2final', 4)] = fig_first_order()
    return F


FIGS = _build()

# 「그림」 낱말에 걸렸지만 실제로는 그림이 필요 없는 문항 — 반응식·서술뿐이다.
NOFIG = {('kch1to3-b', 14)}

# 그리지 못하고 남긴 문항 — 까닭을 함께 적는다(검사가 이 목록만 봐준다).
# (kch1to3 31 은 본문이 소실됐지만 화올 2012 37번의 **원본 크롭을 빌려** 학생에게는
#  온전한 문항이다 — 여기 남길 것이 아니다.)
LEFT = {
    ('chem2-1', 42): '해설의 개수 서술이 스스로 모순 — 원본 확인 전에는 못 그린다',
}


if __name__ == '__main__':
    import io
    parts = ['<!doctype html><meta charset="utf-8"><body style="max-width:1000px;margin:20px auto;font-family:sans-serif">']
    for (e, n), h in sorted(FIGS.items()):
        parts.append('<h3>%s %d</h3>%s<hr>' % (e, n, h))
    io.open('/tmp/figs-preview.html', 'w', encoding='utf-8').write(''.join(parts))
    print('그림 %d개 (문항 기준 %d) · 미해결 %d — /tmp/figs-preview.html' %
          (len(set(map(id, FIGS.values()))), len(FIGS), len(LEFT)))
