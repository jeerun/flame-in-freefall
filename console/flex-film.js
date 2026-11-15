(() => {
  "use strict";

  const host = document.getElementById("lab-film");
  if (!host) return;
  const saved = window.FLEX_FILM_ANALYSIS;

  host.innerHTML = `
    <div class="film-layout">
      <div class="film-view">
        <h2>FLEX on the space station</h2>
        <video class="film-player" controls playsinline preload="metadata"
               aria-label="NASA FLEX fuel-droplet experiment"
               poster="lab-media/flex-before.jpg" src="lab-media/flex-iss.webm">
          <a href="lab-media/flex-iss.webm">Open the bundled NASA video</a>
        </video>
        <p class="lab-subtle">Original footage from Science@NASA and NASA’s Goddard Space Flight Center.</p>
        <a class="lab-source" href="https://svs.gsfc.nasa.gov/11318/" target="_blank" rel="noopener noreferrer">NASA film and experiment notes ↗</a>
      </div>
      <section class="film-finding lab-card" aria-labelledby="film-question">
        <p class="lab-kicker">Ask Ember</p>
        <h3 id="film-question">When does the round flame outline fade?</h3>
        <p>Look for the faint rim around the central droplet. Ember can compare frames sampled one second apart.</p>
        <div class="film-actions">
          <button type="button" class="lab-btn primary" id="film-saved">Show saved frames</button>
          <button type="button" class="lab-btn" id="film-live" hidden>Ask Ember now</button>
        </div>
        <p class="lab-subtle" id="film-status" role="status"></p>
        <div class="film-result" id="film-result" hidden>
          <div class="film-frames"></div>
          <p class="lab-subtle">Select a time to pause the original clip there. In FLEX, combustion can continue after a flame becomes too faint to see.</p>
        </div>
      </section>
    </div>`;

  const player = host.querySelector("video");
  const status = host.querySelector("#film-status");
  const results = host.querySelector("#film-result");
  const frames = results.querySelector(".film-frames");
  const live = host.querySelector("#film-live");
  const showSaved = host.querySelector("#film-saved");
  let pendingTime = null;
  let viewVersion = 0;

  function seek(seconds) {
    player.pause();
    if (player.readyState >= HTMLMediaElement.HAVE_METADATA) {
      player.currentTime = seconds;
    } else {
      pendingTime = seconds;
    }
  }
  player.addEventListener("loadedmetadata", () => {
    if (pendingTime !== null) seek(pendingTime);
    pendingTime = null;
  });
  player.addEventListener("error", () => {
    status.textContent = "The video could not play here. You can still inspect the saved frames or open the NASA film.";
  });

  function validPair(pair) {
    return pair && Number.isInteger(pair.before) && pair.before >= 1 && pair.before <= 21
      && pair.after === pair.before + 1;
  }

  function showPair(pair, message) {
    const sameStills = saved && pair.before === saved.before && pair.after === saved.after;
    frames.replaceChildren();
    for (const [index, key] of ["before", "after"].entries()) {
      const seconds = pair[key];
      const button = document.createElement("button");
      button.type = "button";
      if (sameStills) {
        const image = document.createElement("img");
        image.src = `lab-media/flex-${key}.jpg`;
        image.alt = "";
        button.append(image);
      }
      const label = index === 0 ? "Continuous rim" : "Rim fades";
      button.append(`${label} · 0:${String(seconds).padStart(2, "0")}`);
      button.addEventListener("click", () => seek(seconds));
      frames.append(button);
    }
    results.hidden = false;
    status.textContent = message;
  }

  showSaved.disabled = !validPair(saved);
  if (showSaved.disabled) status.textContent = "The saved frame selection could not be loaded.";
  showSaved.addEventListener("click", () => {
    viewVersion++;
    showPair(saved, `Saved Ember analysis · ${saved.model}. One-second samples from the clip.`);
  });
  document.addEventListener("lab-capabilities", event => {
    live.hidden = !event.detail?.film;
  });
  live.addEventListener("click", async () => {
    const version = ++viewVersion;
    live.disabled = true;
    results.hidden = true;
    status.textContent = "Ember is inspecting the fixed clip samples…";
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 95000);
    try {
      const response = await fetch("/lab/film", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: "{}", signal: controller.signal,
      });
      if (!response.ok) throw new Error("Review unavailable");
      const pair = await response.json();
      if (version !== viewVersion) return;
      if (pair && pair.before === null && pair.after === null) {
        status.textContent = "This run found no single clear transition. Inspect the clip or open the saved frames.";
      } else if (validPair(pair)) {
        showPair(pair, "Live Ember analysis · One-second samples from the clip.");
      } else {
        throw new Error("Unexpected frame selection");
      }
    } catch {
      if (version === viewVersion) {
        status.textContent = "Live vision is unavailable. You can still play the clip and open the saved frames.";
      }
    } finally {
      clearTimeout(timer);
      live.disabled = false;
    }
  });
})();
