#!/usr/bin/env python3
"""네 앱이 **학생 이름을 같은 방식으로 다듬는지** 본다.

왜 이 자가 있나
---------------
네 앱이 같은 학생을 다룬다. 그런데 이름을 시트에 보내기 전에 어떻게 다듬는지가
앱마다 다르면, **같은 아이가 두 사람이 된다.** 선생님이 두 앱을 나란히 놓고
볼 때 한 아이의 기록이 두 줄로 갈라져 있고, 어느 쪽이 진짜인지 알 수 없다.

이건 여태 아무도 안 재고 있었다(`docs/앱별-전수조사.md` 4절 넷째 칸 —
"같은 학생이 두 앱에서 다른 이름").

2026-08-10 에 처음 재어 보니 **갈려 있었다.**

    exam     nameKey    (final.html · final-submit.html)   공백을 모두 지운다
    DT       cleanName  (report · exam · hw_grader · 앱)   공백을 모두 지운다
    KMChC    없다                                          맞춰 보는 자리가 없다
    study64  없다                                          맞춰 보는 자리가 없다

즉 학생이 `홍 길동` 이라고 적으면 exam·DT 는 `홍길동` 으로 맞춰 보지만,
KMChC·study64 는 **맞춰 보는 자리 자체가 없다.** 한 아이가 두 사람이 되어도
아무도 모른다.

⚠ 이 자는 **고치지 않는다.** 다듬는 방식을 바꾸면 이미 시트에 쌓인 이름과
  새로 들어오는 이름이 어긋난다 — 그건 자료를 옮기는 일이고, 선생님이 정할
  칸이다(`docs/선생님이-정할-칸.md`). 여기서는 **갈렸다는 것을 보이고**,
  한번 정한 뒤에는 그 약속을 지킨다.

무엇을 보나
-----------
화면 안에서 이름을 다듬는 자리를 찾아 **어떤 규칙을 쓰는지** 적는다.
규칙은 두 갈래로 나눈다.

    collapse   공백을 모두 지운다 (`replace(/\\s+/g,'')`)  — exam·DT
    trim       앞뒤 공백만 지운다 (`.trim()`)              — KMChC·study64

`AGREED` 에 이름을 적어 두면 그때부터 그 규칙을 어기는 저장소가 빨간불이다.
비어 있으면 **세기만 하고 조용하다** — 아직 안 정한 것을 자가 대신 정하지
않는다(term_drift 와 같은 자리다).

    python3 tools/name_key.py           # 이 저장소가 쓰는 규칙
    python3 tools/name_key.py --check   # 정해 둔 규칙을 어기면 빨간불
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ⚠ **자를 한 번 좁혔다.** 처음에는 이름이 `cleanName`·`nameKey` 이기만 하면
#   다 세었다. 그랬더니 study64-report 의
#
#       function cleanName(){ return (($('studentName')&&…).value||'학생')
#                              .trim().replace(/조준모/g,'') || '학생' }
#
#   까지 '이름 다듬기 규칙' 으로 셌다. 그건 화면에서 값을 읽어 **선생님 이름을
#   지우는** 전혀 다른 함수다. 이름이 같다고 같은 일을 하는 게 아니다.
#
#   맞춰 보는 키는 **글자를 받아 글자를 돌려주는** 함수다. 인자가 없으면
#   화면을 읽는 함수이므로 키가 아니다 — 인자가 있는 것만 센다.
NAMED = re.compile(
    r'function\s+(cleanName|nameKey)\s*\(\s*\w+[^)]*\)\s*\{[^}]*\}'
    r'|(?:const|var|let)\s+(cleanName|nameKey)\s*=\s*\(?\s*\w+[^;\n]{0,120}')
INLINE = re.compile(r'(?:name|nm|nameEl|nameIn)[A-Za-z]*\s*[:.=]\s*'
                    r'[^;,\n]{0,60}\.value\s*\.?[^;,\n]{0,40}')

COLLAPSE = re.compile(r'replace\s*\(\s*/\\s\+/g\s*,\s*[\'"]{2}\s*\)')

# 선생님이 정한 규칙을 여기 적는다. 'collapse' 또는 'trim'.
# **비워 두는 것이 지금 맞다** — 정하기 전에는 세기만 한다.
AGREED = ''


def rules():
    """(화면, 자리, 규칙) 목록."""
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        s = open(p, encoding='utf-8', errors='ignore').read()
        base = os.path.basename(p)
        for m in NAMED.finditer(s):
            frag = m.group(0)
            out.append((base, (m.group(1) or m.group(2) or '?'),
                        'collapse' if COLLAPSE.search(frag) else 'trim'))
        for m in INLINE.finditer(s):
            frag = m.group(0)
            if '.value' not in frag:
                continue
            if 'trim' not in frag and not COLLAPSE.search(frag):
                continue
            out.append((base, '입력칸에서 바로',
                        'collapse' if COLLAPSE.search(frag) else 'trim'))
    # 같은 화면·자리·규칙이 여러 번 나오면 한 번만 센다
    seen, uniq = set(), []
    for r in out:
        if r in seen:
            continue
        seen.add(r)
        uniq.append(r)
    return uniq


def main():
    check = '--check' in sys.argv
    rows = rules()
    if not rows:
        print('이 저장소에는 학생 이름을 다듬는 자리가 없다.')
        if check:
            print('PASS')
        return 0

    # **맞춰 보는 키**와 **입력칸 다듬기**는 다른 일이다. 갈라 적는다 —
    # 섞어 놓으면 "어느 앱이나 하는 .trim()" 이 갈림으로 읽힌다.
    keys = [r for r in rows if r[1] != '입력칸에서 바로']
    ins = [r for r in rows if r[1] == '입력칸에서 바로']
    kinds = sorted({k for _, _, k in keys})

    print('■ 맞춰 보는 키 %d곳%s' % (len(keys), (' · 규칙 ' + ' · '.join(kinds)) if kinds else ''))
    for page, where, kind in keys:
        print('  %-26s %-16s %s' % (page, where, kind))
    if not keys:
        print('  (없다 — 이 저장소는 이름을 맞춰 보는 자리가 없다)')

    print('\n□ 입력칸에서 바로 다듬는 자리 %d곳 (참고 — 어느 앱이나 한다)' % len(ins))
    for page, where, kind in ins:
        print('  %-26s %-16s %s' % (page, where, kind))

    print('\n  collapse  공백을 모두 지운다 — 홍 길동 → 홍길동')
    print('  trim      앞뒤 공백만 지운다 — 홍 길동 → 홍 길동')

    if len(kinds) > 1:
        print('\n⚠ 이 저장소의 **키**가 저장소 안에서 갈려 있다: %s' % ' · '.join(kinds))

    if not AGREED:
        print('\n아직 정해 둔 규칙이 없다(AGREED 가 비어 있다). 세기만 한다 —')
        print('다듬는 방식을 바꾸면 이미 쌓인 이름과 어긋나므로 선생님이 정할 칸이다.')
        if check:
            print('PASS')
        return 0

    bad = [r for r in keys if r[2] != AGREED]
    if bad:
        print('\n⚠ 정해 둔 규칙(%s)을 어기는 자리 %d곳' % (AGREED, len(bad)))
        for page, where, kind in bad:
            print('  %-26s %-16s %s' % (page, where, kind))
        if check:
            print('\nFAIL')
            return 1
        return 0

    print('\n정해 둔 규칙(%s)을 모든 자리가 지킨다.' % AGREED)
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
