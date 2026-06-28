/* ======================================================================
   1) Date sync: ช่อง text (DD/MM/YYYY พ.ศ.) <-> date picker (YYYY-MM-DD ค.ศ.)
   ====================================================================== */

function parseThaiDateToISO(s) {
  if (!s) return "";
  const m = s.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (!m) return "";
  const d = parseInt(m[1], 10);
  const mo = parseInt(m[2], 10);
  const be = parseInt(m[3], 10);
  if (be < 1900 || be > 3000) return "";
  const ce = be - 543;
  return (
    String(ce).padStart(4, "0") +
    "-" + String(mo).padStart(2, "0") +
    "-" + String(d).padStart(2, "0")
  );
}

function isoToThaiDate(iso) {
  if (!iso) return "";
  const m = iso.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!m) return "";
  const ce = parseInt(m[1], 10);
  const mo = parseInt(m[2], 10);
  const d = parseInt(m[3], 10);
  const be = ce + 543;
  return (
    String(d).padStart(2, "0") +
    "/" + String(mo).padStart(2, "0") +
    "/" + String(be)
  );
}

function setupDateSync(textId, pickerId) {
  const text = document.getElementById(textId);
  const pick = document.getElementById(pickerId);
  if (!text || !pick) return;

  // initial: text -> picker
  const init = parseThaiDateToISO(text.value);
  if (init) pick.value = init;

  // เมื่อเลือกจากปฏิทิน
  pick.addEventListener("change", () => {
    if (pick.value) text.value = isoToThaiDate(pick.value);
  });
  // เมื่อพิมพ์ text เสร็จ
  text.addEventListener("input", () => {
    const iso = parseThaiDateToISO(text.value);
    if (iso) pick.value = iso;
  });
}

function setupDatePickerButtons() {
  document.querySelectorAll(".date-picker-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const id = btn.dataset.pickerFor;
      const pick = document.getElementById(id);
      if (!pick) return;
      if (typeof pick.showPicker === "function") {
        try {
          pick.showPicker();
          return;
        } catch (err) {}
      }
      pick.focus();
      pick.click();
    });
  });
}

/* ======================================================================
   2) Planet hover tooltip — event delegation รองรับ dynamic chips
   ====================================================================== */

const POISON_TH = {
  naga:  { icon: "🐍", name: "พิษนาค",
           meaning: "ยาพิษ/สมอง/ความดัน/ส่วนบนของศีรษะ" },
  krut:  { icon: "🦅", name: "พิษครุฑ",
           meaning: "อุบัติเหตุฉับพลัน/อวัยวะส่วนกลาง" },
  sunak: { icon: "🐕", name: "พิษสุนัข",
           meaning: "ศัตรู/ใส่ความ/อุบัติเหตุรถ/ของมีคม" },
};
const SEV_TH = { heavy: "หนัก", light: "เบา" };

