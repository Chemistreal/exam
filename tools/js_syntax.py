#!/usr/bin/env python3
"""화면 안에 박아 넣은 자바스크립트가 **문법이 맞는지** 본다.

왜 필요한가. kmchc/분석_v2.html 은 화면을 열면 자바스크립트가 첫 줄에서
죽어 있었다 — 표 머리에 `scope="col"` 을 붙이는 손질이, 큰따옴표로 묶인
자바스크립트 글자열 **안쪽**에 큰따옴표를 그대로 집어넣었기 때문이다.

    H+="<table><tr><th scope="col">구인</th> …"
                            ^ 여기서 글자열이 끝나 버린다

파일만 보면 멀쩡하다. 검사도 다 통과했다. 그런데 그 화면은 통째로
아무 일도 안 했다. 아무도 안 봤기 때문에 몇 달을 그대로 있었다.

`node --check` 는 실행하지 않고 문법만 본다 — 화면을 띄우지 않아도,
브라우저가 없어도 돈다.

실행:  python3 tools/js_syntax.py            # 세기만
       python3 tools/js_syntax.py --check    # 하나라도 깨졌으면 빨간불
"""
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCRIPT = re.compile(r'<script\b([^>]*)>([\s\S]*?)</script>', re.I)
TYPE = re.compile(r'\btype\s*=\s*["\']([^"\']*)["\']', re.I)
SRC = re.compile(r'\bsrc\s*=\s*["\']', re.I)

# 자바스크립트인 것들. 그 밖(application/json · text/template · importmap)은
# 자바스크립트가 아니라서 문법을 따질 수 없다 — 건드리면 애먼 빨간불이 된다.
JS_TYPES = {'', 'text/javascript', 'application/javascript', 'module',
            'text/ecmascript', 'application/ecmascript'}


def files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in ('.git', 'node_modules', '__pycache__')]
        for f in sorted(fn):
            if f.endswith('.html'):
                yield os.path.join(dp, f)


def check_one(body, module):
    """문법이 맞으면 None, 아니면 첫 줄짜리 사유."""
    suf = '.mjs' if module else '.js'
    fd, path = tempfile.mkstemp(suffix=suf)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            fh.write(body)
        r = subprocess.run(['node', '--check', path],
                           capture_output=True, text=True)
    finally:
        os.unlink(path)
    if r.returncode == 0:
        return None
    for line in r.stderr.splitlines():
        if 'Error' in line:
            return line.strip()
    return '문법 오류'


def main():
    check = '--check' in sys.argv[1:]
    total, broken = 0, []
    for p in files():
        try:
            src = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        for m in SCRIPT.finditer(src):
            attrs, body = m.group(1), m.group(2)
            if SRC.search(attrs):
                continue                       # 바깥 파일 — 여기 몸통이 없다
            t = (TYPE.search(attrs).group(1).strip().lower()
                 if TYPE.search(attrs) else '')
            if t not in JS_TYPES:
                continue
            if not body.strip():
                continue
            total += 1
            why = check_one(body, t == 'module')
            if why:
                line = src[:m.start()].count('\n') + 1
                broken.append((os.path.relpath(p, ROOT), line, why))

    print('화면 안 자바스크립트 ' + str(total) + '덩이 · 깨진 것 ' + str(len(broken)) + '개')
    if broken:
        print('\n열면 아무 일도 안 하는 화면:')
        for rel, line, why in broken:
            print('   ' + rel + ' (' + str(line) + '줄)  ' + why)
    if check and broken:
        print('\nFAIL')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
