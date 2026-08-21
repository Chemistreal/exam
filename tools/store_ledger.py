#!/usr/bin/env python3
"""이 브라우저에 **무엇을 남기는지** 적어 두고, 늘어나면 한 번 묻게 한다.

왜 이 자가 있나
---------------
통합 셸(exam/hub.html)에는 저장 자리를 다섯 칸으로 적어 두고 그 목록을
검사가 지킨다. 새 칸이 생기면 빨간불이 켜지고, 사람이 **"이건 앱 자료가
아니라 이 브라우저의 취향인가"** 를 한 번 묻게 된다. 실제로 그 물음 덕에
넛지 기록에서 학생 이름을 빼고 해시만 남기기로 정했다.

이 저장소에는 그 목록이 없었다. 지금 재어 보니 일곱 칸이고, 일곱 다
**지워도 남의 기록이 안 깨지는 것들**이다. 그 사실을 적어 둔다 — 적어 두지
않으면 여섯 달 뒤에 여덟 번째 칸이 조용히 생긴다.

    dt_admtok        선생님 로그인 표. 지우면 다시 로그인하면 된다
    dt_admgate       관리 화면 첫 문고리. 위와 같다
    dt_stucode       학생이 마지막에 넣은 코드. 다시 치면 된다
    dt_hw_round      숙제 채점판에서 보던 회차. 화면의 기억일 뿐이다
    dt_absov         미응시 표시를 손으로 덮어 둔 것. **선생님 판단이 담긴다**
    dt_pending_hide_v1  할 일 목록에서 접어 둔 줄. 취향이다
    chemistreal_session_v1  마지막에 보던 학생·회차. 취향이다
    chemistreal_grader_v1 · chemistreal_itemstats_v1  채점판 작업 중 상태

⚠ 성적·명단 같은 **남의 기록은 시트에 있고 여기 안 남는다.** 그 성질이
  이 앱이 "브라우저를 비워도 아무것도 안 잃는" 까닭이다. 그것만은 지킨다.

    python3 tools/store_ledger.py           # 지금 쓰는 칸
    python3 tools/store_ledger.py --check   # 적어 둔 것 말고 새 칸이 생기면 빨간불
"""
import collections
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 적어 둔 칸. **늘어날 수는 있지만 늘 때마다 여기를 고치게 한다.**
KNOWN = {
    # 화면·시트 설정
    'chemistreal:synckey':      '시트 동기화 열쇠. 지우면 다시 넣으면 된다',
    'chemistreal:gate':         '문고리를 지난 표. 지우면 다시 지나면 된다',
    'chemistreal:views':        '어느 화면을 몇 번 열었나. 취향이다',
    'chemistreal:pal:recent':   '최근 고른 옷(팔레트). 취향이다',
    'chemistreal:lessons':      '강의에서 본 자리. 취향이다',
    'chemistreal:nudge:seen':   '넛지를 본 표. 같은 말을 두 번 안 하려고 둔다',
    'chemistreal:hint:gloss':   '용어 풀이를 한 번 펼쳐 봤나. 취향이다',
    'note:lastopen':            '마지막에 연 노트. 취향이다',
    'final:renames':            '이름을 고쳐 부른 것. 화면의 기억이다',
    'final:dhlog:':             '동형문제를 풀어 본 기록. 지워도 성적이 안 바뀐다',
    # 약점 60제로 발행한 시험지. **지우면 채점을 못 한다** — 학생이 손에 든
    # 종이가 어느 문항으로 짜였는지는 여기에만 있고, 다시 짜면 그 종이와
    # 어긋난다. 선생님 브라우저에만 남고, weak60.html 에 파일로 내보내는
    # 자리를 따로 두었다.
    'exam.weak60.papers.v1':    '약점 60제로 발행한 시험지. 지우면 그 시험지를 채점 못 한다',
    # 학생 이름이 든 표다 — 저장소의 학생 코드(소금 친 해시)에 이름을 붙여
    # 보려고 선생님이 시트 _이름코드 탭을 붙여넣은 것. 이 브라우저 밖으로
    # 나가지 않고, 지워도 링크는 코드 이름으로 계속 산다.
    'exam.weak60.namecode.v1':  '학생 이름↔코드 표. 지우면 파이널 목록이 이름 대신 코드로 보인다',
    'exam.pick.done.v1':        '이 브라우저에서 채점을 끝낸 회차. 성적표의 「다음 학생」 '
                                '칸이 남은 사람을 앞에 세우는 데만 쓴다 — 점수는 안 들어 있다',
    'exam.pick.namecode.v1':    '「이름 버튼 링크」로 받아 둔 이름표. 학생이 제 이름을 눌러 '
                                '들어가는 자리(final-submit 목록 맨 위)를 그린다. 주소(#n=)로 '
                                '받아 여기에 남긴다 — 저장소에는 코드뿐이고 이름은 없다',
    'chemistreal:final:cslink': '공유 링크로 받은 또래 통계. 다시 열면 다시 온다',
    'chemistreal:final:lastsync': '시트를 마지막에 읽은 시각',
    # 성적표 링크를 **복사한 때**. 보낸 때가 아니다 — 문자는 카톡에서
    # 나가고 이 화면은 그것을 모른다. 지워도 성적이 안 바뀐다(선생님 결정 #32).
    'final:sent':               '성적표 링크를 복사한 때. 화면의 기억이다',
    # 치다 만 답안. 채점해 시트로 보내면 지운다 — 남겨 두면 다음 학생 칸에
    # 앞사람 답이 떠올라 **틀린 채점을 만든다**(선생님 결정 #28).
    'final:draft:':             '치다 만 답안. 채점하면 지워진다',
    # 학생이 «다시 풀었음» 을 손으로 표시한 것(선생님 결정 #20). **시트로 안
    # 간다** — 스스로 세는 자리이지 선생님께 보고되는 자리가 아니다. 보고가
    # 되는 순간 그건 숙제 검사가 된다. 지워도 성적이 안 바뀐다.
    'final:redone:':            '학생이 다시 풀었다고 표시한 문항. 스스로 세는 자리다',

    # ⚠ 여기부터는 **남의 기록**이다. DT 와 성질이 다르다.
    #
    # DT 는 "브라우저를 비워도 아무것도 안 잃는다" 를 지킨다 — 성적·명단이
    # 시트에만 있기 때문이다. exam 은 그럴 수 없다. **채점을 하는 앱**이라
    # 시트가 죽어도 그 자리에서 채점이 끝나야 하고, 그러려면 방금 채점한 것을
    # 손에 들고 있어야 한다. 그래서 아래 세 칸은 **의도해서 둔 것**이다.
    #
    # 대신 두 가지를 지킨다.
    #   · 시트로 보낸 뒤에도 지우지 않는다 — 지우면 창구가 죽었을 때 잃는다
    #   · 여기 있는 것은 **선생님 브라우저**의 것이다. 학부모·학생 브라우저에는
    #     안 남는다(공유 링크는 주소에 실려 오고 저장하지 않는다)
    'chemistreal:roster:':      '⚠ 채점한 학생 제출 기록(이름·답안). 시험 id 마다 한 칸. '
                                '창구가 죽어도 채점이 끝나도록 손에 들고 있는 것이다',
    'chemistreal_responses_v1': '⚠ 응답 관리 화면의 작업 중 자료',
    'j0_ans':                   '⚠ j0 채점판에 넣던 답안(작업 중)',
    'j0_name':                  '⚠ j0 채점판에 넣던 학생 이름(작업 중)',
    'j0_school':                '⚠ j0 채점판에 넣던 학교(작업 중)',
    'j0_grade':                 '⚠ j0 채점판에 넣던 학년(작업 중)',
}

