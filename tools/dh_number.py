#!/usr/bin/env python3
"""기출동형 문항의 **셈이 고른 답과 맞는지** 본다.

보기가 숫자 넷인 문항은 해설이 반드시 그 숫자에 닿아야 한다. 셈을 하다
한 자리 틀리면 해설은 4.44 를 내놓고 답은 ② 를 고르는데, 정작 ② 가
1.35 인 식이 된다. 학생은 해설을 따라가다 답이 안 나오는 것을 보고
**자기가 틀린 줄 안다.**

구조 검사(dh_validate)는 이것을 못 본다. 보기도 넷이고 정답도 1~4 이고
오개념도 셋이라 다 갖췄기 때문이다. 정답 분포 검사(dh_lint)도 못 본다.
숫자를 읽어야 아는 것이라 여기서 본다.

보는 법.

  ① 보기 넷이 모두 '숫자 + 단위' 꼴이고 값이 서로 다른 문항만 고른다
     (보기가 '2차, k = 0.20 M⁻¹s⁻¹' 처럼 여러 값을 담으면 건너뛴다 —
      기계가 무엇을 견줘야 할지 모른다)
  ② 그 문항의 해설에 고른 보기의 값이 나오는가. 3% 안이면 맞다고 본다
     (반올림·유효숫자 때문에 딱 떨어지지 않는다)
  ③ 숫자를 우리말로 적은 것도 센다 — '셋이다' 는 3 이다

2026-08-08 기준 376문항 가운데 375문항이 값에 닿고, 나머지 하나는 '셋'
이라고 적은 자리다(그것도 맞다).

이 자는 **셈이 답에 닿는지**만 본다. 셈이 옳은지는 못 본다 — 화학은 사람이
본다.

    python3 tools/dh_number.py           # 안 닿는 문항
    python3 tools/dh_number.py --check   # 있으면 빨간불 (CI용)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 보기 하나가 '숫자 + 단위' 뿐인가. 단위에 붙는 글자만 허용한다.
ONLY_NUM = re.compile(r'^\s*([-+]?\d+(?:\.\d+)?)\s*(?:[A-Za-z°%·⁻⁰-⁹/²³μΩ]+)?\s*$')
IN_TEXT = re.compile(r'(?<![\d.])[-+]?\d+(?:\.\d+)?')
WORD = {'하나': 1, '둘': 2, '셋': 3, '넷': 4, '다섯': 5, '여섯': 6,
        '일곱': 7, '여덟': 8, '아홉': 9, '열': 10}
TOL = 0.03          # 반올림·유효숫자 때문에 딱 떨어지지 않는다


def choice_values(choices):
    out = []
    for c in choices:
        m = ONLY_NUM.match(str(c).replace(',', ''))
        if not m:
            return None
        out.append(float(m.group(1)))
    return out


def explained(text):
    got = [float(x) for x in IN_TEXT.findall(text.replace(',', ''))]
    for w, n in WORD.items():
        if w in text:
            got.append(float(n))
    return got


def main():
    check = '--check' in sys.argv
    looked, bad = 0, []
    for path in sorted(glob.glob(os.path.join(ROOT, 'donghyung', '*.json'))):
        name = os.path.basename(path)
        if name in ('index.json', '_template.json'):
            continue
        eid = name[:-5]
        qs = json.load(open(path, encoding='utf-8')).get('questions') or {}
        for k in sorted(qs, key=int):
            q = qs[k]
            ch = q.get('choices') or []
            if len(ch) != 4:
                continue
            vals = choice_values(ch)
            if not vals or len(set(vals)) < 4:
                continue
            looked += 1
            want = vals[int(q['answer']) - 1]
            got = explained(str(q.get('explanation') or ''))
            if not any(abs(g - want) <= max(abs(want) * TOL, 1e-9) for g in got):
                bad.append('%s %s번: 고른 보기는 %s 인데 해설에 그 값이 없다'
                           % (eid, k, ch[int(q['answer']) - 1]))

    print('보기가 숫자 넷인 문항 %d개' % looked)
    if bad:
        print('\n해설의 셈이 고른 답에 안 닿는 문항 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\n셈을 다시 하거나, 고른 보기를 셈에 맞춘다. 학생은 해설을 따라가다')
        print('답이 안 나오면 제가 틀린 줄 안다.')
        return 1 if check else 0

    print('모든 문항에서 해설의 셈이 고른 답에 닿는다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
