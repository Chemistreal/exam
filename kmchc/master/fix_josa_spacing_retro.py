# -*- coding: utf-8 -*-
"""소급 조치 — 조사 앞 빈칸 셋(M02162 · M02172 · M02180).

T14 P7 1차 factchecker 가 '무엇인지 를' 꼴을 짚어 국소검사 ⑱ 로 기계화했더니
★앞 배치 셋★ 이 함께 울었다. ⑱ 은 build_t14_p3 에 있고 P4·P5·P6·P7 이 그것을
import 하므로, 고치지 않으면 ★그 세 배치는 다시 빌드되지 않는다★.

▸ ★한쪽만 고치면 다음 재빌드에서 되살아난다★ — 은행과 빌드 파일을 함께 고친다
  (T13 P9 입자 띄어쓰기 소급 조치에서 얻은 것).
▸ 오탐은 이미 검사 쪽에서 걸렀다(3,481 → 80 → 12, 정밀도 12/12). 여기 셋은
  ★모두 진짜★ 이므로 면제 목록이 필요 없다.
▸ M02162 는 '항상 은' 이 조사가 아니라 ★낱말 인용★ 이었다 — 붙여 쓰면 '항상은' 이
  되어 뜻이 흐려지므로 '항상이라는 말이' 로 풀어 쓴다.
  ★고칠 자리를 찾았다고 해서 고치는 방법까지 정해지는 것은 아니다★ — 새로 얻었다.
  처음에는 낱말에 인용부호를 씌웠는데 ★그 자리가 파이썬 문자열 안이라 파일이 깨졌다★.
  ▸ ★문면을 고칠 때는 그 문면이 놓인 그릇도 함께 센다★ — 새로 얻었다.
"""
import json

R = [
    ('build_t14_p3.py', '항상 은 자료 안에서 무너져.', '항상이라는 말이 자료 안에서 무너져.'),
    ('build_t14_p4.py', '급하게 올라가는 자리 부터 봐', '급하게 올라가는 자리부터 봐'),
    ('build_t14_p5.py', '두 사실은 우선순위 로 풀고', '두 사실은 우선순위로 풀고'),
]

for path, old, new in R:
    s = open(path, encoding='utf-8').read()
    assert s.count(old) == 1, f'{path}: {s.count(old)}곳 — {old!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))
    print(f'  · {path}  고침')

BANK = 'master_bank.json'
bank = json.load(open(BANK, encoding='utf-8'))
n = 0
for x in bank:
    if x['id'] not in ('M02162', 'M02172', 'M02180'):
        continue
    for k, v in list(x.items()):
        if not isinstance(v, str):
            continue
        for _, old, new in R:
            if old in v:
                x[k] = v = v.replace(old, new)
                n += 1
assert n == 3, n
json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'  · {BANK}  {n}자리 고침')
print('fix_josa_spacing_retro 적용 완료')
