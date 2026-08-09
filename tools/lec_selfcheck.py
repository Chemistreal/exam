#!/usr/bin/env python3
"""숙제에 **스스로 확인할 기준**이 붙어 있는지 본다.

인출(스스로 꺼내 보기)은 읽기보다 오래 남는다. 그런데 인출은 **맞았는지
알 수 있어야** 값을 한다 — 틀린 채로 꺼내면 틀린 것이 굳는다.

이 저장소의 강의는 그 확인을 답안지가 아니라 **말**로 시킨다.

    그리고 입으로 말해. "ΔG가 음수면 자발적이고, 엔트로피 항에는 온도가
    곱해진다." 한 바퀴 돌리면 이 개념은 네 거다.

숙제 대부분이 계산이 아니라 절차(①②③)라서, 답을 붙이는 것보다 이 쪽이 맞다.
막힘없이 말이 나오면 된 것이고, 안 나오면 어디가 빈지 그 자리에서 안다.

⚠ 처음에 이걸 '정답' 이라는 낱말로 셌다가 **10/125 라고 잘못 말했다.**
  실제로는 101/125 가 이미 하고 있었다. 낱말이 아니라 **하는 일**로 센다.

붙일 문장은 **지어내지 않는다.** 강의마다 마지막 절에 "오늘 들고 갈 한
문장"(`.big`)이 이미 있다. 그 문장을 그대로 가져다 쓴다 — 새로 쓰면 강의가
말한 것과 다른 것을 외우게 할 수 있다.

    python3 tools/lec_selfcheck.py           # 어디에 없는지
    python3 tools/lec_selfcheck.py --write   # 없는 곳에 넣는다
    python3 tools/lec_selfcheck.py --check   # 하나라도 없으면 빨간불
"""
import glob
import html
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HW = re.compile(r'(<div class="hw"><b>직접 해보기[^<]*</b><br>)([\s\S]*?)(</div>)')
BIG = re.compile(r'<div class="big"[^>]*>([\s\S]*?)</div>')
# 이미 하고 있는 꼴. 낱말이 아니라 **시키는 일**을 본다.
# ⚠ 처음엔 '입으로 말해' 를 통째로 찾다가, 사이에 말이 낀 것을 못 잡았다 —
#   013 은 "그리고 입으로 근거(전자 배치)를 **말해**" 라고 이미 시키고 있었는데
#   못 보고 한 줄을 더 붙였다. 두 번 시키는 숙제가 되었다.
#   '말해/설명해/소리 내' 라는 **시키는 말**만 본다.
SAYS = re.compile(r'(말해|말해봐|설명해|소리 ?내|읊)')


def takeaway(src):
    """마지막 '오늘 들고 갈 한 문장'. 없으면 빈 글자."""
    got = BIG.findall(src)
    if not got:
        return ''
    t = html.unescape(re.sub(r'<[^>]+>', '', got[-1]))
    return re.sub(r'\s+', ' ', t).strip()


def scan(path):
    src = open(path, encoding='utf-8').read()
    m = HW.search(src)
    if not m:
        return src, None, '숙제 칸이 없다'
    if SAYS.search(m.group(2)):
        return src, None, None
    line = takeaway(src)
    if not line:
        return src, None, '들고 갈 한 문장이 없다 — 사람이 써야 한다'
    return src, (m, line), None


# 숙제는 대개 "한 바퀴 돌리면 이 개념은 네 거다." 로 닫는다. 그 뒤에 붙이면
# 닫는 말이 두 번 나온다 — 말해 보라는 문장은 **닫는 말 앞**에 들어가야 한다.
CLOSER = re.compile(r'\s*(한 바퀴[^.]*\.|이 정도면[^.]*\.|여기까지[^.]*\.)\s*$')


def add(src, m, line):
    body = m.group(2).rstrip()
    closer = ''
    c = CLOSER.search(body)
    if c:
        closer = ' ' + c.group(1)
        body = body[:c.start()].rstrip()
    if not body.endswith(('.', '!', '?', '다', '야', '어')):
        body += '.'
    # 강의가 쓰는 말투 그대로. 따옴표는 이미 붙어 있는 문장이 많아 두 번 안 씌운다.
    quoted = line if line.startswith(('"', '“', "'")) else '"%s"' % line
    said = ' 그리고 입으로 말해. %s' % quoted
    if not closer:
        closer = ' 막힘없이 나오면 이 개념은 네 거다.'
    return src[:m.start(2)] + body + said + closer + src[m.end(2):]


# ── 예제 · 함정 ────────────────────────────────────────────────────
# 선생님 결정(2026-08-09): **예제는 모두 만든다.** 37편이 비어 있었고 채웠다.
# 처음 배우는 사람에게는 다 풀린 예제가 스스로 풀기보다 크게 남는다 —
# 규칙을 볼 여유가 생기기 때문이다(worked-example effect).
# 함정도 같이 본다. 다섯 편이 비어 있었고 16회차에서 채웠다.
def parts_missing():
    out = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'lec-*.html'))):
        s = open(p, encoding='utf-8').read()
        lack = [n for n, pat in (('예제', 'class="eg"'), ('함정', 'class="trap"'))
                if pat not in s]
        if lack:
            out.append((os.path.basename(p), ' · '.join(lack)))
    return out


def main():
    write = '--write' in sys.argv
    check = '--check' in sys.argv
    files = sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))
    missing, blocked, done = [], [], 0
    for p in files:
        src, todo, why = scan(p)
        if why:
            blocked.append((os.path.basename(p), why))
            continue
        if not todo:
            done += 1
            continue
        missing.append(os.path.basename(p))
        if write:
            m, line = todo
            open(p, 'w', encoding='utf-8').write(add(src, m, line))

    print('강의 %d장 · 숙제에 스스로 확인할 기준이 있는 것 %d장' % (len(files), done))
    lack = parts_missing()
    print('예제·함정이 다 있는 강의 %d장' % (len(files) - len(lack)))
    if lack:
        print('\n비어 있는 것 %d장' % len(lack))
        for n, w in lack:
            print('   %-44s %s 없음' % (n, w))
    if write and missing:
        print('넣었다 %d장' % len(missing))
        for n in missing:
            print('   ', n)
    elif missing:
        print('\n없는 것 %d장' % len(missing))
        for n in missing:
            print('   ', n)
    if blocked:
        print('\n사람이 봐야 하는 것 %d장' % len(blocked))
        for n, w in blocked:
            print('   %-44s %s' % (n, w))
    if check and (missing or blocked or lack):
        print('\nFAIL')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
