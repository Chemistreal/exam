#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""**한 학생의 성적이 뜨는 화면**은 검색에 잡히지 않게 한다.

왜 필요한가
-----------
성적표 링크는 **암호를 묻지 않는다.** 그건 선생님이 정한 것이고(학부모가
문자로 받은 링크를 그냥 눌러서 볼 수 있어야 한다), 검사도 그것을 지킨다
(tests/gate.js '링크 열람에 암호를 묻지 않는다').

그러면 남는 보호막은 **주소를 남이 모른다는 것 하나**뿐이다. 그 주소가 어쩌다
검색에 잡히면 보호막이 통째로 사라진다 — 아이 이름과 점수와 등수가 검색되는
것이다. 링크는 문자·카카오로만 보내지만, 링크가 새는 길은 여럿이다(학부모가
어딘가에 붙여 넣기, 메신저의 미리보기 수집, 브라우저 확장).

재어 보니 세 저장소 어디에도 robots.txt 도 noindex 도 없었다.

무엇을 넣나
-----------
    <meta name="robots" content="noindex,nofollow">

robots.txt 로 막는 것과 다르다. robots.txt 는 '읽지 마라' 이고, 읽지 않은
주소도 남이 건 링크만으로 목록에 오를 수 있다. noindex 는 '목록에 올리지
마라' 라서 이쪽이 맞는 도구다.

⚠ **개인 성적이 뜨는 화면만** 넣는다. 대문(index)·자료 화면까지 막으면 선생님
  사이트가 검색에서 통째로 사라진다 — 그건 고치는 것이 아니라 망치는 것이다.
⚠ 해설지(sol-*)는 개인 정보가 아니라 **수업 자료**다. 검색에 두느냐 마느냐는
  장사에 관한 판단이라 손대지 않는다. 선생님이 정할 일이다.

    실행:  python3 tools/noindex.py            # 세기만
           python3 tools/noindex.py --write    # 없는 곳에 넣는다
           python3 tools/noindex.py --check    # 빠진 곳이 있으면 빨간불
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 한 학생의 이름·점수·등수가 뜨는 화면. 이름으로 고르지 않고 **손으로 적는다** —
# 이름 규칙으로 넓히면 언젠가 대문까지 막는다.
PERSONAL = {
    'exam': ['final.html', 'note.html', 'batch-report.html',
             'integrated-report.html', 'grade-j0.html', 'sample_report.html',
             'final-submit.html'],
    'dt': ['report.html', 'parent_report.html', 'OX_grader.html',
           'OX_grader_prescription.html', 'hw_grader.html'],
    'kmchc': ['report.html', 'answers.html',
              '리포트_고급_미리보기.html', '리포트링크생성기.html'],
}

TAG = '<meta name="robots" content="noindex,nofollow">'
HAS = re.compile(r'<meta[^>]+name\s*=\s*["\']robots["\'][^>]*>', re.I)
HEAD = re.compile(r'<head[^>]*>', re.I)
CHARSET = re.compile(r'<meta[^>]+charset[^>]*>', re.I)


def targets():
    who = os.path.basename(ROOT).lower()
    for key, names in PERSONAL.items():
        if key == who or (key == 'kmchc' and who == 'kmchc'):
            for n in names:
                p = os.path.join(ROOT, n)
                if os.path.exists(p):
                    yield p
            return
    # 저장소 이름이 목록에 없으면 아무것도 안 한다(넓히지 않는다)


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    have = miss = done = 0
    names = []
    for p in targets():
        try:
            src = open(p, encoding='utf-8').read()
        except (OSError, UnicodeDecodeError):
            continue
        if HAS.search(src):
            have += 1
            continue
        miss += 1
        names.append(os.path.basename(p))
        if not write:
            continue
        # charset 바로 뒤에 넣는다. 없으면 <head> 바로 뒤.
        m = CHARSET.search(src) or HEAD.search(src)
        if not m:
            continue
        src = src[:m.end()] + '\n' + TAG + src[m.end():]
        open(p, 'w', encoding='utf-8').write(src)
        done += 1

    if write:
        print(f'검색에서 뺐다: {done}장 (이미 있던 것 {have}장)')
        return 0
    print(f'개인 성적 화면 {have + miss}장 · noindex 있음 {have}장 · 없음 {miss}장')
    for n in names[:10]:
        print('   ' + n)
    if check and miss:
        print('\nFAIL 개인 성적이 뜨는 화면이 검색에 열려 있다 — '
              'python3 tools/noindex.py --write')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
