#!/usr/bin/env python3
"""DT 성적표에서 연 강의에는 **DT 의 말**로 한 줄을 띄운다.

강의 128장은 두 곳에서 열린다 — 이 저장소의 파이널 진단 성적표(final.html),
그리고 DT 주간 성적표(https://chemistreal.github.io/DT/report.html, 새 탭).
그런데 강의 맨 위는 파이널 쪽 말뿐이다.

    ‹ 파이널로                         → 누르면 시험 목록(잠금 화면)
    이번 진단에서 <b>…</b>가 보강으로 잡혔어.

DT 학생은 «파이널» 을 본 적이 없다. 그래서 DT 가 주소에 표시를 실어 보내면
(`?from=dt&c=ch2&r=5#s03`) 맨 위에 한 줄을 띄우고 파이널 말을 걷는다.

    DT 화학Ⅱ 5회에서 틀린 개념입니다 · 성적표로 돌아가기

주소 약속 (DT 가 #절 앞에 붙인다)
    from=dt           이것이 없으면 아무것도 안 바뀐다(예전 그대로)
    c=ch1|ch2|gc      화학Ⅰ · 화학Ⅱ · 일반화학
    r=1…99            회차(0 으로 시작하지 않는 정수)
    c·r 가 없거나 어긋나면 «DT 성적표에서 틀린 개념입니다» 로 쓴다.
    주소의 글자는 **화면에 한 글자도 옮기지 않는다** — 정해 둔 값과 맞는지만
    보고, 쓰는 글자는 이 파일에 적힌 것뿐이다.

«성적표로 돌아가기» — 강의는 새 탭(noopener)에서 열렸다. 그러니 먼저 탭을
닫아 본다(`window.close()`). 닫히지 않으면(브라우저가 막으면) 뒤로 갈 곳이
있을 때 뒤로, 없으면 DT 성적표 첫 화면으로 간다. **학생 코드는 주소에 싣지
않는다.**

조각을 128장에 손으로 붙이면 언젠가 몇 장이 빠진다. 여기서 넣고, 여기서 센다.

    python3 tools/lec_dt_banner.py            # 몇 장에 붙어 있는지
    python3 tools/lec_dt_banner.py --write    # 빠진 장에 붙이고 옛 조각은 갈아 끼운다
    python3 tools/lec_dt_banner.py --check    # 한 장이라도 빠지거나 옛 조각이면 빨간불
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = '<!-- lec-dt-banner:start (tools/lec_dt_banner.py 가 넣습니다. 손으로 고치지 마세요) -->'
END = '<!-- lec-dt-banner:end -->'
TAIL = '</main></body></html>'
BACK = '<script data-lec-back>'

SNIP = START + '''
<style data-lec-dt>
/* DT 성적표에서 온 학생에게만 뜨는 한 줄. 문서 흐름 맨 위에 앉는다(떠 있지
   않다) — #s03 으로 열어도 절 머리를 가리지 않는다. */
.dtb{display:block;margin:10px 0 4px;padding:10px 14px;
  background:var(--wash,#EDF4F1);border:1px solid var(--line,#E8E4DA);border-left:3px solid var(--teal,#0E5A4C);
  border-radius:9px;color:var(--ink,#23201b);font-size:14px;line-height:1.55}
.dtb__t{font-weight:600}
.dtb__sep{color:var(--muted,#6f6a5e)}
.dtb__go{color:var(--teal,#0E5A4C);font-weight:700;text-decoration:underline;text-underline-offset:2px;
  white-space:nowrap;display:inline-block;padding:4px 0}
@media print{.dtb{display:none!important}}
</style>
<script data-lec-dt>
/* DT 주간 성적표에서 연 강의(?from=dt&c=…&r=…)에 한 줄을 띄운다 —
   tools/lec_dt_banner.py 머리말. 주소의 글자는 화면에 옮기지 않는다:
   정해 둔 값과 맞는지만 보고, 쓰는 글자는 아래 표에 있는 것뿐이다. */
(function () {
  var DT = 'https://chemistreal.github.io/DT/report.html';
  var SUBJ = { ch1: '\\ud654\\ud559\\u2160', ch2: '\\ud654\\ud559\\u2161', gc: '\\uc77c\\ubc18\\ud654\\ud559' };
  try {
    var q = new URL(location.href).searchParams;
    if (q.get('from') !== 'dt') return;
    var c = q.get('c'), r = q.get('r');
    var subj = (c && Object.prototype.hasOwnProperty.call(SUBJ, c)) ? SUBJ[c] : null;
    var n = (r && /^[1-9][0-9]?$/.test(r)) ? String(Number(r)) : null;
    var main = document.querySelector('main');
    if (!main) return;

    /* 파이널 쪽 돌아가는 단추를 걷는다 — 누르면 시험 목록(잠금 화면)이다.
       .back 에 display 가 걸려 있어 hidden 속성만으로는 안 숨는다. */
    var back = main.querySelector('a.back');
    if (back) back.style.display = 'none';

    /* 첫 칸의 «이번 진단에서 …가 보강으로 잡혔어.» 는 파이널 진단의 말이다.
       그 한 문장만 걷고 나머지(이 1강을 끝까지 …)는 둔다. 문장 끝을 못 찾으면
       칸을 통째로 접는다. */
    var hw = main.querySelector('.hw');
    if (hw && /^\\s*\\uc774\\ubc88 \\uc9c4\\ub2e8\\uc5d0\\uc11c/.test(hw.textContent)) {
      var cut = false, drop = [];
      for (var k = hw.firstChild; k && !cut; k = k.nextSibling) {
        var i = k.nodeType === 3 ? k.nodeValue.indexOf('. ') : -1;
        if (i >= 0) { k.nodeValue = k.nodeValue.slice(i + 2); cut = true; }
        else drop.push(k);
      }
      if (cut) drop.forEach(function (x) { hw.removeChild(x); });
      else hw.style.display = 'none';
    }

    var box = document.createElement('div');
    box.className = 'dtb';
    box.setAttribute('role', 'note');
    box.setAttribute('data-lec-dt-banner', '');
    var t = document.createElement('span');
    t.className = 'dtb__t';
    /* DT {과목} {N}회에서 틀린 개념입니다 / DT 성적표에서 틀린 개념입니다 */
    t.textContent = (subj && n)
      ? 'DT ' + subj + ' ' + n + '\\ud68c\\uc5d0\\uc11c \\ud2c0\\ub9b0 \\uac1c\\ub150\\uc785\\ub2c8\\ub2e4'
      : 'DT \\uc131\\uc801\\ud45c\\uc5d0\\uc11c \\ud2c0\\ub9b0 \\uac1c\\ub150\\uc785\\ub2c8\\ub2e4';
    var sep = document.createElement('span');
    sep.className = 'dtb__sep';
    sep.setAttribute('aria-hidden', 'true');
    sep.textContent = ' \\u00b7 ';
    var go = document.createElement('a');
    go.className = 'dtb__go';
    go.href = DT;
    go.textContent = '\\uc131\\uc801\\ud45c\\ub85c \\ub3cc\\uc544\\uac00\\uae30';   /* 성적표로 돌아가기 */
    /* 새 탭에서 열렸으니 닫아서 성적표 탭으로 돌려보낸다. 브라우저가 닫기를
       막으면 잠시 뒤 뒤로(갈 곳이 있을 때) 또는 DT 성적표 첫 화면으로. */
    go.addEventListener('click', function (e) {
      if (e.button || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      e.preventDefault();
      try { window.close(); } catch (x) {}
      setTimeout(function () {
        if (window.closed) return;
        if (history.length > 1) history.back();
        else location.href = DT;
      }, 300);
    });
    box.appendChild(t);
    box.appendChild(sep);
    box.appendChild(go);
    if (back) main.insertBefore(box, back);
    else main.insertBefore(box, main.firstChild);
    document.documentElement.setAttribute('data-from', 'dt');
  } catch (e) {}
})();
</script>
''' + END + '\n'

BLOCK = re.compile(re.escape(START.split(' (')[0]) + r'[\s\S]*?' + re.escape(END) + r'\n?')


def pages():
    return sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))


def fix(s):
    """조각을 한 벌만, 지금 것으로.

    있으면 **그 자리에서** 갈아 끼운다. 없으면 `<script data-lec-back>` 바로
    앞에(없으면 끝맺음 앞에) 넣는다 — lec_back.py --write 는 자기 조각을 늘
    끝맺음 바로 앞으로 옮기므로, 그 앞에 앉아야 두 자가 서로 자리를 안 뺏는다."""
    if BLOCK.search(s):
        first = [True]

        def one(m):
            if first[0]:
                first[0] = False
                return SNIP
            return ''
        return BLOCK.sub(one, s)
    if TAIL not in s:
        return None
    at = s.find(BACK)
    if at >= 0:
        return s[:at] + SNIP + s[at:]
    return s.replace(TAIL, SNIP + TAIL, 1)


def main():
    write = '--write' in sys.argv[1:]
    check = '--check' in sys.argv[1:]
    files = pages()
    if not files:
        print('강의 페이지를 못 찾았습니다.')
        return 1

    missing, stale, odd, done = [], [], [], 0
    for p in files:
        rel = os.path.relpath(p, ROOT)
        with open(p, encoding='utf-8') as fh:
            s = fh.read()
        n = len(BLOCK.findall(s))
        if n == 1 and SNIP in s:
            done += 1
            continue
        (stale if n else missing).append(rel)
        if write:
            fresh = fix(s)
            if fresh is None:
                odd.append(rel)
                continue
            with open(p, 'w', encoding='utf-8') as fh:
                fh.write(fresh)

    if write:
        print('붙였습니다: ' + str(len(missing) - len([o for o in odd if o in missing])) + '장 · 갈아 끼운 것 '
              + str(len(stale) - len([o for o in odd if o in stale])) + '장 · 그대로 ' + str(done) + '장')
        if odd:
            print('건너뜀(끝맺음이 다릅니다): ' + ', '.join(odd[:5]) + ('…' if len(odd) > 5 else ''))
            return 1
        return 0

    print('강의 ' + str(len(files)) + '장 · DT 한 줄 ' + str(done) + '장'
          + (' · 빠진 곳 ' + str(len(missing)) + '장' if missing else '')
          + (' · 옛 조각 ' + str(len(stale)) + '장' if stale else ''))
    bad = missing + stale
    if check and bad:
        print('')
        for m in bad[:10]:
            print('  ✗ ' + m)
        if len(bad) > 10:
            print('  … ' + str(len(bad) - 10) + '장 더')
        print('\nFAIL DT 성적표에서 연 학생에게 파이널 말만 보이는 강의가 있습니다.')
        print('     python3 tools/lec_dt_banner.py --write 로 붙이세요.')
        return 1
    if check:
        print('\nPASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
