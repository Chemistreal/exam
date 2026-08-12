#!/usr/bin/env python3
"""강의 125강에 **확인 문제**를 붙인다 — 이미 사람이 검수한 문항에서 골라서.

무엇을 하나
-----------
`tools/lecture_map.py` 의 표를 보고, `donghyung/` 의 검수된 2,490문항 가운데
강의마다 **세 문항**을 골라 `lec-*.html` 안에 박아 넣는다.

    python3 tools/lecture_quiz.py            # 넣는다(고쳐 쓴다)
    python3 tools/lecture_quiz.py --check    # 어긋나면 종료 코드 1

왜 파일 안에 박나 (바깥에서 안 받아 오나)
-----------------------------------------
이 저장소의 규칙이다 — **바깥 stylesheet·script 를 만나면 브라우저는 그리기를
멈추고 기다린다.** 글꼴 한 줄 때문에 첫 화면이 13초였던 일을 겪었다. 확인
문제도 마찬가지라, 받아 오지 않고 처음부터 글 안에 있게 한다. 세 문항이
2.4KB 남짓이라 20KB짜리 강의록에 얹어도 첫 그림이 안 늦는다. 덤으로
**오프라인에서도 열린다** — 서비스워커가 강의록을 통째로 들고 있으므로.

어떻게 고르나
-------------
  1. `lecture_map.matches()` 가 준 순위대로 (개념이 먼저, 지문이 나중)
  2. 같은 순위면 **출처를 돌아가며** 뽑는다 — 세 문항이 한 시험에서만 나오면
     그 시험을 본 학생에게는 셋 다 이미 푼 문제다
  3. 한 문항은 **최대 두 강의**까지만 쓴다. 안 그러면 종합 강의 열 개가
     같은 문항을 돌려 쓴다
  4. 뽑은 것은 **고정이다** — 같은 강의는 늘 같은 세 문항이다. 그래야
     선생님이 한 번 보고 «이건 아니다» 를 말할 수 있다

무엇을 안 하나
--------------
  · 문항을 **짓지 않는다.** 고르기만 한다
  · 정답을 처음부터 보여 주지 않는다. 학생이 고른 뒤에 펼친다
    (오답 노트가 이미 쓰는 규칙이다 — "먼저 스스로 풀게 하고")
  · 두 문항도 못 찾은 강의는 **비운다.** 억지로 채우면 «이 강의를 들으면
    이걸 풀 수 있다» 가 거짓이 된다
"""

import glob
import html
import io
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lecture_map import LECTURE_MAP, matches, area_of   # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PER_LECTURE = 3          # 한 강의에 세 문항 — 강의 끝나고 실제로 풀 만한 양
MIN_LECTURE = 2          # 두 개도 못 채우면 아예 안 붙인다
MAX_REUSE = 2            # 한 문항이 설 수 있는 강의 수

BEGIN = '<!-- 확인문제:시작 (tools/lecture_quiz.py 가 넣습니다. 손으로 고치지 마세요) -->'
END = '<!-- 확인문제:끝 -->'


def load_pool():
    """검수된 문항만 모은다. 순서는 파일 이름 · 문항 번호로 **고정**한다."""
    pool = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'donghyung', '*.json'))):
        if '_template' in f:
            continue
        with io.open(f, encoding='utf-8') as fh:
            d = json.load(fh)
        qs = d.get('questions') if isinstance(d, dict) and 'questions' in d else d
        if not isinstance(qs, dict):
            continue
        src = os.path.basename(f)[:-5]
        for k in sorted((x for x in qs if str(x).isdigit()), key=int):
            v = qs[k]
            if not isinstance(v, dict) or not v.get('verified'):
                continue
            if not (v.get('stem') and v.get('choices') and v.get('answer')):
                continue
            v = dict(v)
            v['_id'] = src + '#' + str(k)
            v['_src'] = src
            pool.append(v)
    return pool


