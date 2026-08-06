/* ============================================================
   채점이 몰릴 때 방금 저장한 줄이 사라지지 않는가
   ------------------------------------------------------------
   2026-08-05, JMChC 모의고사 11회를 열 명 이어서 채점했는데 **셋이
   사라졌다**(김규민 · 전준 · 최민준). 시트에 들어왔다가 없어졌다.

   원인.

     doPost 는 한 줄을 덧붙인 뒤 `recomputeAllExams()` 를 부른다. 그것은
     시트를 통째로 **읽어**(사진을 찍고) 석차·백분위를 다시 계산한 다음
     통째로 **되쓴다**. 저장마다 잠금을 걸지만 20초 안에 못 얻으면
     **잠금 없이 진행**하게 되어 있었다.

     그래서 채점이 몰리면 이렇게 된다.

       A 저장: 줄 덧붙임(147) → 읽음(147장 사진) →  … 계산 중 …
       B 저장: 줄 덧붙임(148) → 읽음 → 계산 → 되씀(148줄)
       A 되씀: **147줄짜리 옛 사진**을 2~148행에 덮어씀
               → B 가 덧붙인 148행이 A 의 마지막 줄로 덮인다
       다음 재계산: 같은 줄이 둘이 되었으니 중복으로 하나를 지운다
               → **B 의 학생이 사라진다**

     시트 줄 수도 딱 맞아떨어졌다. 전날 백업 140줄 + 열 명 채점 − 셋 = 147줄,
     실제로 147줄이었다.

   막는 법. 되쓰기 직전에 **읽을 때의 줄 수와 지금 줄 수를 견준다.** 다르면
   그 사이에 저장이 들어온 것이니 **쓰지 않고 물러난다.**

   물러나도 잃는 것이 없다 — 재계산은 저장마다 도는 것이라 다음 저장이 전부
   다시 맞춘다. 반대로 한 번 덮어쓴 줄은 되돌릴 방법이 없다.

   실행:
       NODE_PATH=/opt/node22/lib/node_modules node tests/concurrent-save.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const env = require('./_gasenv.js');

const ROOT = path.join(__dirname, '..');
const SRC = fs.readFileSync(path.join(ROOT, 'AppsScript-Code.gs'), 'utf8');

let fail = 0;
const chk = (n, got, want) => {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  console.log((ok ? '  PASS  ' : '  FAIL  ') + n +
    (ok ? '' : `  → ${JSON.stringify(got)} (기대 ${JSON.stringify(want)})`));
  if (!ok) fail++;
};

/* 서식 붙이는 손짓(setBackground·setBorder…)은 줄줄이 이어 부른다. 하나하나
   흉내 내면 시험이 시트 API 목록이 되어 버린다 — 모르는 손짓은 자기를 그대로
   돌려주게 두고, 우리가 **보려는 것만** 진짜로 적어 둔다. */
function stubRange(known) {
  const proxy = new Proxy(known, {
    get(t, k) { return (k in t) ? t[k] : () => proxy; },
  });
  return proxy;
}

/* 시트 흉내. 우리가 보려는 것은 딱 둘이다 — 되쓰기와 줄 수. */
function makeSheet(rows) {
  const sh = {
    _rows: rows,                       // 자료 줄만(머리글 제외)
    _head: {},                         // 머리글 칸(1행)
    writes: 0,
    getLastRow() { return this._rows.length + 1; },
    getRange(r, c, nr, nc) {
      if (nr == null) {                // 칸 하나 — 머리글 확인·기록에 쓴다
        const key = r + ',' + c;
        return stubRange({
          getValue: () => (r === 1 ? (sh._head[key] || '') : ''),
          setValue(v) { sh._head[key] = v; return this; },
        });
      }
      return stubRange({
        getValues() { return sh._rows.slice(r - 2, r - 2 + nr).map(x => x.slice()); },
        setValues(v) { sh.writes++; for (let i = 0; i < v.length; i++) sh._rows[r - 2 + i] = v[i].slice(); },
      });
    },
    appendRow(r) { this._rows.push(r.slice()); return this; },
    deleteRow(r) { this._rows.splice(r - 2, 1); },
  };
  /* 머리글은 이미 제대로 박혀 있다고 본다 — 그것을 보려는 시험이 아니다. */
  sh._head['1,18'] = '성적표 문자';
  sh._head['1,19'] = '원점수(감점 반영)';
  return sh;
}

/* 성적기록이 아닌 시트(성적문자 등). 무엇을 하든 받아 주기만 한다. */
function scratchSheet() {
  const d = {
    _rows: [],
    getLastRow: () => 1,
    getRange: () => stubRange({ getValues: () => [[]], getValue: () => '' }),
  };
  return new Proxy(d, { get(t, k) { return (k in t) ? t[k] : () => d; } });
}

