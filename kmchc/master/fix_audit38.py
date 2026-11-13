# -*- coding: utf-8 -*-
"""감사38 조치 — M02073 의 넷째 선지 스핀값을 −1/2 로 바꾼다.

■ 무엇이 걸렸나 (감사38 M — ★G3g 칸별 최빈값 조합★)
  선지 넷을 마디로 갈라 마디마다 가장 흔한 값을 집어 이으면 ★정답만 남았다.★
      ① (0, 0, 0, +1/2)  ② (1, 0, 0, −1/2)  ③ (2, 1, 0, +1/2)  ④ (3, 2, −2, +1/2)
      1칸 0,·1,·2,·3, → 모두 다름(최빈값 없음)
      2칸 0,·0,·1,·2,  → '0,'  (①②)
      3칸 0,·0,·0,·−2, → '0,'  (①②③)
      4칸 +1/2)·−1/2)·+1/2)·+1/2) → '+1/2)' (①③④)
      교집합 = ① — ★네 양자수의 뜻을 하나도 모르고도 정답이 짚힌다.★

■ 무엇을 고치나
  ④ 의 스핀 자기양자수만 +1/2 → −1/2. 4칸이 2 : 2 로 갈려 최빈값이 없어지고,
  교집합이 {①②} 로 넓어져 길이 끊긴다.
  ▸ ④ 는 'mₗ 이 음수라 있을 수 없다고 봄' 을 겨냥한 오답이라 ★mₛ 는 그 판정에
    쓰이지 않는다★ — 값을 바꿔도 오답의 사고 경로가 그대로다.
  ▸ (3, 2, −2, −1/2)도 완전히 유효한 양자수 집합이므로 정답(있을 수 없는 것)은
    여전히 ① 하나뿐이다.

■ 왜 지금인가
  T13 마감 4제가 이 결함을 세 문항에서 동시에 겪고 검사(G3g)를 batch_template 로
  올렸다. 그 검사를 T13 후반 84제에 소급해 돌린 것이 감사38 이고, ★정탐은 이 하나★ 다
  (초판이 낸 13건은 모두 검사 자체의 오탐이라 검사를 좁혔다).

  ※ 은행 전체로는 46제가 같은 결함을 안고 있다(적용 가능 412제의 11.2%).
    T13 밖은 ★소급 부채★ 로 남긴다 — 여기서는 감사 범위인 T13 만 손댄다.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(BASE, 'master_bank.json')
BUILD = os.path.join(BASE, 'build_t13_p11.py')

OLD, NEW = '(3, 2, −2, +1/2)', '(3, 2, −2, −1/2)'
WATCH_ADD = (
    ' ★감사38 조치★ — ④ 의 스핀값을 +1/2 에서 −1/2 로 바꿨다. 넷째 마디가 '
    '+1/2 셋 : −1/2 하나였을 때는 ★칸마다 최빈값을 집어 이으면 정답만 남았다★(G3g). '
    '2 : 2 로 갈라 그 길을 끊었다. ▸ ④ 는 mₗ 의 부호를 겨냥한 오답이라 mₛ 는 판정에 '
    '쓰이지 않는다 — ★되돌리지 말 것.★'
)


def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    it = next(x for x in bank if x['id'] == 'M02073')
    assert it['choices'][3] == OLD, it['choices'][3]

    it['choices'][3] = NEW
    it['solution'] = it['solution'].replace(f'④ {OLD}', f'④ {NEW}')
    assert f'④ {NEW}' in it['solution']
    v = it.setdefault('verified', {})
    v['watch'] = v.get('watch', '').rstrip() + WATCH_ADD

    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    # 빌드 파일도 함께 고쳐 다시 지어도 같은 문면이 나오게 한다.
    src = open(BUILD, encoding='utf-8').read()
    n = src.count(OLD)
    assert n == 3, f'빌드 파일의 문면 수가 {n} — 손으로 볼 것'
    open(BUILD, 'w', encoding='utf-8').write(src.replace(OLD, NEW))

    print(f'감사38 조치 — M02073 ④ {OLD} → {NEW}')
    print(f'  빌드 파일 {os.path.basename(BUILD)} 에서 {n}곳 동기화')
    print(f"  watch {len(v['watch']):,}자")


if __name__ == '__main__':
    main()