def choose(pool):
    """강의번호 → 뽑은 문항들. 붙이는 차례가 뒤에 오지 않게 **작은 강의부터** 준다.

    ⚠ 후보가 적은 강의부터 고른다. 큰 강의가 먼저 집어 가면 후보가 셋뿐인
      강의가 빈손이 된다 — 많이 가진 쪽이 나중에 고르는 것이 맞다.
    """
    cand = {}
    for n in range(1, 126):
        hits = []
        for q in pool:
            r = matches(n, q)
            if r is not None:
                hits.append((r, q))
        hits.sort(key=lambda rq: (rq[0], rq[1]['_id']))
        cand[n] = hits

    used = {}
    out = {}
    for n in sorted(cand, key=lambda x: (len(cand[x]), x)):
        picked, seen_src = [], set()
        # 첫 바퀴 — 출처를 돌아가며(같은 시험에서 몰아 뽑지 않는다)
        for _r, q in cand[n]:
            if len(picked) >= PER_LECTURE:
                break
            if used.get(q['_id'], 0) >= MAX_REUSE or q['_src'] in seen_src:
                continue
            picked.append(q)
            seen_src.add(q['_src'])
        # 둘째 바퀴 — 그래도 모자라면 같은 출처도 받는다
        for _r, q in cand[n]:
            if len(picked) >= PER_LECTURE:
                break
            if used.get(q['_id'], 0) >= MAX_REUSE or q in picked:
                continue
            picked.append(q)
        if len(picked) >= MIN_LECTURE:
            for q in picked:
                used[q['_id']] = used.get(q['_id'], 0) + 1
            out[n] = picked
    return out, cand


def esc(s):
    return html.escape(str(s or ''), quote=True)


def block_html(n, picks):
    """확인 문제 한 덩이. 정답은 학생이 고른 뒤에 펼친다.

    ⚠ 옷(CSS)과 손(JS)을 **이 덩이 안에** 넣는다. `<head>` 에 넣었더니
      `tools/theme.py` 가 124장을 «옷이 안 맞는다» 고 잡았다 — 그 자가 옳다.
      머리는 그 자가 맡은 자리다. 본문 안의 `<style>` 은 HTML5 에서 성한
      것이고, 덩이를 지우면 옷도 같이 지워져 자국이 안 남는다.
    """
    parts = [BEGIN, CSS, JS,
             '<div class="sec lq" data-lecture-quiz>',
             '<div class="sec__h"><span class="sec__no">✓</span>'
             '<span class="sec__t">확인 문제</span></div>',
             '<p class="lq__lead">방금 배운 것으로 풀 수 있는 '
             f'{len(picks)}문항입니다. 답을 고르면 해설이 열립니다 — '
             '<b>먼저 스스로 고르고</b> 나서 보세요.</p>']
    for i, q in enumerate(picks, 1):
        parts.append(f'<div class="lq__q" data-lq="{i}">')
        parts.append(f'<div class="lq__stem"><b>{i}.</b> '
                     + esc(q['stem']).replace('\n', '<br>') + '</div>')
        parts.append(f'<ol class="lq__opts" data-ans="{int(q["answer"])}">')
        for c in q['choices']:
            parts.append('<li><button type="button" class="lq__opt">'
                         + esc(c) + '</button></li>')
        parts.append('</ol>')
        why = q.get('explanationHtml') or ('<p>' + esc(q.get('explanation', '')) + '</p>')
        parts.append('<div class="lq__why" hidden>')
        parts.append('<div class="lq__ans">정답 <b>'
                     + '①②③④⑤'[int(q['answer']) - 1] + '</b></div>')
        parts.append(why)
        if q.get('misconception'):
            parts.append('<div class="lq__miss"><b>자주 걸리는 자리</b> '
                         + esc(q['misconception']) + '</div>')
        parts.append('</div></div>')
    parts.append('<p class="lq__src">검수된 동형문제에서 골랐습니다 '
                 '(사람이 확인한 2,490문항).</p>')
    parts.append('</div>')
    parts.append(END)
    return '\n'.join(parts)


CSS = """<style data-lq-css>
.lq__lead{font-size:14px;opacity:.85}
.lq__q{border:1px solid var(--line,#E8E4DA);border-radius:12px;padding:14px 16px;margin:12px 0}
.lq__stem{margin-bottom:10px;line-height:1.7}
.lq__opts{list-style:none;margin:0;padding:0;display:grid;gap:6px}
.lq__opts li{margin:0}
.lq__opt{display:block;width:100%;text-align:left;padding:9px 12px;font:inherit;line-height:1.55;
  border:1px solid var(--line,#E8E4DA);border-radius:9px;background:transparent;cursor:pointer}
.lq__opt:hover{border-color:var(--teal,#0E5A4C)}
.lq__opt:focus-visible{outline:2px solid var(--teal,#0E5A4C);outline-offset:2px}
.lq__opt.is-key{border-color:var(--teal,#0E5A4C);box-shadow:inset 3px 0 0 var(--teal,#0E5A4C)}
.lq__opt.is-miss{opacity:.55;text-decoration:line-through}
.lq__why{margin-top:11px;padding-top:11px;border-top:1px dashed var(--line,#E8E4DA);font-size:14px;line-height:1.75}
.lq__ans{font-weight:700;margin-bottom:6px}
.lq__miss{margin-top:8px;font-size:13.5px;opacity:.88}
.lq__src{font-size:12.5px;opacity:.6;margin-top:10px}
@media print{.lq__why{display:block!important}}
</style>"""

