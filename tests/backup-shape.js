/* ============================================================
   공개 백업만으로 남의 성적표 링크를 되지을 수 없게 — 회귀 테스트
   ------------------------------------------------------------
   성적표 링크는 이렇게 생겼다.

       index.html#r=<회차>.<답안을 5진수로 접은 값>[.<수험번호>.<이름>]

   뒤의 수험번호·이름은 **없어도 열린다**. 암호도 안 묻는다(그렇게 만든
   것은 학부모가 링크만 눌러 보게 하려던 것이고, 옳은 결정이다). 그러니
   비밀은 **답안 문자열 하나뿐**이다.

   그런데 그 답안 문자열이 공개 저장소 `backup/<날짜>.json` 에 매일 올라간다.
   이름은 소금 친 해시로 가려 두었지만 가릴 필요가 없다 — `exam` 과
   `answers` 만 집으면 그 학생의 성적표 링크가 그대로 나오고, 열면 안에
   이름이 있다.

   그래서 창구가 답안 대신 **틀린 문항 번호만** 실을 수 있게 했다
   (스크립트 속성 `BACKUP_ANSWERS=0`). 스무 개를 틀렸으면 3의 20제곱 가지라
   되지을 수 없다. 잃는 것은 「예전에 ③」 한 줄뿐이다.

   여기서 지키는 것:
   - 속성을 안 두면 **지금 그대로** 답안이 실린다(옛 백업·옛 도구가 안 죽는다)
   - 꺼 두면 답안 문자열이 **한 글자도** 안 실린다
   - 꺼도 «어느 문항을 틀렸나» 는 그대로 나온다 — 두 모양이 같은 답을 준다
   - 꺼도 «안 썼다» 와 «틀리게 썼다» 가 안 뭉뚱그려진다
   - 백업만 다른 저장소로 보낼 수 있고, 안 두면 지금 그대로 간다

   실행:  node tests/backup-shape.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { execFileSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
const GAS = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (!ok) fail++;
  console.log((ok ? '  ok   ' : '  FAIL ') + n +
    (ok ? '' : `\n         받은 것: ${JSON.stringify(got)}\n         바란 것: ${JSON.stringify(want)}`));
};

let PROPS = {};
const ctx = vm.createContext(require('./_gasenv')({
  PropertiesService: { getScriptProperties: () => ({ getProperty: k => (k in PROPS ? PROPS[k] : null) }) },
}));
for (const re of [/var GH_OWNER = [\s\S]*?;/,
                  /function _backupRepo_\([\s\S]*?\n\}/,
                  /function _backupWithAnswers_\([\s\S]*?\n\}/]) {
  const m = GAS.match(re);
  if (!m) { console.log('  FAIL .gs 에서 못 찾았다: ' + re); fail++; }
  else vm.runInContext(m[0], ctx);
}
const repo = () => vm.runInContext('_backupRepo_()', ctx);
const keep = () => vm.runInContext('_backupWithAnswers_()', ctx);

console.log('안 두면 지금 그대로');
PROPS = {};
chk('답안을 싣는다', keep(), true);
chk('exam 저장소로 간다', repo(), { owner: 'Chemistreal', repo: 'exam' });

console.log('\n두면');
PROPS = { BACKUP_ANSWERS: '0' };
chk("'0' 이면 안 싣는다", keep(), false);
for (const v of ['off', 'no', 'false', 'OFF']) {
  PROPS = { BACKUP_ANSWERS: v }; chk(`'${v}' 도 안 싣는다`, keep(), false);
}
for (const v of ['1', 'on', '', '아무말']) {
  PROPS = { BACKUP_ANSWERS: v }; chk(`'${v}' 이면 싣는다`, keep(), true);
}
PROPS = { BACKUP_REPO: 'Chemistreal/exam-backup' };
chk('보낼 저장소를 바꾼다', repo(), { owner: 'Chemistreal', repo: 'exam-backup' });
for (const v of ['이상한값', 'a/b/c', '/', 'x/']) {
  PROPS = { BACKUP_REPO: v };
  chk(`모양이 아니면 지금 그대로: '${v}'`, repo(), { owner: 'Chemistreal', repo: 'exam' });
}

/* ── 백업을 만드는 자리가 실제로 답안을 뺐는가 ─────────────────────── */
console.log('\n창구가 만드는 줄');
const daily = (() => {
  const i = GAS.indexOf('function dailyBackup(');
  let d = 0;
  for (let j = i; j < GAS.length; j++) {
    if (GAS[j] === '{') d++;
    else if (GAS[j] === '}' && --d === 0) return GAS.slice(i, j + 1);
  }
  return GAS.slice(i);
})();
chk('실을지 말지를 물어본다', /_backupWithAnswers_\(\)/.test(daily), true);
chk('안 실을 때는 틀린 번호만 담는다', /last\.wrong\s*=/.test(daily), true);
chk('무엇을 골랐는지는 안 담는다', /last\.chosen|chosen:/.test(daily), false);
chk('보낼 저장소를 물어본다', /_backupRepo_\(\)/.test(daily), true);

/* ── 두 모양이 같은 답을 주는가 ────────────────────────────────────── */
console.log('\n두 모양이 같은 답을 주는가');
const out = execFileSync('python3', ['-'], {
  cwd: ROOT, encoding: 'utf8', input: `
import json, sys
sys.path.insert(0, 'tools')
import gen_student_final as G
exams = {e['id']: e for e in json.load(open('exams.json'))}
e = exams['jmchc-1']
key = e['key']
ans = ''.join(str(((k or 1) % 4) + 1) for k in key)       # 전부 한 칸씩 민 답안
ans = ans[:5] + '0' + ans[6:]                              # 여섯째는 안 쓴 것으로
old = {'answers': ans}
wrong, blank = [], []
for q in range(1, e['nQ'] + 1):
    a = int(ans[q-1])
    if not G._okq(e, q, a):
        wrong.append(q)
        if a == 0: blank.append(q)
new = {'wrong': wrong, 'blank': blank, 'nQ': e['nQ']}
mo = [(q, b) for q, a, b in G._wrong_marks(old, e)]
mn = [(q, b) for q, a, b in G._wrong_marks(new, e)]
print(json.dumps({
  'same': mo == mn,
  'n': len(mo),
  'blankOld': [q for q, b in mo if b],
  'blankNew': [q for q, b in mn if b],
  'hasOld': G._has_marks(old, e),
  'hasNew': G._has_marks(new, e),
  'hasEmpty': G._has_marks({}, e),
}, ensure_ascii=False))
` });
const r = JSON.parse(out.trim().split('\n').pop());
chk('틀린 문항 목록이 두 모양에서 같다', r.same, true);
chk('틀린 것이 넉넉하다', r.n >= 20, true);
chk('안 쓴 문항이 그대로 남는다', r.blankNew, r.blankOld);
chk('안 쓴 문항이 실제로 있다', r.blankOld.length >= 1, true);
chk('옛 모양을 읽는다', r.hasOld, true);
chk('새 모양도 읽는다', r.hasNew, true);
chk('둘 다 없으면 안 읽는다', r.hasEmpty, false);

console.log(fail ? `\n${fail}건 어긋났다` : '\n다 맞다');
process.exit(fail ? 1 : 0);
