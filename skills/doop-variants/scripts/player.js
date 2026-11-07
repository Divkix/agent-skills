// Local stand-in for the Doop prototype player: follows only data-doop-* attributes.
(() => {
  const ID = document.currentScript.dataset.frame;
  const inOverlay = window.parent !== window;
  const store = inOverlay ? window.parent.sessionStorage : sessionStorage;
  const log = (e) => {
    const l = JSON.parse(store.doopLog || "[]");
    l.push({ from: ID, ...e });
    store.doopLog = JSON.stringify(l);
  };
  const interactions = (el) => {
    if (el.dataset.doopInteractions) {
      try { return JSON.parse(el.dataset.doopInteractions); }
      catch { log({ error: "bad data-doop-interactions" }); return []; }
    }
    return el.dataset.doopAction ? [{ on: el.dataset.doopOn || "click", action: el.dataset.doopAction }] : [];
  };
  const go = (id) => inOverlay ? window.parent.postMessage({ doop: "go", id }, "*") : (location.href = id + ".html");
  const closeOverlay = () => document.getElementById("doop-overlay")?.remove();
  const openOverlay = (id) => {
    closeOverlay();
    const s = document.createElement("div");
    s.id = "doop-overlay";
    s.style.cssText = "position:fixed;inset:0;z-index:2147483647;background:rgba(0,0,0,.5);display:flex;justify-content:center;align-items:flex-start";
    const f = document.createElement("iframe");
    const size = (window.DOOP_SIZES || {})[id] || [390, 600];
    f.src = id + ".html";
    f.style.cssText = `border:0;width:${size[0]}px;height:${Math.min(size[1], innerHeight)}px;background:transparent`;
    s.onclick = (e) => e.target === s && closeOverlay();
    s.append(f);
    document.body.append(s);
  };
  const act = (action, el) => {
    const i = action.indexOf(":");
    const kind = i < 0 ? action : action.slice(0, i);
    const arg = i < 0 ? "" : action.slice(i + 1);
    log({ kind, arg, text: (el.innerText || el.getAttribute("aria-label") || "").trim().slice(0, 60) });
    if (kind === "navigate") go(arg);
    else if (kind === "back") inOverlay ? window.parent.history.back() : history.back();
    else if (kind === "overlay") inOverlay ? log({ error: "overlay from overlay" }) : openOverlay(arg);
    else if (kind === "close-overlay") inOverlay ? window.parent.postMessage({ doop: "close" }, "*") : log({ error: "close-overlay outside overlay" });
    else if (kind === "scroll-to") {
      const t = document.querySelector(arg);
      t ? t.scrollIntoView() : log({ error: "scroll-to target missing", arg });
    } else if (kind !== "url") log({ error: "unknown action", action });
  };
  document.addEventListener("click", (e) => {
    for (let el = e.target; el && el !== document; el = el.parentElement) {
      const hit = interactions(el).find((x) => x.on === "click");
      if (hit) { e.preventDefault(); e.stopPropagation(); act(hit.action, el); return; }
    }
    const a = e.target.closest("a[href]");
    if (a) { e.preventDefault(); log({ unwired: a.getAttribute("href"), text: a.innerText.trim().slice(0, 60) }); }
  }, true);
  document.addEventListener("submit", (e) => e.preventDefault(), true);
  document.addEventListener("keydown", (e) => {
    for (const el of document.querySelectorAll("[data-doop-on^='key:'],[data-doop-interactions]")) {
      const hit = interactions(el).find((x) => x.on === "key:" + e.key);
      if (hit) { act(hit.action, el); return; }
    }
  });
  window.addEventListener("message", (e) => {
    if (e.data?.doop === "go") location.href = e.data.id + ".html";
    if (e.data?.doop === "close") closeOverlay();
  });
  window.addEventListener("load", () => {
    for (const el of document.querySelectorAll("[data-doop-on^='delay:'],[data-doop-interactions]")) {
      const hit = interactions(el).find((x) => String(x.on).startsWith("delay:"));
      if (hit) setTimeout(() => act(hit.action, el), Number(hit.on.slice(6)) || 0);
    }
  });
})();
