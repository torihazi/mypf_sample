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
     3つの機能をまとめて実行
     index.html で <script defer> を使っているため、
     ここに来た時点でHTMLは読み込み済み = 要素を安全に操作できます。
     ------------------------------------------------------------------- */
  setupThemeToggle();
  setupScrollAnimation();
  setupMobileMenu();

})();
