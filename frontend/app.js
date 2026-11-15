"use strict";

/* ---------- Text (English / Hindi) ---------- */
const T = {
  en: {
    title: "PCOS risk check",
    lede: "Answer a few questions to see how likely PCOS is. No lab tests needed.",
    basics: "About you", symptoms: "Symptoms", lifestyle: "Lifestyle", labs: "Your reports",
    age: "Age (years)", bmi: "BMI", height: "Height (cm)", weight: "Weight (kg)", calc: "Fill BMI",
    cycle: "Your periods", regular: "Regular", irregular: "Irregular", yes: "Yes", no: "No",
    haslabs: "I have ultrasound or hormone reports",
    check: "Check my risk", download: "Download report (PDF)",
    empty: "Fill in the form, then choose \u201CCheck my risk\u201D.",
    why: "What influenced this result", raises: "raises risk", lowers: "lowers risk",
    bands: { low: "Lower likelihood", moderate: "Moderate likelihood", high: "Higher likelihood" },
    disclaimer: "This is a screening aid, not a medical diagnosis. Only a doctor can confirm PCOS.",
    privacy: "Nothing you enter is stored.",
    demo: "Demo model: trained on synthetic data. Results are not meaningful.",
    error: "Could not get a result. Check your entries and that the server is running.",
    advice: {
      low: ["Your answers point to a lower likelihood. Keep up regular exercise and a balanced diet.",
            "If your periods are irregular or symptoms persist, see a doctor anyway. A screening score does not rule PCOS out."],
      moderate: ["Consider booking a visit with a gynaecologist or physician to discuss your symptoms.",
                 "A pelvic ultrasound and hormone blood tests help confirm or rule out PCOS.",
                 "Track your period dates for a few months and bring the record to your appointment."],
      high: ["Please consult a gynaecologist soon. Your answers match a pattern seen in many women with PCOS.",
             "Ask about a pelvic ultrasound and hormone tests to confirm. Early diagnosis helps prevent complications.",
             "Healthy eating, regular activity and good sleep help with symptoms, and a doctor can guide you further."]
    },
    f: { weight_gain: "Recent weight gain?", hair_growth: "Excess facial or body hair?", skin_darkening: "Skin darkening?",
         hair_loss: "Hair loss?", pimples: "Acne or pimples?", fast_food: "Frequent fast food?", regular_exercise: "Regular exercise?",
         follicle_l: "Follicle count, left ovary", follicle_r: "Follicle count, right ovary", amh: "AMH (ng/mL)", fsh_lh: "FSH/LH ratio",
         age: "Age", bmi: "BMI", cycle_irregular: "Irregular periods" }
  },
  hi: {
    title: "PCOS जोखिम जाँच",
    lede: "कुछ सवालों के जवाब दें और जानें कि PCOS की संभावना कितनी है। किसी लैब टेस्ट की ज़रूरत नहीं।",
    basics: "आपके बारे में", symptoms: "लक्षण", lifestyle: "जीवनशैली", labs: "आपकी रिपोर्ट",
    age: "उम्र (वर्ष)", bmi: "BMI", height: "कद (सेमी)", weight: "वज़न (किग्रा)", calc: "BMI भरें",
    cycle: "माहवारी", regular: "नियमित", irregular: "अनियमित", yes: "हाँ", no: "नहीं",
    haslabs: "मेरे पास अल्ट्रासाउंड या हार्मोन रिपोर्ट है",
    check: "मेरा जोखिम जाँचें", download: "रिपोर्ट डाउनलोड करें (PDF)",
    empty: "फ़ॉर्म भरें, फिर \u201Cमेरा जोखिम जाँचें\u201D दबाएँ।",
    why: "इस नतीजे को किसने प्रभावित किया", raises: "जोखिम बढ़ाता है", lowers: "जोखिम घटाता है",
    bands: { low: "कम संभावना", moderate: "मध्यम संभावना", high: "अधिक संभावना" },
    disclaimer: "यह केवल जाँच में सहायता है, चिकित्सकीय निदान नहीं। PCOS की पुष्टि केवल डॉक्टर कर सकते हैं।",
    privacy: "आपकी दी गई कोई जानकारी सहेजी नहीं जाती।",
    demo: "डेमो मॉडल: नकली डेटा पर प्रशिक्षित। परिणाम सार्थक नहीं हैं।",
    error: "नतीजा नहीं मिल सका। अपनी प्रविष्टियाँ और सर्वर चालू है या नहीं, जाँचें।",
    advice: {
      low: ["आपके जवाब कम संभावना दर्शाते हैं। नियमित व्यायाम और संतुलित आहार जारी रखें।",
            "अगर माहवारी अनियमित है या लक्षण बने रहते हैं, तो फिर भी डॉक्टर को दिखाएँ। यह स्कोर PCOS को पूरी तरह खारिज नहीं करता।"],
      moderate: ["अपने लक्षणों के बारे में स्त्री रोग विशेषज्ञ या डॉक्टर से मिलने पर विचार करें।",
                 "पेल्विक अल्ट्रासाउंड और हार्मोन ब्लड टेस्ट से PCOS की पुष्टि या इनकार किया जा सकता है।",
                 "कुछ महीनों तक माहवारी की तारीखें लिखें और डॉक्टर के पास साथ ले जाएँ।"],
      high: ["कृपया जल्द स्त्री रोग विशेषज्ञ से मिलें। आपके जवाब PCOS वाली कई महिलाओं में दिखने वाले पैटर्न से मेल खाते हैं।",
             "पुष्टि के लिए पेल्विक अल्ट्रासाउंड और हार्मोन जाँच के बारे में पूछें। जल्दी निदान से जटिलताओं से बचाव होता है।",
             "संतुलित आहार, नियमित गतिविधि और अच्छी नींद लक्षणों में मदद करती है। आगे का मार्गदर्शन डॉक्टर देंगे।"]
    },
    f: { weight_gain: "हाल में वज़न बढ़ा?", hair_growth: "चेहरे या शरीर पर ज़्यादा बाल?", skin_darkening: "त्वचा का काला पड़ना?",
         hair_loss: "बाल झड़ना?", pimples: "मुँहासे?", fast_food: "अक्सर फास्ट फूड?", regular_exercise: "नियमित व्यायाम?",
         follicle_l: "फॉलिकल संख्या, बायाँ अंडाशय", follicle_r: "फॉलिकल संख्या, दायाँ अंडाशय", amh: "AMH (ng/mL)", fsh_lh: "FSH/LH अनुपात",
         age: "उम्र", bmi: "BMI", cycle_irregular: "अनियमित माहवारी" }
  }
};

