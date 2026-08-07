#!/usr/bin/env python3
"""강의를 보고 나면 **왔던 자리로** 돌아가야 한다.

강의 페이지(lec-*.html) 맨 위에는 `‹ 파이널로` 가 있고, 그 주소는
`final.html` 로 **박혀** 있었다. 그런데 학생이 강의를 여는 길은 하나다 —
자기 성적표(`final.html#r=…`)의 '오답 개념 클리닉' 에서 누르는 것.

그래서 이렇게 됐다.

    성적표 → 개념강의 → '파이널로' → **시험 목록**(남의 이름과 점수가 있는 곳)
                                     → 코드를 모르니 잠금 화면에 갇힌다

학생은 자기 성적표로 돌아가려 했는데 갈 수가 없다. 주소를 손으로 칠 수도
없다(성적표 주소에는 답안이 통째로 실려 있다).

고치는 법. 성적표에서 강의로 나갈 때 **돌아올 자리를 주소에 실어** 보내고
(`?from=…`), 강의 페이지가 그것으로 돌아가는 단추를 만든다. 실려 오지 않으면
(선생님이 목록에서 강의를 연 경우) 예전 그대로 목록으로 간다.

⚠ 주소에 싣는다(sessionStorage 가 아니다). 강의는 **새 탭**에서 열리는데
  (rel=noopener) 새 탭은 이 탭의 sessionStorage 를 물려받지 않는다. 같은 탭
  에서는 한 번 적힌 것이 계속 남아, 나중에 목록에서 연 강의까지 성적표로
  보내 버린다.

조각을 125장에 손으로 붙이면 언젠가 몇 장이 빠진다. 여기서 넣고, 여기서 센다.

    python3 tools/lec_back.py            # 몇 장에 붙어 있는지
    python3 tools/lec_back.py --write    # 빠진 장에 붙인다
    python3 tools/lec_back.py --check    # 한 장이라도 빠지면 빨간불
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = 'data-lec-back'
TAIL = '</main></body></html>'

SNIP = '''
<script ''' + MARK + '''>
/* 성적표에서 왔으면 성적표로 돌려보낸다(tools/lec_back.py 가 넣는다).

   학생이 강의를 여는 길은 하나다 — 자기 성적표의 '오답 개념 클리닉'.
   그런데 돌아가는 단추가 시험 목록으로 박혀 있어서, 눌러도 자기 성적표가
   아니라 남의 이름과 점수가 있는 목록(잠금 화면)이 나왔다.

   주소를 **받기만** 하고 믿지는 않는다. 같은 곳의 final.html 이고 성적표(#r=)
   일 때만 쓴다 — 아니면 손대지 않고 예전대로 목록으로 간다. 남이 심어 둔
   주소로 학생을 내보내는 길을 열지 않는다. */
(function () {
  function ok(raw) {
    if (!raw) return null;
    try {
      var u = new URL(raw, location.href);
      if (u.origin !== location.origin) return null;
      if (!/(^|\\/)final\\.html$/.test(u.pathname)) return null;
      if (!/[#&]r=/.test(u.hash)) return null;
      return u.href;
    } catch (e) { return null; }
  }
  try {
    var a = document.querySelector('a.back');
    if (!a) return;
    /* **주소에 실려 온 것만** 본다. 강의는 새 탭에서 열리고(rel=noopener)
       새 탭은 sessionStorage 를 물려받지 않으니 그쪽은 도움이 안 되는데,
       같은 탭에서는 한 번 적힌 것이 계속 남아 목록에서 연 강의까지 성적표로
       보내 버린다. 얻는 것 없이 끈적하기만 하다. */
    var to = ok(new URL(location.href).searchParams.get('from'));
    if (!to) return;
    a.href = to;
    a.textContent = '\\u2039 \\uc131\\uc801\\ud45c\\ub85c';   /* ‹ 성적표로 */
  } catch (e) {}
})();
</script>
'''.rstrip() + '\n'

# 예전에 붙여 둔 조각을 통째로 갈아 끼운다 — 고칠 때 125장을 손으로 못 고친다.
OLD = re.compile(r'\n?<script ' + MARK + r'>[\s\S]*?</script>\n?')


def pages():
    return sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))


def has(src):
    return MARK in src


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    files = pages()
    if not files:
        print('강의 페이지를 못 찾았습니다.')
        return 1

    missing, noback, redone, done = [], [], [], 0
    for p in files:
        rel = os.path.relpath(p, ROOT)
        with open(p, encoding='utf-8') as fh:
            s = fh.read()
        # 돌아가는 단추가 없는 장은 붙일 곳이 없다 — 세어서 알린다.
        if 'class="back"' not in s:
            noback.append(rel)
            continue
        if has(s):
            done += 1
            # 조각을 고쳤으면 이미 붙어 있는 것도 갈아 끼운다.
            if write:
                fresh = OLD.sub('\n', s).replace(TAIL, SNIP + TAIL)
                if fresh != s:
                    with open(p, 'w', encoding='utf-8') as fh:
                        fh.write(fresh)
                    redone.append(rel)
            continue
        if TAIL not in s:
            noback.append(rel + '(끝맺음이 다릅니다)')
            continue
        missing.append(rel)
        if write:
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(s.replace(TAIL, SNIP + TAIL))

    if write:
        print('붙였습니다: ' + str(len(missing)) + '장 · 갈아 끼운 것 ' + str(len(redone))
              + '장 · 그대로 ' + str(done - len(redone)) + '장')
        if noback:
            print('건너뜀(돌아가는 단추가 없음): ' + ', '.join(noback[:5])
                  + ('…' if len(noback) > 5 else ''))
        return 0

    print('강의 ' + str(len(files)) + '장 · 돌아가는 자리 기억 ' + str(done) + '장'
          + (' · 빠진 곳 ' + str(len(missing)) + '장' if missing else '')
          + (' · 단추 없음 ' + str(len(noback)) + '장' if noback else ''))
    if check and missing:
        print('')
        for m in missing[:10]:
            print('  ✗ ' + m)
        if len(missing) > 10:
            print('  … ' + str(len(missing) - 10) + '장 더')
        print('\nFAIL 성적표에서 온 학생이 돌아갈 길이 없는 강의가 있습니다.')
        print('     python3 tools/lec_back.py --write 로 붙이세요.')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