function ctxWith(sheet) {
  /* _gasenv 는 **함수**다. Object.assign 으로 베끼면 Utilities 가 안 들어와서
     연도 계산이 통째로 넘어지고, 그러면 재계산이 조용히 실패한다(회차마다
     try 로 감싸 놓아서 겉으로는 멀쩡해 보인다). 제대로 부른다. */
  const ctx = env();
  const scratch = scratchSheet();
  ctx.SpreadsheetApp = {
    getActiveSpreadsheet: () => ({
      getSheetByName: (n) => (n === '성적기록' ? sheet : scratch),
      insertSheet: () => scratch,
    }),
    BorderStyle: { SOLID: 'solid' },
    flush() {},
  };
  ctx.Logger = { log() {} };
  /* 트리거 흉내. 무엇이 걸렸는지 세어 보려고 목록을 들고 있는다. */
  ctx.booked = [];
  ctx.ScriptApp = {
    getProjectTriggers: () => ctx.booked.map(h => ({ getHandlerFunction: () => h })),
    deleteTrigger(t) {
      const i = ctx.booked.indexOf(t.getHandlerFunction());
      if (i >= 0) ctx.booked.splice(i, 1);
    },
    newTrigger(h) {
      const b = { timeBased: () => b, after: () => b, create() { ctx.booked.push(h); return b; } };
      return b;
    },
  };
  /* 잠금 흉내. 몇 번 쥐었는지 세어 둔다 — 저장이 재계산까지 쥐고 있으면
     뒤에 온 저장이 줄을 서고, 그게 이번 사고의 뿌리였다. */
  ctx.locks = { taken: 0, held: 0, maxHeld: 0 };
  ctx.LockService = {
    getScriptLock: () => ({
      waitLock() {
        ctx.locks.taken++; ctx.locks.held++;
        ctx.locks.maxHeld = Math.max(ctx.locks.maxHeld, ctx.locks.held);
      },
      releaseLock() { ctx.locks.held--; },
    }),
  };
  /* doGet 을 부르려면 응답을 만드는 흉내가 있어야 한다. */
  ctx.ContentService = {
    MimeType: { JAVASCRIPT: 'js', JSON: 'json' },
    createTextOutput: (t) => ({ _t: t, setMimeType() { return this; }, getContent() { return this._t; } }),
  };
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  return ctx;
}

const WIDE = 19;
const row = (exam, name, ans) => {
  const r = new Array(WIDE).fill('');
  r[0] = exam; r[1] = name; r[3] = new Date(); r[8] = 30; r[9] = 60;
  r[14] = 30; r[16] = "'" + ans;
  return r;
};

console.log('── 겹친 저장에서 방금 넣은 줄이 살아남는가 ──');
{
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);

  /* A 가 읽은 사진(두 줄). 그 뒤 B 가 한 줄을 덧붙였다. */
  const snapshot = sheet._rows.map(r => r.slice());
  sheet._rows.push(row(T, '김규민', '3'.repeat(60)));      // B 의 저장

  const before = sheet._rows.length;
  const wrote = ctx._flushRows(sheet, snapshot, [], snapshot.length);

  chk('물러났다(안 썼다)', wrote, false);
  chk('시트를 건드리지 않았다', sheet.writes, 0);
  chk('방금 넣은 줄이 그대로 있다', sheet._rows.length, before);
  chk('그 줄이 김규민이다', sheet._rows[2][1], '김규민');
}

console.log('\n── 겹치지 않았으면 예전처럼 쓴다 ──');
{
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);
  const data = sheet._rows.map(r => r.slice());
  data[0][11] = 88;                                        // 백분위를 고쳐 본다
  const wrote = ctx._flushRows(sheet, data, [], data.length);
  chk('썼다', wrote, true);
  chk('고친 값이 반영됐다', sheet._rows[0][11], 88);
}

console.log('\n── 줄 수를 안 넘기면 예전 그대로 (하위호환) ──');
{
  const sheet = makeSheet([row('X', 'ㄱ', '1'), row('X', 'ㄴ', '2')]);
  const ctx = ctxWith(sheet);
  const data = sheet._rows.map(r => r.slice());
  sheet._rows.push(row('X', 'ㄷ', '3'));                    // 사이에 한 줄 들어왔다
  chk('그래도 쓴다', ctx._flushRows(sheet, data, []), true);
}

console.log('\n── 중복 줄은 여전히 지운다 ──');
{
  const T = 'JMChC 모의고사 11회';
  const same = '4'.repeat(60);
  const sheet = makeSheet([row(T, '김지성', same), row(T, '김지성', same), row(T, '오승민', '1'.repeat(60))]);
  const ctx = ctxWith(sheet);
  const data = sheet._rows.map(r => r.slice());
  const drop = ctx._recalcRows(data, T, [], 60);
  ctx._flushRows(sheet, data, drop, data.length);
  chk('같은 이름·같은 답안 한 줄만 남는다', sheet._rows.length, 2);
  chk('다른 학생은 안 지운다', sheet._rows.map(r => r[1]).sort(), ['김지성', '오승민']);
}

