/* ============================================================
   검사는 **진짜 시트에 쓰면 안 된다**
   ------------------------------------------------------------
   2026-08-03, 선생님이 시트에서 이상한 줄들을 찾으셨다.

       기출동형 1회 (2015)  홍길동   http://localhost:8931/final.html#...
       KMChC 2018          예비본   http://localhost:8931/...
       KMChC 2018      오프라인테스트 http://localhost:8932/...
       JMChC 모의고사 6회   이도현   http://localhost:8931/...

   `localhost:8931` 은 **검사용 정적 서버**다. 8932 는 오프라인 검사가 쓰는
   포트다. 즉 이 줄들은 학생이 낸 것이 아니라 **CI 가 돌 때마다 파이널 앱이
   진짜 앱스크립트로 제출한 것**이다.

   그냥 지저분한 것이 아니다. 이 줄들은 석차·백분위·또래 정답률의 모집단에
   그대로 들어간다. 홍길동은 60/60 만점이고 전체본은 44/60 이다 — 진짜
   학생들의 등수가 검사 때문에 밀린다. 학부모에게 나간 숫자가 틀려진다.

   그래서 브라우저를 띄우자마자 **구글로 나가는 길을 끊는다.** 응답이 필요한
   검사는 자기 자리에서 route 를 따로 걸면 된다 — 나중에 건 route 가 먼저
   맞으므로 이 그물이 그것을 막지 않는다.

   쓰는 법:
       const seal = require('./_seal.js');
       const browser = seal(await chromium.launch(...));

   newContext() 든 newPage() 든 여기서 나온 것이면 모두 막힌다. 검사마다
   한 줄씩 적어 넣는 방식이면 언젠가 한 곳이 빠진다 — 실제로 여섯 곳이
   빠져 있었다.
   ============================================================ */
'use strict';

/* 이 검사에서 막은 횟수. 끝에 찍어 두면 "왜 창구가 안 왔지" 를 헤매지 않는다. */
let blocked = 0;

async function armOne(target) {
  await target.route('**://script.google.com/**', route => {
    blocked++;
    /* abort 한다 — 가짜 성공을 돌려주면 검사가 '보냈다' 고 믿고 지나간다.
       앱은 창구 실패를 견디도록 만들어져 있다(못 보낸 것은 다시 보낸다). */
    return route.abort('blockedbyclient');
  });
}

module.exports = function seal(browser) {
  const oc = browser.newContext.bind(browser);
  browser.newContext = async function (...a) {
    const c = await oc(...a);
    await armOne(c);
    return c;
  };
  const op = browser.newPage.bind(browser);
  browser.newPage = async function (...a) {
    const p = await op(...a);
    await armOne(p);
    return p;
  };
  return browser;
};
module.exports.count = function () { return blocked; };
