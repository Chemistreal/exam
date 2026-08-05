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
  const ctx = env.make ? env.make() : Object.assign({}, env);
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

console.log('\n── 겹치면 물러났다고 알린다 ──');
{
  const T = 'JMChC 모의고사 11회';
  const sheet = makeSheet([row(T, '김지성', '1'.repeat(60)), row(T, '오승민', '2'.repeat(60))]);
  const ctx = ctxWith(sheet);
  /* 읽은 직후에 한 줄이 들어오는 상황을 만든다. */
  const realGet = sheet.getRange.bind(sheet);
  let once = false;
  sheet.getRange = function (r, c, nr, nc) {
    const rng = realGet(r, c, nr, nc);
    const gv = rng.getValues;
    rng.getValues = function () {
      const v = gv.call(rng);
      if (!once && nr > 1) { once = true; sheet._rows.push(row(T, '김규민', '3'.repeat(60))); }
      return v;
    };
    return rng;
  };
  const out = ctx.doGet({ parameter: { action: 'recompute', callback: '__c' } });
  const j = JSON.parse(/^__c\(([\s\S]*?)\);?$/.exec(String(out.getContent()))[1]);
  chk('물러났다고 알린다', j.retry, true);
  chk('다시 누르라고 말한다', /다시 눌러/.test(j.msg || ''), true);
  chk('방금 들어온 줄이 살아 있다', sheet._rows.some(r => r[1] === '김규민'), true);
}

console.log(fail ? `\nFAIL ${fail}건` : '\nPASS');
process.exit(fail ? 1 : 0);
