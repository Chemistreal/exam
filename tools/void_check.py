#!/usr/bin/env python3
"""출제 뒤 **폐기된 문항**이 제대로 처리돼 있는지 본다 — `exams.json` 의 `voided`.

'전원정답' 은 두 가지 다른 일에 붙어 있었다.

    · 답이 갈려 모두 인정한 문항
    · 출제 뒤 **문제 자체가 폐기된** 문항

학생이 보는 것은 둘 다 '전원정답' 이라, 오답 카드에서 "이건 왜 다 맞았지"
가 된다. 뒤엣것은 풀 것이 없어진 문항이니 성적표가 '출제 취소' 라고 적는다.

폐기 여부는 짐작하지 않는다. 대회 원본 정답표에 '문제삭제' 로 적힌 것만
옮겨 두었다.

    hwol-2009             51번
    hwol-2010             38 · 42번
    hwol-2014             57번
    hwol-2015             20번
    hwol-2018             34번
    hwol-2019             23 · 42번
    hwol-2021             60번
    kmchc-2025-1-simhwa   38 · 41번

kmchc-2025-1-simhwa 41번은 이 자리를 만들게 된 문항이다. 계산한 ln K 가
답지와 부호가 반대라 한동안 비워 두었는데, 원본 파일 이름이
'…_38번 41번 문제삭제.hwp' 였다 — 답지가 틀린 것이 아니라 문제가 폐기된
것이었다.

hwol-2021 60번은 2026-08-10 에 찾았다. 선생님이 보내 주신 성적표 엑셀의
정답 행이 그 칸에 '문제삭제' 라고 적고 있었고(파일 이름도 '…문제삭제1'),
학생 답도 전원 그 글자로 덮여 있었다. 여태 없었으므로 그 문항을 비운 학생은
**틀린 것으로 세어지고 감점까지 −1** 을 먹고 있었다.

hwol-2014 57번과 hwol-2015 20번은 2026-08-09 에 찾았다. 정답률이 한 칸 밀려
있는 것을 바로잡다가(`tools/rate_check.py` 넷째 검사) 빈칸이 어디에 얹히는지
보고 크롭·답지를 열어 확인했다 — 2014 57번은 문제지가 '정답률 : 삭제처리' 라고
인쇄하고 있었다. 둘 다 여태 전원정답으로만 처리돼 성적표가 '복수정답' 이라고
말하고 있었다.

여기서 보는 것.

  ① 폐기 문항이 실제로 전원정답 처리되어 있는가 (안 그러면 학생이 틀린다)
  ② 문항 번호가 그 회차 범위 안인가
  ③ 폐기 문항을 담은 회차가 통째로 사라지지 않았는가

원본 문제지는 대회 문제라 저장소에 없다. 이 값도 다시 만들 수 없다.

    python3 tools/void_check.py           # 회차별 폐기 문항
    python3 tools/void_check.py --check   # 어긋나면 빨간불
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMS = os.path.join(ROOT, 'exams.json')

FLOOR = 8       # 폐기 문항을 담은 회차 수의 바닥값 (2026-08-10 에 3 → 7 → 8)


def main():
    check = '--check' in sys.argv
    rounds = json.load(open(EXAMS, encoding='utf-8'))
    bad, have = [], []

    for ex in rounds:
        v = ex.get('voided')
        if not v:
            continue
        eid, nQ = ex['id'], int(ex['nQ'])
        have.append(eid)
        multi = ex.get('multi') or {}
        out = [q for q in v if not (isinstance(q, int) and 1 <= q <= nQ)]
        if out:
            bad.append('%s: 문항 번호가 범위 밖 %s (1~%d)' % (eid, out, nQ))
        thin = [q for q in v if len(multi.get(str(q)) or []) < 4]
        if thin:
            bad.append('%s: %s번이 전원정답 처리가 안 되어 있다 — 폐기된 문항인데 '
                       '학생이 틀린 것으로 채점된다' % (eid, thin))
        print('  %-24s %s번' % (eid, ' · '.join(str(q) for q in sorted(v))))

    print('\n폐기 문항을 담은 회차 %d개 (바닥값 %d)' % (len(have), FLOOR))
    if len(have) < FLOOR:
        bad.append('회차가 %d개로 줄었다 — 바닥값은 %d 다. 원본 정답표가 저장소에 '
                   '없어 다시 만들 수 없는 값이다.' % (len(have), FLOOR))

    if bad:
        print('\n어긋난 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        return 1 if check else 0

    print('폐기 문항이 모두 전원정답으로 처리되어 있다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
