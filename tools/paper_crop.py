#!/usr/bin/env python3
"""시험지 페이지(paper-*.html)의 문항 본문을 **PDF 원문 크롭 그림**으로 바꾼다.

왜 —
  이 열 장은 HWP·PDF 에서 글자를 뽑아 만든 것이라, 그림·표·수식이 통째로
  빠져 있다. 머리말에도 「그림·표 자료가 있는 문항은 지문이 요약본일 수
  있음」이라고 적혀 있었다. 요약본은 문항이 아니다 — kch1to2 1번은
  「다음에 있는 원소들의 중성자수를 모두 합하면?」인데 그 «다음» 이 없다.
  글로는 절대 풀 수 없고, 크롭에는 그 표가 그대로 들어 있다.

  그래서 **뽑은 글이 아니라 원문 크롭을 문항 본문으로 삼는다.**
  뽑은 글은 지우지 않고 접어 둔다 — 그림이 안 뜨면 저절로 펼쳐지고,
  숫자를 복사해 갈 자리로도 쓰인다. 다만 「원문이 아니라 옮긴 것」이라고
  이름을 붙여, 둘이 다를 때 무엇을 믿어야 하는지 헷갈리지 않게 한다.

  정답 표시는 접는 자리 **밖**에 남긴다. 이 페이지들은 학생 시험지가 아니라
  「문제+정답+해설」 페이지라, 정답이 안 보이면 쓰임이 달라진다.

두 번 돌려도 같은 결과가 나온다(이미 바꾼 문항은 건너뛴다).

  python3 tools/paper_crop.py --check    안 바뀐 문항이 몇인지 잰다
  python3 tools/paper_crop.py --write    바꾼다
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRC = '①②③④⑤'

# 쪽 → 크롭 회차. -hwp 는 같은 시험의 다른 추출본이라 크롭을 함께 쓴다.
# 번호가 정말 맞는지는 아래 check_key() 가 정답표로 다시 확인한다.
PAGES = {
    'paper-chem2-1.html':      'chem2-1',
    'paper-kch1to2.html':      'kch1to2',
    'paper-kch1to2-b.html':    'kch1to2-b',
    'paper-kch1to3.html':      'kch1to3',
    'paper-kch1to3-b.html':    'kch1to3-b',
    'paper-kch1u1.html':       'kch1u1',
    'paper-kch1u1-hwp.html':   'kch1u1',
    'paper-kch2final.html':    'kch2final',
    'paper-kch2final-hwp.html':'kch2final',
    'paper-kch2to3.html':      'kch2to3',
}

# kch1to3-b 11번은 정답표와 페이지가 갈린다. 이미 따로 다룬 자리라
# (tools/regrade_kch1to3b_q11.py) 번호가 어긋난 것이 아니다 — 눈감아 준다.
KEY_EXEMPT = {('paper-kch1to3-b.html', 11)}

STYLE = """
/* ── 원문 크롭 ──────────────────────────────────────────────────────
   뽑아 쓴 글이 아니라 시험지에 인쇄된 그대로다. 그림·표·수식이 다 있다. */