function setupPlanetTooltip() {
  const tip = document.getElementById("planet-tooltip");
  if (!tip) return;

  const svg = document.querySelector(".zodiac-svg");
  if (!svg) return;

  let stuck = null;

  function getGroup(el) {
    return el.closest(
      ".planet-svg-group[data-tip-planet], .lagna-group[data-tip-planet], .triyangka-marker-group[data-tri-rasi]"
    );
  }

  function buildTipContent(g) {
    const d = g.dataset;
    if (!d.tipPlanet && d.triRasi) {
      let poisonHtml = "";
      if (d.triPoison) {
        const [icon, key] = d.triPoison.split(" ");
        const pinfo = POISON_TH[key];
        if (pinfo) {
          poisonHtml = `
            <div class="tip-row tip-poison">
              <span class="tip-label">⚠️ พิษ</span>
              ${icon} ${pinfo.name}
            </div>
            <div class="tip-row tip-poison-meaning">${pinfo.meaning}</div>`;
        }
      }
      return `
        <div class="tip-title">
          <span class="tip-planet">ตรียางค์ ${d.triDecanate}/3</span>
          <span class="tip-source">(${d.triRasi})</span>
        </div>
        <div class="tip-row"><span class="tip-label">ดาวครอง</span>${d.triLord}</div>
        <div class="tip-row"><span class="tip-label">ช่วง</span>${d.triDegFrom}°-${d.triDegTo}°</div>
        ${poisonHtml}`;
    }
    const retro = d.tipRetro === "1" ? '<span class="retro">(พักร์)</span>' : "";
    let poisonHtml = "";
    if (d.tipPoisonName) {
      const pinfo = POISON_TH[d.tipPoisonName];
      if (pinfo) {
        const sev = SEV_TH[d.tipPoisonSeverity] || "";
        poisonHtml = `
          <div class="tip-row tip-poison">
            <span class="tip-label">⚠️ พิษ</span>
            ${pinfo.icon} ${pinfo.name} (${sev})
          </div>
          <div class="tip-row tip-poison-meaning">${pinfo.meaning}</div>`;
      }
    }
    let dignityHtml = "";
    if (d.tipDignity) {
      const s = parseInt(d.tipStrength || "0", 10);
      let dignityClass = "tip-dignity-neutral";
      let icon = "";
      if (s >= 4) { dignityClass = "tip-dignity-very-strong"; icon = "★"; }
      else if (s >= 2) { dignityClass = "tip-dignity-strong"; icon = "✦"; }
      else if (s >= 1) { dignityClass = "tip-dignity-mild"; icon = "•"; }
      else if (s <= -2) { dignityClass = "tip-dignity-weak"; icon = "✖"; }
      else if (s < 0) { dignityClass = "tip-dignity-low"; icon = "▾"; }
      const sign = s > 0 ? "+" + s : s;
      dignityHtml = `
        <div class="tip-row tip-dignity ${dignityClass}">
          <span class="tip-label">${icon} กำลัง</span>
          ${d.tipDignity} <span class="tip-strength">(${sign})</span>
        </div>`;
    }
    return `
      <div class="tip-title">
        <span class="tip-planet">${d.tipPlanet}</span>
        <span class="tip-source">(${d.tipSource || ""})</span>
        ${retro}
      </div>
      <div class="tip-row"><span class="tip-label">ราศี</span>${d.tipRasi}</div>
      <div class="tip-row"><span class="tip-label">องศา</span>${d.tipDegree}°</div>
      <div class="tip-row"><span class="tip-label">ลิปดา</span>${d.tipArcmin}′</div>
      <div class="tip-row"><span class="tip-label">ฟิลิปดา</span>${d.tipArcsec}″</div>
      ${dignityHtml}
      ${poisonHtml}`;
  }

  function showTip(e, g) {
    tip.innerHTML = buildTipContent(g);
    tip.classList.add("visible");
    tip.setAttribute("aria-hidden", "false");
    moveTip(e);
  }

  function moveTip(e) {
    const padding = 14;
    const tw = tip.offsetWidth;
    const th = tip.offsetHeight;
    let x = e.clientX + padding;
    let y = e.clientY + padding;
    if (x + tw > window.innerWidth - 10) x = e.clientX - tw - padding;
    if (y + th > window.innerHeight - 10) y = e.clientY - th - padding;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }

  function hideTip() {
    tip.classList.remove("visible");
    tip.setAttribute("aria-hidden", "true");
  }

  // ใช้ event delegation บน SVG ทำงานได้กับ dynamic chips ด้วย
  svg.addEventListener("mouseover", (e) => {
    const g = getGroup(e.target);
    if (g && stuck === null) showTip(e, g);
  });
  svg.addEventListener("mousemove", (e) => {
    if (stuck === null && tip.classList.contains("visible")) moveTip(e);
  });
  svg.addEventListener("mouseout", (e) => {
    const g = getGroup(e.target);
    if (g && stuck === null) hideTip();
  });
  svg.addEventListener("click", (e) => {
    const g = getGroup(e.target);
    if (!g) return;
    e.stopPropagation();
    if (stuck === g) {
      stuck = null;
      hideTip();
    } else {
      stuck = g;
      showTip(e, g);
    }
  });

  document.addEventListener("click", (e) => {
    if (stuck && !stuck.contains(e.target) && !tip.contains(e.target)) {
      stuck = null;
      hideTip();
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && stuck) {
      stuck = null;
      hideTip();
    }
  });
}

