(() => {
  "use strict";
  const byId = id => document.getElementById(id);
  const dialog = byId("shareViewDialog");
  const output = byId("shareOutput");
  const input = byId("shareInput");
  let capture, apply;

  function restore(value) {
    let hash = value.trim();
    if (!hash.startsWith("#")) {
      try { hash = new URL(hash).hash; } catch { return false; }
    }
    const spec = window.FLAME_VIEW_LINK.decode(hash);
    return !!spec && apply(spec);
  }

  function open() {
    const current = capture();
    const hash = current && window.FLAME_VIEW_LINK.encode(current.data);
    if (!hash || dialog.open) return;
    const localOnly = !/^https?:$/.test(location.protocol) ||
      /^(localhost\.?|.*\.localhost\.?|127\.[\d.]+|\[::1\]|0\.0\.0\.0)$/i.test(location.hostname);
    byId("shareSubject").textContent = current.label;
    byId("shareHelp").textContent = localOnly
      ? "On another copy of the dashboard, choose Share view → Open a shared view and paste this code."
      : "This link opens the same view on devices that can reach this dashboard.";
    byId("shareOutputLabel").textContent = localOnly ? "View code" : "View link";
    byId("shareCopy").textContent = localOnly ? "Copy code" : "Copy link";
    output.value = localOnly ? hash : location.origin + location.pathname + hash;
    input.value = "";
    byId("shareStatus").textContent = byId("shareError").textContent = "";
    byId("shareImport").open = false;
    dialog.showModal();
    byId("shareCopy").focus();
  }

  async function copy() {
    const value = output.value;
    let copied = false;
    try {
      if (navigator.clipboard) {
        await navigator.clipboard.writeText(value);
        copied = true;
      }
    } catch { /* Insecure LAN origins or a browser permission can disable this API. */ }
    if (!dialog.open || output.value !== value) return;
    if (!copied) {
      output.focus();
      output.select();
      try { copied = document.execCommand("copy"); } catch { /* The selected text remains available. */ }
    }
    byId("shareStatus").textContent = copied ? "Copied." : "Text selected. Use your device’s Copy command.";
  }

  byId("shareForm").addEventListener("submit", event => {
    event.preventDefault();
    if (!restore(input.value)) {
      byId("shareError").textContent = "This view could not be opened. Paste the full code or link from a matching dashboard.";
      input.focus();
      return;
    }
    // Preserve a newly opened view on reload. The input is never used as a navigation URL.
    const current = capture();
    const hash = window.FLAME_VIEW_LINK.encode(current.data);
    try { history.replaceState(history.state, "", hash); } catch { /* Some file viewers disable history. */ }
  });
  byId("shareCopy").addEventListener("click", copy);
  byId("shareClose").addEventListener("click", () => dialog.close());

  function handle(action) {
    if (action === "back") { dialog.close(); return; }
    const focused = document.activeElement;
    if (action === "confirm") { if (dialog.contains(focused)) focused.click(); return; }
    const controls = Array.from(dialog.querySelectorAll("button, input, summary")).filter(el => el.getClientRects().length);
    const dir = action === "left" || action === "up" ? -1 : 1;
    controls[(controls.indexOf(focused) + dir + controls.length) % controls.length].focus();
  }

  window.FLAME_SHARE_VIEW = {
    init(captureCallback, applyCallback) { capture = captureCallback; apply = applyCallback; },
    open, restore, handle, isOpen: () => dialog.open, close: () => dialog.close()
  };
})();
