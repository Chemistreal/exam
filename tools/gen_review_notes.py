#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""확인 필요(reviewNote) 를 한 장에 모은다.

왜 이 화면이 필요한가
---------------------
답지를 손볼 때 「이건 사람이 한 번 봐야 한다」 싶은 자리를 `reviewNote` 로
적어 왔다. 해설지에는 그 문항 옆에 「확인 필요」 로 뜬다 — 그건 **그 문항을
펼친 사람**만 본다. 그래서 마흔일곱 건이 열아홉 회차에 흩어져 있고,
**전부 몇 건인지, 어디에 있는지 한자리에서 볼 곳이 없었다.**

이 화면은 그 마흔일곱을 모아 놓기만 한다. 고치지 않는다 — 무엇을 고칠지는
문항마다 다르고, 더러는 「다음 출제 때 지문에 원자량을 넣어 달라」처럼
출제자만 정할 수 있는 것이다.

⚠ **정답이 적힌다.** 해설지가 이미 정답을 싣고 있으므로 새로 새는 것은 없지만,
   학생에게 보내는 링크가 아니라 **선생님 자리**다. dashboard 에서만 문을 낸다.

    python3 tools/gen_review_notes.py            # 몇 건인지 센다
    python3 tools/gen_review_notes.py --write    # review-notes.html 을 쓴다
    python3 tools/gen_review_notes.py --check    # 화면이 답지와 맞는지
"""

from __future__ import annotations

import glob
import html
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'review-notes.html')
CIRC = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤'}


def esc(s):
    return html.escape(str(s), quote=True)


def collect():
    """답지에서 확인 필요를 긁어 온다. (회차, 번호) 로 정렬한다."""
    titles = {e['id']: e.get('title', e['id'])
              for e in json.load(io.open(os.path.join(ROOT, 'exams.json'),
                                         encoding='utf-8'))}
    rows = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        eid = os.path.basename(p)[:-5]
        d = json.load(io.open(p, encoding='utf-8')).get('questions', {})
        for k, q in d.items():
            note = str(q.get('reviewNote') or '').strip()
            if not note:
                continue
            try:
                n = int(k)
            except ValueError:
                continue
            rows.append({
                'exam': eid,
                'title': titles.get(eid, eid),
                'n': n,
                'answer': q.get('answer'),
                'concept': q.get('concept') or q.get('learningPoint') or '',
                'note': note,
            })
    rows.sort(key=lambda r: (r['exam'], r['n']))
    return rows


CSS = """
:root{--cream:#FBFAF6;--ink:#23201b;--ink-2:#5a564d;--muted:#6f6a5e;
      --teal:#0E5A4C;--brass:#B08D57;--line:#E8E4DA;--ms:#C0603A;
      --warn-bg:#fdf6ec;--mono:ui-monospace,Menlo,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--cream);color:var(--ink);
     font-family:-apple-system,"Noto Sans KR",sans-serif;line-height:1.65}