console.log('\n── 이름이 다르면 절대 안 지운다 ──');
{
  const T = 'JMChC 모의고사 11회';
  /* 사라진 셋은 이름이 서로 달랐다. 중복 지우기로는 없어질 수 없다 —
     그것이 '덮어쓰기가 범인' 이라는 판단의 근거였다. 못박아 둔다. */
  const names = ['김규민', '전준', '최민준', '김지성', '오승민'];
  const sheet = makeSheet(names.map((n, i) => row(T, n, String((i % 4) + 1).repeat(60))));
  const ctx = ctxWith(sheet);
  const data = sheet._rows.map(r => r.slice());
  const drop = ctx._recalcRows(data, T, [], 60);
  chk('지울 줄이 없다', drop, []);
  ctx._flushRows(sheet, data, drop, data.length);
  chk('다섯 명 그대로', sheet._rows.map(r => r[1]).sort(), names.slice().sort());
}

console.log('\n── 지금 다시 맞추기 창구 ──');
{
  /* 재계산은 저장마다 돌지만, 채점이 몰려 겹치면 물러난다. 그러면 그 회차는
     **저장 순간의 인원**이 굳은 채 남는다 — 먼저 채점한 학생은 1명 중 1등,
     나중 학생은 10명 중 3등. 밤 05시 트리거를 기다리지 않고 부를 수 있어야 한다.
     2026-08-05 JMChC 12회가 그랬다. */
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);
  const out = ctx.doGet({ parameter: { action: 'recompute', callback: '__c' } });
  const txt = String(out.getContent());
  chk('JSONP 로 감싼다', /^__c\(/.test(txt), true);
  const j = JSON.parse(/^__c\(([\s\S]*?)\);?$/.exec(txt)[1]);
  if (!j.ok) console.log('  진단: ' + j.error);
  chk('맞췄다고 답한다', j.ok, true);
  chk('몇 회차를 맞췄는지 알린다', typeof j.done, 'number');
  chk('시트에 실제로 썼다', sheet.writes > 0, true);
  /* 전체누적인원(13열)이 두 줄 다 같은 수로 맞춰져야 한다 — 그것이 '총원' 이다. */
  const ns = sheet._rows.map(r => r[13]);
  chk('총원이 두 줄 다 같다', ns[0] === ns[1], true);
}

/* 읽는 순간에 남이 한 줄 밀어 넣는 상황을 만든다. `times` 번만 그런다. */
function raceOnRead(sheet, times, mkRow) {
  const realGet = sheet.getRange.bind(sheet);
  let n = 0;
  sheet.getRange = function (r, c, nr, nc) {
    const rng = realGet(r, c, nr, nc);
    const gv = rng.getValues;
    rng.getValues = function () {
      const v = gv.call(rng);
      if (n < times && nr > 1) { n++; sheet._rows.push(mkRow(n)); }
      return v;
    };
    return rng;
  };
}

console.log('\n── 한 번 겹쳐도 굳지 않는다 (다시 읽어 맞춘다) ──');
{
  /* 물러나기만 하면 그 회차는 저장 순간의 인원이 굳는다 — 먼저 채점한 학생은
     1명 중 1등, 나중 학생은 10명 중 3등. 물러난 뒤 **다시 읽어** 맞춰야
     모든 시험이 그때그때 전체 인원으로 선다. */
  const T = 'JMChC 모의고사 11회';
  /* 총원에는 옛 회차의 인원(EXAM_COHORT 의 base)이 얹힌다. 숫자를 적어 두면
     회차 설정이 바뀔 때마다 시험이 깨진다 — **안 겹쳤을 때와 견준다.** */
  const calm = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  ctxWith(calm).doGet({ parameter: { action: 'recompute', callback: '__c' } });
  const n2 = calm._rows[0][13];

  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);
  raceOnRead(sheet, 1, () => row(T, '김규민', '3'.repeat(60)));
  const j = JSON.parse(/^__c\(([\s\S]*?)\);?$/.exec(
    String(ctx.doGet({ parameter: { action: 'recompute', callback: '__c' } }).getContent()))[1]);
  chk('물러나고 끝내지 않는다', !j.retry, true);
  chk('세 줄 다 있다', sheet._rows.length, 3);
  chk('끼어든 줄까지 총원에 든다', sheet._rows.map(r => r[13]), [n2 + 1, n2 + 1, n2 + 1]);
  chk('예약까지 갈 일이 없었다', ctx.booked, []);
}