# 여기 있으면 안 되는 것 — 남의 기록. 시트에 있어야 한다.
FORBIDDEN = re.compile(r'roster|명단|score|성적|answers?_|응답', re.I)

# 그런데 저장소마다 사정이 다르다. DT 는 "브라우저를 비워도 아무것도 안 잃는다"
# 를 지킬 수 있다 — 성적·명단이 시트에만 있기 때문이다. exam 은 **채점을 하는
# 앱**이라 창구가 죽어도 그 자리에서 채점이 끝나야 하고, 그러려면 방금 채점한
# 것을 손에 들고 있어야 한다.
#
# 그래서 "여기 둬도 되는 것" 을 **까닭과 함께** 적을 자리를 둔다. 비워 두면
# 이 검사는 그 저장소에서 늘 빨간불이고, 늘 빨간불이면 아무도 안 본다.
# 새 칸이 여기 없이 생기면 그때는 걸린다 — 그게 이 자의 일이다.
FORBIDDEN_OK = {
    'chemistreal:roster:':
        '⚠ 채점한 학생 제출 기록(이름·답안). **의도해서 둔다** — exam 은 채점을 '
        '하는 앱이라 시트 창구가 죽어도 그 자리에서 채점이 끝나야 하고, 그러려면 '
        '방금 채점한 것을 손에 들고 있어야 한다. 시트로 보낸 뒤에도 안 지운다. '
        '이것은 **선생님 브라우저**의 것이고, 학부모·학생 브라우저에는 안 남는다 '
        '(공유 링크는 주소에 실려 오고 저장하지 않는다).',
}

