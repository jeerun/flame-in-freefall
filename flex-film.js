(() => {
  "use strict";

  const host = document.getElementById("lab-film");
  if (!host) return;
  const saved = window.FLEX_FILM_ANALYSIS;
  const saffireIV = {
    label: "Watch Saffire-IV fabric footage online ↗",
    url: "https://www.nasa.gov/humans-in-space/the-flame-of-discovery-grows-as-saffire-sets-new-fires-in-space/"
  };
  const clips = {
    flex: {
      button: "FLEX · Droplet", title: "FLEX on the space station", file: "flex-iss.webm", poster: "flex-before.jpg",
      label: "NASA FLEX fuel-droplet experiment",
      note: "Original footage from Science@NASA and NASA’s Goddard Space Flight Center.",
      source: "https://svs.gsfc.nasa.gov/11318/"
    },
    saffire: {
      button: "Saffire-I · Fabric", title: "Saffire-I aboard Cygnus", file: "saffire-1.webm", poster: "saffire-1-poster.jpg",
      label: "NASA Saffire-I image sequence of a burning fabric sample with flashing green illumination",
      note: "NASA’s camera sequence from June 14, 2016. The green light flashes during playback. The two frame buttons show stills.",
      source: "https://www.nasa.gov/centers-and-facilities/glenn/nasa-ignites-fire-experiment-aboard-space-cargo-ship/",
      related: saffireIV,
      question: "Why does the fabric turn green on camera?",
      prompt: "Compare the bright flame near the right edge with the later green frame. Both show the same cotton–fiberglass sample.",
      frames: [[2, "Flame"], [22, "Green light"]],
      explanation: "Green LEDs illuminate the smoke so the cameras can record its movement. The player clock measures time in NASA’s image compilation."
    },
    flex2: {
      button: "FLEX-2 · Soot", title: "Soot around a burning droplet", file: "flex-2.webm", poster: "flex-2-poster.jpg",
      label: "NASA FLEX-2 footage with annotated soot near the flame",
      note: "Silent excerpt from Spherical Flames, 2:08–2:40. The arrows are from Science@NASA and NASA’s Goddard Space Flight Center.",
      source: "https://svs.gsfc.nasa.gov/11640/",
      related: { label: "Watch FLEX-2 flame oscillations online ↗", url: "https://www.youtube.com/watch?v=qQQ1OHW1_F4" },
      question: "Where does the glowing soot go?",
      prompt: "Follow the specks marked by NASA’s arrows, then pause at the flame rim.",
      frames: [[2, "Soot"], [12, "Soot exiting"]],
      explanation: "The first arrows identify glowing soot near the droplet. In the later frame, NASA marks soot leaving the flame."
    },
    sofie: {
      button: "SoFIE-GEL · Extinction", title: "A flame appears to spin", file: "sofie-gel.webm", poster: "sofie-gel-poster.jpg",
      label: "NASA SoFIE-GEL footage of a moving blue flame around solid fuel",
      note: "Silent experiment footage from NASA’s Johnson Space Center archive.",
      source: "https://images.nasa.gov/details/SoFIE-GEL",
      question: "How much of the fuel does the blue flame surround?",
      prompt: "Compare the early blue rim with the remaining bright patches near the end of the clip.",
      frames: [[3, "Blue rim"], [36, "Separated patches"]],
      explanation: "The visible flame appears to chase itself around the fuel. The research team suggests that limited oxygen may let only part of the hot surface support a flame at a given time."
    },
    saffire5: {
      button: "Saffire-V · Ribbed plastic", title: "Ribbed plastic aboard Cygnus", file: "saffire-5.webm", poster: "saffire-5-poster.jpg",
      label: "NASA Saffire-V footage of flame spread over ribbed acrylic",
      note: "Silent NASA Glenn Research Center footage of a ribbed acrylic (PMMA) sample.",
      source: "https://images.nasa.gov/details/GRC-2021-CN-00008",
      related: saffireIV,
      question: "Where does the flame advance first?",
      prompt: "Compare the thinner ribs with the thicker material on the right.",
      frames: [[4, "Early flame"], [15, "Later flame"]],
      explanation: "NASA reports that the flame typically grows and spreads faster on the thinner ribs than on the thicker material to the right."
    },
    saffire6: {
      button: "Saffire-VI · Acrylic", title: "Two views of burning acrylic", file: "saffire-6.webm", poster: "saffire-6-poster.jpg",
      label: "NASA Saffire-VI front and edge views of a burning acrylic sample and temperature sensors",
      note: "NASA Glenn Research Center. This sequence plays at 20× experiment speed. Frame buttons use the video clock.",
      source: "https://www.nasa.gov/centers-and-facilities/glenn/flame-burns-out-on-nasas-long-running-spacecraft-fire-experiment/",
      related: saffireIV,
      question: "What is the glowing wire in the camera view?",
      prompt: "Pause on the labelled wire, then look for the flame front when the airflow changes.",
      frames: [[30, "Glowing wire"], [47, "Airflow reduced"]],
      explanation: "NASA labels the glowing wires as thermocouples. These sensors measure temperature. Their brightness alone does not give a temperature reading."
    }
  };

  host.innerHTML = `
    <div class="film-layout">
      <div class="film-view">
        <div class="film-picker" role="group" aria-label="Choose an experiment"></div>
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
      <section class="film-finding lab-card" id="observation" aria-labelledby="observation-question" hidden>
        <p class="lab-kicker">Read the footage</p>
        <h3 id="observation-question"></h3>
        <p id="observation-prompt"></p>
        <div class="film-actions"></div>
        <details id="observation-answer"><summary>Reveal NASA’s explanation</summary><p></p></details>
        <a id="film-related" class="lab-source" target="_blank" rel="noopener noreferrer" hidden></a>
      </section>
    </div>`;

  const player = host.querySelector("video");
  const status = host.querySelector("#film-status");
  const results = host.querySelector("#film-result");
  const frames = results.querySelector(".film-frames");
  const live = host.querySelector("#film-live");
  const showSaved = host.querySelector("#film-saved");
  const flexPanel = showSaved.closest("section");
  const observation = host.querySelector("#observation");
  const answer = observation.querySelector("details");
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
    answer.open = false;
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
    observation.hidden = key === "flex";
    if (!observation.hidden) {
      host.querySelector("#observation-question").textContent = clip.question;
      host.querySelector("#observation-prompt").textContent = clip.prompt;
      answer.querySelector("p").textContent = clip.explanation;
      const related = host.querySelector("#film-related");
      related.hidden = !clip.related;
      if (clip.related) {
        related.href = clip.related.url;
        related.textContent = clip.related.label;
      }
      const cues = observation.querySelector(".film-actions");
      cues.replaceChildren();
      for (const [seconds, label] of clip.frames) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "lab-btn";
        btn.dataset.seconds = seconds;
        btn.textContent = `${label} · ${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, "0")}`;
        btn.addEventListener("click", () => seek(seconds));
        cues.append(btn);
      }
    }
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
  for (const [key, clip] of Object.entries(clips)) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "lab-btn";
    button.dataset.clip = key;
    button.textContent = clip.button;
    button.addEventListener("click", () => chooseClip(key));
    host.querySelector(".film-picker").append(button);
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
