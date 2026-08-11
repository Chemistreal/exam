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
WFDIR = os.path.join(ROOT, '.github', 'workflows')
README = os.path.join(ROOT, 'README.md')

# 판마다 **언제 도는지**가 다르다. 그 말을 여기 한 번만 적는다.
WHEN = {
    'tests.yml':  '밀 때마다 · 하루 한 번',
    'docs.yml':   '문서를 고칠 때',
    'health.yml': '하루 한 번',
}


def workflows():
    """판 이름 → 그 판의 글."""
    out = {}
    if not os.path.isdir(WFDIR):
        return out
    for f in sorted(os.listdir(WFDIR)):
        if f.endswith(('.yml', '.yaml')):
            out[f] = open(os.path.join(WFDIR, f), encoding='utf-8').read()
    return out


def locks_in_readme():
    """README 의 «자물쇠» 표가 이름을 부르는 자들.

    ⚠ 이 표는 **손으로 적는다.** 그래서 자를 지우거나 이름을 바꿔도 표는
      그대로 남는다 — 표에는 있는데 저장소에는 없는 자물쇠가 생긴다.
      걸어 두지도 않은 자물쇠를 적어 두면, 그 자리는 지켜지는 줄 알고
      아무도 안 본다. **걸지 않은 자는 없는 자와 같다** 의 한 칸 옆이다."""
    if not os.path.exists(README):
        return []
    s = open(README, encoding='utf-8').read()
    i = s.find('## 자물쇠')
    if i < 0:
        return []
    j = s.find('\n## ', i + 1)
    body = s[i:j if j > 0 else len(s)]
    return sorted(set(re.findall(r'(tools/[\w.]+\.py|tests/[\w.-]+\.js)', body)))


def summary(path):
    try:
        doc = ast.get_docstring(ast.parse(open(path, encoding='utf-8').read()))
    except SyntaxError:
        return None
    if not doc:
        return None
    return doc.strip().splitlines()[0].strip()


def when_of(name, has_check, is_gen, wfs):
    """**언제 돌리나.** 손으로 적지 않고 판에서 읽는다 — 적어 두면 갈라진다.

    2026-08-11 에 선생님이 짚으신 것(#35): 차례는 있는데 **언제 돌리는지**가
    아무 데도 없었다. 배포 전에 돌릴 자와 주간으로 볼 자가 섞여 있으면,
    사람은 결국 하나도 안 돌린다."""
    hit = [f for f, txt in wfs.items() if ('tools/' + name) in txt]
    if hit:
        return ' · '.join(WHEN.get(f, f) for f in hit)
    if is_gen:
        return '만들 때 사람이'
    if has_check:
        return '**아무도 안 돌린다**'
    return '사람이 손으로'


def build():
    wfs = workflows()
    ci = '\n'.join(wfs.values())
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
        rows[-1]['when'] = when_of(name, rows[-1]['check'], rows[-1]['gen'], wfs)
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
                '| | 자 | `--check` | 언제 돌리나 | 무엇을 |', '|---|---|---|---|---|']
        for r in group:
            out.append('| %s | `%s` | %s | %s | %s |'
                       % ('✓' if r['ci'] else '', r['name'],
                          '○' if r['check'] else '', r['when'],
                          r['sum'].replace('|', '\\|')))
        out.append('')

    # **아무도 안 돌리는 자**를 따로 세워 둔다. 표 안에 섞여 있으면 안 보인다.
    idle = [r for r in rows if r['when'].startswith('**')]
    if idle:
        out += ['## 아무도 안 돌리는 자 (%d)' % len(idle), '',
                '`--check` 를 받는데 어느 판에도 안 걸려 있다.',
                '**걸지 않은 자는 없는 자와 같다** — 걸든지, 왜 안 거는지 적든지.',
                '']
        for r in idle:
            out.append('- `%s` — %s' % (r['name'], r['sum'].replace('|', '\\|')))
        out.append('')

    # README 의 «자물쇠» 표가 부르는 이름이 실제로 있는가.
    dead = [x for x in locks_in_readme() if not os.path.exists(os.path.join(ROOT, x))]
    if dead:
        out += ['## 표에는 있는데 없는 자물쇠 (%d)' % len(dead), '',
                'README 의 «자물쇠» 표가 이름을 부르는데 저장소에 없다.',
                '걸어 두지도 않은 자물쇠를 적어 두면 그 자리는 지켜지는 줄 알고',
                '아무도 안 본다.', '']
        for x in dead:
            out.append('- `%s`' % x)
        out.append('')
    out += ['---', '',
            '자 %d개 · 판에 걸린 것 %d개 · `--check` 를 받는 것 %d개 · '
            '아무도 안 돌리는 것 %d개 · 표에는 있는데 없는 자물쇠 %d개'
            % (len(rows), sum(1 for r in rows if r['ci']),
               sum(1 for r in rows if r['check']), len(idle), len(dead)), '']
    return '\n'.join(out)


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    want = build()

    # ── 적어 두는 것과 막는 것은 다르다 ─────────────────────────────────
    # 아래 둘은 INDEX.md 에 **적히기만** 해서는 안 된다. 적어 두면 다음 사람이
    # `--write` 로 맞춰 놓고 지나가고, 그때부터 그 줄은 아무도 안 본다.
    # 그래서 여기서 바로 세운다.
    wfs = workflows()
    idle = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'tools', '*.py'))):
        name = os.path.basename(path)
        if not summary(path) or name.startswith('gen_'):
            continue
        src = open(path, encoding='utf-8').read()
        has = "'--check'" in src or '"--check"' in src
        if has and not any(('tools/' + name) in t for t in wfs.values()):
            idle.append(name)
    dead = [x for x in locks_in_readme() if not os.path.exists(os.path.join(ROOT, x))]

    if idle or dead:
        if idle:
            print('\n`--check` 를 받는데 **어느 판에도 안 걸린 자** %d개:' % len(idle))
            for n in idle:
                print('  tools/' + n)
            print('걸든지, 왜 안 거는지 적든지. **걸지 않은 자는 없는 자와 같다.**')
        if dead:
            print('\nREADME 의 «자물쇠» 표에는 있는데 **저장소에 없는** 자 %d개:' % len(dead))
            for n in dead:
                print('  ' + n)
            print('걸어 두지도 않은 자물쇠를 적어 두면, 그 자리는 지켜지는 줄 알고')
            print('아무도 안 본다. 표를 고치든지 자를 되살리든지.')
        if check:
            return 1

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