SET = re.compile(r'localStorage\.setItem\(\s*([A-Za-z_$][\w$]*|[\'"][^\'"]+[\'"])')
CONST = re.compile(r'\b(?:const|var|let)\s+(\w+)\s*=\s*([\'"][^\'"]+[\'"])')
# ⚠ **자가 거짓말한 자리.** 래퍼(`Store.set(KEY,…)`)를 풀 때 파일 안의 모든
#   `.set(…)` 호출을 훑어 이름을 맞춰 봤다. 그랬더니 배지 이름을 담은 지역
#   변수까지 저장 칸이 됐다 — exam/index.html 의
#
#       const map=[['전 문항','check'],['상위','starb'],…]
#       …  const key = 'starb';  …  x.set(key)
#
#   저장 칸 이름은 이 저장소들에서 **대문자 상수**로 둔다(KEY·ROSTER_PREFIX·
#   PAL_KEY·DHLOG…). 래퍼를 풀 때는 그것만 본다. 네 저장소로 견줘 보니
#   이 규칙으로 빠지는 것은 starb 하나뿐이고 나머지는 그대로 남는다.
#   소문자 상수에 저장 칸을 담으면 여기서 안 잡힌다 — 그때는 대문자로 옮긴다.
WRAP_NAME = re.compile(r'^[A-Z][A-Z0-9_]*$')


def keys_in(s):
    """글 한 덩이가 쓰는 저장 칸 이름들.

    파일에서 떼어 둔 까닭은 `tools/lie_check.py` 가 참·거짓 예시를 먹여
    보기 위해서다. 자를 넓히거나 좁히면 그쪽에서 걸린다."""
    names = {k: v.strip('\'"') for k, v in CONST.findall(s)}
    out = set()
    for raw in SET.findall(s):
        if raw[0] in '\'"':
            out.add(raw.strip('\'"'))
        elif raw in names:
            out.add(names[raw])
        else:
            # 래퍼를 거치는 것 — 부르는 자리에서 이름을 찾는다
            for call in re.findall(r'\w+\.(?:set|get|del)\(\s*(\w+)\s*[,)]', s):
                if call in names and WRAP_NAME.match(call):
                    out.add(names[call])
    return out


def keys():
    """화면마다 쓰는 저장 칸. 변수로 쓴 것은 그 파일 안에서 값을 찾아 푼다."""
    got = collections.defaultdict(set)
    for p in sorted(glob.glob(os.path.join(ROOT, '*.html'))):
        for k in keys_in(open(p, encoding='utf-8', errors='ignore').read()):
            got[k].add(os.path.basename(p))
    return got


def main():
    check = '--check' in sys.argv
    got = keys()
    print('이 브라우저에 남기는 칸 %d개\n' % len(got))
    for k in sorted(got):
        mark = '  ' if k in KNOWN else '⚠ '
        print('%s%-26s %-34s %s' % (mark, k, KNOWN.get(k, '**적어 두지 않은 칸**'),
                                    ' '.join(sorted(got[k]))[:40]))
    fresh = sorted(k for k in got if k not in KNOWN)
    gone = sorted(k for k in KNOWN if k not in got)
    bad = sorted(k for k in got if FORBIDDEN.search(k) and k not in FORBIDDEN_OK)
    okd = sorted(k for k in got if FORBIDDEN.search(k) and k in FORBIDDEN_OK)

    if fresh:
        print('\n적어 두지 않은 칸 %d개' % len(fresh))
        print('  늘어나는 것 자체는 괜찮다. 다만 **여기에 한 줄 적고** 지나가라 —')
        print('  "이건 앱 자료가 아니라 이 브라우저의 취향인가" 를 한 번 묻는 것이 이 자의 일이다.')
    if gone:
        print('\n적어 뒀는데 이제 안 쓰는 칸 %d개: %s' % (len(gone), ' '.join(gone)))
        print('  지워도 되지만, 옛 브라우저에 남아 있을 수 있으니 지우는 코드가 있는지 보고 빼라.')
    if okd:
        print('\n남의 기록이지만 **까닭을 적고 두기로 한 것** %d개' % len(okd))
        for k in okd:
            print('  %-26s %s' % (k, FORBIDDEN_OK[k]))
    if bad:
        print('\n⚠ 남의 기록으로 보이는 이름 %d개: %s' % (len(bad), ' '.join(bad)))
        print('  성적·명단은 시트에 있어야 한다. 브라우저를 비워도 아무것도 안 잃는 성질을 지킨다.')
        print('  여기 둬야 할 까닭이 있으면 FORBIDDEN_OK 에 **그 까닭과 함께** 적는다.')

    if check:
        # 없어진 칸은 빨간불이 아니다(줄이는 것은 좋은 일이다).
        print('\n' + ('FAIL' if (fresh or bad) else 'PASS'))
        return 1 if (fresh or bad) else 0
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
