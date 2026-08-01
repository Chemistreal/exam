/* ============================================================
   깃허브 자동 저장 회귀 테스트 (순수 node)
   ------------------------------------------------------------
   학생 응시 기록은 여태 **구글 시트에만** 있었다. 코드·문항·해설은 깃허브에
   있지만 기록은 사본이 없어, 잘못 지우거나 덮어써도 되돌릴 방법이 없었다.

   이제 매일 한 번 시트를 깃허브에 커밋한다. 그런데 저장소는 공개다 —
   학생 이름이 그대로 올라가면 검색에 걸린다. 그래서 **이름 대신 코드**를
   싣는다. 여기서 지키는 것은 대부분 그 한 가지다.

   - 이름·학교·공유링크가 깃허브로 나가지 않는다 (링크에도 이름이 들어 있다)
   - 같은 학생은 늘 같은 코드다(날짜별 백업을 견줄 수 있어야 한다)
   - 이름만 알아도 코드를 만들어 볼 수 없다(소금을 섞는다)
   - 이름↔코드 표는 시트에만 쌓인다(되살릴 때 쓴다)
   - 토큰이 없으면 조용히 넘어간다 — 채점이 멈추면 안 된다
   - 손으로 넣은 기준 기록을 시트 것으로 덮지 않는다
     (엑셀에는 시트에 없는 옛 응시자가 들어 있다)

   실행:  node tests/backup-gs.js
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

/* ── 시트·깃허브를 흉내 낸다 ─────────────────────────────────────── */
function makeCtx(rows, opts) {
  opts = opts || {};
  const tabs = {};
  const puts = [];              // 깃허브에 올라간 것
  const fetched = [];
  function sheet(name, data) {
    return {
      _rows: data,
      getName: () => name,
      getLastRow() { return this._rows.length; },
      getLastColumn() { return (this._rows[0] || []).length; },
      appendRow(r) { this._rows.push(r.slice()); },
      setFrozenRows() {}, setColumnWidth() {},
      getRange(r, c, nr, nc) {
        const s = this; nr = nr || 1; nc = nc || 1;
        return {
          getValues() {
            const out = [];
            for (let i = 0; i < nr; i++) {
              const rr = s._rows[r - 1 + i] || [], L = [];
              for (let j = 0; j < nc; j++) L.push(rr[c - 1 + j]);
              out.push(L);
            }
            return out;
          },
          setValues(v) {
            v.forEach((rr, i) => {
              while (s._rows.length < r - 1 + i) s._rows.push([]);
              s._rows[r - 1 + i] = rr.slice();
            });
            return this;
          },
          setFontWeight() { return this; }, setBackground() { return this; },
          setFontColor() { return this; }, setHorizontalAlignment() { return this; },
          setValue() { return this; },
        };
      },
    };
  }
  tabs['성적기록'] = sheet('성적기록', [[
    '시험','학생이름','공유링크','저장시각','수험번호','응시일','학교','학년',
    '원점수','만점','백점환산','백분위','석차','전체누적인원','맞은개수','영역별 득점','답안(60)','성적표문자','원점수(감점)']].concat(rows));

  // 기본은 '토큰 있음'. 토큰 없는 경우는 그 검사에서만 따로 준다.
  const PROPS = Object.assign({ CODE_SALT: '고정소금', GITHUB_TOKEN: 'tok' }, opts.props || {});
  const ctx = {
    console, Date, JSON, Math, String, Number, Array, Object, isFinite, RegExp,
    SpreadsheetApp: {
      getActiveSpreadsheet: () => ({
        getSheetByName: n => tabs[n] || null,
        insertSheet(n) { tabs[n] = sheet(n, []); return tabs[n]; },
      }),
    },
    PropertiesService: { getScriptProperties: () => ({
      getProperty: k => (k in PROPS ? PROPS[k] : null),
      setProperty: (k, v) => { PROPS[k] = v; },
    }) },
    Utilities: {
      getUuid: () => 'uuid-1234',
      formatDate: (d, tz, f) => {
        const p = n => ('0' + n).slice(-2);
        if (/yyyy-MM-dd/.test(f)) return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate());
        if (/ww/.test(f)) return d.getFullYear() + '-W20';
        return String(d);
      },
      base64Encode: (s) => Buffer.from(s, 'utf8').toString('base64'),
      Charset: { UTF_8: 'utf8' },
      DigestAlgorithm: { SHA_256: 'sha256' },
      computeDigest: (alg, text) => {
        const h = require('crypto').createHash('sha256').update(text, 'utf8').digest();
        return Array.from(h).map(b => (b > 127 ? b - 256 : b));   // Apps Script 는 부호 있는 바이트
      },
    },
    UrlFetchApp: { fetch: (url, o) => {
      fetched.push(url);
      if (opts.onFetch) { const r = opts.onFetch(url, o); if (r) return r; }
      if ((o || {}).method === 'put') { puts.push({ url, body: JSON.parse(o.payload) }); }
      return { getResponseCode: () => ((o || {}).method === 'put' ? 201 : 404),
               getContentText: () => '{}' };
    } },
    ScriptApp: { getProjectTriggers: () => [], deleteTrigger() {},
      WeekDay: { SUNDAY: 0 },
      newTrigger: () => ({ timeBased: () => ({
        everyDays: () => ({ atHour: () => ({ inTimezone: () => ({ create() {} }) }) }),
        onWeekDay: () => ({ atHour: () => ({ inTimezone: () => ({ create() {} }) }) }) }) }) },
    Logger: { log() {} },
  };
  vm.createContext(ctx);
  vm.runInContext(SRC, ctx);
  ctx._puts = puts; ctx._tabs = tabs; ctx._fetched = fetched; ctx._props = PROPS;
  return ctx;
}
const D = (y, m, d) => new Date(y, m - 1, d);
const ROWS = [
  ['JMChC 모의고사 1회','김서준','https://x#r=jmchc-1.abc..~a3',D(2026,3,1),'',D(2026,2,28),'휘문중','2',
   45,60,75,80.5,'3/12',12,45,'원자 10/12',"'"+'1'.repeat(60),'',131],
  ['JMChC 모의고사 1회','이하윤','https://x#r=jmchc-1.def..~b7',D(2026,3,2),'',D(2026,2,28),'대원국제중','3',
   30,60,50,40.0,'9/12',12,30,'원자 5/12',"'"+'2'.repeat(60),'',86],
  ['JMChC 모의고사 2회','김서준','https://x#r=jmchc-2.ghi..~a3',D(2026,3,3),'',D(2026,3,2),'휘문중','2',
   50,60,83,90.0,'1/8',8,50,'원자 11/12',"'"+'3'.repeat(60),'',146],
  ['JMChC 모의고사 2회','박하람','https://x#r=jmchc-2.jkl..~c9',D(2026,3,4),'',D(2026,3,2),'중대부중','2',
   38,60,63,60.0,'4/8',8,38,'원자 7/12',"'"+'4'.repeat(60),'',110],
];

