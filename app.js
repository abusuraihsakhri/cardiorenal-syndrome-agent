"use strict";

const CRS_TYPES = Object.freeze({
  "1": {
    label: "Type 1 — Acute cardiorenal syndrome",
    detail: "Acute cardiac dysfunction leading to acute kidney injury or dysfunction."
  },
  "2": {
    label: "Type 2 — Chronic cardiorenal syndrome",
    detail: "Chronic cardiac dysfunction leading to kidney injury or dysfunction."
  },
  "3": {
    label: "Type 3 — Acute renocardiac syndrome",
    detail: "Acute kidney dysfunction leading to acute cardiac injury or dysfunction."
  },
  "4": {
    label: "Type 4 — Chronic renocardiac syndrome",
    detail: "Chronic kidney disease leading to cardiac injury, disease, or dysfunction."
  },
  "5": {
    label: "Type 5 — Secondary cardiorenal syndrome",
    detail: "A systemic disorder causing simultaneous cardiac and kidney injury or dysfunction."
  }
});

function finiteNumber(value, name) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    throw new Error(name + " must be a finite number.");
  }
  return parsed;
}

function classifyGfr(egfr) {
  const value = finiteNumber(egfr, "eGFR");
  if (value < 0) {
    throw new Error("eGFR must be non-negative.");
  }
  if (value >= 90) return { category: "G1", description: "Normal or high" };
  if (value >= 60) return { category: "G2", description: "Mildly decreased" };
  if (value >= 45) return { category: "G3a", description: "Mildly to moderately decreased" };
  if (value >= 30) return { category: "G3b", description: "Moderately to severely decreased" };
  if (value >= 15) return { category: "G4", description: "Severely decreased" };
  return { category: "G5", description: "Kidney failure" };
}

function analyzeReference({ crsType, egfr, mapValue, cvpValue }) {
  const classification = CRS_TYPES[String(crsType)];
  if (!classification) {
    throw new Error("CRS type must be between 1 and 5.");
  }

  const gfr = classifyGfr(egfr);
  const hasMap = mapValue !== "" && mapValue !== null && mapValue !== undefined;
  const hasCvp = cvpValue !== "" && cvpValue !== null && cvpValue !== undefined;
  if (hasMap !== hasCvp) {
    throw new Error("Enter both MAP and CVP, or leave both blank.");
  }

  let gradient = null;
  if (hasMap && hasCvp) {
    gradient = finiteNumber(mapValue, "MAP") - finiteNumber(cvpValue, "CVP");
  }

  return { classification, gfr, gradient };
}

function preferredTheme() {
  try {
    const saved = localStorage.getItem("crs-theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch (_) {
    // Storage may be disabled; fall back to system preference.
  }
  return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const button = document.getElementById("themeToggle");
  if (button) {
    button.setAttribute(
      "aria-label",
      theme === "dark" ? "Switch to light theme" : "Switch to dark theme"
    );
  }
}

function initializeBrowserApp() {
  const form = document.getElementById("analysisForm");
  const toggle = document.getElementById("themeToggle");
  if (!form || !toggle) return;

  applyTheme(preferredTheme());

  toggle.addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(next);
    try {
      localStorage.setItem("crs-theme", next);
    } catch (_) {
      // Theme still applies for the current page when storage is unavailable.
    }
  });

  function render() {
    const error = document.getElementById("formError");
    try {
      const result = analyzeReference({
        crsType: document.getElementById("crsType").value,
        egfr: document.getElementById("egfr").value,
        mapValue: document.getElementById("mapValue").value,
        cvpValue: document.getElementById("cvpValue").value
      });

      document.getElementById("crsResult").textContent = result.classification.label;
      document.getElementById("crsDetail").textContent = result.classification.detail;
      document.getElementById("gfrResult").textContent =
        result.gfr.category + " — " + result.gfr.description;
      document.getElementById("gfrDetail").textContent =
        "Category based on the entered eGFR value; chronicity is not assessed.";
      document.getElementById("rppResult").textContent =
        result.gradient === null ? "Not calculated" : result.gradient.toFixed(1) + " mmHg";
      error.textContent = "";
    } catch (err) {
      error.textContent = err instanceof Error ? err.message : "Unable to analyze the inputs.";
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    render();
  });

  render();
}

if (typeof module !== "undefined" && module.exports) {
  module.exports = { CRS_TYPES, classifyGfr, analyzeReference };
}

if (typeof document !== "undefined") {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initializeBrowserApp);
  } else {
    initializeBrowserApp();
  }
}
