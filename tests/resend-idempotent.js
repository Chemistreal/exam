/* ============================================================
   **다시 보내도 줄이 늘지 않는다** — 시트 저장은 같은 응시를 덮어쓴다
   ------------------------------------------------------------
   2026-08-12, 선생님이 물으셨다 — *"이런애들 지금 시험 안봤는데 왜
   올라가있어?"* 7월에 본 회차의 학생 넷이 **오늘 날짜로** 시트에 있었다.
   그날 채점한 것은 다른 회차뿐이었다.

   고리는 이랬다.

     ① 앱은 `no-cors` 로 쏘므로 **갔는지 알 수가 없다**
     ② 그래서 «아직 확인 못 함(up:0)» 을 달고 열 때마다 **다시 보낸다**
        — 망이 끊긴 채 채점한 기록을 살리는 유일한 장치다
     ③ `doPost` 가 무조건 appendRow 했다 → 다시 보낼 때마다 **새 줄**,
        저장시각은 `new Date()` = 오늘
     ④ 30초 뒤 재계산이 «이름+답안 같으면 최신 1건만 남김» 으로 정리하면서
        **오늘 것을 남기고 원본을 지웠다**
     ⑤ 7월 기록의 날짜가 오늘로 바뀌어, 오늘 본 것처럼 보였다

   ②는 옳은 설계다. 다만 **다시 보내는 것이 무해하다**는 전제 위에 서 있는데,
   ③이 그 전제를 깨고 있었다. 여기서 지키는 것이 그 전제다.

     · 같은 응시(시험+이름+답안)를 다시 보내도 **줄이 안 는다**
     · **저장시각·응시일이 안 바뀐다** — 그것이 이 병의 증상이었다
     · 다시 보낸 것에 학교·학년이 비어 있어도 **있던 값을 안 지운다**
     · 답안이 다르면 **다시 푼 것**이므로 새 줄이 맞다

   실행:  node tests/resend-idempotent.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* ── 시트를 흉내 낸다 ────────────────────────────────────────────────
   진짜 스프레드시트가 하는 일 가운데 이 검사가 쓰는 것만: 행을 덧붙이고,
   범위를 읽고, 범위를 덮어쓴다. 1부터 세는 행 번호도 그대로 흉내 낸다. */
function makeSheet(rows) {
  const data = rows.map(r => r.slice());
  return {
    _rows: data,
    getLastRow: () => data.length,
    getName: () => '성적기록',
    appendRow(r) { data.push(r.slice()); },
    setFrozenRows() {}, setFontWeight() {},
    getRange(r, c, nr, nc) {
      return {
        getValues() {
          const out = [];
          for (let i = 0; i < (nr || 1); i++) {
            const row = data[r - 1 + i] || [];
            out.push(row.slice(c - 1, c - 1 + (nc || 1)));
          }
          return out;
        },
        setValues(v) {
          for (let i = 0; i < v.length; i++) {
            const ri = r - 1 + i;
            while (data.length <= ri) data.push([]);
            for (let j = 0; j < v[i].length; j++) data[ri][c - 1 + j] = v[i][j];
          }
        },
        setFontWeight() { return this; },
      };
    },
  };
}

function run(sheetRows, payload) {
  const sheet = makeSheet(sheetRows);
  const ctx = {
    console,
    JSON, Date, String, Number, Math, RegExp, Array, Object,
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ({
        getSheetByName: () => sheet,
        insertSheet: () => sheet,
      }),
      flush() {},
    },
    LockService: { getScriptLock: () => ({ waitLock() {}, releaseLock() {} }) },
    ContentService: {
      createTextOutput: t => ({ setMimeType: () => t }),
      MimeType: { JSON: 'json' },
    },
    Logger: { log() {} },
    /* 재계산은 여기서 볼 것이 아니다 — 예약만 되게 하고 안 돌린다.
       (돌리면 이 검사가 «덧붙이기» 가 아니라 «재계산» 을 재게 된다) */
    ScriptApp: { getProjectTriggers: () => [], newTrigger: () => { throw new Error('no'); } },
  };
  ctx.globalThis = ctx;
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx, { filename: 'AppsScript-Code.gs' });
  ctx._bookRecompute_ = () => 'have';          // 예약돼 있는 셈 친다
  ctx.recomputeAllExams = () => {};
  vm.runInContext('doPost({ postData: { contents: ' +
    JSON.stringify(JSON.stringify(payload)) + ' } });', ctx);
  return sheet._rows;
}

