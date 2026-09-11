#!/usr/bin/env python3
"""강의 125장의 **절마다 닻(id)** 을 단다 — 성적표가 «03절» 로 바로 열 수 있게.

무엇이 문제였나
---------------
성적표의 「개념 강의 보기」는 강의를 **첫 줄로만** 연다. 강의는 6~18분(가운데
9분)짜리 통 강의라, 학생은 자기 오답이 가리키는 절을 찾아 내려가야 한다.
그런데 성적표 쪽 배선(why)은 82% 가 «03절» 처럼 절을 **이미 적어 두고**
있었다 — 가리킬 자리는 아는데, 강의에 가리킬 이름이 없었다. 125장 가운데
절에 id 가 있는 장은 0장이었다(id 는 장마다 ct-theme 하나뿐).

규칙 (성적표 쪽과 맞춘 약속)
---------------------------
  · 본문 절 `<div class="sec">` 에는 그 절에 **인쇄된 번호**와 같은 id 를 단다.
        <span class="sec__no">03</span>   →   <div class="sec" id="s03">
    차례가 아니라 **인쇄 번호**다 — 성적표가 적어 둔 «03절» 은 학생 눈에
    보이는 그 숫자다. 둘이 어긋나면 «03절로 가라» 가 다른 절을 연다.
  · 확인 문제 절(`sec lq`, 번호 자리에 ✓)은 `id="q"`.
    이 절은 tools/lecture_quiz.py 가 **다시 만든다.** 그래서 그쪽 틀에도 같은
    id 가 들어 있다 — 여기서만 달면 다음 생성에서 사라진다. 두 자가 같은
    바이트를 내야 서로 빨간불을 켜지 않는다.
  · `.sec{scroll-margin-top:14px}` 한 줄. `#s03` 으로 열면 브라우저가 그 절의
    위 테두리를 화면 맨 위에 딱 붙이는데, 절 사이 간격(14px)만큼 띄운다.
    ⚠ 강의 머리띠(header)는 흐름 안에 있고 고정이 아니다 — 125장 전부
      position:relative 다(재어 봤다). 가리는 상단바가 없으니 이 값은 가려짐을
      피하는 높이가 아니라 **숨 쉴 자리**다. 고정 상단바가 생기면 그 높이만큼
      키워야 한다.

    python3 tools/lec_anchor.py            # 현황
    python3 tools/lec_anchor.py --write    # 빠진 id 와 그 한 줄을 더한다 — 다른 바이트는 그대로
    python3 tools/lec_anchor.py --check    # 빠지거나 어긋나거나 겹치면 빨간불 (CI)

--check 가 보는 것
-----------------
  · 모든 강의의 모든 절(`<div class="sec…">`)에 id 가 있다
  · id 가 인쇄 번호와 같다 (`s03` 인데 04 가 찍혀 있으면 빨간불)
  · 한 장 안에서 id 가 겹치지 않는다 — 절끼리도, 다른 id(ct-theme)와도
  · 절 번호를 못 읽은 절이 없다 (두 자리 숫자도 ✓ 도 아닌 것)
  · scroll-margin-top 규칙이 있다

--write 가 하는 것 · 안 하는 것
------------------------------
  · 여는 태그의 class 바로 뒤에 ` id="…"` 를 **끼워 넣기만** 한다. 줄바꿈·들여쓰기·
    그 밖의 어떤 바이트도 안 건드린다 — 강의는 사람이 손으로 쓴 글이라 자가
    고쳐 쓴 흔적이 diff 에 섞이면 사람이 고친 것을 못 찾는다.
  · 이미 있는 id 가 우리 꼴(`sNN`·`q`)인데 인쇄 번호와 어긋나면 바로잡는다.
    우리 꼴이 아닌 id 는 손대지 않고 알린다 — 누가 일부러 단 것일 수 있다.
  · 같은 번호가 두 절에 찍혀 있으면 **달지 않는다.** 겹친 id 는 앞엣것만 열려
    뒤엣것은 영영 못 여는데, 그것을 조용히 만드는 편이 더 나쁘다.
"""
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 절의 여는 태그 — `<div class="sec">` 와 `<div class="sec lq" data-lecture-quiz>`.
# class 가 "sec" 으로 시작하는 div 만이다("sec__h" 같은 자식은 안 잡힌다).
SEC_OPEN = re.compile(r'<div class="sec(?: [^"]*)?"[^>]*>')
SEC_NO = re.compile(r'<span class="sec__no">([^<]*)</span>')
# 속성으로 붙은 id 만 본다(앞에 공백). `data-id="…"` 는 안 잡힌다.
ID_ATTR = re.compile(r'\sid="([^"]*)"')
CLASS_ATTR = re.compile(r'class="[^"]*"')
OURS = re.compile(r'^(s\d{2}|q)$')

CSS_KEY = '.sec{scroll-margin-top:'
CSS_LINE = ('.sec{scroll-margin-top:14px}'
            '/* #s03 처럼 절로 열 때 절 머리가 화면 위에 딱 붙지 않게 — tools/lec_anchor.py 가 넣는다 */\n')
# 첫 `.sec{…}` 규칙 줄 바로 뒤에 넣는다. 그 줄이 없으면 첫 </style> 앞.
CSS_AFTER = re.compile(r'^\.sec\{[^\n]*\}\n', re.M)
STYLE_END = re.compile(r'</style>')


def pages():
    return sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))