.q__img{display:block;width:100%;height:auto;border:1px solid var(--line);
 border-radius:8px;background:#fff;margin:0 0 12px}
.q__imgfail{display:none;font-family:'IBM Plex Sans KR',sans-serif;font-size:.82rem;
 color:var(--rose);background:#FBF1F2;border:1px solid #EBD3D6;border-radius:8px;
 padding:9px 11px;margin:0 0 12px}
.q__key{font-family:'IBM Plex Sans KR',sans-serif;font-size:.86rem;font-weight:600;
 color:var(--teal);margin:0 0 10px}
.q__text{margin:0 0 12px}
.q__text>summary{cursor:pointer;font-family:'IBM Plex Sans KR',sans-serif;
 font-size:.78rem;color:var(--muted2)}
.q__textnote{font-family:'IBM Plex Sans KR',sans-serif;font-size:.74rem;
 color:var(--muted2);margin:8px 0 10px}
"""

BLOCK = re.compile(r'<div class="q" data-area=.*?(?=\n<div class="q" data-area=|\n</div>\s*\n?<script|\Z)', re.S)


def blocks(html):
    """문항 덩이를 차례로 내준다. (시작, 끝) 자리."""
    starts = [m.start() for m in re.finditer(r'<div class="q" data-area=', html)]
    out = []
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else html.find('<script', s)
        if e < 0:
            e = len(html)
        out.append((s, e))
    return out


def exam_key(eid):
    for e in json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8')):
        if e.get('id') == eid:
            return e.get('key') or []
    return []


def convert(page, eid, key, write):
    path = os.path.join(ROOT, page)
    html = open(path, encoding='utf-8').read()
    done = changed = missing = mismatch = 0

    parts, last = [], 0
    for s, e in blocks(html):
        blk = html[s:e]
        parts.append(html[last:s]); last = e

        m = re.search(r'class="q__no">(\d+)<', blk)
        if not m:
            parts.append(blk); continue
        q = int(m.group(1))

        if 'class="q__img"' in blk:      # 이미 바꾼 문항
            done += 1; parts.append(blk); continue

        if not os.path.exists(os.path.join(ROOT, 'crops', eid, f'{q}.png')):
            missing += 1; parts.append(blk); continue

        # 페이지가 표시한 정답과 정답표를 맞춰 본다. 어긋나면 번호가 다른
        # 시험을 가리키고 있다는 뜻이라 **그림을 붙이지 않는다** — 엉뚱한
        # 문제를 원문이라고 내미는 것이 글로만 보여 주는 것보다 나쁘다.
        picked = [CIRC.index(c[1]) + 1
                  for c in re.findall(r'<div class="ch( correct)?">.*?ch__n">(.)<', blk)
                  if c[0]]
        k = key[q - 1] if q - 1 < len(key) else None
        if picked and k and picked[0] != k and (page, q) not in KEY_EXEMPT:
            mismatch += 1; parts.append(blk); continue

        head_end = blk.index('</div>', blk.index('class="q__h"')) + len('</div>')
        head, body = blk[:head_end], blk[head_end:]

        # 지문·선지를 떼어 접는 자리로 옮긴다. 해설·오개념은 제자리에 둔다.
        found = [mm for mm in (re.search(r'<div class="q__stem">.*?</div>', body, re.S),
                               re.search(r'<div class="q__ch">.*?</div></div>', body, re.S))
                 if mm]
        moved = ''.join(mm.group(0) for mm in found)
        # ⚠ 뒤에서부터 지운다. 앞엣것을 먼저 지우면 뒤엣것의 자리가 밀려
        #   엉뚱한 데를 잘라내 해설 덩이가 통째로 깨진다 — 한 번 그랬다.
        for mm in sorted(found, key=lambda m: m.start(), reverse=True):
            body = body[:mm.start()] + body[mm.end():]

        keyline = (f'<div class="q__key">정답 {CIRC[k-1]}</div>'
                   if k and 1 <= k <= len(CIRC) else '')
        fold = (
            '<details class="q__text"><summary>글로 옮긴 것 보기 (원문이 아닙니다)</summary>'
            '<div class="q__textnote">아래는 HWP·PDF 에서 글자만 뽑은 것이라 '
            '그림·표·수식이 빠져 있을 수 있습니다. 문제는 위 원문을 보세요.</div>'
            + moved + '</details>') if moved.strip() else ''
        img = (
            f'<img class="q__img" src="crops/{eid}/{q}.png" '
            f'alt="{q}번 원문" loading="lazy" '
            'onerror="this.style.display=\'none\';'
            'var p=this.parentNode,d=p.querySelector(\'details.q__text\');'
            'if(d){d.open=true;}else{var f=p.querySelector(\'.q__imgfail\');'
            'if(f)f.style.display=\'block\';}">'
            f'<div class="q__imgfail">원문 이미지를 불러오지 못했습니다. 시험지 {q}번을 확인해 주세요.</div>')

        parts.append(head + '\n' + img + keyline + fold + body)
        changed += 1

    parts.append(html[last:])
    out = ''.join(parts)

    if changed and '.q__img{' not in out:
        out = out.replace('.q__stem{', STYLE.strip() + '\n.q__stem{', 1)

    if write and out != html:
        open(path, 'w', encoding='utf-8').write(out)
    return changed, done, missing, mismatch


def main():
    write = '--write' in sys.argv
    tot = [0, 0, 0, 0]
    for page, eid in sorted(PAGES.items()):
        key = exam_key(eid)
        c, d, mi, mm = convert(page, eid, key, write)
        for i, v in enumerate((c, d, mi, mm)):
            tot[i] += v
        flag = '✅' if (mi or mm) == 0 else '⚠'
        print(f'{flag} {page:26s} 원문크롭 {c+d:3d}/60'
              + (f' · 크롭없음 {mi}' if mi else '')
              + (f' · 정답표와 어긋남 {mm}' if mm else '')
              + (f' · 이번에 바꾼 것 {c}' if c else ''))
    print(f'\n합계 — 바꿈 {tot[0]} · 이미 됨 {tot[1]} · 크롭없음 {tot[2]} · 어긋남 {tot[3]}')
    if not write:
        print('(--write 를 붙여야 실제로 바뀝니다)')
    return 1 if (tot[2] or tot[3]) else 0


if __name__ == '__main__':
    raise SystemExit(main())
