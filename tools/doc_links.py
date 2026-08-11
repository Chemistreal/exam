#!/usr/bin/env python3
"""문서에 적은 **다른 문서 이름이 눌러서 열리는지** 본다.

왜 이 자가 있나
---------------
2026-08-10, 선생님 말씀.

    "docs/성적표를-읽는-사람.md 라고만 적지말고 링크를 해줘야 읽어"

맞는 말이다. 나는 파일 이름을 적어 놓고 읽으실 거라고 생각했다. 선생님은
휴대폰으로 보시는데, 그건 **그냥 글자**다. 눌러도 아무 일도 안 난다.

문서끼리도 같았다 — 여덟 문서가 서로를 백틱 안 글자로만 부르고 있었다.
스물한 곳을 링크로 바꿨다.

무엇을 보나
-----------
  ① 백틱 안에 `docs/무엇.md` 라고만 적힌 곳 — 눌러도 안 열린다
  ② 링크로 걸어 놓았는데 **그 파일이 없는** 곳 — 눌렀는데 404 다

②가 ①보다 나쁘다. ①은 안 열리는 줄 알지만, ②는 열릴 줄 알고 눌렀다가
빈손이 된다. **안 한 것만 못하다.**

⚠ 이 자는 글의 좋고 나쁨을 안 본다. **닿는지만 본다.**

    python3 tools/doc_links.py           # 어디가 글자로만 있나
    python3 tools/doc_links.py --check   # 안 열리는 링크가 있으면 빨간불
"""
import glob
import os
import re
import sys
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINK = re.compile(r'\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)')
BARE = re.compile(r'`(docs/[^`]+\.md)`')


def files():
    out = sorted(glob.glob(os.path.join(ROOT, 'docs', '*.md')))
    rd = os.path.join(ROOT, 'README.md')
    if os.path.exists(rd):
        out.append(rd)
    return out


def main():
    check = '--check' in sys.argv
    dead, bare, total = [], [], 0

    for path in files():
        rel = os.path.relpath(path, ROOT)
        base = os.path.dirname(path)
        try:
            s = open(path, encoding='utf-8').read()
        except OSError:
            continue

        for m in LINK.finditer(s):
            t = m.group(1)
            if t.startswith(('http://', 'https://', 'mailto:')):
                continue
            total += 1
            p = os.path.normpath(os.path.join(base, urllib.parse.unquote(t)))
            if not os.path.exists(p):
                dead.append((rel, t))

        for m in BARE.finditer(s):
            # 정말 있는 문서를 글자로만 적어 둔 것. 없는 파일 이름이면 링크가
            # 아니라 그냥 옛 이름이므로 여기서 안 센다(그건 ②가 잡는다).
            if os.path.exists(os.path.join(ROOT, m.group(1))):
                bare.append((rel, m.group(1)))

    print('문서 %d개 · 저장소 안 링크 %d개' % (len(files()), total))

    if bare:
        print('\n□ 눌러도 안 열리는 이름 %d곳 (있는 문서인데 글자로만 적혔다)'
              % len(bare))
        for rel, t in bare[:12]:
            print('  %-30s %s' % (rel, t))

    if dead:
        print('\n⚠ 걸어 놓았는데 **안 열리는** 링크 %d곳' % len(dead))
        for rel, t in dead:
            print('  %-30s %s' % (rel, urllib.parse.unquote(t)))
        print('\n열릴 줄 알고 눌렀다가 빈손이 되는 것은 안 건 것만 못하다.')
        if check:
            print('\nFAIL')
            return 1
        return 0

    if bare:
        print('\n안 열리는 링크는 없다. 위 %d곳은 링크로 바꾸면 눌러서 열린다.'
              % len(bare))
    else:
        print('\n적어 둔 문서 이름이 모두 눌러서 열린다.')
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
