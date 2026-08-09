#!/usr/bin/env python3
"""R&D 화면이 **자기 상태를 말하는지** 본다.

이 저장소에는 진단 R&D 화면이 서른둘 있다. 어떤 것은 실제 데이터로 돌고,
어떤 것은 데이터가 쌓이기를 기다리고, 어떤 것은 설계를 그려 둔 것이다.
셋이 겉으로는 똑같이 생겼다 — 표가 있고 숫자가 있고 색이 칠해져 있다.

시제품을 완성품처럼 보여 주면, 나중에 진짜 완성품이 와도 못 믿는다.
그래서 화면마다 **지금 무엇 위에 서 있는지** 한 줄이 있어야 한다.

    "카탈로그는 1차 초안이라 선생님 검수 대상입니다."          (오개념 카탈로그)
    "구인·예측 타당도와 규준은 아직 확정 전입니다."            (진단 리포트)
    "커버리지는 실제 문항 2,310개에서 셉니다 — 추정이 아닙니다."  (시험 설계)

세 번째처럼 **잘 돌고 있다는 말도 상태**다. 한계만 적으라는 것이 아니라,
무엇 위에 서 있는지를 적으라는 것이다.

⚠ 여기서 보는 것은 **그런 문장이 있는가**뿐이다. 그 말이 사실인지는
  기계가 모른다(넷째 원칙). 없는 것만 짚는다.

    python3 tools/page_honesty.py           # 말 안 하는 화면
    python3 tools/page_honesty.py --check   # 하나라도 있으면 빨간불
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RND = re.compile(
    r'^(item-|cat|cdm|mirt|knowledge-|learning-|mastery-|spaced-|profile-|ontology-|'
    r'misconception-|multi-|olympiad-|conceptual-|constructed-|content-|test-blueprint|'
    r'longitudinal|diagnosis-|prereq-dag|qmatrix|calibration|response-manager|'
    r'data-import|integrated-report|teaching-brief|system-guide)')

# 상태를 말하는 낱말. 한계만이 아니라 "실제 데이터에서 온다" 도 상태다.
SAYS = re.compile(r'초안|검수 대상|시제품|프로토타입|데모|가정|아직|한계|확정 전|'
                  r'예정|설계 가설|추정이 아닙|실제 데이터|기다')


def text(path):
    s = open(path, encoding='utf-8', errors='ignore').read()
    s = re.sub(r'<(script|style)[\s\S]*?</\1>', '', s)
    return html.unescape(re.sub(r'<[^>]+>', ' ', s))


def main():
    check = '--check' in sys.argv
    pages = [p for p in sorted(glob.glob(os.path.join(ROOT, '*.html')))
             if RND.search(os.path.basename(p))]
    bad = [os.path.basename(p) for p in pages if not SAYS.search(text(p))]
    print('R&D 화면 %d장 · 자기 상태를 말하는 것 %d장' % (len(pages), len(pages) - len(bad)))
    if bad:
        print('\n말 안 하는 화면 %d장' % len(bad))
        for n in bad:
            print('   ', n)
        print('\n한 줄이면 된다 — 무엇 위에 서 있는지, 어디까지 믿어도 되는지.')
    if check:
        print('\n' + ('FAIL' if bad else 'PASS'))
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