const BAND_COLOR = { low: "#2E7D6B", moderate: "#C27A12", high: "#B3304A" };
const SYMPTOMS = ["weight_gain", "hair_growth", "skin_darkening", "hair_loss", "pimples"];
const LIFESTYLE = ["fast_food", "regular_exercise"];
const LABS = [
  { key: "follicle_l", min: 0, max: 40, step: 1, val: 6 },
  { key: "follicle_r", min: 0, max: 40, step: 1, val: 6 },
  { key: "amh", min: 0, max: 30, step: 0.1, val: 3 },
  { key: "fsh_lh", min: 0, max: 20, step: 0.1, val: 1 },
];

let lang = "en";
let lastResult = null;
let hasChecked = false;
let timer = null;
const $ = (id) => document.getElementById(id);

/* ---------- Form ---------- */
const yesNo = (key, name) => `
  <div class="row"><span class="q" id="q-${key}">${name}</span>
    <span class="seg" role="radiogroup" aria-labelledby="q-${key}">
      <label><input type="radio" name="${key}" value="0" checked><span>${T[lang].no}</span></label>
      <label><input type="radio" name="${key}" value="1"><span>${T[lang].yes}</span></label>
    </span></div>`;

function readState() {
  const s = {};
  document.querySelectorAll("#form input").forEach((el) => {
    if (el.type === "radio" && el.checked) s[el.name] = el.value;
    else if (el.type === "number") s[el.name] = el.value;
  });
  return s;
}

