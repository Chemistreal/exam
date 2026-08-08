#!/usr/bin/env python3
"""자 예순 개의 **차례**를 만든다 — `tools/INDEX.md`.

`tools/` 에 자가 예순 가까이 된다. 어느 자가 무엇을 재는지 한자리에 모은 것이
없어서, 있는 자를 못 찾고 새로 만들거나 이미 막아 둔 결함을 다시 파는 일이
생긴다. 실제로 `tools/README.md` 는 자 차례가 아니라 **동형문제 집필 원칙**
문서인데 이름 때문에 차례로 오해하기 쉽다.

자마다 설명 첫 줄이 이미 있다. 그것을 모아 적는다 — 두 벌로 적지 않는다.

  · CI 에 걸린 자는 ✓ 로 표시한다. 걸리지 않은 자는 사람이 손으로 돌린다
  · `--check` 를 받는 자인지도 적는다
  · 갈래는 이름으로 가른다: gen_* 는 만드는 자, 나머지는 재는 자

    python3 tools/gen_tool_index.py           # 어긋난 곳
    python3 tools/gen_tool_index.py --write   # 다시 적는다
    python3 tools/gen_tool_index.py --check   # 어긋나면 빨간불 (CI용)
"""
import ast
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'INDEX.md')
WF = os.path.join(ROOT, '.github', 'workflows', 'tests.yml')


def summary(path):
    try:
        doc = ast.get_docstring(ast.parse(open(path, encoding='utf-8').read()))
    except SyntaxError:
        return None
    if not doc:
        return None
    return doc.strip().splitlines()[0].strip()


def build():
    ci = open(WF, encoding='utf-8').read() if os.path.exists(WF) else ''
    rows = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'tools', '*.py'))):
        name = os.path.basename(path)
        s = summary(path)
        if not s:
            continue
        src = open(path, encoding='utf-8').read()
        rows.append({
            'name': name,
            'sum': s,
            'check': "'--check'" in src or '"--check"' in src,
            'ci': ('tools/' + name) in ci,
            'gen': name.startswith('gen_'),
        })
    made = [r for r in rows if r['gen']]
    measured = [r for r in rows if not r['gen']]

    out = ['# tools 차례',
           '',
           '`python3 tools/gen_tool_index.py --write` 가 자마다의 설명 첫 줄을 모아 적는다.',
           '손으로 고치지 않는다.',
           '',
           '- ✓ CI 에 걸려 있다 (`.github/workflows/tests.yml`)',
           '- `--check` 를 받는 자는 어긋나면 종료 코드 1 을 낸다',
           '']
    for title, group in (('재는 자', measured), ('만드는 자', made)):
        out += ['## %s (%d)' % (title, len(group)), '',
                '| | 자 | `--check` | 무엇을 |', '|---|---|---|---|']
        for r in group:
            out.append('| %s | `%s` | %s | %s |'
                       % ('✓' if r['ci'] else '', r['name'],
                          '○' if r['check'] else '', r['sum'].replace('|', '\\|')))
        out.append('')
    out += ['---', '',
            '자 %d개 · CI 에 걸린 것 %d개 · `--check` 를 받는 것 %d개'
            % (len(rows), sum(1 for r in rows if r['ci']),
               sum(1 for r in rows if r['check'])), '']
    return '\n'.join(out)


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    want = build()
    cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
    n = want.count('\n| ')
    print('자 차례 %d줄' % n)
    if want == cur:
        print('tools/INDEX.md 가 자들과 맞는다.')
        return 0
    if write:
        open(OUT, 'w', encoding='utf-8').write(want)
        print('tools/INDEX.md 에 다시 적었다.')
        return 0
    print('\ntools/INDEX.md 가 낡았다 — 자가 늘거나 설명이 바뀌었다.')
    print('python3 tools/gen_tool_index.py --write 로 맞춘다.')
    return 1 if check else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
