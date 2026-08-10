#!/usr/bin/env python3
"""CI 가 부르는 자가 **거기서 실제로 돌 수 있는지** 본다.

왜 이 자가 있나
---------------
2026-08-10 에 GitHub 판 검사를 열어 보니 **여섯 번 가운데 여섯 번이 빨간불**
이었다. 그런데 아무도 안 보고 있었다 — 나도 손에서만 돌려 보고 초록이라고
말하고 있었다.

까닭은 하나였다. **자는 있는데 그 자가 CI 에서 돌 수 없었다.**

    tools/crop_align.py        import fitz      → ModuleNotFoundError
    tools/pdf_answer_leak.py   import pymupdf   → ModuleNotFoundError

PyMuPDF 를 설치하는 줄이 없었다. 즉 크롭이 한 칸 밀리는 것도, 문제지에 답이
실리는 것도 **CI 는 한 번도 막은 적이 없다.** 사람이 손으로 돌릴 때만 걸렸다.

같은 날 브라우저 검사에서도 같은 일을 했다.

    DT        tests/narrow.js 를 playwright **설치보다 앞**에 걸었다
    KMChC     브라우저가 없는 CI 에 REQUIRE_BROWSER=1 로 세 개를 걸었다
    study64   같음 — 그 뒤 선생님 커밋 일곱 개가 그것 때문에 빨간불이었다

이 저장소들의 원칙이 "재는 것과 막는 것은 다르다" 인데, 그 한 칸 앞에 더
있는 것이 이것이다 — **돌 수 있는 것과 걸어 둔 것은 다르다.**

무엇을 보나
-----------
  ① CI 가 부르는 `tools/*.py` 가 바깥 꾸러미를 쓰면, 그것을 설치하는 줄이
     같은 판에 있는가
  ② CI 가 부르는 `node tests/*.js` 가 playwright 를 쓰면
     ㄱ. 설치하는 줄이 있는가
     ㄴ. 그 줄이 **이 단계보다 앞에** 있는가 (뒤면 못 찾는다)

⚠ 빨간불이 아니라 **못 도는 것**을 잡는 자다. 검사가 통째로 안 돌면 그 아래
  자들도 다 안 돈다 — 한 줄 때문에 판 전체가 죽는다.

    python3 tools/ci_deps.py           # 판마다 무엇이 필요한가
    python3 tools/ci_deps.py --check   # 못 도는 자가 있으면 빨간불
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 꾸러미 이름과 import 이름이 다른 것. 사람이 알아야 하는 것이라 적어 둔다.
ALIAS = {
    'fitz': 'PyMuPDF', 'pymupdf': 'PyMuPDF',
    'PIL': 'Pillow', 'yaml': 'PyYAML', 'bs4': 'beautifulsoup4',
}

STEP_PY = re.compile(r'run:\s*python3?\s+(tools/[a-z_0-9]+\.py|tests/[a-z_0-9]+\.py)')
STEP_JS = re.compile(r'run:\s*(?:[A-Z_]+=\S+\s+)*node\s+(tests/[a-z\-0-9]+\.js)')
PIP = re.compile(r'pip install[^\n]*?((?:--\S+\s+)*)([A-Za-z0-9_.\- ]+)$', re.M)
PW_INSTALL = re.compile(r'playwright install|npm install --prefix tests|npm ci --prefix tests')
# ⚠ **자를 한 번 좁혔다.** 처음에는 `node tests/*.js` 를 모두 브라우저 검사로
#   보고 playwright 를 요구했다. 그랬더니 KMChC 의 engine-sync.js·read-api.js
#   처럼 브라우저를 아예 안 쓰는 검사까지 걸었다. 그리고 NODE_PATH 를 **단계
#   마다** 찾아서, exam 처럼 판 전체 `env:` 로 주는 저장소를 통째로 걸었다.
#   넓게 잡는 자는 사람이 경고를 무시하게 만든다 — 파일을 열어 확인한다.
NEEDS_PW = re.compile(r'require\([\'"]?[^\'")]*playwright|PLAYWRIGHT_MODULE')
# 건너뛰기를 막는 스위치. 이것이 없으면 playwright 가 없을 때 **조용히 0** 으로
# 끝난다 — 건너뛴 것은 초록으로 세지 않는다.
REQUIRE = re.compile(r'REQUIRE_BROWSER')


def third_party(path):
    """이 파일이 쓰는 바깥 꾸러미 이름들(표준 라이브러리·같은 저장소 파일은 뺀다)."""
    std = set(sys.stdlib_module_names)
    out = set()
    try:
        s = open(os.path.join(ROOT, path), encoding='utf-8').read()
    except OSError:
        return out
    for a, b in re.findall(r'^\s*import (\w+)|^\s*from (\w+) import', s, re.M):
        mod = a or b
        if not mod or mod in std:
            continue
        if os.path.exists(os.path.join(ROOT, 'tools', mod + '.py')):
            continue                       # 같은 저장소의 자를 부르는 것
        if os.path.exists(os.path.join(ROOT, 'tests', mod + '.py')):
            continue
        out.add(mod)
    return out


def workflows():
    return sorted(glob.glob(os.path.join(ROOT, '.github', 'workflows', '*.yml')))


def main():
    check = '--check' in sys.argv
    bad, seen = [], 0

    for wf in workflows():
        text = open(wf, encoding='utf-8').read()
        name = os.path.relpath(wf, ROOT)

        installed = set()
        for _, pkgs in PIP.findall(text):
            installed |= {p for p in pkgs.split() if not p.startswith('-')}

        py = sorted(set(STEP_PY.findall(text)))
        js = sorted(set(STEP_JS.findall(text)))
        if not py and not js:
            continue
        seen += 1
        print('[%s] python 자 %d개 · 브라우저 검사 %d개 · 설치 %s'
              % (name, len(py), len(js), ' '.join(sorted(installed)) or '(없음)'))

        # ① python 꾸러미
        for f in py:
            for mod in sorted(third_party(f)):
                pkg = ALIAS.get(mod, mod)
                if pkg not in installed and mod not in installed:
                    bad.append('%s: `%s` 가 %s 를 쓰는데 설치하는 줄이 없다 '
                               '(pip install %s)' % (name, f, mod, pkg))

        # ② playwright — 브라우저를 **실제로 쓰는** 검사만 본다
        browser = []
        for f in js:
            try:
                src = open(os.path.join(ROOT, f), encoding='utf-8').read()
            except OSError:
                continue
            if NEEDS_PW.search(src):
                browser.append((f, bool(REQUIRE.search(src))))
        # NODE_PATH 는 판 전체 env 로 줄 수도 있다(exam 이 그렇게 한다)
        job_env = 'NODE_PATH' in re.sub(r'run:[^\n]*', '', text)
        if browser:
            m = PW_INSTALL.search(text)
            if not m:
                bad.append('%s: 브라우저 검사 %s 가 걸려 있는데 playwright 를 '
                           '설치하는 줄이 없다'
                           % (name, ', '.join(f for f, _ in browser)))
            else:
                for f, guarded in browser:
                    at = text.find('node ' + f)
                    if at < 0:
                        at = text.find(f)
                    if 0 <= at < m.start():
                        how = ('빨간불이 난다' if guarded
                               else '**조용히 건너뛴다** — 건너뛴 것은 초록이 아니다')
                        bad.append('%s: `%s` 가 playwright 설치보다 **앞**에 있다 '
                                   '— %s' % (name, f, how))
                    if not job_env and 'NODE_PATH' not in text[max(0, at - 200):at]:
                        bad.append('%s: `%s` 에 NODE_PATH=tests/node_modules 가 '
                                   '없다 — 설치해도 못 찾는다' % (name, f))

    if not seen:
        print('이 저장소의 판에는 부르는 자가 없다.')
        if check:
            print('PASS')
        return 0

    if bad:
        print('\n⚠ CI 에서 **돌 수 없는** 자리 %d곳' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n한 줄이 못 돌면 그 아래 자들도 다 안 돈다 — 판 전체가 죽는다.')
        if check:
            print('\nFAIL')
            return 1
        return 0

    print('\nCI 가 부르는 자들이 거기서 돌 수 있다.')
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
