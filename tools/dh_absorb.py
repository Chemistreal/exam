#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""집필한 동형문제 조각을 은행으로 옮기면서 **개념 이름을 답지와 맞춘다.**

왜 맞춰야 하나
--------------
동형문제는 두 갈래로 학생에게 간다.

    ① 그 문항의 짝            donghyung/<시험id>.json 의 같은 번호
    ② 같은 개념의 다른 문제    donghyung/index.json 의 concept 로 찾는다

②는 **이름이 맞아야만** 찾아진다. 답지가 「계수맞추기」라고 부르는 것을 은행이
「화학 반응식의 계수 맞추기」라고 부르면, 같은 개념인데 서로를 못 본다.

집필 에이전트에게 「원문의 concept 를 그대로 쓰되, 개념이 아닌 딱지(「납」·「비율」·
「표기법」)면 진짜 개념 이름으로 바꿔라」 라고 일렀다. 실제로 kch1u1 열넷 중 넷은
그렇게 고쳐 왔는데, 나머지 열은 **이미 멀쩡하던 이름까지** 띄어쓰기를 넣어 바꿨다
(「한계반응물」→「한계 반응물」, 「양적관계」→「양적 관계」). 그대로 두면 은행에
같은 개념이 두 이름으로 갈라져 앉는다.

말로 이른 것은 지켜지지 않을 수 있다. 여기서 자료를 보고 맞춘다.

맞추는 규칙 — 은행 색인(donghyung/index.json)에 **이미 있는 이름을 이긴다**

    ① 답지 이름이 은행에 있다        → 답지 이름을 쓴다 (쪼개지 않는다)
    ② 답지 이름은 없고 새 이름이 있다  → 새 이름으로, 답지도 함께 고친다
    ③ 둘 다 없다                   → 새 이름으로, 답지도 함께 고친다
                                    (「납」보다 「중성자수」가 낫다)

    python3 tools/dh_absorb.py <시험id> [...]          # 무엇이 어떻게 될지만
    python3 tools/dh_absorb.py <시험id> [...] --write  # 은행을 쓰고 답지를 고친다
    python3 tools/dh_absorb.py --all [--write]
    python3 tools/dh_absorb.py --check                 # DH_SETS 와 은행 파일이 맞는가 (CI)
