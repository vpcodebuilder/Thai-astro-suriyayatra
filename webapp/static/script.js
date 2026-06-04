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

document.addEventListener("DOMContentLoaded", () => {
  setupDateSync("birth_date_th", "birth_date_picker");
  setupDatePickerButtons();
  setupPlanetTooltip();
  setupViewTabs();
  setupTriyangkaToggle();
  setupTransitScrubber();
  setupScrollRestore();
});
