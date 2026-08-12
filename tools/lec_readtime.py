#!/usr/bin/env python3
"""강의마다 **읽는 데 얼마나 걸리는지** 적는다.

왜 적나
-------
시작 전에 "10분" 이라고 알면 시작한다. 모르면 미룬다. 강의는 성적표에서
"이 개념이 약하다" 는 말과 함께 열리는데, 그 순간 학생이 하는 계산은
"지금 이걸 열면 얼마나 걸리지?" 하나다. 답이 없으면 나중으로 미룬다.

무엇을 근거로 하나
------------------
⚠ 이건 **어림값이다.** 그래서 화면에도 "약" 이라고 적는다 — 이 저장소는
  숫자를 낼 때 무엇을 근거로 한 숫자인지 반드시 같이 적는다(`응시 N명
  기준의 잠정치…`). 어림을 사실처럼 적으면 그 약속이 깨진다.

  · 한국어 읽기 속도는 흔히 분당 300~400자로 잡는다. 여기서는 **350자**.
  · 화학 강의는 식과 표에서 멈추므로 **식·표마다 15초**를 더한다.
  · 1분 미만은 올리고, 3분 단위로 끊지 않고 그대로 적는다.

지금 값: 최소 6분 · **중앙 9분** · 최대 18분.

    python3 tools/lec_readtime.py           # 얼마나 걸리나
    python3 tools/lec_readtime.py --write   # 강의 머리에 적는다
    python3 tools/lec_readtime.py --check   # 적힌 값이 글과 어긋나면 빨간불
"""
import glob
import html
import math
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CPM = 350          # 분당 글자 (한국어 읽기 · 어림)
PAUSE = 15         # 식·표에서 멈추는 시간(초)
# ⚠ 붙일 때 ' · ' 를 같이 넣으므로, 뗄 때도 같이 떼야 한다. 안 그러면 세 글자가
#   남아 경계에 걸린 장이 8분 ↔ 9분을 오간다(실제로 083 이 그랬다).
MARK = re.compile(r'(?:\s*·\s*)?<span class="rt">[^<]*</span>')
# ── 확인 문제는 **읽는 것이 아니라 푸는 것**이다 ────────────────────────
#  화면에 적히는 말은 «읽는 데 약 12분» 이다. 확인 문제 세 문항을 분당
#  350자로 세면 «17분» 이 되는데, 그건 두 번 거짓말이다 — 읽는 시간이라고
#  해 놓고 푸는 것을 섞었고, 세 문항을 실제로 푸는 데 드는 시간은 그 어림보다
#  훨씬 길다. 읽는 시간은 읽는 것만 센다. 문항이 몇 개인지는 그 덩이가
#  제 머리말에서 스스로 말한다(«방금 배운 것으로 풀 수 있는 3문항입니다»).
QUIZ = re.compile(r'<!-- 확인문제:시작.*?확인문제:끝 -->', re.S)


def minutes(src):
    b = QUIZ.sub('', src)
    b = re.sub(r'<(script|style)[\s\S]*?</\1>', '', b)
    b = MARK.sub('', b)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', b)))
    stops = len(re.findall(r'class="(?:eqn|lv|big)"', b)) + len(re.findall(r'<table', b))
    return max(1, math.ceil(len(t) / CPM + stops * PAUSE / 60))


def read_mark(src):
    m = MARK.search(src)
    if not m:
        return None
    n = re.search(r'(\d+)', m.group(0))
    return int(n.group(1)) if n else None


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))
    got, wrong, missing = [], [], []
    for p in files:
        src = open(p, encoding='utf-8').read()
        want = minutes(src)
        got.append(want)
        have = read_mark(src)
        if write:
            tag = '<span class="rt">읽는 데 약 %d분</span>' % want
            if have is None:
                # 머리의 '회차 · 영역' 줄 뒤에 붙인다. 거기가 학생이 제목 다음으로 보는 자리다.
                new, n = re.subn(r'(<div class="sub">[^<]*)(</div>)',
                                 r'\1 · ' + tag + r'\2', src, count=1)
                if not n:
                    missing.append(os.path.basename(p))
                    continue
            else:
                new = MARK.sub(tag, src, count=1)
            open(p, 'w', encoding='utf-8').write(new)
        elif have is None:
            missing.append(os.path.basename(p))
        elif have != want:
            wrong.append((os.path.basename(p), have, want))

    import statistics as st
    print('강의 %d장 · 읽는 시간 최소 %d분 · 중앙 %d분 · 최대 %d분'
          % (len(files), min(got), st.median(got), max(got)))
    print('  (분당 %d자 + 식·표마다 %d초 · **어림값이다**)' % (CPM, PAUSE))
    if write:
        print('\n적었다 %d장' % (len(files) - len(missing)))
    if missing:
        print('\n적을 자리를 못 찾은 장 %d개' % len(missing))
        for n in missing[:8]:
            print('   ', n)
    if wrong:
        print('\n적힌 값이 글과 어긋난 장 %d개' % len(wrong))
        for n, h, w in wrong[:8]:
            print('   %-44s %d분이라 적혔는데 지금 글은 %d분' % (n, h, w))
    if check:
        bad = bool(missing or wrong)
        print('\n' + ('FAIL' if bad else 'PASS'))
        return 1 if bad else 0
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
