#!/usr/bin/env python3
"""화면 안 CSS 가 **닫혀 있는가**.

2026-08-14 에 있었던 일
-----------------------
허브에서 3D 를 걷어내다가 `.brand h1{` 을 **첫 줄만 남기고** 이어지는 줄을
같이 지웠다. 규칙 하나가 안 닫힌 채로 남았고, 브라우저는 그 뒤 CSS 를 통째로
버렸다 — `.pane{display:none}` 이 사라져 **탭 열두 개가 한꺼번에 펼쳐졌다.**

한 글자였고, 화면 전체가 무너졌다.

그때 이 저장소에 있던 자들
--------------------------
  · `tools/js_syntax.py`     — 자바스크립트가 깨졌나  → 통과
  · `tools/theme.py`         — 색이 규칙대로인가      → 통과
  · `tools/print_styles.py`  — 인쇄 규칙이 있나       → 통과
  · `tests/*.js`             — 화면이 도는가          → **못 돌렸다**(느리다)

**CSS 가 문법으로 성한지 보는 자는 없었다.** 자바스크립트는 보면서 CSS 는 안
봤다. 자가 못 본 것과 거기 없는 것은 다르다 — 이건 없던 쪽이다.

여기서 보는 것
--------------
`<style>` 안에서 중괄호가 맞는지만 본다. 색·이름·쓰임새는 안 본다(그건 다른
자들 몫이다). **한 글자짜리 사고가 화면 전체를 먹는 자리**만 지킨다.

  · 여는 것과 닫는 것의 수가 같은가
  · 중간에 음수로 내려가지 않는가 (`}` 가 먼저 오는 것)
  · 주석이 닫혀 있는가 (`/*` 만 있고 `*/` 가 없으면 뒤가 통째로 먹힌다)

실행:
    python3 tools/css_syntax.py            # 어디가 안 닫혔나
    python3 tools/css_syntax.py --check    # 하나라도 있으면 종료 코드 1
"""

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STYLE = re.compile(r'<style[^>]*>(.*?)</style>', re.S)


def strip_comments(css):
    """주석을 지우되 **줄 수는 지킨다** — 줄 번호를 그대로 짚으려고."""
    return re.sub(r'/\*.*?\*/', lambda m: '\n' * m.group(0).count('\n'), css, flags=re.S)


def scan_one(path):
    src = io.open(path, encoding='utf-8').read()
    bad = []
    for m in STYLE.finditer(src):
        css = m.group(1)
        base = src[:m.start(1)].count('\n') + 1        # 이 조각의 첫 줄 번호

        # ① 주석이 안 닫혔나 — 이게 있으면 뒤 계산이 다 헛것이다
        opens = len(re.findall(r'/\*', css))
        closes = len(re.findall(r'\*/', css))
        if opens != closes:
            bad.append((path, base, '주석이 안 닫혔다 (/* %d개 · */ %d개)' % (opens, closes)))
            continue

        c = strip_comments(css)
        depth, stack = 0, []
        for i, line in enumerate(c.split('\n')):
            for ch in line:
                if ch == '{':
                    stack.append(base + i)
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth < 0:
                        bad.append((path, base + i, '닫는 } 가 여는 { 보다 먼저 왔다'))
                        depth = 0
                    elif stack:
                        stack.pop()
        for ln in stack:
            line = src.split('\n')[ln - 1].strip()
            bad.append((path, ln, '안 닫힌 { — ' + line[:58]))
    return bad


def main():
    check = '--check' in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, '*.html')))
    bad, n = [], 0
    for f in files:
        try:
            src = io.open(f, encoding='utf-8').read()
        except OSError:
            continue
        if '<style' not in src:
            continue
        n += 1
        bad += scan_one(f)

    print('화면 %d장의 CSS 를 봤다 · 안 닫힌 자리 %d곳' % (n, len(bad)))
    if bad:
        print()
        for path, ln, why in bad[:40]:
            print('  %s:%d  %s' % (os.path.relpath(path, ROOT), ln, why))
        print('\n⚠ 안 닫힌 규칙 하나면 브라우저가 **그 뒤 CSS 를 통째로 버린다.**')
        print('  허브에서는 .pane{display:none} 이 날아가 탭이 한꺼번에 펼쳐졌다.')
        if check:
            print('\nFAIL')
            return 1
        return 0
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
