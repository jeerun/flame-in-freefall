// The dashboard uses this transport only for research when its local model is unavailable.
const hostedResearch = (() => {
  const origin = document.currentScript.dataset.origin || location.origin;
  let backend = "";
  let statusRequest;

  function probe() {
    if (!statusRequest) {
      statusRequest = fetch(origin + "/api/status", { credentials: "omit", cache: "no-store" })
        .then(async response => {
          if (!response.ok) return;
          const status = await response.json();
          if (status.research === true && typeof status.backend === "string" && status.backend.trim()) {
            backend = status.backend.trim();
          }
        })
        .catch(() => {});
    }
    return statusRequest;
  }

  async function ask({ question, selected, need }, onText, onEnd, signal) {
    const label = backend + " (hosted research)";
    const payload = { question };
    if (/^PSI-\d+$/.test(selected)) payload.selected = selected;
    if (["prevention", "detection", "suppression", "cabin air"].includes(need)) payload.need = need;
    try {
      const response = await fetch(origin + "/api/ask", {
        method: "POST", credentials: "omit", headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload), signal
      });
      const result = await response.json();
      if (!response.ok || typeof result.answer !== "string" || !result.answer.trim()) {
        throw new Error(typeof result.error === "string" ? result.error : "Hosted research is unavailable.");
      }
      onText(result.answer);
      onEnd(null, result.answer, { label, sources: Array.isArray(result.sources) ? result.sources : [] });
    } catch (err) {
      onEnd(err, "", { label });
    }
  }

  function showSources(box, sources) {
    const links = document.createElement("span");
    links.className = "took";
    for (const source of sources || []) {
      if (!source || !/^PSI-\d+$/.test(source.id)) continue;
      const url = "https://psi.nasa.gov/physci/repo/data/investigations/" + source.id;
      if (source.url !== url) continue;
      links.append(links.childNodes.length ? ", " : "NASA records supplied to Ember: ");
      const link = document.createElement("a");
      link.href = url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = source.name ? source.name + " [" + source.id + "]" : source.id;
      links.append(link);
    }
    if (links.childNodes.length) box.append(links);
  }

  return { probe, ask, showSources, get backend() { return backend; } };
})();
