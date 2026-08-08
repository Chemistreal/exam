#!/usr/bin/env python3
"""125 개념표가 **화면 스물넷에 따로** 적혀 있다 — 다 같은 말을 하는지 본다.

분석 화면들은 개념 코드('001'~'125')와 그 이름·영역을 저마다 품고 있다.
바깥 파일로 빼지 않는 것은 이 저장소의 규칙이다(바깥 stylesheet·script 는
첫 그림을 막는다). 대신 갈라지지 않게 재는 자가 있어야 하는데 없었다.

품는 꼴이 셋이다. 화면마다 필요한 만큼만 든다.

    l            이름만            olympiad-depth
    l · a        이름 · 영역        열아홉 장
    l · a · f    + 강의 파일        diagnosis-v1 · misconception-catalog · ontology-browser

여기서 보는 것.

  ① 스물넷이 모두 125 코드를 다 들고 있는가
  ② 같은 코드의 **이름과 영역이 화면마다 같은가**
  ③ 강의 파일(f)이 실제로 있는가 — 눌러 보고 나서야 아는 자리다

이름을 한 장에서만 고치면 나머지 스물셋이 옛 이름을 든 채로 남는다.
학생은 같은 개념을 화면마다 다른 이름으로 만난다.

    python3 tools/concept_table.py           # 어긋난 곳
    python3 tools/concept_table.py --fix     # 가장 많은 쪽으로 맞춘다
    python3 tools/concept_table.py --check   # 어긋나면 빨간불 (CI용)
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEAD = "const N={'001':{"
ITEM = re.compile(r"'(\d{3})':\{((?:[a-z]+:'(?:[^'\\]|\\.)*',?)+)\}")
FIELD = re.compile(r"([a-z]+):'((?:[^'\\]|\\.)*)'")


def span(src):
    i = src.find(HEAD)
    if i < 0:
        return None
    depth, k = 0, src.find('{', i)
    while k < len(src):
        c = src[k]
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i, k + 1
        elif c == "'":
            k += 1
            while k < len(src) and src[k] != "'":
                k += 2 if src[k] == '\\' else 1
        k += 1
    return None


def read(seg):
    out = {}
    for m in ITEM.finditer(seg):
        out[m.group(1)] = dict(FIELD.findall(m.group(2)))
    return out


def main():
    fix = '--fix' in sys.argv
    check = '--check' in sys.argv
    pages = {}
    for path in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        src = open(path, encoding='utf-8', errors='ignore').read()
        sp = span(src)
        if not sp:
            continue
        pages[os.path.basename(path)] = (src, sp, read(src[sp[0]:sp[1]]))
    if not pages:
        print('개념표를 품은 화면이 없다.')
        return 0

    # 코드마다 가장 많이 쓰인 이름·영역을 바른 값으로 본다
    truth = {}
    for code in sorted({c for _, _, t in pages.values() for c in t}):
        for f in ('l', 'a'):
            vals = collections.Counter(t[code][f] for _, _, t in pages.values()
                                       if code in t and f in t[code])
            if vals:
                truth.setdefault(code, {})[f] = vals.most_common(1)[0][0]

    bad, fixed = [], 0
    for name, (src, (a, b), tbl) in sorted(pages.items()):
        miss = [c for c in truth if c not in tbl]
        if miss:
            bad.append('%s: 코드 %d개가 없다 (%s…)' % (name, len(miss), ', '.join(miss[:4])))
        off = [(c, f, tbl[c][f], truth[c][f])
               for c in sorted(tbl) if c in truth
               for f in ('l', 'a')
               if f in tbl[c] and f in truth[c] and tbl[c][f] != truth[c][f]]
        for c, f, got, want in off:
            bad.append("%s: '%s' 의 %s 가 '%s' — 다른 화면은 '%s'"
                       % (name, c, f, got, want))
        gone = [(c, tbl[c]['f']) for c in sorted(tbl)
                if tbl[c].get('f') and not os.path.exists(os.path.join(ROOT, tbl[c]['f']))]
        for c, f in gone:
            bad.append('%s: %s 가 가리키는 강의 %s 가 없다' % (name, c, f))
        if fix and off:
            seg = src[a:b]
            for c, f, got, want in off:
                seg = re.sub(r"('%s':\{[^}]*?%s:')%s(')" % (c, f, re.escape(got)),
                             lambda m: m.group(1) + want + m.group(2), seg, count=1)
            open(os.path.join(ROOT, name), 'w', encoding='utf-8').write(src[:a] + seg + src[b:])
            fixed += 1

    print('개념표를 품은 화면 %d장 · 코드 %d개' % (len(pages), len(truth)))
    if bad:
        print('\n어긋난 곳 %d%s:' % (len(bad), ' → 맞췄다' if fix else ''))
        for x in bad[:20]:
            print('  ' + x)
        if len(bad) > 20:
            print('  … 외 %d' % (len(bad) - 20))
        if fix:
            return 0
        print('\npython3 tools/concept_table.py --fix 로 맞춘다 (없는 코드·강의는 손으로).')
        return 1 if check else 0

    print('스물넷이 같은 이름과 영역을 든다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
