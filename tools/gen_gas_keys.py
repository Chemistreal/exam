"""정답표를 창구(AppsScript-Code.gs)에 실어, 보내온 점수를 서버가 **다시 세게** 한다.

왜 필요한가
-----------
채점은 전부 브라우저에서 일어나고, 그 결과(`total`·`correct`·석차·백분위)를
그대로 시트에 보낸다. **창구에는 정답표가 없어서, 보내온 수가 맞는지 가릴
방법이 아예 없다.** 재계산조차 보내온 값을 그대로 읽는다.

그래서 누구든 아무 이름으로 만점을 올릴 수 있고, 그런 줄 몇 개면 **다른
학생의 석차·백분위·또래 정답률이 전부 흔들린다.** 실제로 그런 일이 있었다 —
CI 의 브라우저 검사가 진짜 창구로 제출해서 학생이 아닌 줄이 모집단에 들어갔고,
진짜 학생들의 등수를 밀어냈다(`_purgeTestRows` 가 그 뒤처리다).

무엇을 하고, 무엇을 안 하나
---------------------------
**다시 세어 보고, 어긋나면 적어 둔다. 점수는 안 고친다.**

점수를 서버가 말없이 갈아 치우면 그게 더 위험하다 — 정답 키를 나중에 고친
회차(전원정답 처리 등)에서는 옛 줄이 통째로 「틀린 것」이 되고, 선생님은
왜 바뀌었는지 알 수 없다. 그래서 판정만 하고 `검증기록` 시트에 남긴다.
무엇을 할지는 그것을 보고 정하시면 된다.

무엇을 싣는가
-------------
문항마다 **인정하는 답의 집합**만 싣는다. 화면의 채점 규칙(`okq`)과 같다.

    '*'      전원정답 — 답을 안 써도 맞은 것으로 센다
             (miss · voided · multi 가 넷 다인 문항)
    '3'      3번만
    '23'     2번·3번 둘 다 인정(multi)

제목으로 찾는다 — 시트에 들어가는 것은 회차 id 가 아니라 **제목**이고, 제목은
바뀐다('화올 2018' → 'KMChC 2018'). 그래서 `EXAM_TITLES` 와 같은 별칭 표를
그대로 쓴다.

실행
----
    python3 tools/gen_gas_keys.py           # 어긋나면 알려만 준다(검사)
    python3 tools/gen_gas_keys.py --write   # AppsScript-Code.gs 에 써 넣는다
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_exam_titles import build as build_titles  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
GS = ROOT / "AppsScript-Code.gs"
BEGIN = "var EXAM_KEYS = {"
END = "};"


def accepted(exam: dict, q: int) -> str:
    """q번 문항이 인정하는 답. 화면의 okq 와 같은 규칙이다."""
    multi = (exam.get("multi") or {}).get(str(q)) or []
    if q in (exam.get("miss") or []):
        return "*"
    if q in (exam.get("voided") or []):
        return "*"
    if len(multi) >= 4:
        return "*"
    if multi:
        return "".join(sorted(str(int(x)) for x in multi))
    key = exam.get("key") or []
    if q - 1 >= len(key) or not key[q - 1]:
        return "*"          # 키가 없는 자리는 판정하지 않는다(전원 인정과 같게 둔다)
    return str(int(key[q - 1]))


def build() -> dict[str, dict]:
    live = {e["id"]: e for e in json.loads((ROOT / "exams.json").read_text(encoding="utf-8"))}
    titles = build_titles()
    out: dict[str, dict] = {}
    for eid, names in titles.items():
        exam = live.get(eid)
        if not exam:
            continue                      # 옛 id — 지금 exams.json 에 없다
        n = int(exam.get("nQ") or len(exam.get("key") or []))
        if not n:
            continue
        acc = "".join(accepted(exam, q) if len(accepted(exam, q)) == 1 else "?" for q in range(1, n + 1))
        # 인정 답이 둘 이상인 자리는 한 글자로 못 적는다 — 그 자리만 따로 싣는다
        many = {q: accepted(exam, q) for q in range(1, n + 1) if len(accepted(exam, q)) > 1}
        for name in names:
            out[name] = {"n": n, "acc": acc, "many": many}
    return out


def render(table: dict[str, dict]) -> str:
    lines = [BEGIN]
    for name in sorted(table):
        v = table[name]
        many = ""
        if v["many"]:
            inner = ", ".join(f"{q}:'{a}'" for q, a in sorted(v["many"].items()))
            many = f", many:{{{inner}}}"
        lines.append(f"  '{name}': {{n:{v['n']}, acc:'{v['acc']}'{many}}},")
    lines.append(END)
    return "\n".join(lines)


def main() -> int:
    block = render(build())
    source = GS.read_text(encoding="utf-8")
    if BEGIN not in source:
        print(f"FAIL {GS.name} 에 `{BEGIN}` 자리가 없다 — 먼저 그 자리를 만들어야 한다.")
        return 1
    start = source.index(BEGIN)
    stop = source.index("\n" + END, start) + len("\n" + END)
    if source[start:stop] == block:
        print(f"PASS 정답표가 {len(build())}개 제목만큼 실려 있고 exams.json 과 맞는다.")
        return 0
    if "--write" not in sys.argv:
        print("FAIL 창구의 정답표가 exams.json 과 어긋난다 — `--write` 로 다시 만든다.")
        return 1
    GS.write_text(source[:start] + block + source[stop:], encoding="utf-8")
    print(f"AppsScript-Code.gs 에 정답표를 실었다 ({len(build())}개 제목).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
