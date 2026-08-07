#!/usr/bin/env python3
"""`explanation`(글) 에서 `explanationHtml`(해설지에 실릴 꼴) 을 만든다.

해설지 생성기(`gen_sol_page.py`)는 `explanationHtml` 만 읽는다. 글만 써 넣고
이것을 빠뜨리면 **해설지가 통째로 비어 나온다** — 파일은 만들어지고 검사도
지나가므로 아무도 모른다(2026-08-07 에 실제로 그랬다).

글의 꼴은 정해져 있다.

    사고과정 <문장> <문장> … → ③

'사고과정' 을 머리글로 올리고, 문장마다 한 줄로 끊고, 마지막 '→ ③' 을
굵게 세운다. 이미 explanationHtml 이 있는 문항은 건드리지 않는다 —
손으로 공들여 쓴 것을 기계가 덮어쓰면 안 된다.

    python3 tools/gen_expl_html.py <시험id> [--write]
    python3 tools/gen_expl_html.py --check      # 글은 있는데 꼴이 없는 곳이 있나
"""
import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRC = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤'}


def build(text):
    """글 한 덩이를 해설지 꼴로 바꾼다."""
    t = text.strip()
    if not t:
        return ''
    head = ''
    m = re.match(r'^(사고과정)\s*', t)
    if m:
        head = '<h4>사고과정</h4>\n'
        t = t[m.end():]

    # 맨 끝의 '→ ③' 은 따로 세운다.
    tail = ''
    m = re.search(r'→\s*([①-⑤])\s*$', t)
    if m:
        tail = '<p class="step">→ <b>%s</b></p>' % m.group(1)
        t = t[:m.start()].strip()

    # 문장마다 한 줄. 마침표 뒤가 공백이면 끊는다(소수점은 뒤에 숫자가 와서 안 끊긴다).
    parts = [s.strip() for s in re.split(r'(?<=[.。])\s+', t) if s.strip()]
    body = '\n'.join('<p class="step">%s</p>' % html.escape(s, quote=False) for s in parts)
    return head + body + ('\n' + tail if tail else '')


def run(path, write):
    data = json.load(open(path, encoding='utf-8'))
    qs = data.get('questions') or {}
    made = missing = 0
    for k in sorted(qs, key=int):
        q = qs[k]
        expl = str(q.get('explanation') or '').strip()
        cur = str(q.get('explanationHtml') or '').strip()
        if not expl or cur:
            continue
        missing += 1
        if write:
            q['explanationHtml'] = build(expl)
            made += 1
    if write and made:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write('\n')
    return missing, made


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    write = '--write' in sys.argv
    check = '--check' in sys.argv

    paths = ([os.path.join(ROOT, 'answers', '%s.json' % a) for a in args]
             if args else sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))))

    total = 0
    for p in paths:
        missing, made = run(p, write)
        if missing:
            total += missing
            print('  %-34s 글은 있는데 꼴이 없는 문항 %d개%s'
                  % (os.path.basename(p), missing, ' → 만들었다' if made else ''))
    if not total:
        print('해설 글이 있는 문항은 모두 해설지 꼴을 갖췄다')
        return 0
    if write:
        return 0
    print('\npython3 tools/gen_expl_html.py --write 로 만든다.')
    return 1 if check else 0


if __name__ == '__main__':
    sys.exit(main())