function renderForm() {
  const t = T[lang], prev = readState();
  const g = (title, rows) => `<fieldset class="group"><legend>${title}</legend>${rows}</fieldset>`;
  const num = (key, label, min, max, step, val) => `
    <div class="row"><label for="${key}">${label}</label>
      <input class="num" type="number" id="${key}" name="${key}" min="${min}" max="${max}" step="${step}" value="${val}" inputmode="decimal"></div>`;

  $("fields").innerHTML =
    g(t.basics,
      num("age", t.age, 12, 60, 1, prev.age ?? 25) +
      num("bmi", t.bmi, 12, 55, 0.1, prev.bmi ?? 22) +
      `<div class="bmi-help"><span>${t.height}</span><input class="num" type="number" id="h" min="100" max="220" aria-label="${t.height}">
        <span>${t.weight}</span><input class="num" type="number" id="w" min="25" max="200" aria-label="${t.weight}">
        <button type="button" id="calc">${t.calc}</button></div>` +
      `<div class="row"><span class="q" id="q-cycle">${t.cycle}</span>
        <span class="seg" role="radiogroup" aria-labelledby="q-cycle">
          <label><input type="radio" name="cycle_irregular" value="0" checked><span>${t.regular}</span></label>
          <label><input type="radio" name="cycle_irregular" value="1"><span>${t.irregular}</span></label>
        </span></div>`) +
    g(t.symptoms, SYMPTOMS.map((k) => yesNo(k, t.f[k])).join("")) +
    g(t.lifestyle, LIFESTYLE.map((k) => yesNo(k, t.f[k])).join(""));

  $("labs").innerHTML = `<legend>${t.labs}</legend>` +
    LABS.map((l) => num(l.key, t.f[l.key], l.min, l.max, l.step, prev[l.key] ?? l.val)).join("");

  // restore radios
  Object.entries(prev).forEach(([k, v]) => {
    const r = document.querySelector(`input[type=radio][name="${k}"][value="${v}"]`);
    if (r) r.checked = true;
  });

  $("calc").onclick = () => {
    const h = parseFloat($("h").value), w = parseFloat($("w").value);
    if (h > 0 && w > 0) { $("bmi").value = (w / ((h / 100) ** 2)).toFixed(1); schedule(); }
  };
}