/* ======================================================================
   3) View tabs (ดูดวง / ศึกษาโหราศาสตร์)
   ====================================================================== */

function setupViewTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  if (tabs.length === 0) return;

  function applyView(view) {
    document.body.classList.remove("view-general", "view-student");
    document.body.classList.add("view-" + view);
    tabs.forEach((t) => t.classList.toggle("active", t.dataset.view === view));
    try {
      localStorage.setItem("preferred_view", view);
    } catch (e) {}
  }

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => applyView(btn.dataset.view));
  });

  let saved = "general";
  try {
    saved = localStorage.getItem("preferred_view") || "general";
  } catch (e) {
    saved = "general";
  }
  if (saved !== "general" && saved !== "student") saved = "general";
  applyView(saved);
}

/* ======================================================================
   4) Toggle ตรียางค์ + ธาตุ
   ====================================================================== */

function setupTriyangkaToggle() {
  const stage = document.querySelector(".zodiac-stage");
  if (!stage) return;

  function bindToggle(cbId, layerClass, storageKey, defaultOn) {
    const cb = document.getElementById(cbId);
    if (!cb) return;
    const onCls = layerClass + "-on";
    const offCls = layerClass + "-off";
    const def = defaultOn === false ? "0" : "1";

    function apply(on) {
      stage.classList.toggle(onCls, on);
      stage.classList.toggle(offCls, !on);
      cb.checked = on;
    }
    let saved = def;
    try {
      const v = localStorage.getItem(storageKey);
      if (v !== null) saved = v;
    } catch (e) {}
    apply(saved === "1");

    cb.addEventListener("change", () => {
      const next = cb.checked;
      apply(next);
      try { localStorage.setItem(storageKey, next ? "1" : "0"); } catch (e) {}
    });
  }

  bindToggle("toggle-rasi",      "rasi",      "rasi_visible",      true);
  bindToggle("toggle-element",   "element",   "element_visible",   true);
  bindToggle("toggle-bhava",     "bhava",     "bhava_visible",     true);
  bindToggle("toggle-triyangka", "triyangka", "triyangka_visible", true);
  bindToggle("toggle-orbit",     "orbit",     "orbit_view",        false);

  // collapsible chart-cb-stack — default ปิด, จำสถานะใน localStorage
  document.querySelectorAll(".chart-cb-stack").forEach(function (stack) {
    const btn = stack.querySelector(".chart-cb-toggle");
    if (!btn) return;
    const STORAGE_KEY = "chart_cb_open";
    const initOpen = localStorage.getItem(STORAGE_KEY) === "1";
    stack.dataset.open = initOpen ? "true" : "false";
    btn.setAttribute("aria-expanded", initOpen ? "true" : "false");

    btn.addEventListener("click", function (e) {
      e.preventDefault();
      const isOpen = stack.dataset.open === "true";
      const next = !isOpen;
      stack.dataset.open = next ? "true" : "false";
      btn.setAttribute("aria-expanded", next ? "true" : "false");
      localStorage.setItem(STORAGE_KEY, next ? "1" : "0");
    });

    // click outside → ปิด (เฉพาะตอน open)
    document.addEventListener("click", function (e) {
      if (stack.dataset.open !== "true") return;
      if (stack.contains(e.target)) return;
      stack.dataset.open = "false";
      btn.setAttribute("aria-expanded", "false");
      localStorage.setItem(STORAGE_KEY, "0");
    });
  });
}

/* ======================================================================
   5) Transit Scrubber — เลื่อนวันดาวจร → re-submit form เพื่อให้ทุก section
   อัพเดทพร้อมกัน (คำทำนาย, ภพ, สรุป, oracle ฯลฯ)
   ====================================================================== */

