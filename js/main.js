/* =====================================================================
   main.js ｜ サイトの動き（JavaScript）をまとめたファイル
   ---------------------------------------------------------------------
   このファイルには3つの機能が入っています。
     1. ダークモード切替
     2. スクロールアニメーション
     3. スマホ用メニュー（ハンバーガー）の開閉
   それぞれを関数に分けて、最後にまとめて実行しています。
   ===================================================================== */

/* 全体を関数で囲っておくと、変数名が他のファイルとぶつからず安全です。
   末尾の () で「定義してすぐ実行」しています（即時実行関数といいます）。 */
(function () {
  "use strict"; // 書き間違いをエラーで知らせてくれる、おまじない


  /* -------------------------------------------------------------------
     機能1：ダークモード切替
     ・ボタンを押すたびに light ⇄ dark を切り替える
     ・選んだテーマは localStorage に保存し、次回訪問時も覚えている
     ・初期テーマの適用は index.html の <head> 内スクリプトが担当
     ------------------------------------------------------------------- */
  function setupThemeToggle() {
    var toggleBtn = document.getElementById("theme-toggle");
    if (!toggleBtn) return; // ボタンが無ければ何もしない（安全対策）

    var icon = toggleBtn.querySelector(".theme-icon");

    // 今のテーマに合わせて、ボタンの見た目（アイコンと説明文）を整える
    function updateButton() {
      var current = document.documentElement.getAttribute("data-theme");
      if (current === "dark") {
        icon.textContent = "☀️";
        toggleBtn.setAttribute("aria-label", "ライトモードに切り替える");
      } else {
        icon.textContent = "🌙";
        toggleBtn.setAttribute("aria-label", "ダークモードに切り替える");
      }
    }

    updateButton(); // ページ読み込み時に1回実行して表示を合わせる

    // ボタンがクリックされたときの処理
    toggleBtn.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark"; // 反対のテーマにする

      document.documentElement.setAttribute("data-theme", next); // 画面に反映
      localStorage.setItem("theme", next);                       // 保存して記憶
      updateButton();                                            // ボタン見た目を更新
    });
  }


  /* -------------------------------------------------------------------
     機能2：スクロールアニメーション
     ・data-animate が付いた要素を見張る
     ・その要素が画面内に入ったら is-visible クラスを付ける
       （実際のフワッと表示はCSS側で行う）
     ・IntersectionObserver = 「要素が見えたか」を効率よく判定する仕組み
     ------------------------------------------------------------------- */
  function setupScrollAnimation() {
    var targets = document.querySelectorAll("[data-animate]");
    if (targets.length === 0) return;

    // IntersectionObserver に対応していない古い環境では、
    // アニメなしで全部すぐ表示しておく（フォールバック）
    if (!("IntersectionObserver" in window)) {
      targets.forEach(function (el) { el.classList.add("is-visible"); });
      return;
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        // isIntersecting = その要素が画面に入っている、という意味
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target); // 一度表示したら見張りを終了
        }
      });
    }, {
      threshold: 0.15 // 要素が15%見えたら「入った」と判定
    });

    // すべての対象を見張りに登録する
    targets.forEach(function (el) { observer.observe(el); });
  }


  /* -------------------------------------------------------------------
     機能3：スマホ用メニュー（ハンバーガー）の開閉
     ・ハンバーガーボタンでメニューを開閉
     ・メニュー内のリンクを押したら自動で閉じる
     ・画面をPC幅に広げたら自動で閉じる
     ------------------------------------------------------------------- */
  function setupMobileMenu() {
    var menuBtn = document.getElementById("menu-toggle");
    var nav     = document.getElementById("nav");
    if (!menuBtn || !nav) return;

    // メニューを開く
    function openMenu() {
      nav.classList.add("nav--open");
      menuBtn.setAttribute("aria-expanded", "true");
      menuBtn.setAttribute("aria-label", "メニューを閉じる");
    }

    // メニューを閉じる
    function closeMenu() {
      nav.classList.remove("nav--open");
      menuBtn.setAttribute("aria-expanded", "false");
      menuBtn.setAttribute("aria-label", "メニューを開く");
    }

    // ボタンが押されたら、開いていれば閉じ、閉じていれば開く
    menuBtn.addEventListener("click", function () {
      var isOpen = nav.classList.contains("nav--open");
      if (isOpen) {
        closeMenu();
      } else {
        openMenu();
      }
    });

    // メニュー内のリンクを押したら、移動と同時に閉じる
    nav.querySelectorAll(".nav-link").forEach(function (link) {
      link.addEventListener("click", closeMenu);
    });

    // 画面幅がPCサイズ（768px以上）になったら、開いたままにせず閉じる
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 768) {
        closeMenu();
      }
    });
  }


  /* -------------------------------------------------------------------
     機能4：画面遷移（SPA風の画面切り替え）
     ・5つのセクション（.screen）のうち、1枚だけを表示する
     ・#リンク を押すと URL の # が変わる。それを合図に、いまの画面を
       フェードアウト → 次の画面をフェードイン する
     ・最初の表示は、開いたときの URL の # に合わせてすぐ決める
     ------------------------------------------------------------------- */
  function setupScreenRouter() {
    var screens  = document.querySelectorAll(".screen");
    var navLinks = document.querySelectorAll(".nav-link");
    var prevBtn  = document.getElementById("prev-screen"); // 左の「前へ」ボタン
    var nextBtn  = document.getElementById("next-screen"); // 右の「次へ」ボタン
    if (screens.length === 0) return; // 画面が無ければ何もしない（安全対策）

    var FADE_MS = 350;       // フェードの長さ。CSS .screen の transition と同じ
    var isAnimating = false; // いま切り替え中かどうか（連打よけ）

    // URL の # から「表示すべき画面のid」を求める。
    // 該当する .screen が無ければ、先頭の画面（hero）に戻す。
    function resolveTargetId() {
      var id = location.hash.replace("#", "");          // "#about" → "about"
      var el = id ? document.getElementById(id) : null;
      if (el && el.classList.contains("screen")) return id;
      return screens[0].id;                             // フォールバック = "hero"
    }

    // 画面の中の data-animate 要素を、その場で表示状態にする。
    // 機能2（スクロール監視）とは別に、画面が出た瞬間に確実に動かすため。
    function revealAnimations(screenEl) {
      if (!screenEl) return;
      screenEl.querySelectorAll("[data-animate]").forEach(function (el) {
        el.classList.add("is-visible");
      });
    }

    // ナビの「現在地」表示を更新する。
    // 表示中の画面に対応するリンクへ aria-current="page" を付ける。
    function updateNav(activeId) {
      navLinks.forEach(function (link) {
        var linkId = link.getAttribute("href").replace("#", "");
        if (linkId === activeId) {
          link.setAttribute("aria-current", "page");
        } else {
          link.removeAttribute("aria-current");
        }
      });
    }

    // 画面の並び順（hero→about→…→contact）の中で、id が何番目かを返す。
    function indexOfScreen(id) {
      var index = -1;
      screens.forEach(function (s, i) { if (s.id === id) index = i; });
      return index;
    }

    // 左右の移動ボタンの有効／無効を切り替える。
    // 先頭の画面では「前へ」、末尾の画面では「次へ」を押せないようにする。
    function updateSideButtons(activeId) {
      if (!prevBtn || !nextBtn) return;
      var index = indexOfScreen(activeId);
      prevBtn.disabled = (index <= 0);
      nextBtn.disabled = (index >= screens.length - 1);
    }

    // フェード（opacity の transition）が終わるのを待つ。
    // transitionend を待つのが基本だが、「視差効果を減らす」設定などで
    // イベントが来ないこともあるので、setTimeout を保険に併用する。
    // どちらか早く来た方で、処理を1回だけ実行する。
    function onFadeDone(el, callback) {
      var finished = false;
      function finish() {
        if (finished) return;            // 2回目以降は無視
        finished = true;
        el.removeEventListener("transitionend", finish);
        callback();
      }
      el.addEventListener("transitionend", finish);
      setTimeout(finish, FADE_MS + 100); // CSS の長さより必ず少し長くする
    }

    // 指定した画面を「フェードなしで即座に」表示する（初回表示用）。
    function showInstant(targetId) {
      screens.forEach(function (s) {
        s.hidden = (s.id !== targetId);  // 対象だけ表示、ほかは隠す
        s.classList.remove("is-leaving", "is-entering");
      });
      updateNav(targetId);
      updateSideButtons(targetId);
      revealAnimations(document.getElementById(targetId));
    }

    // 指定した画面へ、フェードしながら切り替える。
    function transitionTo(targetId) {
      // いま表示中（hidden でない）の画面を探す
      var current = null;
      screens.forEach(function (s) { if (!s.hidden) current = s; });

      if (!current || current.id === targetId) return; // 同じ画面なら何もしない
      if (isAnimating) return;                          // 切り替え中なら無視
      isAnimating = true;

      var next = document.getElementById(targetId);

      // 1) いまの画面を透明にする（フェードアウト開始）
      current.classList.add("is-leaving");

      // 2) フェードアウトの完了を待ってから、中身を入れ替える
      onFadeDone(current, function () {
        current.hidden = true;
        current.classList.remove("is-leaving");

        // 3) 次の画面を「透明のまま」表示する
        next.classList.add("is-entering");
        next.hidden = false;

        // 4) 1フレーム置いてから透明を解除する（→ フェードインが始まる）。
        //    requestAnimationFrame を2回使うのは、1回だとブラウザが
        //    「表示」と「透明解除」をまとめてしまい、変化と見なされず
        //    アニメーションが起きないことがあるため。
        requestAnimationFrame(function () {
          requestAnimationFrame(function () {
            next.classList.remove("is-entering");
          });
        });

        updateNav(targetId);
        updateSideButtons(targetId);
        revealAnimations(next);
        window.scrollTo(0, 0);  // 前の画面でスクロールしていても先頭に戻す
        isAnimating = false;
      });
    }

    // 左右の移動ボタン：いま表示中の画面を基準に、1つ前／1つ後の画面へ。
    // location.hash を書き換えると hashchange が起き、下の流れで切り替わる。
    function goByStep(step) {
      var current = null;
      screens.forEach(function (s) { if (!s.hidden) current = s; });
      if (!current) return;
      var target = indexOfScreen(current.id) + step;
      if (target < 0 || target >= screens.length) return; // 端なら何もしない
      location.hash = "#" + screens[target].id;
    }
    if (prevBtn) prevBtn.addEventListener("click", function () { goByStep(-1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { goByStep(1); });

    // URL の # が変わったら、それを合図に画面を切り替える。
    // ナビ・Heroのボタン・ロゴ・矢印・左右ボタンはすべて #リンク（または
    // # を書き換える）なので、ここ1か所で受け止めれば個別処理は要りません。
    window.addEventListener("hashchange", function () {
      transitionTo(resolveTargetId());
    });

    // 初回表示：開いたときの URL の # に合わせて画面を決める
    showInstant(resolveTargetId());
  }


  /* -------------------------------------------------------------------
     機能5：ローディング画面（初期表示）
     ・開いた直後の loading... 表示を、少し見せてからフェードして消す
     ・静的サイトはすぐ読み込みが終わるので、わざと最低表示時間を設ける
     ------------------------------------------------------------------- */
  function setupLoading() {
    var loader = document.getElementById("loading");
    if (!loader) return; // ローディング要素が無ければ何もしない（安全対策）

    var MIN_VISIBLE_MS = 1400; // この時間は必ず loading... を見せる

    setTimeout(function () {
      loader.classList.add("is-done");                 // フェードアウト開始
      // フェード（CSSの .5s）が終わったころ、DOMから取り除いて後片付け
      setTimeout(function () { loader.remove(); }, 600);
    }, MIN_VISIBLE_MS);
  }


  /* -------------------------------------------------------------------
     5つの機能をまとめて実行
     index.html で <script defer> を使っているため、
     ここに来た時点でHTMLは読み込み済み = 要素を安全に操作できます。
     ------------------------------------------------------------------- */
  setupThemeToggle();
  setupScrollAnimation();
  setupMobileMenu();
  setupScreenRouter();
  setupLoading();

})();
