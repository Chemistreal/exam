/* ============================================================
   성적표 문자 다양화 회귀 테스트 (브라우저 불필요 — CI 에서 돈다)
   ------------------------------------------------------------
   문자에서 인사·안내·마무리가 매번 글자 하나까지 같았다. 명언만 돌아가고
   나머지는 고정이라, 같은 학부모가 회차마다 같은 문장을 받았다.

       "방향이 정확합니다. 오답 개념만 촘촘히 메우면 다음 시험에서
        확실한 도약이 기대됩니다."

   게다가 명언 색인이 매 실행 0부터 시작해, 각 밴드의 첫 학생은 늘 같은
   명언을 받았다.

   여기서 지키는 것:
   - 한 회차에서 여러 학생이 서로 다른 문장을 받는다
   - 같은 학생이 다음 회차에 다른 문장을 받는다
   - 같은 학생·같은 회차를 다시 돌리면 같은 문장이 나온다(고쳐 보내도 안 튄다)
   - {이름}·{범위} 같은 자리표시자가 그대로 찍히지 않는다
   - 조사가 붙는다(주기율'은' / 해결'을')

   실행:  node tests/message-variety.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

// Apps Script 전역만 평가한다. 시트 API 는 부르지 않으므로 스텁으로 충분하다.
const gas = {
  Logger: { log() {} }, SpreadsheetApp: {}, ContentService: {}, Utilities: {},
  PropertiesService: { getScriptProperties: () => ({ getProperty: () => '' }) },
};
vm.createContext(gas);
vm.runInContext(fs.readFileSync(path.join(__dirname, '..', 'AppsScript-Code.gs'), 'utf8'), gas);

const AREAS = '주기율 1/4, 산화환원 10/14, 고체 2/2';
const build = (title, nm, pct, qi) =>
  gas._buildReportMsg(title, nm, Math.round(pct * 0.6), pct, 70, AREAS, 'https://ex/1', qi || 0);

console.log('── 문장 목록 ──');
[['MSG_OPEN', 4], ['MSG_LEAD', 4], ['MSG_TOPIC', 4],
 ['MSG_STRONG', 0], ['MSG_WEAK', 0], ['MSG_CLOSE', 0]].forEach(([name, min]) => {
  const v = gas[name];
  const n = Array.isArray(v) ? v.length : Object.values(v).reduce((a, b) => a + b.length, 0);
  console.log(`  ${name} ${n}개`);
  if (min) chk(`${name} 가 ${min}개 이상`, n >= min, true);
});
chk('마무리 문장이 밴드마다 4개 이상', Object.keys(gas.MSG_CLOSE).every(b => gas.MSG_CLOSE[b].length >= 4), true);

console.log('\n── 자리표시자·조사 ──');
const one = build('JMChC 모의고사 6회', '이도현', 60);
chk('{…} 가 그대로 남지 않는다', /\{[^}]+\}/.test(one), false);
chk('이름이 들어간다', one.includes('이도현'), true);
chk('회차 제목이 들어간다', one.includes('JMChC 모의고사 6회'), true);
chk('링크가 들어간다', one.includes('https://ex/1'), true);
chk('강·약 영역이 들어간다', /주기율/.test(one) && /고체/.test(one), true);
// 받침 있는 말 뒤 '은', 없는 말 뒤 '는' — _fill 이 붙인다
const josa = [];
for (let i = 0; i < 40; i++) josa.push(build('T' + i + '회', '학생' + i, 60));
chk('잘못된 조사(…율는 / …결를)가 없다', josa.some(m => /[율흘물]는|해결를/.test(m)), false);

console.log('\n── 같은 회차, 학생끼리 ──');
const NAMES = ['김지성', '김규민', '이도현', '김시헌', '조민성', '장수호', '양준원', '강찬영'];
const sameRound = NAMES.map((n, i) => build('JMChC 모의고사 6회', n, 60, i));
const firstLines = sameRound.map(m => m.split('\n')[0]);
const closings = sameRound.map(m => m.split('\n').slice(-2)[0]);
const quotes = sameRound.map(m => m.split('\n').slice(-3)[0]);
console.log(`  인사 ${new Set(firstLines).size}종 · 마무리 ${new Set(closings).size}종 · 명언 ${new Set(quotes).size}종 (학생 ${NAMES.length}명)`);
chk('인사가 한 가지로 굳지 않는다', new Set(firstLines).size >= 3, true);
chk('마무리가 한 가지로 굳지 않는다', new Set(closings).size >= 3, true);
chk('명언은 같은 묶음 안에서 안 겹친다', new Set(quotes).size, NAMES.length);

console.log('\n── 같은 학생, 회차끼리 ──');
const ROUNDS = ['JMChC 모의고사 6회', 'JMChC 모의고사 7회', 'JMChC 모의고사 8회',
                'JMChC 모의고사 9회', 'JMChC 모의고사 10회'];
const sameKid = ROUNDS.map(t => build(t, '이도현', 60));
const kidClose = sameKid.map(m => m.split('\n').slice(-2)[0]);
const kidOpen = sameKid.map(m => m.split('\n')[0]);
const kidQuote = ROUNDS.map(t => build(t, '이도현', 60, 0).split('\n').slice(-3)[0]);
console.log(`  인사 ${new Set(kidOpen).size}종 · 마무리 ${new Set(kidClose).size}종 · 명언 ${new Set(kidQuote).size}종 (회차 ${ROUNDS.length}개)`);
chk('회차가 바뀌면 마무리도 바뀐다', new Set(kidClose).size >= 3, true);
/* 예전에는 명언 색인이 매 실행 0부터라, 각 밴드의 첫 학생은 회차가 달라져도
   늘 같은 명언을 받았다. 이제 회차별로 시작점을 옮긴다. */
chk('첫 학생 명언이 회차마다 바뀐다', new Set(kidQuote).size >= 3, true);

console.log('\n── 다시 돌려도 같은 문장 ──');
chk('같은 학생·같은 회차는 그대로', build('JMChC 모의고사 6회', '이도현', 60), one);

console.log('\n── 성취 밴드별 마무리 ──');
[['high', 92], ['mid', 66], ['low', 35]].forEach(([band, pct]) => {
  const got = NAMES.map(n => build('JMChC 모의고사 6회', n, pct).split('\n').slice(-2)[0]);
  const inPool = got.every(g => gas.MSG_CLOSE[band].indexOf(g) >= 0);
  chk(`${band} 은 ${band} 마무리만 쓴다`, inPool, true);
  chk(`${band} 마무리가 여러 가지`, new Set(got).size >= 3, true);
});

console.log('\n── 예시 (같은 회차 · 세 학생) ──');
[0, 1, 2].forEach(i => console.log('  · ' + sameRound[i].split('\n').slice(-2)[0]));

console.log(fail ? `\n실패 ${fail}건` : '\n전부 통과');
process.exit(fail ? 1 : 0);
