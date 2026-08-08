#!/usr/bin/env python3
"""선생님께 남긴 메모가 학생 화면으로 새어 나가지 않는지 본다.

문제를 정리하다 보면 답지에 이런 말을 적게 된다.

    ※ 공식 성적표 정답표에는 ③으로 표기되어 있으나 … (정답표 오류)
    [회수 키는 ②이나 실측값은 ④. HWP 공식 해설로 최종 확정 예정.]
    원본 문제지의 반응식 확인 필요.

셋 다 **선생님이 판단할 일**을 적어 둔 것이지 학생에게 할 말이 아니다.
그런데 적어 넣은 자리가 `misconception`·`explanation` 이라, 그대로 성적표의
오답 카드와 해설지에 실려 나갔다. 학생은 자기 오답 옆에서 "최종 확정 예정"
을 읽는다 — 자기가 무엇을 틀렸는지가 아니라 만드는 사람의 사정을 읽는다.

메모를 지우자는 것이 아니다. 정답표가 틀렸다는 지적은 남겨야 한다. 자리를
옮긴다: `editorNote` 에 넣는다. 이 칸은 성적표도 해설지도 읽지 않는다.

여기서는 학생이 읽는 칸에 메모 표시가 남아 있는지만 본다.

⚠ '※' 하나만으로는 안 잡는다. 학생에게 하는 주의도 ※ 로 쓰기 때문이다
   ("※ 여기서 32.6 ÷ 95.0 으로 계산하면 … 1000배 차이를 꼭 반영하세요").
   만드는 사람의 사정을 가리키는 말이 함께 있을 때만 잡는다.

    python3 tools/editor_note.py           # 새어 나간 자리를 보여 준다
    python3 tools/editor_note.py --check   # 하나라도 있으면 빨간불
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 학생이 읽는 칸
FACING = ('misconception', 'explanation', 'explanationHtml', 'concept', 'learningPoint')

# 만드는 사람의 사정을 가리키는 말. 학생에게 하는 주의와 갈리는 것만 넣는다.
MARK = re.compile(
    r'정답표\s*오류|정답표에는|공식\s*성적표|회수\s*키'
    r'|최종\s*확정|확정\s*예정|확인\s*필요|검토\s*필요|추후\s*보완'
    r'|렌더\s*누락|추출\s*실패|원본\s*확인|TODO|FIXME|미확인'
)


def scan():
    out = []
    for path in sorted(glob.glob(os.path.join(ROOT, 'answers', '*.json'))):
        data = json.load(open(path, encoding='utf-8'))
        for k, q in sorted((data.get('questions') or {}).items(),
                           key=lambda kv: int(kv[0])):
            for f in FACING:
                v = q.get(f)
                if not isinstance(v, str):
                    continue
                m = MARK.search(v)
                if m:
                    out.append((os.path.basename(path)[:-5], k, f, m.group(),
                                v.strip().replace('\n', ' ')[:80]))
    return out


def main():
    check = '--check' in sys.argv
    hits = scan()
    if not hits:
        print('선생님께 남긴 메모가 학생 화면에 남아 있지 않다.')
        return 0

    where = sorted({(h[0], h[1]) for h in hits})
    print('학생이 읽는 칸에 남은 메모 %d군데 · 문항 %d개\n' % (len(hits), len(where)))
    for eid, qn, f, mark, txt in hits:
        print('  %-20s %3s번 %-16s [%s]' % (eid, qn, f, mark))
        print('      %s' % txt)
    print('\n메모를 지우지 말고 editorNote 로 옮긴다 — 성적표도 해설지도 이 칸을 읽지 않는다.')
    print('글(explanation)을 고쳤으면 꼴도 다시 만든다: python3 tools/gen_expl_html.py --write')
    return 1 if check else 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except BrokenPipeError:
        os._exit(0)
