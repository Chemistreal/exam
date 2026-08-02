#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""화면을 한 줄씩 재는 자.

왜 필요한가
-----------
"좀 흐린가?" 로는 아무것도 안 고쳐진다. 이번 작업에서 실제로 고친 것은 전부
**재고 나서** 나왔다 — 통합 셸의 --muted 3.52:1, DT 성적표의 9px 글씨,
파이널과 셸의 팔레트가 갈린 것. 눈으로는 셋 다 안 보였다.

화면이 419개다. 손으로 다 볼 수 없으니 기계가 매번 본다. 여기서 재는 것은
**사람이 판단할 필요가 없는 것들**뿐이다 — 화학 내용의 옳고 그름은 사람이 본다.

    실행:  python3 tools/audit_pages.py [경로...]     # 기본: 이 저장소
           python3 tools/audit_pages.py --tier a      # 매일 여는 화면만
"""
import os, re, sys, json, math, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 사람이 매일 여는 화면(A) · 학부모·학생에게 나가는 화면(B)
TIER_A = {'hub.html', 'final.html', 'index.html', 'lecture-index.html'}
TIER_B = {'final-submit.html'}

MIN_FONT = 11.5          # 학부모가 휴대폰으로 읽는다
AA_TEXT, AA_BIG, AA_UI = 4.5, 3.0, 3.0


def lum(hexv):
    h = hexv.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def ratio(a, b):
    x, y = lum(a), lum(b)
    return (max(x, y) + 0.05) / (min(x, y) + 0.05)


HEX = re.compile(r'#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b')
VAR = re.compile(r'--([a-zA-Z0-9-]+)\s*:\s*(#[0-9A-Fa-f]{3,6})')
FONT = re.compile(r'font-size:\s*(\d+(?:\.\d+)?)px')


def audit(path):
    """한 화면에서 사람 판단이 필요 없는 결함만 모은다."""
    try:
        s = open(path, encoding='utf-8', errors='ignore').read()
    except Exception as e:
        return [('읽기 실패', str(e))]
    out = []
    name = os.path.basename(path)

    # ── 뼈대 ──────────────────────────────────────────────
    if not re.search(r'<html[^>]*\blang=', s):
        out.append(('lang 없음', '화면 낭독기가 어느 말인지 모른다'))
    if not re.search(r'<meta[^>]*name=["\']viewport', s):
        out.append(('viewport 없음', '휴대폰에서 데스크톱 폭으로 그려진다'))
    if not re.search(r'<meta[^>]*charset', s):
        out.append(('charset 없음', '한글이 깨질 수 있다'))
    if not re.search(r'<title>\s*\S', s):
        out.append(('title 없음', '탭·즐겨찾기·공유에 이름이 안 뜬다'))

    # ── 글자 크기 ─────────────────────────────────────────
    small = [float(x) for x in FONT.findall(s) if float(x) < MIN_FONT]
    if small:
        out.append(('작은 글씨 %d곳' % len(small),
                    '가장 작은 %.1fpx (바닥 %.1fpx)' % (min(small), MIN_FONT)))

    # ── 팔레트 대비 ───────────────────────────────────────
    vs = dict(VAR.findall(s))
    bgs = [v for k, v in vs.items()
           if re.search(r'paper|bg|cream|surface|white|card', k, re.I) and lum(v) > .5]
    if not bgs:
        bgs = ['#FFFFFF']
    fgs = [(k, v) for k, v in vs.items()
           if re.search(r'ink|text|sub|muted|faint|fg', k, re.I)]
    for k, v in fgs:
        worst = min(ratio(v, b) for b in bgs)
        if worst < AA_TEXT:
            out.append(('--%s 대비 %.2f:1' % (k, worst), '본문 글씨는 %.1f:1 필요' % AA_TEXT))

    # ── 손가락 자리 ───────────────────────────────────────
    tiny = re.findall(r'padding:\s*[0-3]px\s+\d+px[^;}]*;[^}]*font-size:\s*(?:[0-9.]+)px', s)
    if len(tiny) > 3:
        out.append(('좁은 단추 %d곳' % len(tiny), '손가락 자리는 32px 이상이 좋다'))

    # ── 안전장치 ─────────────────────────────────────────
    # ⚠ 이 자는 두 번 거짓말을 했다. 처음엔 `[^;]*` 가 여러 줄을 건너뛰어
    # esc() 를 제대로 쓴 자리를 잡았고, 고친 뒤에도 문장 뒤쪽의 엉뚱한 .name 을
    # 잡았다. 잘못 재는 자는 안 재느니만 못하다 — 사람이 경고를 무시하게 되고,
    # 그러면 진짜가 와도 안 본다. 글자를 이어 붙이는 자리만 본다: '…'+r.name+'…'
    # 한 번 더: 클립보드에 넣는 그냥 글자('── ' + r.name)까지 잡으면 또 거짓말이다.
    # 바로 앞 따옴표 안에 태그(<)가 있는 자리 — 즉 HTML 을 잇는 자리만 본다.
    RAW = re.compile(r"<[^'\"]{0,80}['\"]\s*\+\s*(?!esc\()[A-Za-z_$][\w$.]*\.(?:name|school)\s*\+")
    if RAW.search(s):
        out.append(('이름을 그대로 붙임', "esc() 없이 '…'+이름+'…' 로 잇는 자리가 있다"))
    return out


def tier_of(name):
    if name in TIER_A:
        return 'A'
    if name in TIER_B:
        return 'B'
    if re.match(r'(paper|sol|munje|haeseol|omr)[-_]', name):
        return 'C'
    return 'B'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--tier'):
            only = sys.argv[sys.argv.index(a) + 1].upper()
    roots = args or [ROOT]
    files = []
    for r in roots:
        if os.path.isfile(r):
            files.append(r)
        else:
            for f in sorted(os.listdir(r)):
                if f.endswith('.html'):
                    files.append(os.path.join(r, f))
    rows, byKind = [], collections.Counter()
    for f in files:
        t = tier_of(os.path.basename(f))
        if only and t != only:
            continue
        d = audit(f)
        for what, why in d:
            byKind[re.sub(r'\d+', 'N', what)] += 1
        if d:
            rows.append((t, os.path.basename(f), d))
    rows.sort(key=lambda x: (x[0], -len(x[2])))
    for t, n, d in rows[:40]:
        print('[%s] %-30s %d건' % (t, n, len(d)))
        for what, why in d[:4]:
            print('        %-26s %s' % (what, why))
    print('\n── 결함 갈래별 ──')
    for k, v in byKind.most_common(14):
        print('  %-30s %d' % (k, v))
    print('\n화면 %d개 · 결함 있는 화면 %d개' % (len(files), len(rows)))


if __name__ == '__main__':
    main()
