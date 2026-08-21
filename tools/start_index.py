#!/usr/bin/env python3
"""`START_HERE_index.html` 이 실제 파일과 맞는지 본다.

스스로 '전체 파일 인덱스' 라고 적어 둔 장이다. 그런데 손으로 카드를 붙여 온
장이라, 새 화면을 만들어도 여기까지 오는 길이 없다. 실제로 여덟 장이 빠져
있었다 — 통합 셸(hub) 과 학생 제출 화면(final-submit) 처럼 큰 화면까지.

구획 머리에 적힌 숫자도 손으로 세어 온 것이라 셋이 어긋나 있었다
(운영 앱 4↔6 · 문제 은행 10↔11 · 풀이 해설 72↔74).

여기서 보는 것.

  ① 없는 파일로 거는 링크가 있는가
  ② 저장소의 화면 가운데 목록에 없는 것이 있는가
  ③ 구획 머리의 숫자가 그 구획의 카드 수와 같은가

  자기 자신과 `_` 로 시작하는 것(다른 장이 불러 쓰는 밑틀)은 안 싣는다.

    python3 tools/start_index.py           # 어긋난 곳
    python3 tools/start_index.py --check   # 어긋나면 빨간불 (CI용)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, 'START_HERE_index.html')
SELF = 'START_HERE_index.html'


def hidden_sol_pages():
    """학생 개인 회차의 해설지는 이 목록에 안 싣는다.

    student-finals.json 의 회차는 `hidden:true` 다 — 주소를 아는 사람만 연다.
    '전체 파일 인덱스' 에 이름을 실으면 「누구에게만 준 것」 이 공개 목록이
    되어 버린다. 성적표(final.html)가 그 자리에서 링크를 만들어 거는 것이
    이 장들의 문이다(tools/page_doors.py 도 같은 자리를 안다).
    """
    out = set()
    for side in ('student-finals.json', 'teacher-exams.json'):
        p = os.path.join(ROOT, side)
        if not os.path.exists(p):
            continue
        for e in json.load(open(p, encoding='utf-8')).get('exams', []):
            if e.get('hidden'):
                out.add('sol-final-%s.html' % e['id'])
    return out


def main():
    check = '--check' in sys.argv
    src = open(PAGE, encoding='utf-8').read()
    linked = set(re.findall(r'href="([^"]+\.html)"', src))
    real = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.html'))}
    bad = []

    dead = sorted(l for l in linked if l not in real)
    for l in dead:
        bad.append('없는 파일로 건다: %s' % l)

    skip = hidden_sol_pages()
    missing = sorted(r for r in real
                     if r not in linked and r != SELF and not r.startswith('_')
                     and r not in skip)
    for r in missing:
        bad.append('목록에 없다: %s' % r)

    nsec = 0
    for m in re.finditer(r'<section id="([a-z]+)">', src):
        i = m.start()
        j = src.index('</section>', i)
        blk = src[i:j]
        nsec += 1
        n = len(re.findall(r'<a class="fc', blk))
        w = re.search(r'<span class="n">(\d+)</span>', blk)
        if w and int(w.group(1)) != n:
            bad.append('구획 %s: 적힌 수 %s ≠ 실제 카드 %d'
                       % (m.group(1), w.group(1), n))

    print('건 링크 %d · 저장소 화면 %d · 구획 %d' % (len(linked), len(real), nsec))
    if bad:
        print('\n어긋난 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        return 1 if check else 0

    print('목록이 실제 파일과 맞는다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
