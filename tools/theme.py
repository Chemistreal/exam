#!/usr/bin/env python3
"""화면 261장에 **같은 옷**을 입힌다.

왜 필요한가. 팔레트가 261번 따로 적혀 있고, 그러는 동안 값이 갈라졌다.

    --line   8가지  (#E8E4DA 179장 · #e6e2da 54장 · #E6DECF 13장 · …)
    --ink    6가지  (#23201b 181장 · #1a1a1a 54장 · …)
    --teal   5가지  (#0E5A4C 233장 · #0E7A6E 13장 · …)
    --paper  2가지  (#fff 181장 · #F4EFE6 23장)

한 장씩 보면 다 멀쩡하다. 나란히 놓아야 어긋난 게 보이는데, 나란히 놓을
일이 없으니 아무도 몰랐다. 통합 셸에서 탭을 옮겨 다니면 종이색이 미묘하게
바뀐다 — "왜 뭔가 안 맞지" 의 정체다.

**바깥 CSS 파일로 안 뺀다.** 바깥 stylesheet 를 만나면 브라우저는 그리기를
멈추고 기다린다 — 글꼴 한 줄 때문에 첫 화면이 13초였던 일을 겪었다. 대신
이 도구가 화면마다 **같은 조각을 안에 박아 넣고**, CI 가 어긋난 장을 잡는다.

## 넣는 것

1) 팔레트 한 벌 — 갈라진 값을 하나로 모은다
2) 머리띠 — 놋쇠 밑선 · 새겨 넣은 분자 문양 · 다듬은 글자
3) 갈래별 표식 — 개념강의는 놋쇠, 해설지는 옥색, 문제지는 먹, 도구는 쪽빛.
   **한 벌이되 한 벌로만 보이지는 않게** 한다
4) 어디서나 같은 마무리 — 고른 자리 표시 · 초점 테두리 · 표의 숫자 자릿수

## 안 건드리는 것

- `@media print` — 인쇄는 `print_styles.py` 가 맡는다. 새 규칙은 전부
  `@media screen` 안에 넣는다. 안 그러면 뒤에 온 내 규칙이 인쇄 규칙을
  이겨서 **흰 종이에 흰 글씨**가 된다(오늘 겪은 그 모양이다)
- 화면 고유의 짜임새 — 색과 마무리만 손댄다

사용:
    python3 tools/theme.py            # 어떤 장이 어긋나 있나
    python3 tools/theme.py --write    # 입힌다
    python3 tools/theme.py --check    # 어긋난 장이 있으면 빨간불 (CI)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIR = {'.git', 'node_modules', '__pycache__', 'tests'}
MARK = 'ct-theme'
VERSION = '4'

# ── 갈래 ────────────────────────────────────────────────────────────
# 한 벌이되, 어느 갈래의 화면인지는 한눈에 보이게 한다. 밑선 한 줄과
# 머리글 색만 바꾼다 — 그 이상 바꾸면 한 벌로 안 보인다.
FAMILY = (
    ('lec-',    'brass', '개념강의'),
    ('sol-',    'teal',  '해설지'),
    ('paper-',  'ink',   '문제지'),
    ('omr-',    'ink',   'OMR'),
    ('grade-',  'teal',  '채점'),
)
DEFAULT_FAMILY = ('tool', '도구')

ACCENT = {
    'brass': '#AF8B55',
    'teal':  '#3A7A6B',
    'ink':   '#8C8578',
}

# ── 팔레트 한 벌 ────────────────────────────────────────────────────
# 값은 **제일 많이 쓰이던 것**으로 모았다. 소수 쪽을 고른 자리는 없다 —
# 다수결이 아니라 대비를 재서 고른 자리만 다르다(아래 주석 참고).
TOKENS = """--ink:#23201b;--ink-2:#5a564d;--muted:#6f6a5e;
  --line:#E8E4DA;--line-2:#D8D2C4;
  --paper:#fff;--cream:#FBFAF6;--bg:#FBFAF6;--sunk:#F4F1E9;
  --teal:#0E5A4C;--teal-d:#3A7A6B;--wash:#EDF4F1;
  --brass:#B08D57;--gold:#B08D57;
  /* 놋쇠는 두 가지 일을 한다. 밑선·테두리(그림, 3:1)는 밝은 쪽이 예쁘고,
     흰 글씨를 얹는 바탕이나 글자색으로 쓰면 3.09:1 로 못 읽는다.
     그래서 **글자용 놋쇠**를 따로 둔다 — 흰 글씨 위에서 4.95:1. */
  --brass-ink:#8A6B3A;
  --ms:#B8562F;--ok:#2F7A4F;--ok-bg:#eef5f2;
  --serif:"Hahmlet","Nanum Myeongjo",serif;
  --mono:ui-monospace,Menlo,monospace"""

# ── 남의 결을 덮지 않는다 ────────────────────────────────────────────
# 처음에는 팔레트를 통째로 덮었다. 그러다 DT 의 `roster.html` 을 망가뜨렸다 —
# 그 화면은 **일부러 어두운 화면**이라 --ink 가 밝은 글자색(#e9e7e0)이었는데,
# 여기서 어두운 먹색을 씌우자 어두운 바탕에 어두운 글씨가 되어 **1.14:1**,
# 즉 아무것도 안 보이게 됐다.
#
# 하려던 일은 '갈라진 값을 모으는 것' 이지 '다른 설계를 덮는 것' 이 아니다.
# 그래서 **밝기가 크게 다르면 그 이름표는 손대지 않는다.** 조금 어긋난 것은
# 모으고, 다르게 지은 것은 그대로 둔다.
OLD = re.compile(r'<style id="' + MARK + r'"[^>]*>[\s\S]*?</style>\s*', re.I)
HEX = re.compile(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')


def _lum(v):
    """색이면 상대 휘도, 색이 아니면 None."""
    v = v.strip()
    m = HEX.match(v)
    if not m:
        return None
    h = m.group(1)
    if len(h) == 3:
        h = h[0] * 2 + h[1] * 2 + h[2] * 2
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


LIGHT_GAP = 0.22          # 이보다 밝기가 벌어지면 다른 설계로 본다


def own_tokens(src):
    """이 화면이 스스로 적어 둔 :root 값들."""
    out = {}
    for r in re.finditer(r':root\s*\{([^}]*)\}', src):
        for m in re.finditer(r'--([a-z0-9-]+)\s*:\s*([^;}]+)', r.group(1)):
            out.setdefault(m.group(1), m.group(2).strip())
    return out


def tokens_for(src):
    """이 화면에 넣을 팔레트. 밝기가 크게 다른 이름표는 빼고 돌려준다."""
    own = own_tokens(src)
    keep, dropped = [], []
    for part in TOKENS.replace('\n', ' ').split(';'):
        part = part.strip()
        if not part or ':' not in part:
            continue
        name, val = part.split(':', 1)
        name = name.strip().lstrip('-')
        mine, theirs = _lum(val), _lum(own.get(name, ''))
        if mine is not None and theirs is not None and abs(mine - theirs) > LIGHT_GAP:
            dropped.append(name)
            continue
        keep.append(part)
    return ';'.join(keep), dropped


BODY_RULE = re.compile(r'(?:^|[}\n;])\s*(?:html\s*,\s*)?body\s*\{([^}]*)\}', re.I)
STYLES = re.compile(r'<style[^>]*>([\s\S]*?)</style>', re.I)
HAS_IMG = re.compile(r'background(-image)?\s*:[^;]*(gradient|url\()', re.I)


def has_body_image(src):
    """이 화면이 이미 제 배경 그림을 가지고 있는가.

    KMChC 는 종이 위에 옅은 빛 무리(radial-gradient) 두 겹을 깔아 두었다.
    거기에 벤젠 고리를 얹으면 background-image 를 통째로 갈아 끼우게 되어
    **원래 있던 빛 무리가 사라진다.** 어두운 화면을 안 덮는 것과 같은 이유로,
    이미 제 그림이 있는 화면에는 표식을 안 얹는다.

    ⚠ 처음에는 글 전체에서 `body … { … background … url(` 를 찾았다. 그러자
      자바스크립트 안의 중괄호까지 걸려서, 멀쩡한 화면 여덟 장에 표식이 안
      깔렸다. 이제 **<style> 안의 body 규칙만** 본다. 내가 넣은 조각은 뺀다.
    """
    body = OLD.sub('', src)
    for css in STYLES.findall(body):
        for m in BODY_RULE.finditer(css):
            if HAS_IMG.search(m.group(1)):
                return True
    return False


def is_dark(src):
    """스스로 어두운 화면으로 지은 곳인가. 여백의 표식도 여기서는 안 깐다."""
    own = own_tokens(src)
    for k in ('bg', 'paper', 'card', 'panel', 'surface'):
        L = _lum(own.get(k, ''))
        if L is not None and L < 0.18:
            return True
    return False


# 머리띠 안에 새겨 넣는 분자 문양. 가로로 이어 붙는다.
# ⚠ 색을 **어둡게만** 쓴다. 밝은 선을 얹으면 띠가 밝아져서 그 위의 글씨
#   대비가 내려간다 — 문양 하나 때문에 읽히는 것을 내주지 않는다.
#   어둡게 새기면 대비는 오히려 올라간다.
GUILLOCHE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='104'"
    " viewBox='0 0 200 104'%3E%3Cg fill='none' stroke='%23000' stroke-width='2'"
    " stroke-linecap='round' opacity='0.20'%3E"
    "%3Cpath d='M0 72 L25 38 L50 72 L75 38 L100 72 L125 38 L150 72 L175 38 L200 72'/%3E"
    "%3Cpath d='M25 38 L25 15 M75 38 L75 15 M125 38 L125 15 M175 38 L175 15'/%3E"
    "%3C/g%3E%3Cg fill='%23000' opacity='0.17'%3E"
    "%3Ccircle cx='25' cy='38' r='6'/%3E%3Ccircle cx='75' cy='38' r='6'/%3E"
    "%3Ccircle cx='125' cy='38' r='6'/%3E%3Ccircle cx='175' cy='38' r='6'/%3E"
    "%3Ccircle cx='50' cy='72' r='6'/%3E%3Ccircle cx='100' cy='72' r='6'/%3E"
    "%3Ccircle cx='150' cy='72' r='6'/%3E%3Ccircle cx='0' cy='72' r='6'/%3E"
    "%3Ccircle cx='200' cy='72' r='6'/%3E"
    "%3Ccircle cx='25' cy='15' r='3.4'/%3E%3Ccircle cx='75' cy='15' r='3.4'/%3E"
    "%3Ccircle cx='125' cy='15' r='3.4'/%3E%3Ccircle cx='175' cy='15' r='3.4'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

# 문양은 **가운데를 비운다.** 제목이 앉는 자리에 무늬가 깔리면 글자 획과
# 무늬 선이 섞여 읽기가 나빠진다. 가장자리에서만 보이게 가린다.
GUI_MASK = ('radial-gradient(ellipse 62% 130% at 50% 50%,'
            'rgba(0,0,0,0) 0%,rgba(0,0,0,0) 42%,#000 100%)')


# 화면 오른쪽 여백에 크게 새겨 넣는 벤젠 고리. **글 뒤가 아니라 여백**에
# 앉도록 오른쪽 바깥으로 밀어 두었다. 아주 옅다(선 불투명도 0.055) —
# 재어 보니 글자 대비가 0.01 도 안 움직인다. 그래도 좁은 화면에서는 끈다.
SEAL = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='520' height='560'"
    " viewBox='0 0 520 560'%3E%3Cg fill='none' stroke='%230E5A4C' stroke-width='9'"
    " stroke-linejoin='round' opacity='0.055'%3E"
    "%3Cpath d='M260 60 L433 160 L433 360 L260 460 L87 360 L87 160 Z'/%3E"
    "%3Cpath d='M260 120 L381 190 L381 330 L260 400 L139 330 L139 190 Z'/%3E"
    "%3Cpath d='M260 60 L260 0 M433 160 L485 130 M433 360 L485 390"
    " M260 460 L260 520 M87 360 L35 390 M87 160 L35 130'/%3E%3C/g%3E"
    "%3Cg fill='%230E5A4C' opacity='0.05'%3E"
    "%3Ccircle cx='260' cy='60' r='17'/%3E%3Ccircle cx='433' cy='160' r='17'/%3E"
    "%3Ccircle cx='433' cy='360' r='17'/%3E%3Ccircle cx='260' cy='460' r='17'/%3E"
    "%3Ccircle cx='87' cy='360' r='17'/%3E%3Ccircle cx='87' cy='160' r='17'/%3E"
    "%3C/g%3E%3C/svg%3E"
)

# 머리글 밑에 긋는 가늘어지는 선. **이미 밑선이 있는 화면에는 안 긋는다** —
# 두 줄이 겹치면 고친 게 아니라 지저분해진 것이다.
HAIRLINE = re.compile(r'header\s*\{[^}]*border-bottom', re.I)


def block(family, accent, band, rule, tokens, seal):
    """이 화면에 박아 넣을 조각."""
    a = ACCENT[accent]
    css = [
        '/* 이 조각은 tools/theme.py 가 넣습니다. 손으로 고치지 마세요 —',
        '   다음 실행에서 덮어써집니다. 색을 바꾸려면 그 파일을 고치세요. */',
        ':root{' + tokens + '}',
        'html{color-scheme:light;-webkit-text-size-adjust:100%}',
        '@media screen{',
        '  body{-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}',
        # 고른 자리·초점. 어느 화면에서나 같은 손맛이 나야 한 벌로 느껴진다.
        '  ::selection{background:#0E5A4C26}',
        '  :focus-visible{outline:2px solid ' + a + ';outline-offset:2px;border-radius:3px}',
        # 표의 숫자는 자릿수를 맞춘다. 점수·인원이 세로로 안 맞으면 눈으로 세게 된다.
        '  table{font-variant-numeric:tabular-nums}',
        '  hr{border:0;border-top:1px solid var(--line)}',
        # 오른쪽 여백에 앉는 벤젠 고리. 글 폭이 좁아지는 화면에서는 끈다 —
        # 여백이 없어지면 글 뒤로 들어온다.
    ]
    if seal:
        css.append(
            '  @media (min-width:1080px){body{'
            'background-image:url("' + SEAL + '");'
            'background-repeat:no-repeat;background-attachment:fixed;'
            'background-position:right -110px top 90px;background-size:520px 560px}}')
    if band:
        css += [
            # 머리띠 — 놋쇠 밑선과 새겨 넣은 문양.
            '  header{position:relative;overflow:hidden;'
            'background:#0E5A4C linear-gradient(135deg,#0E5A4C 0%,#0B4238 100%);'
            'border-bottom:2px solid ' + a + '}',
            "  header::after{content:'';position:absolute;inset:0;pointer-events:none;"
            'background-image:url("' + GUILLOCHE + '");'
            'background-size:200px 104px;background-position:center;'
            '-webkit-mask-image:' + GUI_MASK + ';mask-image:' + GUI_MASK + '}',
            '  header>*{position:relative;z-index:1}',
            '  header .logo{letter-spacing:.18em;font-weight:600;opacity:.92}',
            '  header h1{letter-spacing:-.01em}',
            '  header .sub{letter-spacing:.01em}',
        ]
    else:
        # 띠가 없는 화면(해설지 · 문제지 · 목록)은 머리글이 종이 위에 얹혀
        # 있다. 갈래 색으로 가늘어지는 선 하나를 그어 어디까지가 머리인지
        # 눈에 걸리게 한다.
        css += [
            '  header .logo{letter-spacing:.16em;font-weight:700}',
        ]
        if rule:
            css.append(
                "  header::after{content:'';display:block;height:3px;margin-top:16px;"
                'border-radius:2px;background:linear-gradient(90deg,' + a + ' 0%,'
                + a + '66 34%,' + a + '00 76%)}')
    css.append('}')
    return ('<style id="' + MARK + '" data-v="' + VERSION + '" data-fam="' + family +
            '" data-seal="' + ('1' if seal else '0') + '">'
            + '\n'.join(css) + '</style>')


def files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIR]
        for f in sorted(fn):
            if f.endswith('.html'):
                yield os.path.join(dp, f)


BAND = re.compile(r'header\s*\{[^}]*linear-gradient\(\s*180deg\s*,\s*#0E5A4C', re.I)
HEADEND = re.compile(r'</head\s*>', re.I)


def plan(path, src):
    name = os.path.basename(path)
    fam, _label = DEFAULT_FAMILY[0], DEFAULT_FAMILY[1]
    accent = 'teal'
    for pre, acc, _lab in FAMILY:
        if name.startswith(pre):
            fam, accent = pre.rstrip('-'), acc
            break
    # 머리띠는 **그 화면이 이미 옥색 띠를 그리고 있을 때만** 손댄다.
    # 해설지처럼 흰 머리를 쓰는 화면에 띠를 씌우면 짜임새가 깨진다.
    css = src.split('</style>')[0] if '</style>' in src else src
    band = bool(BAND.search(css))
    tokens, _dropped = tokens_for(src)
    return block(fam, accent, band, not band and not HAIRLINE.search(css),
                 tokens, not is_dark(src) and not has_body_image(src))


def apply(src, want):
    out = OLD.sub('', src)
    m = HEADEND.search(out)
    if not m:
        return None                       # <head> 가 없는 조각 파일 — 건드리지 않는다
    return out[:m.start()] + want + '\n' + out[m.start():]


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    off, done, skip = [], 0, 0
    for p in files():
        try:
            src = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        want = plan(p, src)
        new = apply(src, want)
        if new is None:
            skip += 1
            continue
        if new == src:
            done += 1
            continue
        off.append(os.path.relpath(p, ROOT))
        if write:
            open(p, 'w', encoding='utf-8').write(new)

    if write:
        print('같은 옷을 입혔다: ' + str(len(off)) + '장 (이미 맞던 것 ' + str(done) + '장)')
        return 0
    print('맞는 장 ' + str(done) + ' · 어긋난 장 ' + str(len(off)) +
          (' · <head> 가 없어 건너뛴 것 ' + str(skip) if skip else ''))
    if off:
        for f in off[:12]:
            print('   ' + f)
        if len(off) > 12:
            print('   … 외 ' + str(len(off) - 12) + '장')
    if check and off:
        print('\nFAIL 옷이 안 맞는 장이 있습니다 — python3 tools/theme.py --write')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