function _isoAddDays(iso, delta) {
  const [y, m, d] = iso.split("-").map(Number);
  const dt = new Date(y, m - 1, d);
  dt.setDate(dt.getDate() + delta);
  return (
    dt.getFullYear() + "-" +
    String(dt.getMonth() + 1).padStart(2, "0") + "-" +
    String(dt.getDate()).padStart(2, "0")
  );
}

function _todayISO() {
  const now = new Date();
  return (
    now.getFullYear() + "-" +
    String(now.getMonth() + 1).padStart(2, "0") + "-" +
    String(now.getDate()).padStart(2, "0")
  );
}

function _nowTime() {
  const now = new Date();
  return (
    String(now.getHours()).padStart(2, "0") + ":" +
    String(now.getMinutes()).padStart(2, "0")
  );
}

function setupTransitScrubber() {
  const card = document.getElementById("transit-info-card");
  if (!card) return;

  const form = document.getElementById("birth-form");
  const hiddenDate   = document.getElementById("hidden_transit_date");
  const hiddenTime   = document.getElementById("hidden_transit_time");
  const hiddenScroll = document.getElementById("hidden_scroll_target");
  if (!form || !hiddenDate || !hiddenTime) return;

  const meta = document.getElementById("chart-meta");
  const initialDate = meta ? meta.dataset.transitDate : _todayISO();
  const initialTime = meta ? meta.dataset.transitTime : _nowTime();

  let currentDate = initialDate;
  let currentTime = initialTime;

  const datePicker = document.getElementById("scrubber-date-picker");
  const timePicker = document.getElementById("scrubber-time-picker");
  const statusEl   = document.getElementById("scrubber-status");

  function submitWith(newDate, newTime) {
    hiddenDate.value = newDate;
    hiddenTime.value = newTime;
    if (hiddenScroll) hiddenScroll.value = "1";
    if (statusEl) {
      statusEl.textContent = "กำลังคำนวณ…";
      statusEl.className = "scrubber-status loading";
    }
    card.classList.add("scrubber-busy");
    // เก็บ scroll position ปัจจุบัน → restore หลัง reload
    try {
      sessionStorage.setItem("transit_scroll_y", String(window.scrollY));
    } catch (e) {}
    form.submit();
  }

  card.querySelectorAll(".scrub-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const delta = parseInt(btn.dataset.delta, 10);
      let newDate, newTime;
      if (delta === 0) {
        newDate = _todayISO();
        newTime = _nowTime();
      } else {
        newDate = _isoAddDays(currentDate, delta);
        newTime = currentTime;
      }
      submitWith(newDate, newTime);
    });
  });

  if (datePicker) {
    datePicker.addEventListener("change", () => {
      if (datePicker.value) {
        // sync ISO → BE text input
        const dpTh = document.getElementById("scrubber-date-picker-th");
        if (dpTh) {
          const [yy, mm, dd] = datePicker.value.split("-").map(Number);
          dpTh.value = `${dd}/${String(mm).padStart(2,"0")}/${yy + 543}`;
        }
        submitWith(datePicker.value, currentTime);
      }
    });
  }

  // BE-format text input (DD/MM/YYYY พ.ศ.) — parse + submit
  const dpTh = document.getElementById("scrubber-date-picker-th");
  if (dpTh) {
    function commitTh() {
      const m = dpTh.value.trim().match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
      if (!m) return;
      const dd = parseInt(m[1], 10);
      const mm = parseInt(m[2], 10);
      const beY = parseInt(m[3], 10);
      if (beY < 2000 || beY > 3100 || mm < 1 || mm > 12 || dd < 1 || dd > 31) return;
      const ceY = beY - 543;
      const iso = `${ceY}-${String(mm).padStart(2,"0")}-${String(dd).padStart(2,"0")}`;
      if (datePicker) datePicker.value = iso;
      submitWith(iso, currentTime);
    }
    dpTh.addEventListener("change", commitTh);
    dpTh.addEventListener("blur", commitTh);
    dpTh.addEventListener("keydown", (e) => {
      if (e.key === "Enter") { e.preventDefault(); commitTh(); }
    });
  }

  if (timePicker) {
    timePicker.addEventListener("change", () => {
      if (timePicker.value) submitWith(currentDate, timePicker.value);
    });
  }
}

