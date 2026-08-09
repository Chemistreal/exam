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
import os, re, sys, json, math, collections, urllib.parse

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
LINK = re.compile(r'(?:href|src)\s*=\s*["\']([^"\'#?][^"\']*)["\']')


def audit(path):
    """한 화면에서 사람 판단이 필요 없는 결함만 모은다."""
    try:
        s = open(path, encoding='utf-8', errors='ignore').read()
    except Exception as e:
        return [('읽기 실패', str(e))]
    out = []
    name = os.path.basename(path)

    # ⚠ 여덟 번째 거짓말. **조각 파일**에 한 장의 뼈대를 요구했다.
    #   study64-report 의 `eng2p/app/body/*.html` 은 합쳐져서 한 화면이 되는
    #   토막인데, lang·viewport·charset·title 이 없다고 열여덟 장을 걸었다.
    #   토막에 <title> 을 넣으면 오히려 합친 화면에 제목이 여럿 생긴다.
    #   <html> 이 없으면 한 장이 아니다 — 뼈대는 합쳐지는 쪽에서 본다.
    #   그리고 <html> 을 **여는** 토막도 있다(00_head.html) — 닫는 </html> 는
    #   다른 토막에 있다. 여는 것만 보고 한 장이라고 하면 그 토막에 <h1> 이
    #   없다고 걸린다. 한 장은 열고 **닫기까지** 한 것이다.
    if not (re.search(r'<html[\s>]', s) and '</html>' in s):
        return []

    # ── 뼈대 ──────────────────────────────────────────────
    if not re.search(r'<html[^>]*\blang=', s):
        out.append(('lang 없음', '화면 낭독기가 어느 말인지 모른다'))
    if not re.search(r'<meta[^>]*name=["\']viewport', s):
        out.append(('viewport 없음', '휴대폰에서 데스크톱 폭으로 그려진다'))
    if not re.search(r'<meta[^>]*charset', s):
        out.append(('charset 없음', '한글이 깨질 수 있다'))
    if not re.search(r'<title>\s*\S', s):
        out.append(('title 없음', '탭·즐겨찾기·공유에 이름이 안 뜬다'))
    # 낭독기는 "이 화면이 무엇인가" 를 제목 단계로 읽는다. h3 부터 시작하면
    # 위에 뭔가 더 있다고 착각한다. 눈에 보이는 제목은 있는데 <h1> 만 없던
    # 화면이 DT 에 134장 있었다(해설지·문제지·OMR 전부).
    if not re.search(r'<h1[\s>]', s):
        out.append(('h1 없음', '화면 낭독기가 무엇에 관한 화면인지 못 읽는다'))
    # <th>과목</th><td>화학</td> 같은 줄에서 scope 가 없으면, 낭독기가 값을
    # 읽을 때 어느 머리에 딸린 값인지 말해 주지 못한다.
    noscope = re.findall(r'<th\b(?![^>]*\bscope=)', s)
    if noscope:
        out.append(('표 머리에 scope 없음 %d곳' % len(noscope),
                    '낭독기가 어느 칸의 머리인지 모른다'))

    # ── 글자 크기 ─────────────────────────────────────────
    small = [float(x) for x in FONT.findall(s) if float(x) < MIN_FONT]
    if small:
        out.append(('작은 글씨 %d곳' % len(small),
                    '가장 작은 %.1fpx (바닥 %.1fpx)' % (min(small), MIN_FONT)))

    # ── 팔레트 대비 ───────────────────────────────────────
    # ⚠ 이 자가 세 번째로 거짓말을 한 자리. 예전에는 **밝은** 바탕만 골랐고,
    # 못 고르면 흰색으로 쳤다. 그래서 어두운 화면(minimalism/index.html:
    # --bg #060817 위 흰 글씨)에서 흰 글씨를 흰 바탕에 얹어 재고 1.04:1 이라고
    # 했다 — 실제로는 가장 잘 읽히는 화면이다.
    # 그 장이 밝은 화면인지 어두운 화면인지 먼저 정하고, **그 쪽 바탕**으로 잰다.
    vs = dict(VAR.findall(s))
    # ⚠ 네 번째 거짓말. 이름에 'bg' 가 들어가면 다 바탕으로 쳤다. 그래서
    # --ok-bg(맞은 문항의 연둣빛 띠), --ms-bg, --warn-bg 같은 **상태 색**까지
    # 바탕이 되었고, 거기에 아무 글자색이나 얹어 재고는 모자란다고 했다.
    # --brass-ink 하나가 --ok-bg 위에서 4.47 이라는 이유로 262장 가운데
    # **261장**이 빨간불이었다. 그런 자리는 화면에 없다.
    # 바탕은 **이름 그 자체가 바탕인 것**만 친다. 'ok-bg' 처럼 앞에 무언가
    # 붙은 것은 그 색의 옅은 띠지 종이가 아니다.
    # ⚠ 여섯 번째 거짓말. 이름을 **그대로** 맞춰 보느라 번호 붙은 바탕을
    #   못 알아봤다 — study64-report/index.html 은 --bg0 #040612 인 어두운
    #   화면인데, bg0 가 목록에 없어 바탕이 하나도 없는 것으로 보고 흰 종이로
    #   쳤다. 그래서 그 화면의 흰 글씨(--text #f7fbff)를 1.04:1 이라고 했다.
    #   (세 번째 거짓말과 같은 종류다. 이번엔 이름 끝의 숫자 때문이었다.)
    SURFACE = {'bg', 'paper', 'cream', 'surface', 'card', 'sunk', 'page',
               'white', 'canvas', 'panel'}
    allbg = [v for k, v in vs.items()
             if re.sub(r'\d+$', '', k.lower()) in SURFACE]
    dark_page = bool(allbg) and sum(1 for v in allbg if lum(v) <= .5) > len(allbg) / 2
    bgs = [v for v in allbg if (lum(v) <= .5) == dark_page]
    if not bgs:
        bgs = ['#000000'] if dark_page else ['#FFFFFF']
    fgs = [(k, v) for k, v in vs.items()
           if re.search(r'ink|text|sub|muted|faint|fg', k, re.I)]
    for k, v in fgs:
        # --brand-ink 는 종이가 아니라 --brand-bg 위에 얹힌다. 짝이 있으면
        # 그 짝 위에서 잰다 — 안 그러면 hub 의 크림색 제목을 흰 종이에 얹어
        # 재고 1.00:1 이라고 한다(실제로는 가장 잘 읽히는 자리다).
        stem = re.sub(r'[-_]?(ink|text|sub|muted|faint|fg)\d*$', '', k, flags=re.I)
        pair = [w for kk, w in vs.items() if stem and re.fullmatch(
            re.escape(stem) + r'[-_]?bg\d*', kk, re.I)]
        # ⚠ 아홉 번째. 한 파일에 밝은 팔레트와 어두운 팔레트가 **둘 다** 있는
        #   화면이 있다(DT roster.html — --bg #0f1216 인데 --paper #FAFAF7 도
        #   갖고 있다). 다수결로 한쪽을 고르면 반대쪽 글자색이 통째로 거짓
        #   경고가 된다(--ink 1.07:1 이라고 했다 · 실제 15.17:1). 밝기로
        #   짝지어도 **중간 회색**에서 깨진다(--muted #9aa0a8 은 어두운 바탕에서
        #   7.12, 흰 바탕에서 2.52 — 어느 쪽으로 붙여도 한쪽은 틀린다).
        #
        #   여기서 멈추고 사실을 적는다: 글자색이 어느 바탕에 얹히는지는 CSS
        #   글만 보고 알 수 없다. 그래서 **이 화면이 가진 바탕 어느 하나에서도**
        #   4.5 를 못 넘을 때만 결함으로 센다. "이 화면 어디에 놓아도 안 읽힌다"
        #   는 사람 판단이 필요 없는 사실이다.
        best = max(ratio(v, b) for b in (pair or allbg or bgs))
        if best < AA_TEXT:
            out.append(('--%s 대비 %.2f:1' % (k, best), '어느 바탕에서도 %.1f:1 미만' % AA_TEXT))

    # ── 손가락 자리 ───────────────────────────────────────
    # ⚠ 일곱 번째 거짓말. 작고 여백 좁은 것을 전부 '단추' 로 쳤다. 그런데
    #   `.qdGapPill` · `.prRel` 같은 것은 **누르는 자리가 아니라 표시용 딱지**다.
    #   손가락이 닿을 일이 없는 것에 손가락 자리를 요구하면, 사람은 그 경고를
    #   무시하는 법부터 배운다. 규칙 이름이 **누르는 것**을 가리킬 때만 센다.
    TAPPY = re.compile(r'(btn|button|\btab\b|chip|link|nav|menu|toggle|pill-?btn|'
                       r'\ba[:.]|cursor:\s*pointer)', re.I)
    tiny = []
    for m in re.finditer(r'([^{}]{0,120})\{([^}]*padding:\s*[0-3]px\s+\d+px[^}]*'
                         r'font-size:\s*[0-9.]+px[^}]*)\}', s):
        sel, body = m.group(1), m.group(2)
        if TAPPY.search(sel) or 'cursor:pointer' in body.replace(' ', ''):
            tiny.append(sel.strip()[-40:])
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

    # ── 없는 곳으로 가는 링크 ─────────────────────────────
    # 눌러 보고 나서야 안다. 네 저장소를 훑어 보니 지금은 하나도 없는데,
    # 없을 때 걸어 두어야 새로 생기는 것을 잡는다.
    # ⚠ 만들어 넣는 주소(`'sol-final-'+esc(id)+'.html'`)는 정적으로 확인할 수
    #   없다. 정규식이 앞토막만 잘라 오므로 **뒤에 + 가 붙었는지**로 가른다 —
    #   이걸 안 가르면 멀쩡한 자리를 두 개 잡는다(실제로 그랬다).
    here = os.path.dirname(os.path.abspath(path))
    dead = []
    for m in LINK.finditer(s):
        u = m.group(1).strip()
        if u.startswith(('http://', 'https://', 'data:', 'mailto:', 'tel:',
                         'javascript:', '//', 'blob:')):
            continue
        if '${' in u or '{{' in u:
            continue
        if s[m.end():m.end() + 3].lstrip().startswith('+'):
            continue
        rel = urllib.parse.unquote(u.split('?')[0].split('#')[0])
        if not rel:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(here, rel))):
            dead.append(u)
    if dead:
        out.append(('없는 곳으로 가는 링크 %d개' % len(dead),
                    '눌러 보고 나서야 안다 — ' + ', '.join(sorted(set(dead))[:3])))
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
            continue
        # 하위 폴더까지 본다. 여기 앱은 premium/ · v2/ 처럼 판이 폴더로 나뉜다 —
        # 위층만 보면 그 둘은 아무도 안 재는 화면이 된다.
        for dirpath, dirnames, names in os.walk(r):
            dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '__pycache__')]
            for f in sorted(names):
                if f.endswith('.html'):
                    files.append(os.path.join(dirpath, f))
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
    # 지금 0장이다. 0 을 자물쇠로 걸어 두어야 다음에 하나라도 생기면 걸린다 —
    # 261장이던 시절에는 아무도 안 봤다.
    return 1 if ('--check' in sys.argv and rows) else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