"""
import glob
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIP = os.path.join(ROOT, 'donghyung', '_wip')
# 은행에서 넘어오면 안 되는 기출 참조 필드 (tools/dh_merge.py 와 같은 목록)
BANNED = ('sourceExamId', 'sourceQuestion', 'sourceExamTitle',
          'matchLevel', 'matchScore', 'image')


def load(p):
    return json.load(io.open(p, encoding='utf-8'))


def bank_names():
    """은행 색인이 아는 개념 이름. 곁이름(_alias)으로 닿는 것도 아는 것으로 센다."""
    idx = load(os.path.join(ROOT, 'donghyung', 'index.json'))
    con = set(idx.get('concept') or {})
    al = idx.get('_alias') or {}
    return con, {k: v for k, v in al.items() if v in con}


def resolves(name, con, al):
    return bool(name) and (name in con or name in al)


def dh_sets():
    """final.html 의 DH_SETS 를 글자 그대로 잘라 읽는다.

    ⚠ tests/wrongbook-assets.py 도 같은 자리를 같은 방식으로 읽는다. 그래서 그
      표 안에는 주석을 넣지 않는다(설명은 표 위에 적혀 있다).
    """
    s = io.open(os.path.join(ROOT, 'final.html'), encoding='utf-8').read()
    m = re.search(r'const DH_SETS=(\{.*?\});', s, re.S)
    if not m:
        return None, s, None
    body = re.sub(r"'", '"', m.group(1))
    return json.loads(body), s, m


def check_sets():
    """은행 파일이 생겼는데 DH_SETS 가 아직 «없다» 고 말하고 있으면 빨간불.

    DH_SETS 에 빈 배열로 적힌 회차는 dhSetIds 가 [] 를 돌려주고, 오답노트의
    동형문제 자리는 개념 풀로 대신 채운다. 은행을 집필해 놓고 이 표를 안 고치면
    **집필한 문항이 화면에 한 장도 안 나온다** — 파일은 있고 검사는 지나가고
    아무도 모른다. 반대로 표에서 지웠는데 파일이 없으면 없는 파일을 부른다.
    """
    sets, _, m = dh_sets()
    if sets is None:
        print('final.html 에서 DH_SETS 를 못 찾았다')
        return 1
    bad = 0
    for eid, ids in sorted(sets.items()):
        have = os.path.exists(os.path.join(ROOT, 'donghyung', '%s.json' % eid))
        if have and not ids:
            print('[%s] 은행 파일이 있는데 DH_SETS 가 빈 배열이다 — 화면에 한 장도 안 나온다' % eid)
            bad += 1
        for x in ids:
            if not os.path.exists(os.path.join(ROOT, 'donghyung', '%s.json' % x)):
                print('[%s] DH_SETS 가 없는 파일을 부른다: %s' % (eid, x))
                bad += 1
    print('\nDH_SETS %d회차 · 어긋난 곳 %d' % (len(sets), bad))
    return 1 if bad else 0


def drop_from_sets(eid):
    """은행이 생긴 회차를 DH_SETS 의 «없음» 목록에서 뺀다.

    빼면 dhSetIds 의 기본값([id])이 살아나 제 은행을 읽는다.
    """
    sets, s, m = dh_sets()
    if sets is None or sets.get(eid) != []:
        return False
    body = m.group(1)
    new = re.sub(r"\s*'%s'\s*:\s*\[\s*\],?" % re.escape(eid), '', body)
    new = re.sub(r',(\s*\})', r'\1', new)
    new = re.sub(r'\{\s*,', '{', new)
    s = s[:m.start(1)] + new + s[m.end(1):]
    io.open(os.path.join(ROOT, 'final.html'), 'w', encoding='utf-8').write(s)
    return True


def main():
    write = '--write' in sys.argv
    if '--check' in sys.argv:
        return check_sets()
    ids = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--all' in sys.argv:
        ids = sorted({os.path.basename(p).split('__')[0]
                      for p in glob.glob(os.path.join(WIP, '*__*.json'))})
    if not ids:
        print(__doc__)
        return 1

    exams = {e['id']: e for e in load(os.path.join(ROOT, 'exams.json'))}
    con, al = bank_names()
    rc = 0

    # ── 같은 옛 이름에 새 이름이 여럿 붙는 것을 먼저 하나로 모은다 ──
    #
    # 회차마다 다른 에이전트가 집필하므로, 답지가 둘 다 「돌턴」이라 부르던 것을
    # 한쪽은 「돌턴 원자설」, 다른 쪽은 「돌턴 원자론」으로 바꿔 온다. 그대로 두면
    # 같은 개념이 은행에 두 이름으로 앉아 서로를 못 본다 — 이름을 고쳐 놓고
    # 고치기 전과 똑같은 상태가 되는 셈이다.
    #
    # 여럿이면 **많이 쓰인 이름**을, 같으면 짧은 이름을 고른다(짧은 쪽이 대개
    # 군더더기가 없다). 무엇으로 모았는지는 화면에 적는다.
    votes = {}
    for eid in ids:
        apath = os.path.join(ROOT, 'answers', '%s.json' % eid)
        if not os.path.exists(apath):
            continue
        src0 = load(apath).get('questions') or {}
        for q in sorted(glob.glob(os.path.join(WIP, '%s__*.json' % eid))):
            for k, v in load(q).items():
                old_c = str((src0.get(k) or {}).get('concept') or '').strip()
                new_c = str((v or {}).get('concept') or '').strip()
                if old_c and new_c and old_c != new_c and not resolves(old_c, con, al):
                    votes.setdefault(old_c, {}).setdefault(new_c, 0)
                    votes[old_c][new_c] += 1
    canon = {}
    for old_c, cand in votes.items():
        if len(cand) < 2:
            continue
        best = sorted(cand.items(), key=lambda kv: (-kv[1], len(kv[0]), kv[0]))[0][0]
        canon[old_c] = best
        print('여러 이름으로 갈린 개념 「%s」 → 「%s」 로 모은다 (%s)'
              % (old_c, best,
                 ' · '.join('%s %d' % (n, c) for n, c in sorted(cand.items()))))

    for eid in ids:
        exam = exams.get(eid)
        if not exam:
            print('[%s] exams.json 에 없는 시험' % eid)
            rc = 1
            continue
        parts = sorted(glob.glob(os.path.join(WIP, '%s__*.json' % eid)))
        if not parts:
            print('[%s] 조각이 없다' % eid)
            rc = 1
            continue

        apath = os.path.join(ROOT, 'answers', '%s.json' % eid)
        adoc = load(apath) if os.path.exists(apath) else {'questions': {}}
        src = adoc.get('questions') or {}

        merged, kept, moved, fresh, notes = {}, 0, 0, 0, []
        for p in parts:
            for k, v in load(p).items():
                if k in merged:
                    print('[%s] 문항 번호 중복: %s (%s)' % (eid, k, os.path.basename(p)))
                    rc = 1
                    continue
                for b in BANNED:
                    v.pop(b, None)
                v['origin'] = 'authored'
                v['verified'] = True
                old = str((src.get(k) or {}).get('concept') or '').strip()
                new = str(v.get('concept') or '').strip()
                if old in canon and new != canon[old]:
                    new = canon[old]
                    v['concept'] = new
                if old and new and old != new:
                    if resolves(old, con, al):
                        v['concept'] = old
                        kept += 1
                        notes.append('%s번 %s ← %s (은행이 아는 이름을 지킨다)' % (k, old, new))
                    else:
                        if resolves(new, con, al):
                            moved += 1
                        else:
                            fresh += 1
                        if src.get(k) is not None:
                            src[k]['concept'] = new
                        notes.append('%s번 %s → %s (답지도 함께 고친다)' % (k, old, new))
                merged[k] = v

        nQ = exam['nQ']
        missing = [str(n) for n in range(1, nQ + 1) if str(n) not in merged]
        if missing:
            print('[%s] 누락된 문항 %d개: %s'
                  % (eid, len(missing), ', '.join(missing[:12])))
            rc = 1
            continue

        print('[%s] %d문항 · 답지 이름을 지킨 자리 %d · 답지를 고칠 자리 %d(은행에 있는 이름 %d, 새 이름 %d)'
              % (eid, len(merged), kept, moved + fresh, moved, fresh))
        for n in notes:
            print('    ' + n)

        if write:
            out = {
                'schemaVersion': 2,
                'examId': eid,
                'examTitle': exam.get('title', ''),
                'strategy': 'original-authored',
                'note': '각 문항의 개념·사고과정에 맞춰 새로 집필한 독자 문항. 기출 복제 아님.',
                'questions': {str(n): merged[str(n)] for n in range(1, nQ + 1)},
            }
            dest = os.path.join(ROOT, 'donghyung', '%s.json' % eid)
            io.open(dest, 'w', encoding='utf-8').write(
                json.dumps(out, ensure_ascii=False, indent=1) + '\n')
            if os.path.exists(apath) and (moved or fresh):
                io.open(apath, 'w', encoding='utf-8').write(
                    json.dumps(adoc, ensure_ascii=False, indent=1) + '\n')
            print('    → donghyung/%s.json (%d문항)' % (eid, nQ))
            if drop_from_sets(eid):
                print('    → final.html 의 DH_SETS 에서 «없음» 표시를 뺐다')

    if not write:
        print('\n(--write 를 붙이면 실제로 쓴다)')
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
