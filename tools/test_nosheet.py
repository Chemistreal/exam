#!/usr/bin/env python3
"""브라우저를 띄우는 검사는 **모두 시트를 막고 시작한다.**

2026-08-12 에 있었던 일
-----------------------
선생님이 물으셨다 — *"이런애들 지금 시험 안봤는데 왜 올라가있어?"*

재어 보니 이랬다. 브라우저 검사 스물넷 가운데 **아홉이 시트를 안 막고**
있었고, 그 가운데 셋은 **채점까지 했다.** 채점은 곧 시트로 보내는 일이다.
POST 를 세어 확인했다.

    tests/blank-vs-wrong.js      POST 2번   이름 «무응답점검»
    tests/area-verdict.js        POST 1번   이름 «분류점검»
    tests/answer-not-before.js   POST 2번   이름 «자료링크점검»

판이 한 번 돌 때마다 학원 시트에 그 이름들이 쌓이고 있었다. 나머지 여섯은
쓰지는 않았지만 **진짜 명단을 읽었다** — 실패하면 실제 학생 이름과 점수가
러너 로그로 흘러나온다.

`tests/_nosheet.js` 는 이 일을 막으려고 진작에 만들어 둔 자다. 그 머리말에
이렇게 적혀 있었다 — *"검사가 학원 시트를 읽는 것 자체가 안 될 일이다."*
**있는데 안 걸었다.** 걸지 않은 자는 없는 자와 같다.

그래서 이 자가 센다
-------------------
`chromium` 을 부르는 검사 파일마다 `_nosheet.js` 를 쓰는지 본다. 안 쓰면
빨간불이다. 손으로 `route()` 를 적어 막는 것도 **안 쳐 준다** —

  · `script.google.com` 만 막으면 302 로 넘어가는
    `script.googleusercontent.com` 을 못 덮는다
  · 그냥 끊으면(`abort`) 앱이 '맞추는 중' 에서 안 넘어가는 자리가 있다
  · 화면 하나에만 걸면 나중에 여는 화면이 샌다

세 가지 다 이 저장소가 값을 치르고 배운 것이고, `_nosheet.js` 안에 들어 있다.
같은 것을 손으로 다시 만들면 그 배움을 안 쓰는 것이 된다.

실행:
    python3 tools/test_nosheet.py            # 어디가 안 막혔나
    python3 tools/test_nosheet.py --check    # 안 막힌 것이 있으면 종료 코드 1
"""

import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 브라우저를 띄우지 않는 도우미. 여기 있는 것은 안 센다.
HELPERS = {'_serve.js', '_nosheet.js', '_seal.js', '_watchdog.js', 'run.js'}

# 시트 창구를 부르는 화면. 이 가운데 하나라도 여는 검사는 막아야 한다.
DOORS = re.compile(r'\b(final\.html|hub\.html|final-submit\.html|note\.html)')


def scan():
    rows = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'tests', '*.js'))):
        base = os.path.basename(p)
        if base in HELPERS:
            continue
        try:
            src = io.open(p, encoding='utf-8').read()
        except OSError:
            continue
        if 'chromium' not in src:
            continue                      # 브라우저를 안 띄우는 검사
        undefined = None
        # 머리말(주석)만 보고 «막았다» 고 치지 않는다 — 실제로 부르는지 본다.
        call = re.search(r'\bnoSheet\s*\(\s*([A-Za-z_$][\w$]*)\s*\)', src)
        wired = bool(call)
        required = "require('./_nosheet.js')" in src
        # **부른 자와 도는 자는 다르다.** 2026-08-12, 열다섯 곳에 이 줄을 걸면서
        # 두 곳에 `noSheet(browser)` 를 적었는데 그 파일이 브라우저를 담아 둔
        # 이름은 `b` 였다. 판에서는 `ReferenceError: browser is not defined` 로
        # 죽었고 — 다행히 죽었다 — 이 자는 그때도 «걸려 있다» 고 답했다.
        # 넘겨주는 이름이 그 파일 안에 실제로 있는지 본다.
        if call:
            nm = call.group(1)
            if not re.search(r'\b(?:const|let|var|function)\s+' + re.escape(nm) + r'\b', src):
                wired = False
                undefined = nm
        # 손으로 막아야만 하는 검사가 하나 있다 — **나가는 POST 를 세는 것**이
        # 목적인 검사다(`tests/silent-resend.js`). 그런 검사는 `_nosheet` 를
        # 쓰면 셀 것이 사라진다. 다만 **말없이 빠져나가지는 못하게** 한다:
        # 까닭을 적고, 창구를 실제로 덮는 자리를 갖춰야 봐 준다.
        # 막는 길은 **둘**이다. 끊거나(abort), 가로채서 내가 지은 답을
        # 주거나(fulfill). 둘 다 진짜 시트에는 한 글자도 안 나간다 —
        # playwright 는 route 를 가로챈 요청을 망으로 안 내보낸다.
        #
        # 처음에는 `abort` 만 쳐 줬는데, 화면에 **자료를 먹여 놓고** 보는
        # 검사는 끊으면 아무것도 안 그려져서 잴 것이 없다(tests/hub-dash.js).
        # 그런 검사가 fulfill 을 쓴다는 이유로 «안 막았다» 고 하면, 자가
        # 맞는 말을 안 하는 것이 된다.
        _flat = src.replace(' ', '')
        excused = ('NOSHEET-예외:' in src
                   and re.search(r"route\(\s*['\"][^'\"]*script\.google", src)
                   and ('r.abort()' in _flat or 'r.fulfill(' in _flat))
        if excused:
            wired = required = True
        # 손으로 막은 자리 — 쳐 주지는 않지만 무엇이 있었는지는 적는다.
        handmade = bool(re.search(r"route\(\s*['\"][^'\"]*(?:script\.google|macros/s)", src))
        opens = bool(DOORS.search(src))
        rows.append({'file': 'tests/' + base, 'wired': wired and required,
                     'handmade': handmade, 'opens': opens,
                     'undefined': undefined,
                     'grades': 'scoreAuto' in src})
    return rows


def main():
    check = '--check' in sys.argv
    rows = scan()
    bad = [r for r in rows if not r['wired']]
    print('브라우저를 띄우는 검사 %d개 · 시트를 막은 것 %d개'
          % (len(rows), len(rows) - len(bad)))
    if bad:
        print('\n⚠ 시트를 안 막은 검사 %d개' % len(bad))
        for r in bad:
            why = []
            if r['grades']:
                why.append('**채점한다 — 시트에 줄을 쓴다**')
            elif r['opens']:
                why.append('창구를 부르는 화면을 연다 — 진짜 명단을 읽는다')
            if r['undefined']:
                why.append('**noSheet(%s) 인데 이 파일에 «%s» 가 없다** — 판에서 터진다'
                           % (r['undefined'], r['undefined']))
            if r['handmade']:
                why.append('손으로 막아 두었지만 그것으로는 모자란다(머리말 참조)')
            print('   %-34s %s' % (r['file'], ' · '.join(why) or '확인 필요'))
        print('\n고치는 법 — launch 바로 뒤에 한 줄:')
        print("    const noSheet = require('./_nosheet.js');")
        print('    await noSheet(browser);   // 화면이 아니라 **브라우저**에 건다')
        if check:
            print('\nFAIL')
            return 1
        return 0
    print('\n모두 막혀 있다 — 검사가 학원 시트를 건드리지 않는다.')
    if check:
        print('PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
