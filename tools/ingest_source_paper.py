#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""선생님이 주신 **원본 시험지 PDF** 를 저장소에 들인다.

왜 —
  교재에서 옮겨 온 여덟 회차는 크롭이 **PDF 를 자른 것이 아니라 글을 그린
  것**이었다. HWPX 에서 캔 글을 HTML 로 그려 그림으로 뽑고, 그 그림들을 이어
  문제지 PDF 를 엮었다. 그래서 원문의 첨자·수식·그림·표가 빠지고, 문장 부호도
  사라졌다(「알파 붕괴를 1회 한다 알파 붕괴에서는…」처럼 마침표가 없다).
  2026-09-06 에 선생님이 원본 PDF 를 주셨다. 이제 진짜로 자른다.

무엇을 하나
  1. 원본에서 **정답표가 실린 쪽을 뺀다.** 이 저장소는 공개이고 「인쇄용 PDF」
     단추가 학생에게 그대로 보인다 — 정답표가 딸려 가면 안 된다.
  2. 남은 쪽으로 <회차>-problem.pdf 를 다시 쓴다.
  3. 회색 「문제 N」 딱지가 60개인지 세어 본다. 60이 아니면 멈춘다 —
     크롭이 한 칸씩 밀리는 것보다 안 만드는 편이 낫다.

    python3 tools/ingest_source_paper.py <회차> <원본.pdf> [--write]
"""
import difflib
import json
import os
import re
import sys

import fitz

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 정답이 실린 쪽을 알아보는 말. 하나라도 걸리면 그 쪽은 안 싣는다.
ANSWER_MARK = re.compile(r'문\s*항\s*번\s*호|정\s*답\s*표|^\s*정\s*답\s*$', re.M)


def labels_on(page) -> int:
    """그 쪽에 있는 회색 「문제 N」 딱지 수. build_wrongbook_assets 와 같은 자다."""
    n = 0
    for dr in page.get_drawings():
        r, fill = dr['rect'], dr.get('fill')
        if (fill and 60 < r.width < 130 and 15 < r.height < 25
                and 60 < r.x0 < 110 and all(0.74 < c < 0.85 for c in fill)):
            n += 1
    return n


def align(doc, exam_id) -> tuple[int, int, list[int]]:
    """딱지 N 자리의 글이 답지 N번 지문과 겹치는가. (맞음, 견줌, 어긋난 번호)"""
    path = os.path.join(ROOT, 'answers', '%s.json' % exam_id)
    if not os.path.exists(path):
        return 0, 0, []
    ans = json.load(open(path, encoding='utf-8')).get('questions') or {}
    spots = []
    for pi, page in enumerate(doc):
        for dr in page.get_drawings():
            r, fill = dr['rect'], dr.get('fill')
            if (fill and 60 < r.width < 130 and 15 < r.height < 25
                    and 60 < r.x0 < 110 and all(0.74 < c < 0.85 for c in fill)):
                spots.append((pi, r))
    spots.sort(key=lambda x: (x[0], x[1].y0))
    norm = lambda s: re.sub(r'[^0-9가-힣]', '', s or '')
    good, seen, bad = 0, 0, []
    for i, (pi, r) in enumerate(spots):
        nxt = spots[i + 1] if i + 1 < len(spots) else None
        y1 = nxt[1].y0 if (nxt and nxt[0] == pi) else 900.0
        here = norm(doc[pi].get_text('text', clip=fitz.Rect(0, r.y0 - 2, 600, y1)))
        stem = norm((ans.get(str(i + 1)) or {}).get('stem') or '')
        if len(stem) < 12:
            continue            # 지문이 그림뿐인 문항 — 글로는 못 맞춘다
        seen += 1
        run = difflib.SequenceMatcher(None, stem[:60], here[:400]).find_longest_match(
            0, min(60, len(stem)), 0, min(400, len(here))).size
        if run >= 10:
            good += 1
        else:
            bad.append(i + 1)
    return good, seen, bad


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 2:
        raise SystemExit(__doc__)
    exam_id, src = args
    write = '--write' in sys.argv

    doc = fitz.open(src)
    drop, keep = [], []
    for i, page in enumerate(doc):
        text = page.get_text() or ''
        # 문항이 실린 쪽은 무슨 일이 있어도 남긴다 — 문항 안에 「정답률」이
        # 적혀 있어 말만 보고 버리면 시험지에 구멍이 난다.
        if labels_on(page) or not ANSWER_MARK.search(text):
            keep.append(i)
        else:
            drop.append(i)

    out = fitz.open()
    out.insert_pdf(doc, from_page=0, to_page=len(doc) - 1)
    for i in reversed(drop):
        out.delete_page(i)

    labels = sum(labels_on(p) for p in out)
    print('%s ← %s' % (exam_id, os.path.basename(src)))
    print('  쪽 %d → %d (정답표 %d쪽을 뺐다: %s)'
          % (len(doc), len(out), len(drop), ', '.join(str(i + 1) for i in drop) or '없음'))
    print('  회색 「문제 N」 딱지 %d개' % labels)

    if labels != 60:
        print('  ⚠ 딱지가 60개가 아니다 — 싣지 않는다. 크롭이 한 칸씩 밀리는 것보다 낫다.')
        return 1

    good, seen, bad = align(out, exam_id)
    if seen:
        print('  답지와 자리 맞춤 %d/%d문항%s'
              % (good, seen, '' if not bad else ' · 어긋남 %s' % bad[:8]))
        # 한 칸 밀리면 그 뒤가 통째로 어긋난다. 몇 개만 어긋나는 것은 답지의
        # 지문이 요약본이거나 그림뿐인 자리다 — 자리가 밀린 것과는 꼴이 다르다.
        if good < seen * 0.9:
            print('  ⚠ 절반 넘게 어긋난다 — 다른 회차의 시험지일 수 있다. 싣지 않는다.')
            return 1
    dest = os.path.join(ROOT, '%s-problem.pdf' % exam_id)
    if write:
        out.save(dest, garbage=4, deflate=True)
        print('  → %s (%dKB)' % (os.path.basename(dest), os.path.getsize(dest) // 1024))
    else:
        print('  (--write 를 붙여야 실제로 씁니다)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