def want_id(printed):
    if printed is None:
        return None
    printed = printed.strip()
    if printed == '✓':                       # ✓ — 확인 문제
        return 'q'
    if re.fullmatch(r'\d{2}', printed):
        return 's' + printed
    return None


def sections(src):
    """[(여는 태그 match, 인쇄 번호, 기대 id, 지금 id)] — 글에 나오는 차례로."""
    opens = list(SEC_OPEN.finditer(src))
    out = []
    for i, m in enumerate(opens):
        end = opens[i + 1].start() if i + 1 < len(opens) else len(src)
        n = SEC_NO.search(src, m.end(), end)
        printed = n.group(1) if n else None
        cur = ID_ATTR.search(m.group(0))
        out.append((m, printed, want_id(printed), cur.group(1) if cur else None))
    return out


def look(src):
    """한 장을 본다. 문제 목록(사람 말)과 고칠 계획을 같이 돌려준다."""
    secs = sections(src)
    problems, plan = [], []          # plan: (match, new_tag)
    wants = [w for _m, _p, w, _c in secs if w]
    dup_want = {w for w in wants if wants.count(w) > 1}
    for m, printed, want, cur in secs:
        where = '절 «%s»' % (printed.strip() if printed else '?')
        if want is None:
            problems.append(where + ' — 번호를 못 읽었다 (두 자리 숫자도 ✓ 도 아니다)')
            continue
        if want in dup_want:
            problems.append(where + ' — 같은 번호가 두 절에 찍혀 있다')
            continue
        if cur == want:
            continue
        if cur is None:
            problems.append(where + ' — id 가 없다 (id="%s" 이어야)' % want)
            plan.append((m, CLASS_ATTR.sub(lambda c: c.group(0) + ' id="' + want + '"',
                                            m.group(0), count=1)))
        elif OURS.match(cur):
            problems.append(where + ' — id="%s" 인데 인쇄 번호는 %s 다' % (cur, want))
            plan.append((m, m.group(0).replace(' id="' + cur + '"', ' id="' + want + '"', 1)))
        else:
            problems.append(where + ' — 다른 id="%s" 가 달려 있다 (손대지 않는다)' % cur)
    # 겹친 id — 절끼리도, 절이 아닌 것(ct-theme)과도.
    ids = ID_ATTR.findall(src)
    for d in sorted({x for x in ids if ids.count(x) > 1}):
        problems.append('id="%s" 가 %d번 겹친다' % (d, ids.count(d)))
    css_missing = CSS_KEY not in src
    if css_missing:
        problems.append('scroll-margin-top 규칙이 없다')
    return secs, problems, plan, css_missing


def rewrite(src, plan, css_missing):
    """계획대로만 바꾼다 — 끼워 넣기뿐, 다른 바이트는 그대로."""
    out, pos = [], 0
    for m, new in sorted(plan, key=lambda x: x[0].start()):
        out.append(src[pos:m.start()])
        out.append(new)
        pos = m.end()
    out.append(src[pos:])
    s = ''.join(out)
    if css_missing:
        m = CSS_AFTER.search(s)
        if m:
            s = s[:m.end()] + CSS_LINE + s[m.end():]
        else:
            m = STYLE_END.search(s)
            if m:
                s = s[:m.start()] + CSS_LINE + s[m.start():]
    return s


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    files = pages()
    if not files:
        print('강의 페이지를 못 찾았습니다.')
        return 1

    n_sec = n_ok = 0
    bad = {}                 # 파일 → 문제 목록
    unread = []              # 번호를 못 읽은 절이 있는 파일
    written = 0
    for p in files:
        rel = os.path.relpath(p, ROOT)
        with io.open(p, encoding='utf-8') as fh:
            src = fh.read()
        secs, problems, plan, css_missing = look(src)
        n_sec += len(secs)
        n_ok += sum(1 for _m, _p, w, c in secs if w and c == w)
        if any(w is None for _m, _p, w, _c in secs):
            unread.append(rel)
        if write and (plan or css_missing):
            new = rewrite(src, plan, css_missing)
            if new != src:
                with io.open(p, 'w', encoding='utf-8') as fh:
                    fh.write(new)
                written += 1
            # 쓰고 나서 남는 문제만 알린다(못 읽음 · 겹침 · 남의 id).
            _s, problems, _pl, _cm = look(new)
        if problems:
            bad[rel] = problems

    print('강의 %d장 · 절 %d개 · id 가 인쇄 번호와 맞는 절 %d개'
          % (len(files), n_sec, n_ok)
          + (' · 문제 있는 장 %d' % len(bad) if bad else ''))
    if write:
        print('고친 장 %d' % written)
    if unread:
        print('\n절 번호를 못 읽은 장 %d — 두 자리 숫자도 ✓ 도 아닌 절이 있다:' % len(unread))
        for f in unread[:20]:
            print('  ' + f)
    if bad:
        print('')
        for f in list(bad)[:12]:
            print('  ✗ ' + f)
            for why in bad[f][:4]:
                print('      ' + why)
        if len(bad) > 12:
            print('  … %d장 더' % (len(bad) - 12))
    if check:
        if bad:
            print('\nFAIL 성적표가 «03절» 로 열 수 없는 절이 있습니다.')
            print('     python3 tools/lec_anchor.py --write 로 달고, 못 읽은 번호는 손으로 보세요.')
            return 1
        print('\nPASS 절마다 id="sNN" · 확인 문제 id="q" · 겹침 없음')
        return 0
    return 1 if (write and bad) else 0


if __name__ == '__main__':
    sys.exit(main())
