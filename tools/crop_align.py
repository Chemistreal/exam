#!/usr/bin/env python3
"""문항 크롭이 **그 문항 자리에서** 잘렸는지 본다.

크롭은 문제지의 회색 딱지('문제 26')를 찾아 그 자리부터 다음 딱지 앞까지를
잘라 만든다. 그런데 문제지에는 문항 딱지가 아닌 회색 상자가 섞여 있다.

    묶음 문두   '문제 22-23' — 문항 둘이 나눠 쓰는 자료 위에 붙는다
    잘못 박힌 딱지  hwol-2018 의 스물여섯째 상자에는 '문제 52' 라고 적혀 있다

이런 상자를 문항으로 세면 **그 뒤 크롭이 통째로 한 칸씩 밀린다.** 오답
카드에 엉뚱한 문제가 실리고 마지막 문항은 크롭이 없어진다. 실제로 여덟
회차가 그랬고, hwol-2018 은 26번부터 예순까지 서른다섯 장이 밀려 있었다.

화면은 멀쩡하고 파일 수도 맞아서 다른 검사는 전부 초록불이다. 그림을 열어
봐야 아는데, 딱지 글자는 자모로 흩어져 있어 기계가 못 읽는다.

그래서 사람이 한 번 읽어 표에 적어 두었다(GROUPED · STRAY). 이 자는 표와
문제지를 견줘 **셈이 맞는지**만 본다.

    지나온 회색 상자 = 문항 수 + 묶음 문두 + 잘못 박힌 딱지

어긋나면 표에 없는 상자가 새로 생긴 것이다. 그 자리에서 멈춘다 — 모르고
지나가면 그 뒤가 다 밀린다.

그리고 **남는 상자**가 있는지 본다. 표를 다 쓰고 나면 마지막 문항 뒤로는
그 쪽에 회색 상자가 하나도 없어야 한다. 이어 붙은 해설 뭉치는 늘 두 쪽 넘게
뒤에서 시작한다(서른아홉 회차 모두 그렇다). 마지막 문항과 **같은 쪽**에
상자가 더 있으면 그것은 문항도 자료도 아닌 것이 끼어 있다는 뜻이다 —
hwol-2018 이 딱 그 모양이었다.

그림을 그리지 않으므로 빠르다(서른아홉 회차 14초).

사람이 한 번 눈으로 본 것(2026-08-08). 서른아홉 회차 **마지막 문항**의 크롭이
어느 딱지에서 잘렸는지 그 딱지를 다 뽑아 읽었다. 예순 문항 회차는 모두
'문제 60', 쉰 문항 회차 셋은 모두 '문제 50' 이었다. 중간에 한 칸이라도
밀리면 꼬리가 어긋나므로, 이것으로 서른아홉 회차의 앞뒤가 맞는 것을 봤다.

    python3 tools/crop_align.py           # 회차마다 딱지 셈
    python3 tools/crop_align.py --check   # 안 맞으면 빨간불 (CI용)
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))


def main():
    check = '--check' in sys.argv
    import fitz
    import build_wrongbook_assets as B

    exams = json.load(open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))
    # 이 자의 전제(회색 문항 딱지 배치)가 성립하지 않는 문제지.
    # 크롭 수·문항 대응은 wrongbook-assets 가 따로 세므로 여기서만 건너뛴다.
    skip = {
        'usnco-2026-natl-1': '미국 원판 PDF 라 회색 문항 딱지가 없다 (2026-08-21)',
    }
    bad, ok = [], 0
    for e in exams:
        # 크롭을 **우리가 그린** 회차는 이 자의 전제 밖이다. 이 자는 원본
        # 문제지 PDF 에서 회색 문항 딱지를 찾아 «크롭이 제 문항 자리에서
        # 잘렸는가» 를 본다. 그런데 단원별 회차는 반대다 — 크롭을 먼저 그리고
        # 그 크롭들로 PDF 를 엮었으므로 어긋날 자리가 없다.
        # (문항 수와 크롭 수가 맞는지는 tests/wrongbook-assets.py 가 따로 센다.)
        _src = e.get('source')
        if isinstance(_src, dict) and _src.get('tool') == 'tools/ingest_legacy_exam.py':
            ok += 1
            continue
        if e['id'] in skip:
            print('  %-22s 건너뜀 — %s' % (e['id'], skip[e['id']]))
            ok += 1
            continue
        pdf = os.path.join(ROOT, e.get('pdf') or '')
        if not e.get('pdf') or not os.path.exists(pdf):
            bad.append('%s: 문제지 PDF 가 없다 (%s)' % (e['id'], e.get('pdf')))
            continue
        doc = fitz.open(pdf)
        try:
            hs = B.question_headers(doc, int(e['nQ']), e['id'])
        except RuntimeError as err:
            bad.append('%s: %s' % (e['id'], err))
            doc.close()
            continue
        # 남는 상자: 마지막 문항 뒤, 같은 쪽에 또 있는 회색 상자
        allb = []
        for pi in range(doc.page_count):
            for dr in doc[pi].get_drawings():
                r, f = dr['rect'], dr.get('fill')
                if f and 60 < r.width < 85 and 15 < r.height < 25 \
                        and 60 < r.x0 < 110 and all(0.74 < c < 0.85 for c in f):
                    allb.append((pi, r.y0))
        allb.sort()
        last = hs[-1]
        surplus = [b for b in allb
                   if b[0] == last.page_index and b[1] > last.rect.y0]
        if surplus:
            bad.append('%s: 마지막 문항(%d쪽) 뒤에 딱지가 %d개 더 있다 — '
                       '문항도 자료도 아닌 것이 끼어 있다'
                       % (e['id'], last.page_index + 1, len(surplus)))
        g = len(B.GROUPED.get(e['id'], []))
        st = len(B.STRAY.get(e['id'], []))
        note = []
        if g:
            note.append('묶음 %d' % g)
        if st:
            note.append('잘못 박힌 딱지 %d' % st)
        print('  %-22s 문항 %d%s' % (e['id'], len(hs),
                                     ' · ' + ' · '.join(note) if note else ''))
        ok += 1
        doc.close()

    print('\n딱지 셈이 맞는 회차 %d/%d' % (ok, len(exams)))
    if bad:
        print('\n어긋난 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n새로 생긴 상자는 사람이 한 번 읽고 tools/build_wrongbook_assets.py 의')
        print('GROUPED(묶음 문두) 또는 STRAY(잘못 박힌 딱지)에 적어야 한다.')
        return 1 if check else 0

    print('딱지 셈이 맞고 남는 상자도 없다.')
    print('※ 이 자가 보증하는 것은 셈이다. 딱지에 적힌 번호까지 읽지는 못한다 —')
    print('   글자가 자모로 흩어져 있다. 표(GROUPED·STRAY)는 사람이 읽어 적은 것이다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