// คง scroll position เดิมหลัง submit จาก scrubber (ไม่กระโดดบนสุด)
function setupScrollRestore() {
  const flag = document.body.dataset.scrollTarget;
  if (flag !== "transit") return;
  let y = 0;
  try {
    const stored = sessionStorage.getItem("transit_scroll_y");
    if (stored !== null) {
      y = parseInt(stored, 10) || 0;
      sessionStorage.removeItem("transit_scroll_y");
    }
  } catch (e) {}
  // disable browser scroll restoration ที่อาจรบกวน
  if ("scrollRestoration" in history) {
    history.scrollRestoration = "manual";
  }
  // ทำหลัง layout settle (รอ font/SVG พร้อม)
  requestAnimationFrame(() => {
    window.scrollTo(0, y);
    // ทำซ้ำหลัง layout จริงๆ เสร็จ — กัน images/SVG ที่ delay
    setTimeout(() => window.scrollTo(0, y), 50);
  });
}

/* ====================================================================== */

/* ======================================================================
   Floating Chat Widget
   ====================================================================== */
function setupAstroChat() {
  const fab      = document.getElementById("chat-fab");
  const panel    = document.getElementById("chat-panel");
  const closeBtn = document.getElementById("chat-panel-close");
  const backdrop = document.getElementById("chat-backdrop");
  const form     = document.getElementById("chat-form");
  const history  = document.getElementById("chat-history");

  if (!fab) return;

  // ปุ่มอยู่ระหว่างพัฒนา — แสดง toast แทนการเปิด panel
  if (fab.classList.contains("chat-fab--dev")) {
    fab.addEventListener("click", () => {
      let toast = document.getElementById("chat-dev-toast");
      if (!toast) {
        toast = document.createElement("div");
        toast.id = "chat-dev-toast";
        toast.className = "chat-dev-toast";
        toast.textContent = "🔮 ฟีเจอร์ถามโหร AI อยู่ระหว่างพัฒนา — เร็วๆ นี้";
        document.body.appendChild(toast);
      }
      toast.classList.add("chat-dev-toast--show");
      clearTimeout(window._chatDevToastTimer);
      window._chatDevToastTimer = setTimeout(() => {
        toast.classList.remove("chat-dev-toast--show");
      }, 2500);
    });
    return;
  }

  if (!panel) return;

  // --- toggle open/close ---
  function openPanel() {
    panel.classList.remove("chat-panel--closing");
    panel.classList.add("chat-panel--open");
    backdrop.classList.add("chat-backdrop--visible");
    fab.classList.add("chat-fab--open");
    fab.querySelector(".chat-fab-icon").textContent = "✕";
    panel.setAttribute("aria-hidden", "false");
    if (history) history.scrollTop = history.scrollHeight;
    document.getElementById("chat-question")?.focus();
  }
  function closePanel() {
    panel.classList.add("chat-panel--closing");
    backdrop.classList.remove("chat-backdrop--visible");
    fab.classList.remove("chat-fab--open");
    fab.querySelector(".chat-fab-icon").textContent = "🔮";
    panel.setAttribute("aria-hidden", "true");
    // หลัง animation จบ (0.18s) ค่อย remove --open
    setTimeout(() => {
      panel.classList.remove("chat-panel--open", "chat-panel--closing");
    }, 200);
  }

  fab.addEventListener("click", () => {
    if (fab.disabled) return;
    panel.classList.contains("chat-panel--open") ? closePanel() : openPanel();
  });
  closeBtn?.addEventListener("click", closePanel);
  backdrop.addEventListener("click", closePanel);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closePanel(); });

  // --- ไม่มี form (ยังไม่ผูกดวง) → จบแค่นี้ ---
  if (!form) return;

  const input   = document.getElementById("chat-question");
  const sendBtn = form.querySelector(".chat-send-btn");

  // chips ใน panel-footer
  document.querySelectorAll(".chat-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      if (!input) return;
      input.value = chip.dataset.q || "";
      form.dispatchEvent(new Event("submit", { cancelable: true }));
    });
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const q = input.value.trim();
    if (!q) return;

    appendBubble("user", q);
    input.value = "";
    sendBtn.disabled = true;
    const loadingEl = appendLoading();

    try {
      const data = new FormData(form);
      data.set("question", q);
      const res = await fetch("/chart/ask", { method: "POST", body: data });

      const ct = res.headers.get("content-type") || "";

      // --- preview / error → JSON ก้อนเดียว ---
      if (ct.includes("application/json")) {
        const json = await res.json();
        loadingEl.remove();
        if (json.error) {
          appendBubble("error", "❌ " + json.error);
          return;
        }
        if (json.mode === "preview") {
          const autoNote = json.auto_warning
            ? "\n⚠️ ระบบตรวจพบเกณฑ์ระวัง → เสริมหมวดนี้อัตโนมัติ" : "";
          const header = `[Preview] หมวด: ${json.intents.join(" + ")}${autoNote}\n` +
                         `หมายเหตุ: ${json.note}\n\n`;
          appendBubble("preview", header + json.prompt_preview);
        }
        return;
      }

      // --- Claude streaming → SSE ---
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let aiBubble = null;
      let aiBody = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // SSE แต่ละ event คั่นด้วย \n\n
        let idx;
        while ((idx = buffer.indexOf("\n\n")) !== -1) {
          const rawEvent = buffer.slice(0, idx);
          buffer = buffer.slice(idx + 2);
          if (!rawEvent.startsWith("data:")) continue;

          let payload;
          try {
            payload = JSON.parse(rawEvent.slice(5).trim());
          } catch { continue; }

          if (payload.type === "meta") {
            loadingEl.remove();
            aiBubble = appendBubble("ai", "", payload.intents.join(" + "));
            aiBody = aiBubble.querySelector(".chat-ai-body");
          } else if (payload.type === "chunk" && aiBody) {
            aiBody.textContent += payload.text;
            history.scrollTop = history.scrollHeight;
          } else if (payload.type === "error") {
            if (aiBubble) aiBubble.remove();
            loadingEl.remove();
            appendBubble("error", "❌ " + payload.message);
          } else if (payload.type === "done") {
            // จบ
          }
        }
      }
    } catch (err) {
      loadingEl.remove();
      appendBubble("error", "❌ เชื่อมต่อ server ไม่ได้: " + err.message);
    } finally {
      sendBtn.disabled = false;
      input.focus();
    }
  });

  function appendBubble(type, text, meta = "") {
    const div = document.createElement("div");
    if (type === "user") {
      div.className = "chat-bubble chat-bubble-user";
      div.textContent = text;
    } else if (type === "ai") {
      div.className = "chat-bubble chat-bubble-ai";
      if (meta) {
        const m = document.createElement("span");
        m.className = "chat-meta";
        m.textContent = "🔮 โหร AI · " + meta;
        div.appendChild(m);
      }
      const body = document.createElement("div");
      body.className = "chat-ai-body";
      body.textContent = text;
      div.appendChild(body);
    } else if (type === "preview") {
      div.className = "chat-bubble chat-bubble-preview";
      const m = document.createElement("span");
      m.className = "chat-meta";
      m.textContent = "📋 Prompt Preview — mock mode (ยังไม่มี API key)";
      div.appendChild(m);
      const body = document.createElement("div");
      body.textContent = text;
      div.appendChild(body);
    } else {
      div.className = "chat-bubble chat-bubble-error";
      div.textContent = text;
    }
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
    return div;
  }

  function appendLoading() {
    const div = document.createElement("div");
    div.className = "chat-loading";
    div.innerHTML = "<span></span><span></span><span></span>";
    history.appendChild(div);
    history.scrollTop = history.scrollHeight;
    return div;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setupDateSync("birth_date_th", "birth_date_picker");
  setupDatePickerButtons();
  setupPlanetTooltip();
  setupViewTabs();
  setupTriyangkaToggle();
  setupTransitScrubber();
  setupScrollRestore();
  setupAstroChat();
});
