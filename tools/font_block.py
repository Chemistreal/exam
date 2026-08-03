#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""바깥 글꼴이 **첫 화면을 인질로 잡는 것**을 푼다.

왜 필요한가
-----------
브라우저는 `<link rel=stylesheet>` 를 만나면 **그리기를 멈추고 기다린다.**
그 stylesheet 가 바깥(구글·CDN)에서 오면, 저쪽이 늦거나 안 닿는 동안 화면은
'글꼴만 못생긴 상태' 가 아니라 **아무것도 없는 흰 종이**다.

재어 보니 이랬다(3G · CPU 4배 느리게, 구글이 대답하지 않는 망).

    index.html   첫 그림  13,184 ms      ← 바깥 글꼴을 기다린다
    hub.html     첫 그림     504 ms      ← 이 줄이 없다
    final.html   첫 그림     584 ms      ← 이 줄이 없다

같은 저장소, 같은 망, 같은 브라우저다. 차이는 그 한 줄뿐이었다.
고친 뒤 index.html 은 **856 ms** 가 됐다.

학원 와이파이·학교 망·통신 장애 어느 하나만 걸려도 학생과 학부모는 빈 화면을
본다. **글꼴 때문에.** 그중에는 학부모가 여는 성적표(report.html·
parent_report.html)도 있다.

무엇을 하나
-----------
    <link rel=stylesheet href="…">
    →
    <link rel=stylesheet media="print" onload="this.media='all'" href="…">
    <noscript><link rel=stylesheet href="…"></noscript>

`media="print"` 이면 브라우저가 '인쇄할 때만 쓰는 것' 으로 보아 **기다리지
않는다.** 다 받은 뒤 `onload` 에서 `media` 를 `all` 로 되돌리니 글꼴은 그대로
온다. 오는 동안에는 대체 글꼴(Noto Sans KR·시스템 글꼴)로 이미 읽힌다.
자바스크립트가 꺼져 있으면 `<noscript>` 로 예전처럼 받는다.

⚠ **글꼴만 미룬다.** 글꼴이 아닌 stylesheet(예: 수식·표 모양을 정하는 CSS)를
  미루면 화면이 한 번 흐트러졌다가 제자리를 찾는다 — 그건 빈 화면보다 나을
  것이 없다. 그래서 주소가 글꼴 창구임이 분명한 것만 손댄다. 새 CDN 이 늘면
  아래 FONTISH 에 사람이 적어 넣어야 한다(자동으로 넓히지 않는다).

    실행:  python3 tools/font_block.py            # 세기만
           python3 tools/font_block.py --write    # 막는 것을 푼다
           python3 tools/font_block.py --check    # 남아 있으면 빨간불
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK = re.compile(r'<link\b[^>]*?>', re.I)
NOSCRIPT = re.compile(r'<noscript>[\s\S]*?</noscript>', re.I)

# 글꼴 창구로 확인한 것만. 사람이 보고 늘린다.
FONTISH = (
    'fonts.googleapis.com',
    'fonts.gstatic.com',
    'cdn.jsdelivr.net/gh/orioncactus/pretendard',   # Pretendard (한글)
)


def attr(name, tag):
    m = re.search(r'\b' + name + r'\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return m.group(1) if m else None


def blocking(tag):
    """이 <link> 가 그리기를 막는 바깥 글꼴인가."""
    if not re.search(r'rel\s*=\s*["\']?stylesheet', tag, re.I):
        return False
    href = attr('href', tag) or ''
    if not re.match(r'https?://|//', href):
        return False                       # 같은 곳에서 오는 것은 기다려도 짧다
    md = (attr('media', tag) or 'all').strip().lower()
    if md != 'all':
        return False                       # 이미 풀어 둔 것
    return any(k in href for k in FONTISH)


def freed(tag):
    """막지 않게 고친 <link> 와, 자바스크립트가 없을 때를 위한 짝."""
    href = attr('href', tag)
    body = tag.rstrip()
    close = '/>' if body.endswith('/>') else '>'
    body = body[:-len(close)].rstrip()
    # media 가 있으면 갈아 끼우고, 없으면 더한다
    if attr('media', body + close):
        body = re.sub(r'\bmedia\s*=\s*["\'][^"\']*["\']', 'media="print"', body, flags=re.I)
    else:
        body += ' media="print"'
    body += ' onload="this.media=\'all\'"'
    one = body + close
    return one + '\n<noscript><link rel="stylesheet" href="' + href + '"></noscript>'


def files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in ('.git', 'node_modules', '__pycache__')]
        for f in sorted(fn):
            if f.endswith('.html'):
                yield os.path.join(dp, f)


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    hit = fixed = 0
    names = []
    for p in files():
        try:
            src = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        # <noscript> 안의 것은 원래 안 막는다 — 자리만 비워 두고 센다
        masked = NOSCRIPT.sub(lambda m: ' ' * len(m.group(0)), src)
        spots = [m for m in LINK.finditer(masked) if blocking(m.group(0))]
        if not spots:
            continue
        hit += len(spots)
        names.append((os.path.relpath(p, ROOT), len(spots)))
        if not write:
            continue
        out = src
        for m in reversed(spots):           # 뒤에서부터 — 앞에서 하면 자리가 밀린다
            out = out[:m.start()] + freed(m.group(0)) + out[m.end():]
            fixed += 1
        open(p, 'w', encoding='utf-8').write(out)

    if write:
        print(f'첫 화면을 막던 글꼴을 풀었다: {fixed}곳')
        return 0
    print(f'그리기를 막는 바깥 글꼴 {hit}곳 · {len(names)}장')
    for n, c in names[:10]:
        print(f'   {n}  {c}곳')
    if len(names) > 10:
        print(f'   … 외 {len(names)-10}장')
    if check and hit:
        print('\nFAIL 바깥 글꼴이 첫 화면을 막고 있다 — '
              'python3 tools/font_block.py --write')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
