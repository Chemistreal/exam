/* ============================================================
   **제출한 답안이 사라지지 않는가** — 순수 node
   ------------------------------------------------------------
   2026-08-21, 선생님 — *"기출동형 4회 채점해서 보냈다는데 구글 스프레드시트에
   기록이 안되어있어."*

   그때 판 것: 구형 iOS 사파리는 `fetch(keepalive:true)` 를 무시해서, 보내자마자
   화면을 넘기면 요청이 끊긴다. 그래서 못 보낸 답안을 브라우저에 적어 두고
   다음에 열 때 다시 보내는 큐를 놓았다. 그런데 그 큐 자체에 답안을 **잃는**
   자리가 둘 있었다.

     ① 스냅샷을 await 너머로 들고 있었다
        pendFlush 가 들어올 때의 목록을 통째로 쥔 채 항목마다 2.5초씩 기다렸고,
        끝나서 그 스냅샷을 다시 썼다. 그 사이에 학생이 제출하면 새 항목이
        **덮어써 지워진다.** 그 제출의 직접 전송까지 실패했다면 답안은 흔적
        없이 사라진다 — 시트에도 없고, 큐에도 없고, 경고도 안 뜬다.

     ② 큐가 넘칠 때 «가장 오래된 것» 부터 버렸다
        `slice(-30)`. 그런데 오래된 것은 대개 **아직 한 번도 못 보낸** 답안이고,
        새것은 방금 세 번 보내 본 것이다. 잃으면 안 되는 쪽을 골라 버렸다.

   두 자리 다 주석으로만 지켜지고 있었다(검사 0건). 다음 사람이 스냅샷 꼴로
   되돌려도 CI 가 안 잡는다. 그래서 여기서 **실제로 경합을 일으켜** 센다.

   실행:  node tests/pending-queue.js
   ============================================================ */
'use strict';
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(ROOT, 'final-submit.html'), 'utf8');

let pass = 0, fail = 0;
function chk(desc, ok, extra) {
  console.log((ok ? '  PASS  ' : '  FAIL  ') + desc + (extra ? '  ' + extra : ''));
  ok ? pass++ : fail++;
}

/* 구현을 그대로 떼어 온다 — 검사가 제 사본을 들고 갈라지지 않게. */
function cut(from, to) {
  const a = html.indexOf(from);
  if (a < 0) throw new Error('없다: ' + from);
  const b = html.indexOf(to, a);
  if (b < 0) throw new Error('끝을 못 찾음: ' + to);
  return html.slice(a, b + to.length);
}
const SRC = cut("var PEND_KEY='exam.submit.pending.v1'",
  'function pendStuck(){ return pendAll().filter(function(x){ return x.n>=PEND_MAX; }); }');

function harness(post) {
  const store = {};
  const localStorage = {
    getItem: k => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
  };
  const env = new Function('localStorage', 'Date', 'sheetPost', 'SHEET_ENDPOINT',
    'navigator', 'fetch', 'Blob', 'Promise', 'setTimeout',
    SRC.replace(/^function sheetPost[\s\S]*?\n}\n/m, '') +
    ';return {all:pendAll, save:pendSave, add:pendAdd, drop:pendDrop, ' +
    'flush:pendFlush, stuck:pendStuck, MAX:PEND_MAX};');
  return env(localStorage, Date, post, '', {}, null, null, Promise, setTimeout);
}

/* ── ① 보내는 사이에 제출해도 안 지워진다 ── */
console.log('── 보내는 사이에 학생이 제출한다 ──');
{
  let release;
  const gate = new Promise(r => { release = r; });
  const seen = [];
  const Q = harness(async p => { seen.push(p.answers); await gate; return true; });

  Q.add({ exam: 'A', name: '홍길동', answers: '111' });   // 못 보낸 옛 답안
  const flushing = Q.flush();                             // 보내기 시작 — 여기서 멈춘다
  /* 바로 그 창에서 새 제출이 들어온다. 실제 코드의 submitAns 가 하는 그대로. */
  setImmediate(() => {
    Q.add({ exam: 'B', name: '홍길동', answers: '222' });
    release();
  });
  flushing.then(() => {
    const left = Q.all().map(x => x.p.answers).sort();
    chk('보내는 사이에 들어온 답안이 큐에 남아 있다',
      left.indexOf('222') >= 0, '큐: [' + left.join(' ') + ']');
    chk('옛 답안도 안 사라진다', left.indexOf('111') >= 0);
    step2();
  });
}