function applyStaticText() {
  const t = T[lang];
  document.documentElement.lang = lang;
  document.title = t.title;
  $("t-title").textContent = t.title;
  $("t-lede").textContent = t.lede;
  $("t-haslabs").textContent = t.haslabs;
  $("check").textContent = t.check;
  $("download").textContent = t.download;
  $("t-why").textContent = t.why;
  $("empty").textContent = t.empty;
  $("disclaimer").textContent = t.disclaimer;
  $("privacy").textContent = t.privacy;
  $("error").textContent = t.error;
  document.querySelectorAll(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
  const banner = $("demo-banner");
  if (!banner.hidden) banner.textContent = t.demo;
}

/* ---------- Dial ---------- */
const CX = 110, CY = 110, R = 88;
const pt = (p, r = R) => { const a = Math.PI * (1 - p); return [CX + r * Math.cos(a), CY - r * Math.sin(a)]; };
const arc = (p0, p1, color) => {
  const [x0, y0] = pt(p0), [x1, y1] = pt(p1);
  return `<path d="M${x0} ${y0} A${R} ${R} 0 0 1 ${x1} ${y1}" fill="none" stroke="${color}" stroke-width="16" stroke-linecap="butt" opacity=".9"/>`;
};

function drawDial(result) {
  let svg = arc(0, 0.4, BAND_COLOR.low) + arc(0.4, 0.7, BAND_COLOR.moderate) + arc(0.7, 1, BAND_COLOR.high);
  if (result) {
    const p = result.risk, [x, y] = pt(p), [x2, y2] = pt(p, R - 30), col = BAND_COLOR[result.band];
    svg += `<line x1="${x2}" y1="${y2}" x2="${x}" y2="${y}" stroke="#231F2E" stroke-width="3"/>
            <circle cx="${x}" cy="${y}" r="9" fill="#fff" stroke="#231F2E" stroke-width="3"/>
            <text x="${CX}" y="${CY - 12}" text-anchor="middle" font-size="40" font-weight="800" fill="${col}">${result.risk_percent.toFixed(0)}%</text>`;
  } else {
    svg += `<text x="${CX}" y="${CY - 12}" text-anchor="middle" font-size="40" font-weight="800" fill="#DDD8E6">--</text>`;
  }
  $("dial").innerHTML = svg;
}

/* ---------- API ---------- */
function buildPayload() {
  const s = readState(), tier = $("has-labs").checked ? 2 : 1;
  const p = { tier, age: parseInt(s.age, 10), bmi: parseFloat(s.bmi) };
  ["cycle_irregular", ...SYMPTOMS, ...LIFESTYLE].forEach((k) => (p[k] = parseInt(s[k], 10)));
  if (tier === 2) {
    p.follicle_l = parseInt(s.follicle_l, 10); p.follicle_r = parseInt(s.follicle_r, 10);
    p.amh = parseFloat(s.amh); p.fsh_lh = parseFloat(s.fsh_lh);
  }
  return p;
}

async function check() {
  hasChecked = true;
  $("error").hidden = true;
  try {
    const res = await fetch("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(buildPayload()) });
    if (!res.ok) throw new Error(res.status);
    lastResult = await res.json();
    showResult();
  } catch (e) {
    $("error").hidden = false;
  }
}

function showResult() {
  const r = lastResult, t = T[lang];
  if (!r) return;
  drawDial(r);
  $("band").textContent = t.bands[r.band];
  $("band").style.color = BAND_COLOR[r.band];
  $("empty").hidden = true;
  $("detail").hidden = false;
  $("advice").innerHTML = t.advice[r.band].map((a) => `<li>${a}</li>`).join("");
  const max = Math.max(...r.factors.map((f) => Math.abs(f.contribution)), 0.01);
  $("factors").innerHTML = r.factors.map((f) => {
    const up = f.direction === "raises";
    return `<li><span>${t.f[f.feature] || f.label}</span><span class="effect">${up ? t.raises : t.lowers}</span>
      <span class="bar"><i style="width:${(Math.abs(f.contribution) / max) * 100}%;background:${up ? BAND_COLOR.high : BAND_COLOR.low}"></i></span></li>`;
  }).join("");
}

async function downloadReport() {
  try {
    const res = await fetch("/api/report", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(buildPayload()) });
    if (!res.ok) throw new Error(res.status);
    const url = URL.createObjectURL(await res.blob());
    const a = Object.assign(document.createElement("a"), { href: url, download: "pcos_screening_report.pdf" });
    document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
  } catch (e) { $("error").hidden = false; }
}

function schedule() { if (!hasChecked) return; clearTimeout(timer); timer = setTimeout(check, 350); }

/* ---------- Wiring ---------- */
$("form").addEventListener("submit", (e) => { e.preventDefault(); check(); });
$("form").addEventListener("input", schedule);
$("form").addEventListener("change", schedule);
$("has-labs").addEventListener("change", () => { $("labs").hidden = !$("has-labs").checked; });
$("download").addEventListener("click", downloadReport);
document.querySelectorAll(".lang button").forEach((b) => b.addEventListener("click", () => {
  lang = b.dataset.lang; renderForm(); applyStaticText();
  if (lastResult) showResult(); else $("band").textContent = "";
}));

fetch("/api/meta").then((r) => r.json()).then((m) => {
  if (m.demo_model) { $("demo-banner").hidden = false; $("demo-banner").textContent = T[lang].demo; }
}).catch(() => {});

renderForm(); applyStaticText(); drawDial(null);
