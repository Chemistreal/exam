#!/usr/bin/env python3
"""성적표가 **아이를 어디에 세우는 말**을 할 때, 다음 걸음을 같이 말하는지 본다.

왜 이 자가 여기 있나
--------------------
DT 저장소에 같은 이름의 자가 있다(선생님 결정 #38 — *"`report_msg.py` 가 DT 에만
있다"*). 거기서는 석차 문구가 다섯 칸으로 갈리는데, 위 세 칸이 **비교로 시작해
비교로 끝났다.**

    최상위권입니다. 반에서 상위 약 3%에 듭니다. 반 평균보다 12점 높습니다.

옮겨 와서 이 저장소에 대 보니 **여기도 같았다.** 두 자리가 걸렸다.

    화면  `percSec`         연도누적 총석차 12/104 · 상위 15% · 백분위 85
    책    Percentile 절     누적 응시 104명 기준, … 상위 15% 구간에 있습니다

둘 다 **위치만 말하고 끝난다.** 학부모가 그 줄에서 얻는 것은 «우리 아이가 저기
있구나» 뿐이고, 그 다음에 무엇을 하면 되는지는 다른 장으로 넘어가야 나온다.

⚠ 낱말로 «좋은 말/나쁜 말» 을 재지 않는다
------------------------------------------
DT 쪽에서 이미 겪은 것이다 — 손실로 말했나 이득으로 말했나를 낱말로 재 봤더니
부정문에서 그대로 뒤집혔다("지나간 회차에 빚이 **없다**" 를 손실 문장으로 셌다).
못 재는 것은 못 잰다고 적는다.

여기서 재는 것은 **구조** 하나다 — 위치를 말한 덩이 안에 «다음에 무엇을 하면
되는지»가 같이 있는가. 이건 사람 판단이 필요 없다.

한계
----
`final.html` 의 **글자**를 본다. 위치를 말하는 새 자리가 여기 적힌 표시(상위 N% ·
백분위 · 석차) 없이 생기면 이 자는 못 본다. 재는 것과 막는 것은 다르다.

    python3 tools/report_msg.py           # 위치를 말하는 자리와 그 다음 걸음
    python3 tools/report_msg.py --check   # 다음 걸음이 없는 자리가 있으면 빨간불
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'final.html')

# 아이를 어디에 세우는 말.
#
# ⚠ 낱말만 보면 안 된다. 처음에 `백분위|총석차` 로만 봤더니
#   «백분위·문항별 분석으로 진단을 제공합니다» 같은 **기능 소개**까지
#   위치를 말하는 자리로 셀다. 위치를 말하는 문장은 그 말 **바로 뒤에 값이 온다** —
#   `상위 <b>15%`, `총석차 ${rank}/`, `백분위 '+perc`.
PLACE = re.compile(r"(?:상위|백분위|총석차|반석차)\s*(?:<b>|\$\{|'\+|\"\+|\d)")

# 다음 걸음. **낱말이 아니라 «무엇을 하면 되는지»** 를 가리키는 말만 센다.
# (DT 의 같은 자가 쓰는 것과 같은 뜻이다 — 낱말 목록은 저장소마다 다르다)
STEP = re.compile(r'회복|잡으면|보완|다시 풀|읽어|도전|채워|끝내면|정독|복습')

# 위치 표시가 나온 자리에서 앞뒤로 이만큼을 «같은 덩이» 로 본다.
# 성적표의 한 절이 대략 이 안에 들어간다.
#
# ⚠ **보이는 글자만 센다.** 주석을 지운 자리는 공백으로 남는데(줄 번호를
#   지키려고), 그 공백까지 거리로 세면 «주석이 길다» 는 이유로 같은 절이
#   다른 절이 된다. 실제로 그래서 한 자리가 계속 빨간불이었다 — 화면에는
#   안 보이는 글자가 사람과 사람 사이를 갈라 놓은 셈이다.
SPAN = 700

# 위치를 말하지만 다음 걸음이 없어도 되는 자리와 **까닭**.
# 비워 두면 이 자는 늘 빨간불이고, 늘 빨간불이면 아무도 안 본다.
ALLOWED = {
    'bk-postrack': '그림 위의 눈금표(하위—상위). 문장이 아니라 자다',
    'bk-posends': '위와 같다',
    'st"><b>': '한 줄 요약의 숫자 칸. 바로 아래 문장이 말을 잇는다',
    '"백분위":': '용어 풀이. 이 학생 이야기가 아니라 «백분위» 라는 말의 뜻이다',
    'bits.join': 'Word 표지의 결론 한 줄(#9). 숫자 셋을 나란히 세운 자리이고, '
                 '바로 다음 장인 «한 장 요약» 이 말을 잇는다',
    "stat.push": 'Word 한 장 요약의 숫자 표. 표는 문장이 아니다 — 같은 장 아래 '
                 '«먼저 손댈 곳» 이 다음 걸음을 말한다',
}


# **화면에 뜨는 글**인지 가리는 표. 위치 표시 둘레에 이런 것이 있어야
# 사람에게 하는 말이다 — 없으면 코드나 변수 이름이다.
RENDERED = re.compile(r'<(div|span|b|p|td|h[1-6])\b|class=|run\(|txt\(')


def strip_code_comments(s):
    """주석을 걷어낸다.

    ⚠ 처음에는 안 걷어내고 쟀다. 그랬더니 **열일곱 곳**을 짚었는데 진짜는
      둘이었다 — 나머지는 «백분위만 적어 두면 그래서 몇 등이냐를 되묻는다»
      같은 **주석**과 변수 이름이었다. 잘못 재는 자는 안 재느니만 못하다.
      사람이 경고를 무시하게 되고, 그러면 진짜가 와도 안 본다
      (`tools/lie_check.py` 머리말).

    글자 수를 지켜야 줄 번호가 안 밀리므로, 지우는 대신 **같은 길이의
    공백으로 바꾼다.**"""
    out = list(s)
    for m in re.finditer(r'/\*.*?\*/', s, re.S):
        for i in range(m.start(), m.end()):
            if out[i] != '\n':
                out[i] = ' '
    for m in re.finditer(r'(?m)^[ \t]*//.*$', s):
        for i in range(m.start(), m.end()):
            out[i] = ' '
    return ''.join(out)


def blocks():
    """위치를 말하는 덩이들. (몇째 줄, 앞뒤 글, 다음 걸음이 있나)"""
    s = strip_code_comments(open(SRC, encoding='utf-8').read())
    out, seen = [], set()
    def around(i, j):
        """보이는 글자로 앞뒤 SPAN 만큼. 공백은 안 센다(위 주석)."""
        a, n = i, 0
        while a > 0 and n < SPAN:
            a -= 1
            if not s[a].isspace():
                n += 1
        b, n = j, 0
        while b < len(s) and n < SPAN:
            if not s[b].isspace():
                n += 1
            b += 1
        return s[a:b]

    for m in PLACE.finditer(s):
        chunk = around(m.start(), m.end())
        line = s.count('\n', 0, m.start()) + 1
        if line in seen:
            continue
        # 화면에 뜨는 글이 아니면(코드·변수) 세지 않는다 — 위 strip 주석 참고.
        if not RENDERED.search(s[max(0, m.start() - 200):m.end() + 200]):
            continue
        # 같은 덩이 안의 여러 표시를 한 번만 센다
        for ln in range(line, line + 6):
            seen.add(ln)
        why = None
        for k, v in ALLOWED.items():
            if k in s[max(0, m.start() - 120):m.end() + 120]:
                why = v
                break
        out.append({'line': line, 'has': bool(STEP.search(chunk)),
                    'why': why, 'txt': re.sub(r'\s+', ' ', s[m.start():m.end() + 90])})
    return out


def main():
    check = '--check' in sys.argv
    rows = blocks()
    bad = [r for r in rows if not r['has'] and not r['why']]

    print('아이를 어디에 세우는 말 %d곳\n' % len(rows))
    for r in rows:
        mark = '✓' if r['has'] else ('·' if r['why'] else '✗')
        print('  %s  %5d줄  %s' % (mark, r['line'], r['txt'][:70]))
        if r['why']:
            print('           적어 둠 — %s' % r['why'])

    if not bad:
        print('\n위치를 말하는 자리마다 다음 걸음이 같이 있다.')
        return 0

    print('\n위치만 말하고 **다음 걸음이 없는** 자리 %d곳:' % len(bad))
    for r in bad:
        print('  %5d줄  %s' % (r['line'], r['txt'][:70]))
    print('\n학부모가 그 줄에서 얻는 것은 «우리 아이가 저기 있구나» 뿐이다.')
    print('그 문장 안에 다음에 무엇을 하면 되는지를 같이 적는다.')
    print('문장이 아니라 자·눈금이면 tools/report_msg.py 의 ALLOWED 에')
    print('**까닭과 함께** 적는다.')
    return 1 if check else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