/* ── ② 큐가 넘칠 때, 못 보낸 것을 남기고 포기한 것을 버린다 ── */
function step2() {
  console.log('\n── 큐가 서른을 넘길 때 ──');
  const Q = harness(async () => true);
  const a = [];
  /* 큐의 **앞쪽**에 한 번도 못 보낸 옛 답안 열다섯 — 잃으면 안 되는 것들.
     뒤쪽에는 이미 세 번 보내 본(=포기한) 항목 열다섯. 이 배치가 핵심이다:
     맨 앞부터 자르면 «못 보낸 것» 을 버리고 «포기한 것» 을 남긴다. */
  for (let i = 0; i < 15; i++) {
    a.push({ p: { exam: 'unsent' + i, name: '홍길동', answers: '1' + i }, t: 1000 + i, n: 0 });
  }
  for (let i = 0; i < 15; i++) {
    a.push({ p: { exam: 'gaveup' + i, name: '홍길동', answers: '9' + i }, t: 2000 + i, n: Q.MAX });
  }
  Q.save(a);
  chk('먼저 서른 개가 들어간다', Q.all().length === 30, Q.all().length + '개');
  /* 방금 제출한, 아직 한 번도 못 보낸 답안 */
  Q.add({ exam: '오늘', name: '홍길동', answers: '3141' });
  const left = Q.all();
  chk('큐는 여전히 서른이다', left.length === 30, left.length + '개');
  chk('방금 제출한 답안이 살아 있다',
    left.some(x => x.p.answers === '3141'), '한 번도 못 보낸 것을 버리면 안 된다');
  chk('한 번도 못 보낸 옛 답안 열다섯이 다 살아 있다',
    left.filter(x => x.n === 0 && /^1/.test(x.p.answers)).length === 15,
    left.filter(x => x.n === 0 && /^1/.test(x.p.answers)).length + '개 남음');
  chk('대신 포기한 것 하나가 빠졌다',
    left.filter(x => x.n >= Q.MAX).length === 14,
    left.filter(x => x.n >= Q.MAX).length + '개 남음');
  chk('남은 것들의 순서는 그대로다',
    JSON.stringify(left.map(x => x.p.exam)) ===
    JSON.stringify(left.map(x => x.p.exam).slice().sort((p, q) =>
      (a.concat([{ p: { exam: '오늘' } }]).findIndex(y => y.p.exam === p)) -
      (a.concat([{ p: { exam: '오늘' } }]).findIndex(y => y.p.exam === q)))),
    left.map(x => x.p.exam).slice(0, 3).join(' ') + ' …');

  console.log('\n── 세 번까지만 보낸다 ──');
  const R = harness(async () => true);
  R.add({ exam: 'C', name: '홍길동', answers: '77' });
  (async () => {
    let tries = 0;
    for (let i = 0; i < 5; i++) tries += await R.flush();
    chk('한 답안을 네 번 보내지 않는다', tries === R.MAX, tries + '번');
    chk('그 뒤에는 «확인 안 됨» 으로 남는다', R.stuck().length === 1);

    console.log('\n── 구현이 스냅샷으로 되돌아가지 않았는가 ──');
    chk('pendFlush 가 항목마다 목록을 다시 읽는다',
      /for\s*\(var i=0;i<sigs\.length;i\+\+\)\s*\{\s*\n\s*var a=pendAll\(\);/.test(html), true);
    chk('pendSave 가 slice\\(-30\\) 으로 앞부터 자르지 않는다',
      !/JSON\.stringify\(a\.slice\(-30\)\)/.test(html), true);

    console.log('\n' + (fail ? `실패 ${fail}건 / 통과 ${pass}건`
      : `통과 ${pass}건 — 보내는 사이에 제출해도, 큐가 넘쳐도 답안이 안 사라진다.`));
    process.exit(fail ? 1 : 0);
  })();
}
