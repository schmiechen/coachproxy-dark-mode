(function () {
  if (window.__cpDarkMode) return;
  window.__cpDarkMode = true;

  var KEY = 'cpTheme';
  var MODES = ['auto', 'light', 'dark'];
  var LABELS = { auto: '◐ Auto', light: '☀ Light', dark: '☾ Dark' };
  var mq = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  function saved() {
    try { var v = localStorage.getItem(KEY); return MODES.indexOf(v) >= 0 ? v : 'auto'; }
    catch (e) { return 'auto'; }
  }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }

  function apply() {
    var mode = saved();
    var dark = mode === 'dark' || (mode === 'auto' && mq && mq.matches);
    document.documentElement.setAttribute('data-cp-theme', dark ? 'dark' : 'light');
    var b = document.getElementById('cp-theme-toggle');
    // Only touch the DOM when something changed: the observer below watches this subtree.
    if (b && b.textContent !== LABELS[mode]) {
      b.textContent = LABELS[mode];
      b.setAttribute('aria-label', 'Theme: ' + mode + '. Tap to change.');
    }
  }

  function mount() {
    var bar = document.getElementById('nr-dashboard-toolbar');
    var b = document.getElementById('cp-theme-toggle');
    if (!b) {
      b = document.createElement('button');
      b.id = 'cp-theme-toggle';
      b.type = 'button';
      b.addEventListener('click', function (e) {
        e.stopPropagation();
        save(MODES[(MODES.indexOf(saved()) + 1) % MODES.length]);
        apply();
      });
    }
    if (bar && b.parentNode !== bar) { b.classList.remove('cp-floating'); bar.appendChild(b); }
    else if (!bar && !b.parentNode) { b.classList.add('cp-floating'); document.body.appendChild(b); }
    apply();
  }

  apply();
  if (mq) {
    if (mq.addEventListener) mq.addEventListener('change', apply);
    else if (mq.addListener) mq.addListener(apply);
  }
  // Angular builds the toolbar after load and rebuilds it on navigation, so keep it mounted.
  var pending = false;
  new MutationObserver(function () {
    if (pending) return;
    pending = true;
    setTimeout(function () { pending = false; mount(); }, 100);
  }).observe(document.documentElement, { childList: true, subtree: true });
  mount();
})();
