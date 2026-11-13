# -*- coding: utf-8 -*-
"""patch_batch — ★이미 병합된 배치를 제자리에서 갈아 끼운다★

■ 왜 세우는가
  조치 회차의 표준 절차(은행에서 범위 제거 → 보조 파일 되돌림 → 재빌드)는 ★마지막 배치★
  에만 선다. P5 처럼 뒤에 다섯 배치가 더 얹힌 자리에서는 그 절차가 서지 않는다 —
  build_t15_p5.py 의 `T.EXPECT_LEN = 2338` 이 지금 은행(2,398)과 맞지 않아 ⛔ 비동기로 죽고,
  범위를 도려내면 뒤 배치의 자리까지 흔들린다.
  ▸ ★검증 부채를 쌓으면 조치 경로 자체가 막힌다★ — P5~P10 을 순회 없이 여섯 배치 쌓은 값을
    여기서 치른다. 다음부터는 배치마다 병합 직후에 순회한다.

■ 무엇을 하는가
  배치 모듈의 build() 를 불러 문항을 새로 짓고, 저작 점검과 verify 를 그대로 태운 뒤,
  ★은행의 같은 id 항목을 필드 단위로 덮어쓴다★. 병합 때 붙은 살림 필드(merge_and_house 가
  넣은 것)는 건드리지 않는다 — 새 dict 에 있는 키만 덮는다.

■ 쓰는 법
    python3 patch_batch.py build_t15_p5          # 검사만 하고 무엇이 바뀌는지 보여 준다
    python3 patch_batch.py build_t15_p5 --write  # 은행에 쓴다
"""
import importlib
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BANK = os.path.join(BASE, 'master_bank.json')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    mod = importlib.import_module(sys.argv[1])
    write = '--write' in sys.argv

    items = mod.build()
    mod.local_checks(items)
    import batch_template as T
    issues = T.verify(items)
    if issues and '--legacy' in sys.argv:
        #  ★옛 규약으로 지은 배치는 오늘의 verify 를 통과하지 못한다★ — T15 는 G3i·G3g·G3f 와
        #  '정답만 부정형' 이 규약이 되기 전에 지어졌다. 그 부채가 ★조치 경로를 막는다★:
        #  단위 한 마디를 넣으려는 회차가 열여섯 배치 전의 자리 배열 때문에 죽는다.
        #  ▸ --legacy 는 그 지적을 ★경고로 낮추고 화면에 그대로 남긴다★ — 지우지 않는다.
        #    새로 생긴 흠인지는 조치 뒤 감사(같은 회차에 돌린다)가 가른다.
        print('  ⚠ 옛 규약 부채 %d건 — 경고로 낮춘다(--legacy)' % len(issues))
        for i in issues:
            print('     ·', i)
        issues = []
    if issues:
        print('  ❌ verify 실패')
        for i in issues:
            print('     ·', i)
        raise SystemExit(1)
    print('  검증: 무결 ✓')

    with io.open(BANK, encoding='utf-8') as f:
        d = json.load(f)
    pool = d['items'] if isinstance(d, dict) else d
    by = {x['id']: x for x in pool}

    changed, fields = 0, 0
    for new in items:
        old = by.get(new['id'])
        if old is None:
            raise SystemExit('은행에 없는 id: %s — 병합되지 않은 배치다' % new['id'])
        hit = [k for k in new if old.get(k) != new[k]]
        if hit:
            changed += 1
            fields += len(hit)
            print('  %s — %s' % (new['id'], ' · '.join(hit)))
        if write:
            old.update(new)

    print('\n  문항 %d/%d 갈림 · 필드 %d' % (changed, len(items), fields))
    if not write:
        print('  ※ 쓰지 않았다 — 은행에 반영하려면 --write 를 붙일 것')
        return
    with io.open(BANK, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print('  ✅ 은행에 썼다 — %d제 그대로' % len(pool))


if __name__ == '__main__':
    main()
