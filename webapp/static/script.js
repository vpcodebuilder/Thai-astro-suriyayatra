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
      // วิธีมาตรฐาน (Chrome, Edge, Firefox ใหม่)
      if (typeof pick.showPicker === "function") {
        try {
          pick.showPicker();
          return;
        } catch (err) {
          // some browsers throw if not triggered by user gesture
        }
      }
      // fallback: focus + click (iOS Safari)
      pick.focus();
      pick.click();
    });
  });
}

/* ======================================================================
   2) Planet hover tooltip
   ====================================================================== */

const RASI_DEG_OF_30 = {
  // not used here; conversion done server-side
};

function setupPlanetTooltip() {
  const tip = document.getElementById("planet-tooltip");
  if (!tip) return;

  // ดาว/ลัคนา (มี data-tip-planet) + triyangka markers (มี data-tri-rasi)
  const groups = document.querySelectorAll(
    ".planet-svg-group[data-tip-planet], .lagna-group[data-tip-planet], .triyangka-marker-group[data-tri-rasi]"
  );

  groups.forEach((g) => {
    g.addEventListener("mouseenter", (e) => showTip(e, g));
    g.addEventListener("mousemove", (e) => moveTip(e));
    g.addEventListener("mouseleave", () => hideTip());
    // touch
    g.addEventListener("click", (e) => {
      showTip(e, g);
      setTimeout(hideTip, 3500);
    });
  });

  // poison key → ไทย
  const POISON_TH = {
    naga:  { icon: "🐍", name: "พิษนาค",
             meaning: "ยาพิษ/สมอง/ความดัน/ส่วนบนของศีรษะ" },
    krut:  { icon: "🦅", name: "พิษครุฑ",
             meaning: "อุบัติเหตุฉับพลัน/อวัยวะส่วนกลาง" },
    sunak: { icon: "🐕", name: "พิษสุนัข",
             meaning: "ศัตรู/ใส่ความ/อุบัติเหตุรถ/ของมีคม" },
  };
  const SEV_TH = { heavy: "หนัก", light: "เบา" };

  function showTip(e, g) {
    const d = g.dataset;
    // triyangka marker (ไม่มี tip-planet)
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
            <div class="tip-row tip-poison-meaning">${pinfo.meaning}</div>
          `;
        }
      }
      tip.innerHTML = `
        <div class="tip-title">
          <span class="tip-planet">ตรียางค์ ${d.triDecanate}/3</span>
          <span class="tip-source">(${d.triRasi})</span>
        </div>
        <div class="tip-row"><span class="tip-label">ดาวครอง</span>${d.triLord}</div>
        <div class="tip-row"><span class="tip-label">ช่วง</span>${d.triDegFrom}°-${d.triDegTo}°</div>
        ${poisonHtml}
      `;
    } else {
      // ดาว/ลัคนา
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
            <div class="tip-row tip-poison-meaning">${pinfo.meaning}</div>
          `;
        }
      }
      tip.innerHTML = `
        <div class="tip-title">
          <span class="tip-planet">${d.tipPlanet}</span>
          <span class="tip-source">(${d.tipSource})</span>
          ${retro}
        </div>
        <div class="tip-row"><span class="tip-label">ราศี</span>${d.tipRasi}</div>
        <div class="tip-row"><span class="tip-label">องศา</span>${d.tipDegree}°</div>
        <div class="tip-row"><span class="tip-label">ลิปดา</span>${d.tipArcmin}′</div>
        <div class="tip-row"><span class="tip-label">ฟิลิปดา</span>${d.tipArcsec}″</div>
        ${poisonHtml}
      `;
    }
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
    // ไม่ให้หลุดจอด้านขวา/ล่าง
    if (x + tw > window.innerWidth - 10) x = e.clientX - tw - padding;
    if (y + th > window.innerHeight - 10) y = e.clientY - th - padding;
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }

  function hideTip() {
    tip.classList.remove("visible");
    tip.setAttribute("aria-hidden", "true");
  }
}

/* ====================================================================== */

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
    } catch (e) {
      /* localStorage may be blocked — ignore */
    }
  }

  tabs.forEach((btn) => {
    btn.addEventListener("click", () => applyView(btn.dataset.view));
  });

  // Restore preferred view, default to "general"
  let saved = "general";
  try {
    saved = localStorage.getItem("preferred_view") || "general";
  } catch (e) {
    saved = "general";
  }
  if (saved !== "general" && saved !== "student") saved = "general";
  applyView(saved);
}

// Toggle ตรียางค์ & ธาตุ layer บนผัง — จำสถานะใน localStorage
function setupTriyangkaToggle() {
  const cb = document.getElementById("toggle-triyangka");
  const stage = document.querySelector(".zodiac-stage");
  if (!cb || !stage) return;

  function apply(on) {
    if (on) {
      stage.classList.add("triyangka-on");
      stage.classList.remove("triyangka-off");
    } else {
      stage.classList.remove("triyangka-on");
      stage.classList.add("triyangka-off");
    }
    cb.checked = on;
  }

  let saved = "1";
  try { saved = localStorage.getItem("triyangka_visible") || "1"; } catch (e) {}
  apply(saved === "1");

  cb.addEventListener("change", () => {
    const next = cb.checked;
    apply(next);
    try { localStorage.setItem("triyangka_visible", next ? "1" : "0"); } catch (e) {}
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupDateSync("birth_date_th", "birth_date_picker");
  setupDateSync("transit_date_th", "transit_date_picker");
  setupDatePickerButtons();
  setupPlanetTooltip();
  setupViewTabs();
  setupTriyangkaToggle();
});
