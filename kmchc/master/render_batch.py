# -*- coding: utf-8 -*-
"""render_batch.py — 에이전트가 지은 초안(JSON)을 배치 빌더(.py)로 옮겨 적는다

  쓰임:  python3 render_batch.py <초안.json> <출력.py> <START_ID> <EXPECT_LEN> <TAIL_FROM>
                [제목] [BATCH_NOTE] [테마이름] [테마번호]

  왜 도구로 두는가
    에이전트를 여럿 띄워 문항을 ★동시에★ 짓게 하면 초안은 병렬로 얻지만, 은행에 넣는 일은
    한 줄로 세워야 한다(master_bank.json 은 하나뿐이고 EXPECT_LEN 이 앞뒤를 묶는다).
    그래서 ★짓는 일은 흩고 옮겨 적는 일은 모은다★ — 이 파일이 그 이음매다.

  초안 JSON 의 꼴(에이전트 스키마와 같다)
    {"items":[{"id","skill","track","dok","difficulty","esr","stem","choices"[4],"answer",
               "proof","wrongs"[{"text","note","type"}],"dev","calc","scenario","objective",
               "lead","prose","wmap"[{"text","retort"}],"diag"}]}

  ★문면은 손대지 않는다★ — 길이·자카드·인용 같은 규약은 local_checks 와 lenplan 이 잡는다.
  여기서 고치기 시작하면 어느 자리가 에이전트의 것이고 어느 자리가 내 것인지 흐려진다.
"""
import json
import os
import sys


def lit(s):
    """한글이 그대로 보이는 파이썬 문자열 리터럴 — JSON 문자열은 파이썬 리터럴의 부분집합이다."""
    return json.dumps(s, ensure_ascii=False)


HEAD = '''# -*- coding: utf-8 -*-
"""{title}

  ★에이전트 초안 → render_batch.py 로 옮겨 적음★ — 문면은 초안 그대로다.
"""
import re

import batch_template as T

T.START_ID = {start!r}
T.COUNT = {count}
T.EXPECT_LEN = {expect}
T.THEME = {theme!r}
T.TT = {tt}
T.UNIT = 'I'
T.BATCH_NOTE = {note}


def q(i, sk, tr, dok, df, esr, stem, cs, ans, proof, wr, dev, calc, scen, obj,
      lead, prose, wmap, diag):
    x = T.mk(i, sk, tr, dok, df, esr, stem, cs, ans, proof, wr, dev, calc, scen, obj=obj)
    T.sol(x, lead, prose, wmap, diag)
    return x


def build():
    it = []

'''


def render(item):
    cs = ',\n         '.join(lit(c) for c in item['choices'])
    wr = ',\n         '.join('(%s, %s, %s)' % (lit(w['text']), lit(w['note']), lit(w['type']))
                             for w in item['wrongs'])
    wm = ',\n         '.join('%s: %s' % (lit(w['text']), lit(w['retort'])) for w in item['wmap'])
    return (
        "    it.append(q(%s, %s,\n"
        "        %s, %d, %s, %.2f,\n"
        "        %s,\n"
        "        [%s], %d,\n"
        "        %s,\n"
        "        [%s],\n"
        "        %s,\n"
        "        %s,\n"
        "        %s, %s,\n"
        "        %s,\n"
        "        %s,\n"
        "        {%s},\n"
        "        %s))\n\n" % (
            lit(item['id']), lit(item['skill']),
            lit(item['track']), int(item['dok']), lit(item['difficulty']), float(item['esr']),
            lit(item['stem']),
            cs, int(item['answer']),
            lit(item['proof']),
            wr,
            lit(item['dev']),
            lit(item['calc']),
            lit(item['scenario']), lit(item['objective']),
            lit(item['lead']),
            lit(item['prose']),
            wm,
            lit(item['diag'])))


def main():
    src, out, start, expect, tail_from = sys.argv[1:6]
    title = sys.argv[6] if len(sys.argv) > 6 else 'T16 배치'
    note = sys.argv[7] if len(sys.argv) > 7 else title
    theme = sys.argv[8] if len(sys.argv) > 8 else '전자친화도·전기음성도'
    tt = int(sys.argv[9]) if len(sys.argv) > 9 else 16
    d = json.load(open(src, encoding='utf-8'))
    items = d['items'] if isinstance(d, dict) else d
    body = HEAD.format(title=title, start=start, count=len(items), expect=int(expect),
                       note=lit(note), theme=theme, tt=tt)
    for x in items:
        body += render(x)
    body += "    return it\n\n\n"
    tail = open(tail_from, encoding='utf-8').read()
    body += tail[tail.index('_ANON = re.compile'):]
    open(out, 'w', encoding='utf-8').write(body)
    print('✅ %s — %d제 (%s ~ %s)' % (os.path.basename(out), len(items),
                                     items[0]['id'], items[-1]['id']))


if __name__ == '__main__':
    main()