console.log('\n── 계속 겹치면 조금 뒤 혼자 다시 돈다 ──');
{
  /* 세 번 다시 읽어도 계속 겹치면 지금 채점이 몰리는 중이다. 그 저장들이
     스스로 맞추겠지만 **마지막 저장이 겹쳐 물러난 경우**는 뒤에 아무도 없다.
     그 자리를 예약이 메운다 — 아무도 안 누르는 것이 정상이어야 한다. */
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);
  raceOnRead(sheet, 99, (n) => row(T, '난입' + n, String((n % 4) + 1).repeat(60)));
  const j = JSON.parse(/^__c\(([\s\S]*?)\);?$/.exec(
    String(ctx.doGet({ parameter: { action: 'recompute', callback: '__c' } }).getContent()))[1]);
  chk('물러났다고 알린다', j.retry, true);
  chk('저절로 맞춰진다고 말한다', /저절로|1분/.test(j.msg || ''), true);
  chk('한 번도 안 썼다', sheet.writes, 0);
  chk('난입한 줄이 다 살아 있다', sheet._rows.filter(r => /^난입/.test(r[1])).length, 3);
  chk('조금 뒤로 예약했다', ctx.booked, ['recomputeSoon']);

  /* 예약은 하나만. 열 명이 몰아 채점하면 예약도 열 개가 되고, 앱스크립트
     트리거는 20개가 상한이다. */
  ctx.doGet({ parameter: { action: 'recompute', callback: '__c' } });
  chk('예약은 하나만 건다', ctx.booked, ['recomputeSoon']);

  /* 예약이 돌 때 자기 예약을 안 지우면, 그때도 겹쳤을 경우 '이미 걸려 있다' 로
     보여 영영 다시 안 걸린다. */
  ctx.recomputeSoon();
  chk('예약이 돌면 다시 걸 수 있다', ctx.booked, ['recomputeSoon']);
}

console.log('\n── 저장은 덧붙이고 끝난다 (재계산은 예약한다) ──');
{
  /* 2026-08-06. 저장이 재계산을 **끝까지 돌린 뒤** 잠금을 놓고 있었다. 재계산은
     시트를 통째로 읽고 다시 쓰는 일이라 몇 초가 걸린다 — 열 명을 이어 채점하면
     마지막 사람은 그만큼 줄을 서고, 화면은 '보냈다' 는데 시트에는 한참 안 보인다.
     앱은 못 갔다고 보고 다시 보내고, 같은 줄이 쌓였다가 중복 지우기에 지워진다.
     **줄이 생겼다 지워졌다** 하던 것이 그것이다. */
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60))]);
  const ctx = ctxWith(sheet);
  const post = (nm, ans) => ctx.doPost({ postData: { contents: JSON.stringify({
    exam: T, name: nm, total: 30, max: 60, correct: 30, answers: ans, areas: '', n: 1, rank: 1,
  }) } });

  const r1 = JSON.parse(String(post('오승민', '2'.repeat(60)).getContent()));
  chk('저장은 성공이라고 답한다', r1.ok, true);
  chk('줄이 붙었다', sheet._rows.length, 2);
  chk('저장이 시트를 다시 쓰지 않는다', sheet.writes, 0);
  chk('재계산을 예약해 뒀다', ctx.booked, ['recomputeSoon']);

  /* 열 명을 이어 채점해도 예약은 하나, 되쓰기는 0 이다. */
  const before = ctx.locks.taken;
  for (let i = 0; i < 9; i++) post('학생' + i, String((i % 4) + 1).repeat(60));
  chk('열 명이 다 붙었다', sheet._rows.length, 11);
  chk('그래도 되쓰기는 없다', sheet.writes, 0);
  chk('예약은 여전히 하나', ctx.booked, ['recomputeSoon']);
  chk('저장마다 잠금을 쥐긴 한다', ctx.locks.taken - before, 9);
  chk('잠금을 겹쳐 쥐지 않는다', ctx.locks.held, 0);

  /* 예약이 돌면 그때 전부 맞춘다. */
  ctx.recomputeSoon();
  chk('예약이 돌면 그때 쓴다', sheet.writes > 0, true);
  chk('열한 줄 그대로', sheet._rows.length, 11);
  const ns = sheet._rows.map(r => r[13]);
  chk('총원이 모두 같다', ns.every(x => x === ns[0]), true);
  chk('예약을 지우고 돌았다', ctx.booked, []);
}

console.log('\n── 한 회차만 맞출 때도 같다 ──');
{
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);
  raceOnRead(sheet, 1, () => row(T, '김규민', '3'.repeat(60)));
  chk('겹쳐도 결국 맞춘다', ctx.recomputeExam(T, [], 60), true);
  chk('총원이 세 줄 다 같다', sheet._rows.map(r => r[13]), [3, 3, 3]);
}

console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
process.exit(fail ? 1 : 0);
