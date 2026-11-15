(() => {
  "use strict";

  const host = document.getElementById("lab-film");
  if (!host) return;
  const saved = window.FLEX_FILM_ANALYSIS;
  const clips = {
    flex: {
      title: "FLEX on the space station", file: "flex-iss.webm", poster: "flex-before.jpg",
      label: "NASA FLEX fuel-droplet experiment",
      note: "Original footage from Science@NASA and NASA’s Goddard Space Flight Center.",
      source: "https://svs.gsfc.nasa.gov/11318/"
    },
    saffire: {
      title: "Saffire-I aboard Cygnus", file: "saffire-1.webm", poster: "saffire-1-poster.jpg",
      label: "NASA Saffire-I image sequence of a burning fabric sample with flashing green illumination",
      note: "NASA’s camera sequence from June 14, 2016. The green light flashes during playback. The two frame buttons show stills.",
      source: "https://www.nasa.gov/centers-and-facilities/glenn/nasa-ignites-fire-experiment-aboard-space-cargo-ship/"
    }
  };

  host.innerHTML = `
    <div class="film-layout">
      <div class="film-view">
        <div class="film-picker" role="group" aria-label="Choose an experiment">
          <button type="button" class="lab-btn" data-clip="flex" aria-pressed="true">FLEX · Droplet</button>
          <button type="button" class="lab-btn" data-clip="saffire" aria-pressed="false">Saffire-I · Fabric</button>
        </div>
        <h2 id="film-title"></h2>
        <video class="film-player" controls playsinline preload="metadata"
               aria-describedby="film-note">
          <a>Open the bundled NASA clip</a>
        </video>
        <p class="lab-subtle" id="film-note"></p>
        <p class="lab-subtle" id="film-error" role="status" hidden></p>
        <a class="lab-source" id="film-source" target="_blank" rel="noopener noreferrer">NASA footage and experiment notes ↗</a>
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
      <section class="film-finding lab-card" id="saffire-reading" aria-labelledby="saffire-question" hidden>
        <p class="lab-kicker">Read the footage</p>
        <h3 id="saffire-question">Why does the fabric turn green on camera?</h3>
        <p>Compare the bright flame near the right edge with the later green frame. Both show the same cotton–fiberglass sample.</p>
        <div class="film-actions">
          <button type="button" class="lab-btn" data-seconds="2">Flame · 0:02</button>
          <button type="button" class="lab-btn" data-seconds="22">Green light · 0:22</button>
        </div>
        <details id="saffire-answer"><summary>Reveal NASA’s explanation</summary>
          <p>Green LEDs illuminate the smoke so the cameras can record its movement. The player clock measures time in NASA’s image compilation.</p>
        </details>
      </section>
    </div>`;

  const player = host.querySelector("video");
  const status = host.querySelector("#film-status");
  const results = host.querySelector("#film-result");
  const frames = results.querySelector(".film-frames");
  const live = host.querySelector("#film-live");
  const showSaved = host.querySelector("#film-saved");
  const flexPanel = showSaved.closest("section");
  const saffirePanel = host.querySelector("#saffire-reading");
  const playerError = host.querySelector("#film-error");
  let clipKey;
  let pendingTime = null;
  let review = null;

  function cancelReview() {
    if (review) review.abort();
    review = null;
    live.disabled = false;
  }

  function resetActivity() {
    cancelReview();
    player.pause();
    pendingTime = null;
    if (player.readyState >= HTMLMediaElement.HAVE_METADATA) player.currentTime = 0;
    frames.replaceChildren();
    results.hidden = true;
    status.textContent = showSaved.disabled ? "The saved frame selection could not be loaded." : "";
    host.querySelector("#saffire-answer").open = false;
  }

  function chooseClip(key) {
    if (key === clipKey) return;
    resetActivity();
    clipKey = key;
    const clip = clips[key];
    for (const button of host.querySelectorAll("[data-clip]")) {
      button.setAttribute("aria-pressed", String(button.dataset.clip === key));
    }
    flexPanel.hidden = key !== "flex";
    saffirePanel.hidden = key !== "saffire";
    host.querySelector("#film-title").textContent = clip.title;
    host.querySelector("#film-note").textContent = clip.note;
    host.querySelector("#film-source").href = clip.source;
    playerError.hidden = true;
    player.setAttribute("aria-label", clip.label);
    player.poster = "lab-media/" + clip.poster;
    player.src = "lab-media/" + clip.file;
    player.querySelector("a").href = player.src;
    player.load();
  }
  for (const button of host.querySelectorAll("[data-clip]")) {
    button.addEventListener("click", () => chooseClip(button.dataset.clip));
  }
  for (const button of saffirePanel.querySelectorAll("[data-seconds]")) {
    button.addEventListener("click", () => seek(Number(button.dataset.seconds)));
  }
  host.addEventListener("leave-film", resetActivity);

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
    if (!player.error) return;
    playerError.hidden = false;
    playerError.textContent = "This browser could not play the bundled clip. The NASA source has the original footage.";
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
  chooseClip("flex");
  showSaved.addEventListener("click", () => {
    if (clipKey !== "flex") return;
    cancelReview();
    showPair(saved, `Saved Ember analysis · ${saved.model}. One-second samples from the clip.`);
  });
  document.addEventListener("lab-capabilities", event => {
    live.hidden = !event.detail?.film;
  });
  live.addEventListener("click", async () => {
    if (clipKey !== "flex" || review) return;
    live.disabled = true;
    results.hidden = true;
    status.textContent = "Ember is inspecting the fixed clip samples…";
    const controller = new AbortController();
    review = controller;
    const timer = setTimeout(() => controller.abort(), 95000);
    try {
      const response = await fetch("/lab/film", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: "{}", signal: controller.signal,
      });
      if (!response.ok) throw new Error("Review unavailable");
      const pair = await response.json();
      if (review !== controller) return;
      if (pair && pair.before === null && pair.after === null) {
        status.textContent = "This run found no single clear transition. Inspect the clip or open the saved frames.";
      } else if (validPair(pair)) {
        showPair(pair, "Live Ember analysis · One-second samples from the clip.");
      } else {
        throw new Error("Unexpected frame selection");
      }
    } catch {
      if (review === controller) {
        status.textContent = "Live vision is unavailable. You can still play the clip and open the saved frames.";
      }
    } finally {
      clearTimeout(timer);
      if (review === controller) {
        review = null;
        live.disabled = false;
      }
    }
  });
})();