const HEAD = ['시험', '학생이름', '공유링크', '저장시각', '수험번호', '응시일', '학교', '학년',
  '원점수', '만점', '백점환산', '백분위', '석차', '전체누적인원',
  '맞은개수', '영역별 득점', '답안(60)'];

const ANS = '2'.repeat(60);
const JULY = new Date('2026-07-22T03:44:14Z');

/* 7월에 채점돼 시트에 들어간 줄 하나. */
const seeded = () => [HEAD.slice(), [
  'KMChC 2018', '이도현', 'https://…/final.html#r=hwol-2018.x..~name', JULY,
  '', '2026-07-22', '백현중', '2', 43, 60, 72, 77.6, '25/114', 114,
  43, '액체,용액 4/4', "'" + ANS, '', 129,
]];

/* 앱이 «아직 확인 못 함» 이라며 **똑같은 것을 다시 보낸다.**
   링크로 열린 성적표에서 온 것이라 학교·학년이 비어 있다 — 실제로 그랬다. */
const resend = {
  exam: 'KMChC 2018', name: '이도현', link: '', examno: '', date: '2026-08-12',
  school: '', grade: '', total: 43, max: 60, pct100: 72, percentile: 78.1,
  rank: '24/112', n: 112, correct: 43, areas: '액체,용액 4/4', answers: ANS, raw: 114,
};

console.log('── 같은 응시를 다시 보냈다 ──');
{
  const rows = run(seeded(), resend);
  chk('줄이 안 늘었다', rows.length - 1, 1);
  chk('저장시각이 그대로다 (오늘로 안 바뀐다)', rows[1][3].getTime(), JULY.getTime());
  chk('응시일이 그대로다', String(rows[1][5]), '2026-07-22');
  chk('학교가 안 지워졌다', rows[1][6], '백현중');
  chk('학년이 안 지워졌다', rows[1][7], '2');
  chk('링크가 안 지워졌다', /final\.html#r=/.test(String(rows[1][2])), true);
  /* 다시 계산된 값(백분위·석차·인원)은 새것으로 갱신돼야 한다 —
     그 사이 응시자가 늘었으면 그 자리가 실제로 달라진다. */
  chk('백분위는 새 값으로 갱신된다', rows[1][11], 78.1);
  chk('전체누적인원도 갱신된다', rows[1][13], 112);
}

console.log('\n── 세 번 더 보내도 마찬가지다 ──');
{
  let rows = seeded();
  for (let i = 0; i < 3; i++) rows = run(rows, resend);
  chk('세 번을 더 보내도 한 줄이다', rows.length - 1, 1);
  chk('저장시각이 여전히 7월이다', rows[1][3].getTime(), JULY.getTime());
}

console.log('\n── 답안이 다르면 다시 푼 것이다 ──');
{
  const again = Object.assign({}, resend, { answers: '3'.repeat(60), total: 40 });
  const rows = run(seeded(), again);
  chk('새 줄이 생긴다', rows.length - 1, 2);
  chk('7월 줄은 그대로 남는다', rows[1][3].getTime(), JULY.getTime());
  chk('새 줄의 답안이 다르다', String(rows[2][16]).replace(/^'/, ''), '3'.repeat(60));
}

console.log('\n── 다른 학생·다른 회차는 안 건드린다 ──');
{
  const other = Object.assign({}, resend, { name: '김윤후', school: '해누리중' });
  const rows = run(seeded(), other);
  chk('다른 이름이면 새 줄', rows.length - 1, 2);
  const otherExam = Object.assign({}, resend, { exam: 'KMChC 2019' });
  const rows2 = run(seeded(), otherExam);
  chk('다른 회차면 새 줄', rows2.length - 1, 2);
}

console.log('\n── 이름의 띄어쓰기가 달라도 같은 응시다 ──');
{
  const spaced = Object.assign({}, resend, { name: '이 도현' });
  const rows = run(seeded(), spaced);
  chk('«이 도현» 도 같은 줄로 본다', rows.length - 1, 1);
}

console.log('\n── 첫 저장은 그대로 덧붙는다 ──');
{
  const rows = run([HEAD.slice()], resend);
  chk('빈 시트에 한 줄이 생긴다', rows.length - 1, 1);
  chk('저장시각이 찍힌다', rows[1][3] instanceof Date, true);
}

console.log(fail ? `\n실패 ${fail}건`
  : '\n다시 보내도 줄이 안 늘고, 처음 본 날이 안 바뀐다.');
process.exit(fail ? 1 : 0);
