"""T12 P13 12차 조치 — 해설 문면 1

■ M01927 △ (factchecker) — ★마무리 한 줄이 두 한계를 한쪽 조항으로 몰았다★
  본문과 자가진단은 붕괴 차단을 ★비복사 조항★ 에, 선스펙트럼을 ★불연속 조항★ 에 나누어
  배정하는데, 9차에 넣은 마무리만 두 한계의 뿌리를 '머무를 자리가 정해져 있다' 하나로 몰았다.
  factchecker 가 ★오학습 경로★ 를 구체적으로 짚었다 — 학생이 "궤도가 띄엄띄엄하니 안
  무너진다"로 배울 수 있는데, 궤도가 불연속이어도 가속 전하의 복사는 그대로 막히지 않는다.
  한 가정의 ★두 반쪽★ 이 각각 무엇을 막는지 갈라 적는다.
  ▸ 이 자리는 8·9·11·12차 네 번째 손질이다. 뒤 문장을 고칠 때마다 그것을 요약한 앞뒤 줄이
    남아 어긋났다. ★한 문단을 고치면 그 문단을 예고하거나 요약하는 줄을 함께 볼 것.★

■ solver 10차 0건 · defender 8·9차 0건(입력 불변) · factchecker 12차 ✗ 0 · △ 1
  factchecker 의 △ 는 9차 4건 → 10차 4건 → 11차 3건 → 12차 1건으로 줄고 있다.
"""
import json, os
BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'master_bank.json')

def main():
    bank = json.load(open(BANK, encoding='utf-8'))
    d = {x['id']: x for x in bank}
    it = d['M01927']
    old = ('두 한계를 함께 푼 뿌리는 결국 "머무를 자리가 정해져 있다"는 한 마디야.')
    new = ('두 한계를 함께 푼 것은 한 가정의 두 반쪽이야 — "머무를 자리가 정해져 있다"는 쪽이 '
           '선을 만들고, "그 자리에 있는 동안에는 빛을 내지 않는다"는 쪽이 붕괴를 막지.')
    assert it['solution'].count(old) == 1
    it['solution'] = it['solution'].replace(old, new)
    for x in bank:
        assert '★' not in x['solution'] and '**' not in x['solution'], x['id']
    json.dump(bank, open(BANK, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('P13 12차 조치 완료 — 해설 문면 1')

if __name__ == '__main__':
    main()
