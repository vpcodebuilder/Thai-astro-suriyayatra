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

/* ======================================================================
   2) Planet hover tooltip
   ====================================================================== */

const RASI_DEG_OF_30 = {
  // not used here; conversion done server-side
};

function setupPlanetTooltip() {
  const tip = document.getElementById("planet-tooltip");
  if (!tip) return;

  const groups = document.querySelectorAll(
    ".planet-svg-group[data-tip-planet], .lagna-group[data-tip-planet]"
  );

  groups.forEach((g) => {
    g.addEventListener("mouseenter", (e) => showTip(e, g));
    g.addEventListener("mousemove", (e) => moveTip(e));
    g.addEventListener("mouseleave", () => hideTip());
    // เปิดด้วย touch ด้วย
    g.addEventListener("click", (e) => {
      showTip(e, g);
      setTimeout(hideTip, 3500);
    });
  });

  function showTip(e, g) {
    const d = g.dataset;
    const retro = d.tipRetro === "1" ? '<span class="retro">(พักร์)</span>' : "";
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
    `;
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

document.addEventListener("DOMContentLoaded", () => {
  setupDateSync("birth_date_th", "birth_date_picker");
  setupDateSync("transit_date_th", "transit_date_picker");
  setupPlanetTooltip();
});