JS = """<script data-lq-js>
/* 고르면 그때 해설이 열린다. 처음부터 열어 두면 학생은 읽고 지나간다 —
   자기 판단을 한 번 걸고 넘어가야 «왜 하필 그걸 골랐는지» 를 짚을 수 있다.
   인쇄할 때는 CSS 가 해설을 펼친다(종이에는 누를 것이 없다). */
document.addEventListener('click', function (e) {
  var b = e.target.closest && e.target.closest('.lq__opt');
  if (!b) return;
  var ol = b.closest('.lq__opts'), q = b.closest('.lq__q');
  if (!ol || !q || ol.dataset.done) return;
  ol.dataset.done = '1';
  var key = Number(ol.dataset.ans);
  [].forEach.call(ol.querySelectorAll('.lq__opt'), function (o, i) {
    if (i + 1 === key) o.classList.add('is-key');
    else if (o === b) o.classList.add('is-miss');
  });
  var why = q.querySelector('.lq__why');
  if (why) why.hidden = false;
});
</script>"""


def strip_block(s):
    """덩이를 걷어낸다 — **앞뒤 빈 줄까지** 같이.

    ⚠ 처음에는 덩이만 지웠다. 그랬더니 넣을 때마다 빈 줄이 하나씩 늘어서
      **두 번 돌리면 결과가 달라졌다**(자가 124장을 «어긋난다» 고 잡았다 —
      옳은 말이었다). 넣는 자와 재는 자가 같은 글을 만들지 못하면 그 자는
      영영 빨간불이다. 앞뒤 줄바꿈을 먹고 한 줄로 되돌린다.
    """
    return re.sub(r'\n*' + re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n*',
                  '\n', s, flags=re.S)


def apply_to_page(path, block):
    with io.open(path, encoding='utf-8') as fh:
        s = fh.read()
    base = strip_block(s)
    if block is None:
        return base, base != s
    # 「직접 해보기(숙제)」 앞에 넣는다 — 확인 문제를 풀고 나서 숙제로 간다.
    hw = base.rfind('<div class="hw">')
    if hw < 0:
        hw = base.rfind('</body>')
    out = base[:hw] + block + '\n\n' + base[hw:]
    return out, out != s


def main():
    check = '--check' in sys.argv
    pool = load_pool()
    picks, cand = choose(pool)
    pages = sorted(glob.glob(os.path.join(ROOT, 'lec-*.html')))
    num = {}
    for p in pages:
        m = re.search(r'lec-(\d{3})', os.path.basename(p))
        if m:
            num[int(m.group(1))] = p

    changed, missing = [], []
    for n in range(1, 126):
        p = num.get(n)
        if not p:
            continue
        got = picks.get(n)
        if not got:
            missing.append(n)
        block = block_html(n, got) if got else None
        out, diff = apply_to_page(p, block)
        if diff:
            changed.append(os.path.basename(p))
            if not check:
                with io.open(p, 'w', encoding='utf-8') as fh:
                    fh.write(out)

    have = 125 - len(missing)
    print(f'확인 문제가 붙은 강의 {have}강 / 125강 · 쓴 문항 '
          f'{len({q["_id"] for v in picks.values() for q in v})}개')
    if missing:
        print(f'  비운 강의 {len(missing)}강 — 풀에 맞는 문항이 {MIN_LECTURE}개도 없다: '
              + ', '.join(f'{n:03d}' for n in missing))
    if check:
        if changed:
            print(f'\n어긋난 강의 {len(changed)}장 — `python3 tools/lecture_quiz.py` 로 다시 넣으세요.')
            for c in changed[:10]:
                print('   ', c)
            return 1
        print('\n강의록의 확인 문제가 표와 맞습니다.')
        return 0
    print(f'\n고친 강의록 {len(changed)}장')
    return 0


if __name__ == '__main__':
    sys.exit(main())
