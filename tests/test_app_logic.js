"use strict";

const assert = require("node:assert/strict");
const { classifyGfr, analyzeReference } = require("../app.js");

assert.equal(classifyGfr(90).category, "G1");
assert.equal(classifyGfr(89.9).category, "G2");
assert.equal(classifyGfr(60).category, "G2");
assert.equal(classifyGfr(59.9).category, "G3a");
assert.equal(classifyGfr(45).category, "G3a");
assert.equal(classifyGfr(44.9).category, "G3b");
assert.equal(classifyGfr(30).category, "G3b");
assert.equal(classifyGfr(29.9).category, "G4");
assert.equal(classifyGfr(15).category, "G4");
assert.equal(classifyGfr(14.9).category, "G5");

const result = analyzeReference({
  crsType: "3",
  egfr: "44",
  mapValue: "80",
  cvpValue: "15"
});
assert.equal(result.classification.label, "Type 3 — Acute renocardiac syndrome");
assert.equal(result.gfr.category, "G3b");
assert.equal(result.gradient, 65);

assert.throws(() => classifyGfr(-1), /non-negative/);
assert.throws(
  () => analyzeReference({ crsType: "1", egfr: "60", mapValue: "80", cvpValue: "" }),
  /both MAP and CVP/
);

console.log("Browser reference logic tests passed.");
