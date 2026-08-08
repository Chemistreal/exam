#!/usr/bin/env python3
"""채점하는 정답과 **해설이 말하는 정답**이 같은지 본다.

같은 문항의 정답이 두 곳에 적혀 있다.

    exams.json          key · multi · voided   ← 성적표가 **채점에 쓰는** 것
    answers/<id>.json   answer · acceptableAnswers · 해설 끝의 화살표
                                               ← 오답 카드·해설지가 **보여 주는** 것

둘이 갈리면 학생은 맞았다고 채점된 문항의 해설에서 다른 답을 본다. 점수는
맞으니 아무도 안 걸린다. 실제로 한 자리가 그랬다 — jmchc-9 50번은 채점에서
전원정답인데 해설은 '→ ④' 라고만 적혀 있었다.

여기서 보는 것.

  ① answer 가 exams.json 의 key 와 같은가
  ② acceptableAnswers 가 multi(없으면 key 하나)와 같은가
  ③ 해설 끝의 화살표(→ ②)가 key 와 같은가
     — 복수정답·폐기 문항은 화살표를 그렇게 안 쓰므로 건너뛴다

폐기(voided) 문항은 채점도 해설도 '전원정답' 한 가지라 견줄 것이 없다.

    python3 tools/answer_sync.py           # 갈린 곳을 보여 준다
    python3 tools/answer_sync.py --check   # 갈렸으면 빨간불 (CI용)
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CIRC = {'①': 1, '②': 2, '③': 3, '④': 4}


def main():
    check = '--check' in sys.argv
    exams = {e['id']: e for e in json.load(
        open(os.path.join(ROOT, 'exams.json'), encoding='utf-8'))}
    bad, seen = [], 0

    for path in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        eid = os.path.basename(path)[:-5]
        ex = exams.get(eid)
        if not ex:
            continue                      # 회차가 없는 해설은 orphan_scan 이 본다
        qs = json.load(open(path, encoding='utf-8')).get('questions') or {}
        void = set(ex.get('voided') or [])
        multi = ex.get('multi') or {}
        for k, v in sorted(qs.items(), key=lambda x: int(x[0])):
            q = int(k)
            if q in void or not (1 <= q <= int(ex['nQ'])):
                continue
            seen += 1
            key = ex['key'][q - 1]
            if v.get('answer') != key:
                bad.append('%s %d번: answer %s ≠ 채점 정답 %s'
                           % (eid, q, v.get('answer'), key))
            want = sorted(multi.get(k) or [key])
            got = sorted(v.get('acceptableAnswers') or [])
            if got != want:
                bad.append('%s %d번: 인정 답 %s ≠ 채점 %s' % (eid, q, got, want))
            if k not in multi:
                m = re.search(r'([①②③④])\s*$', (v.get('explanation') or '').strip())
                if m and CIRC[m.group(1)] != key:
                    bad.append('%s %d번: 해설 화살표 %s ≠ 채점 정답 %s'
                               % (eid, q, m.group(1), key))

    print('견준 문항 %d개 (회차 %d)' % (seen, len(exams)))
    if bad:
        print('\n채점과 해설이 갈린 곳 %d:' % len(bad))
        for b in bad:
            print('  ' + b)
        print('\nexams.json 이 채점의 근거다. 해설 쪽을 그쪽에 맞춘다 —')
        print('반대로 고치면 학생 점수가 조용히 바뀐다.')
        return 1 if check else 0

    print('채점하는 정답과 해설이 말하는 정답이 모두 같다.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
