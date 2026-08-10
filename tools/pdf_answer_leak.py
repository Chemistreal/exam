#!/usr/bin/env python3
"""문제지 PDF 에 **답이 실려 있는지** 본다.

왜 이 자가 있나
---------------
2026-08-10, 선생님이 알려 주셨다 — 문제지에 정답이 문제 바로 옆에 적혀 있다.

열어 보니 그랬다. `hwol-2017-problem.pdf` 는 문항마다 이렇게 인쇄되어 있었다.

    문제 1        정답률 : %  ④
    주기율표와 관련된 다음의 설명 중에서 옳은 것은?

그리고 `kmchc-2018-problem.pdf` · `kmchc-2019-problem.pdf` 는 **문제지가
아니었다.** 앞 네 쪽이 표지·주의사항, 다섯째 쪽이 **정답표 전체**, 그 뒤가
전부 정답률과 답이 붙은 해설이었다. 즉 '문제지 PDF ↓' 를 누르면 정답표가
통째로 내려왔다.

이것이 왜 큰가 — `final.html` 은 이 링크를 **답안지 바로 위**에 놓는다
(`examAssetsHTML`). 채점 뒤가 아니라 **답을 넣기 전** 화면이다.

그리고 크롭이 이 PDF 에서 잘려 나온다. `crops/hwol-2017/1.png` 은
'정답률 : % ④' 를 그대로 담고 있었다 — 오답 카드에 답이 실려 있었다.

무엇을 보나
-----------
  ① **답 글자** — '정답률' 이 적힌 줄에 ①~⑤ 가 같이 있으면 그것이 답이다.
     (정답률 숫자만 있는 것은 답이 아니다. 힌트지 답이 아니다 — 가른다)
  ② **정답표** — '문항번호 답' 표가 문제지 안에 있다
  ③ **해설** — 풀이가 문제지 안에 이어 붙어 있다

⚠ **답지·해설지는 안 본다.** `answerPdf`·`bookPdf`·`*-answer.pdf`·
  `*-solution-book.pdf` 는 답이 있는 것이 맞다. 문제지만 본다.

⚠ 이 자는 **고치지 않는다.** 원본 문제지는 대회 자료라 기계가 지어낼 수
  없다. 깨끗한 문제지는 선생님이 주셔야 한다.

그날 무엇을 했나 (2026-08-10)
-----------------------------
  · 2017 · 2018 · 2019 — 선생님이 진짜 문제지를 주셔서 갈아 끼우고 크롭
    180장을 다시 만들었다. 정답 키가 새 문제지와 맞는 것을 문항별로 봤다
  · 나머지 23개 — 뒤에 붙은 정답표·해설 쪽만 잘라 냈다. **문제 쪽은 한
    장도 안 건드렸다**(마지막 문항 딱지가 늘 정답표 바로 앞 쪽에 있었고,
    자른 뒤에도 crop_align.py 가 39/39 로 맞는다)
  · 잘라 낸 쪽은 버리지 않고 `<회차>-answer.pdf` 로 남겨 **채점 뒤 화면
    에서만** 걸었다(선생님 결정)
  · 화면 쪽 구멍도 같이 막았다 — examAssetsHTML 이 답안지 바로 위에
    정답·해설 링크를 걸고 있었다. tests/answer-not-before.js 가 지킨다

⚠ 아직 남은 것: `Chemistreal/exam` 은 **공개 저장소**라 답이 실려 있던 옛
  PDF 26개가 **git 이력에 그대로 남아 있다.** 커밋 주소를 아는 사람은
  여전히 받을 수 있다. 이력을 고쳐 쓰는 것은 되돌릴 수 없는 일이라
  선생님이 정하실 칸으로 남겨 두었다(2026-08-10: 일단 그대로 둔다).

    python3 tools/pdf_answer_leak.py           # 회차마다
    python3 tools/pdf_answer_leak.py --check   # 답이 실려 있으면 빨간불
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CIRCLED = set('①②③④⑤⑥')
TABLE = re.compile(r'문항\s*번호\s*답|문항번호\s*답')
SOL = re.compile(r'\[\s*해\s*설\s*\]|해\s*설\s*[:：]|풀\s*이\s*[:：]')

# 답이 실려 있어도 되는 것 — 답지·해설지다.
ANSWER_FILE = re.compile(r'-(answer|solution-book)\.pdf$')

# 여기에 까닭과 함께 적으면 넘어간다. **비워 두는 것이 맞다** — 문제지에
# 답이 실려도 되는 까닭은 없다. 자리만 둔다.
LEAK_OK: dict[str, str] = {}


def scan(path):
    """(답 글자 수, 정답표 쪽, 해설 쪽)."""
    import pymupdf
    doc = pymupdf.open(path)
    glyph, table, sol = 0, [], []
    try:
        for i in range(len(doc)):
            page = doc[i]
            text = page.get_text()
            if TABLE.search(text):
                table.append(i + 1)
            if SOL.search(text):
                sol.append(i + 1)
            words = page.get_text('words')
            for r in [w for w in words if '정답률' in w[4]]:
                ymid = (r[1] + r[3]) / 2
                # 같은 줄에서 '정답률' 오른쪽에 동그라미 숫자가 있으면 그게 답이다
                if any(w[4].strip() in CIRCLED for w in words
                       if w[1] <= ymid <= w[3] and w[0] > r[2]):
                    glyph += 1
    finally:
        doc.close()
    return glyph, table, sol


def main():
    check = '--check' in sys.argv
    exams = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    bad, seen = [], 0
    for e in exams:
        name = e.get('pdf')
        if not name:
            continue
        path = os.path.join(ROOT, name)
        if not os.path.exists(path) or ANSWER_FILE.search(name):
            continue
        seen += 1
        glyph, table, sol = scan(path)
        why = []
        if glyph:
            why.append('답 글자 %d개가 문제 옆에' % glyph)
        if table:
            why.append('정답표 p%s' % ','.join(map(str, table[:3])))
        if sol:
            why.append('해설 p%s' % ','.join(map(str, sol[:3])))
        mark = '  '
        if why and name not in LEAK_OK:
            bad.append((e['id'], name, ' · '.join(why)))
            mark = '⚠ '
        elif why:
            mark = '· '
        print('%s%-24s %-34s %s' % (mark, e['id'], name, ' · '.join(why) or '깨끗하다'))

    print('\n문제지 %d개 · 답이 실린 문제지 %d개' % (seen, len(bad)))
    if bad:
        print('\n학생이 답을 넣기 **전** 화면에서 내려받는 파일이다'
              '(final.html 의 examAssetsHTML 이 답안지 바로 위에 놓는다).')
        for eid, name, why in bad:
            print('  %-24s %-34s %s' % (eid, name, why))
        print('\n원본 문제지는 대회 자료라 기계가 지어낼 수 없다 — 깨끗한 문제지로'
              ' 갈아 끼운 뒤\n크롭을 다시 만든다'
              '(python3 tools/build_wrongbook_assets.py --exams <id> --force-crops).')
        return 1 if check else 0

    print('문제지에 답이 실려 있지 않다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