header{background:linear-gradient(180deg,#0E5A4C,#0a3f36);color:#fff;
       padding:26px 16px;text-align:center}
header .logo{font-size:12px;letter-spacing:.2em;opacity:.8;font-weight:600}
header h1{margin:7px 0 4px;font-size:24px}
header .sub{font-size:12.5px;opacity:.86}
.wrap{max-width:900px;margin:0 auto;padding:16px}
.back{display:inline-block;margin:14px 0 4px;font-size:12.5px;color:var(--teal);
      text-decoration:none;border-bottom:1px dotted var(--brass)}
.intro{background:var(--warn-bg);border-left:3px solid var(--ms);border-radius:9px;
       padding:12px 15px;font-size:12.5px;color:#8a5a3a;margin:12px 0 18px}
.intro b{color:#5a3520}
.sum{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.sum .c{background:#fff;border:1px solid var(--line);border-radius:10px;
        padding:9px 14px;font-size:12.5px;color:var(--ink-2)}
.sum .c b{display:block;font-size:19px;color:var(--teal);
          font-family:var(--mono);line-height:1.3}
.grp{background:#fff;border:1px solid var(--line);border-radius:12px;
     padding:14px 18px;margin-bottom:14px}
.grp h2{font-size:15px;margin:0 0 3px;color:var(--teal);
        display:flex;align-items:baseline;gap:9px;flex-wrap:wrap}
.grp h2 .n{font-family:var(--mono);font-size:11.5px;background:#eef5f2;
           color:var(--teal);border-radius:7px;padding:2px 9px;font-weight:700}
.grp h2 a{font-size:11.5px;color:var(--ink-2);text-decoration:none;
          border-bottom:1px dotted var(--brass);font-weight:500}
.it{border-top:1px solid #f3efe6;padding:11px 0 3px}
.it:first-of-type{border-top:0}
.it .hd{font-size:12.5px;font-weight:700;margin-bottom:4px;
        display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
.it .hd .qn{font-family:var(--mono);color:var(--ms)}
.it .hd .ans{font-size:11.5px;color:var(--ink-2);font-weight:500}
.it .hd .cc{font-size:11.5px;color:var(--muted);font-weight:500}
.it p{margin:0 0 7px;font-size:12.5px;color:var(--ink-2);white-space:pre-wrap}
footer{max-width:900px;margin:0 auto;padding:8px 16px 34px;
       font-size:11.5px;color:var(--muted)}
@media(max-width:600px){.wrap{padding:12px}.grp{padding:12px 14px}}
"""


def build(rows):
    by = {}
    for r in rows:
        by.setdefault(r['exam'], []).append(r)

    p = []
    p.append('<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8">')
    p.append('<meta name="viewport" content="width=device-width, '
             'initial-scale=1, maximum-scale=5">')
    p.append('<meta name="robots" content="noindex,nofollow">')
    p.append('<title>확인 필요 모음 · CHEMISTREAL</title>')
    p.append('<style>%s</style></head><body>' % CSS)
    p.append('<header><div class="logo">CHEMISTREAL</div>'
             '<h1>확인 필요 모음</h1>'
             '<div class="sub">답지를 손보다가 「사람이 한 번 봐야 한다」고 '
             '적어 둔 자리를 한 장에 모았다</div></header>')
    p.append('<div class="wrap">')
    p.append('<a class="back" href="dashboard.html">← 선생님 화면으로</a>')

    p.append('<div class="sum">')
    p.append('<div class="c">모두<b>%d건</b></div>' % len(rows))
    p.append('<div class="c">회차<b>%d개</b></div>' % len(by))
    top = max(by.items(), key=lambda kv: len(kv[1]))
    p.append('<div class="c">가장 많은 회차<b>%s</b>%d건</div>'
             % (esc(top[0]), len(top[1])))
    p.append('</div>')

    p.append('<div class="intro">'
             '<b>이 화면은 고치지 않는다 — 모아 놓기만 한다.</b> '
             '무엇을 고칠지는 문항마다 다르고, 더러는 「다음 출제 때 지문에 '
             '원자량을 넣어 달라」처럼 <b>출제자만 정할 수 있는 것</b>이다. '
             '각 줄의 회차 이름을 누르면 그 회차 해설지로 간다.<br>'
             '⚠ 정답이 함께 적힌다. 해설지가 이미 싣고 있는 것이지만 '
             '<b>학생에게 보내는 링크가 아니다.</b></div>')

    for eid in sorted(by):
        items = by[eid]
        t = items[0]['title']
        sol = 'sol-final-%s.html' % eid
        link = ('<a href="%s">해설지 열기 →</a>' % esc(sol)
                if os.path.exists(os.path.join(ROOT, sol)) else '')
        p.append('<div class="grp">')
        p.append('<h2>%s <span class="n">%s</span> %s</h2>'
                 % (esc(t), esc(eid), link))
        for r in items:
            ans = ('정답 %s' % CIRC.get(r['answer'], r['answer'])
                   if r['answer'] is not None else '')
            cc = ('· %s' % esc(r['concept'])) if r['concept'] else ''
            p.append('<div class="it"><div class="hd">'
                     '<span class="qn">%d번</span>'
                     '<span class="ans">%s</span>'
                     '<span class="cc">%s</span></div>'
                     '<p>%s</p></div>'
                     % (r['n'], esc(ans), cc, esc(r['note'])))
        p.append('</div>')

    p.append('</div>')
    p.append('<footer>이 화면은 <code>tools/gen_review_notes.py</code> 가 '
             '답지(<code>answers/*.json</code>)의 <code>reviewNote</code> 에서 '
             '만든다. 손으로 고치지 말고 답지를 고친 뒤 다시 만들어라.</footer>')
    p.append('</body></html>')
    return '\n'.join(p) + '\n'


def themed(page):
    """만든 글에도 **같은 옷**을 입힌다.

    안 입히면 이 생성기와 tools/theme.py 가 영영 어긋난다 — 저 자는 파일에
    옷을 입히고, 여기는 그걸 모른 채 옛 모양을 다시 만들어 낸다. 그러면
    둘 중 하나는 늘 빨간불이다(gen_sol_page.py 도 같은 까닭으로 그렇게 한다).
    """
    sys.path.insert(0, os.path.join(ROOT, 'tools'))
    import theme
    return theme.apply(page, theme.plan(os.path.basename(OUT), page)) or page


def main():
    check = '--check' in sys.argv
    write = '--write' in sys.argv
    rows = collect()
    by = {}
    for r in rows:
        by.setdefault(r['exam'], []).append(r)
    print('확인 필요 %d건 · %d회차' % (len(rows), len(by)))
    for eid in sorted(by, key=lambda k: (-len(by[k]), k)):
        print('  %-22s %2d건  %s'
              % (eid, len(by[eid]), ', '.join('%d번' % r['n'] for r in by[eid])))

    want = themed(build(rows))
    have = io.open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else None

    if write:
        io.open(OUT, 'w', encoding='utf-8').write(want)
        print('\n%s 에 적었다 (%.1fKB)'
              % (os.path.basename(OUT), len(want.encode('utf-8')) / 1024))
        return 0

    if have is None:
        print('\nreview-notes.html 이 없다 — --write 로 만든다.')
        return 1 if check else 0
    if have != want:
        print('\nFAIL review-notes.html 이 답지와 어긋난다 — --write 로 다시 만든다.')
        return 1 if check else 0
    print('\nPASS 화면이 답지와 맞는다.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