console.log('── 이름이 깃허브로 나가지 않는다 ──');
{
  const ctx = makeCtx(ROWS);
  ctx.dailyBackup();
  chk('파일 하나를 올린다', ctx._puts.length, 1);
  const put = ctx._puts[0];
  chk('날짜별 파일이다', /backup\/\d{4}-\d{2}-\d{2}\.json$/.test(put.url), true);
  const text = Buffer.from(put.body.content, 'base64').toString('utf8');
  /* 여기가 이 검사의 이유다. 저장소는 공개고, 한 번 올라간 것은 커밋 이력에
     영영 남는다. */
  ['김서준', '이하윤', '박하람', '휘문중', '대원국제중', '중대부중'].forEach(w =>
    chk("'" + w + "' 이 안 실린다", text.indexOf(w), -1));
  // 공유 링크에는 이름이 base64 로 들어 있다. 링크째로 실으면 이름이 나간다.
  chk('공유 링크가 안 실린다', /https:\/\/x#r=/.test(text), false);

  const j = JSON.parse(text);
  chk('네 줄이 다 실린다', j.rows.length, 4);
  chk('코드로 바뀌었다', /^s[0-9a-z]{11}$/.test(j.rows[0].code), true);
  chk('같은 학생은 같은 코드', j.rows[0].code, j.rows[2].code);
  chk('다른 학생은 다른 코드', j.rows[0].code !== j.rows[1].code, true);
  chk('점수·답안은 그대로', [j.rows[0].correct, j.rows[0].answers.length, j.rows[0].raw], [45, 60, 131]);
  chk('학년은 남긴다(개인 특정 불가)', j.rows[0].grade, '2');
}

console.log('\n── 이름만 알아도 코드를 못 만든다 ──');
{
  /* 소금을 안 섞으면 이름을 아는 사람이 코드를 만들어 대조해 볼 수 있다.
     소금은 이 프로젝트에만 있다. */
  const a = makeCtx(ROWS, { props: { CODE_SALT: '소금하나' } });
  const b = makeCtx(ROWS, { props: { CODE_SALT: '소금둘' } });
  chk('소금이 다르면 코드도 다르다',
      a._codeOf_('김서준', '휘문중') !== b._codeOf_('김서준', '휘문중'), true);
  chk('소금이 같으면 늘 같은 코드',
      a._codeOf_('김서준', '휘문중'), makeCtx(ROWS, { props: { CODE_SALT: '소금하나' } })._codeOf_('김서준', '휘문중'));
  // 이름 앞뒤 공백은 같은 사람이다(앱·시트가 이미 그렇게 센다)
  chk('공백은 같은 사람', a._codeOf_(' 김 서준 ', '휘문중'), a._codeOf_('김서준', '휘문중'));
  chk('이름이 없으면 코드도 없다', a._codeOf_('', '휘문중'), '');
  // 소금이 없으면 만들어 두고, 그 뒤로는 바뀌지 않아야 한다
  const c = makeCtx(ROWS, { props: {} });
  const c1 = c._codeOf_('김서준', '휘문중'), c2 = c._codeOf_('김서준', '휘문중');
  chk('소금이 없으면 만들어 둔다', !!c._props.CODE_SALT, true);
  chk('만든 뒤에는 안 바뀐다', c1, c2);
}

console.log('\n── 이름↔코드 표는 시트에만 ──');
{
  const ctx = makeCtx(ROWS);
  ctx.dailyBackup();
  const tab = ctx._tabs['_이름코드'];
  chk('표 탭이 생긴다', !!tab, true);
  chk('학생 수만큼 줄이 선다', tab._rows.length - 1, 3);       // 김서준·이하윤·박하람
  chk('이름이 표에는 있다', tab._rows.slice(1).map(r => r[1]).sort(), ['김서준', '박하람', '이하윤']);
  ctx.dailyBackup();                                          // 두 번 돌려도
  chk('같은 학생을 두 번 안 적는다', ctx._tabs['_이름코드']._rows.length - 1, 3);
}

console.log('\n── 토큰이 없으면 조용히 넘어간다 ──');
{
  /* 백업이 안 된다고 채점이 멈추면 안 된다. 토큰은 선생님이 나중에 넣는다. */
  const ctx = makeCtx(ROWS, { props: { GITHUB_TOKEN: '' } });
  ctx.dailyBackup(); ctx.rebuildBaseline(); ctx.weeklyReport();
  chk('아무것도 안 올린다', ctx._puts.length, 0);
  chk('예외로 죽지 않는다', true, true);
}

console.log('\n── 기준 기록: 손으로 넣은 것을 안 덮는다 ──');
{
  /* 엑셀에는 이 시트에 없는 옛 응시자가 들어 있다. 시트만으로 덮으면
     모집단이 46명에서 2명으로 줄어든다 — 석차가 통째로 틀어진다. */
  const old = { exams: { 'jmchc-1': { n: 46, hist: { 30: 46 }, byHand: true },
                         'jmchc-9': { n: 30, hist: { 20: 30 }, byHand: true } } };
  const ctx = makeCtx(ROWS, { props: { GITHUB_TOKEN: 'tok' }, onFetch: (url, o) => {
    if (/raw\.githubusercontent/.test(url))
      return { getResponseCode: () => 200, getContentText: () => JSON.stringify(old) };
    return null;
  } });
  ctx.rebuildBaseline();
  chk('한 번 올린다', ctx._puts.length, 1);
  const j = JSON.parse(Buffer.from(ctx._puts[0].body.content, 'base64').toString('utf8'));
  chk('손으로 넣은 1회차는 그대로', j.exams['jmchc-1'].n, 46);
  chk('손으로 넣은 9회차도 그대로', j.exams['jmchc-9'].n, 30);
  chk('시트에만 있는 2회차가 새로 생긴다', !!j.exams['jmchc-2'], true);
  chk('기준 기록에 이름이 없다', /김서준|이하윤|박하람|휘문중/.test(JSON.stringify(j)), false);
}

console.log('\n── 기준 기록: 모집단이 안 되면 안 만든다 ──');
{
  const ctx = makeCtx([ROWS[2]], { props: { GITHUB_TOKEN: 'tok' } });   // 2회차 한 명뿐
  ctx.rebuildBaseline();
  chk('한 명뿐이면 안 올린다', ctx._puts.length, 0);
}

console.log('\n── 주간 리포트 ──');
{
  const now = new Date();
  const recent = ROWS.map(r => r.slice());
  recent.forEach((r, i) => { r[3] = new Date(now.getTime() - (i + 1) * 86400000); });
  const ctx = makeCtx(recent, { props: { GITHUB_TOKEN: 'tok' } });
  ctx.weeklyReport();
  chk('한 장 올린다', ctx._puts.length, 1);
  const md = Buffer.from(ctx._puts[0].body.content, 'base64').toString('utf8');
  chk('마크다운이다', /report\/.*\.md$/.test(ctx._puts[0].url), true);
  chk('회차별 표가 있다', /\| 회차 \| 채점 \| 평균 \| 최고 \|/.test(md), true);
  chk('학생 수를 센다', /학생 3명/.test(md), true);
  chk('이름이 안 실린다', /김서준|이하윤|박하람|휘문중/.test(md), false);

  const oldOnly = ROWS.map(r => r.slice());
  oldOnly.forEach(r => { r[3] = new Date(now.getTime() - 90 * 86400000); });
  const ctx2 = makeCtx(oldOnly, { props: { GITHUB_TOKEN: 'tok' } });
  ctx2.weeklyReport();
  chk('이번 주 채점이 없으면 안 올린다', ctx2._puts.length, 0);
}

console.log('\n── 깃허브에 쓰는 방식 ──');
{
  const ctx = makeCtx(ROWS, { props: { GITHUB_TOKEN: 'tok' } });
  ctx.dailyBackup();
  const put = ctx._puts[0];
  chk('브랜치를 지정한다', put.body.branch, 'main');
  chk('커밋 메시지가 있다', /자동 백업 \d{4}-\d{2}-\d{2} · 4건/.test(put.body.message), true);
  // 같은 날 두 번 돌면 덮어써야 한다 — sha 없이 PUT 하면 깃허브가 거부한다
  chk('기존 파일 sha 를 먼저 물어본다',
      ctx._fetched.some(u => /contents\/backup\/.*\?ref=main$/.test(u)), true);
  // 실패를 삼키면 백업이 안 되는 줄도 모른다
  let threw = false;
  const bad = makeCtx(ROWS, { props: { GITHUB_TOKEN: 'tok' },
    onFetch: (url, o) => ((o || {}).method === 'put'
      ? { getResponseCode: () => 403, getContentText: () => 'forbidden' } : null) });
  try { bad.dailyBackup(); } catch (e) { threw = /깃허브 저장 실패 403/.test(e.message); }
  chk('실패하면 조용히 넘어가지 않는다', threw, true);
}

console.log(fail ? `\n${fail}개 실패` : '\n모두 통과');
process.exit(fail ? 1 : 0);
