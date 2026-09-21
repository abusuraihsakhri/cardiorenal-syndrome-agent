# Cardiorenal Syndrome Agent

Educational and research-oriented reference utilities for the five-type Acute Dialysis Quality Initiative (ADQI) cardiorenal syndrome classification, KDIGO GFR categories, and a simple MAP−CVP pressure-gradient calculation.

> **Use limitation:** This repository is not validated clinical decision support. It does not diagnose cardiorenal syndrome, estimate prognosis, or recommend treatment. Do not enter identifiable patient information.

## What it includes

- ADQI cardiorenal syndrome Types 1–5 reference classification.
- KDIGO GFR categories G1, G2, G3a, G3b, G4, and G5.
- Optional arithmetic MAP−CVP pressure-gradient calculation.
- A compact browser interface with light/dark themes; all browser inputs stay local.
- Python CLI and optional FastAPI interface.
- Legacy threshold-audit imports retained for compatibility, explicitly labeled as demonstration rules.
- Tests covering classification boundaries, CSV parsing, audit-chain tamper detection, and browser calculation logic.

The browser application uses plain HTML, CSS, and JavaScript. It does not load Pyodide because the reference calculations are small enough to implement directly in the browser without a Python/WebAssembly runtime.

## Browser use

Open `index.html` locally, or use the GitHub Pages deployment after it is enabled and verified. Choose a CRS type, enter an eGFR value, optionally enter both MAP and CVP, and select **Analyze**.

The GFR category is contextual information only. G1 or G2 alone does not establish CKD, and CKD assessment requires chronicity and/or other markers of kidney damage.

## Python use

Requires Python 3.10 or newer.

~~~bash
git clone https://github.com/abusuraihsakhri/cardiorenal-syndrome-agent.git
cd cardiorenal-syndrome-agent
python -m pip install -e ".[dev]"
~~~

Reference classification:

~~~bash
python cli.py classify --crs-type 1 --egfr 55 --map 75 --cvp 12
~~~

Batch compatibility audit:

~~~bash
python cli.py batch -i sample.csv -o results.csv
~~~

Optional API:

~~~bash
python -m pip install -e ".[server]"
python cli.py serve
~~~

The compatibility audit uses historical, configurable demonstration thresholds. Its output must not be interpreted as a clinical alert, validated risk score, or treatment recommendation.

## Testing

~~~bash
python -m pip install -e ".[server,dev]"
python -m pytest
python -m ruff check . --select E9,F63,F7,F82
node --check app.js
node tests/test_app_logic.js
pip-audit --skip-editable
~~~

## References

- Ronco C, McCullough P, Anker SD, et al. *Cardio-renal syndromes: report from the consensus conference of the Acute Dialysis Quality Initiative.* Eur Heart J. 2010;31(6):703–711. doi:10.1093/eurheartj/ehp507.
- KDIGO. *2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease.*

## Privacy and security

The static browser interface performs calculations locally and does not send inputs to a server. The optional Python compatibility layer contains a limited regular-expression identifier screen; it is not a de-identification system and does not establish HIPAA compliance. The in-memory audit chain uses HMAC-SHA256 and a process-random key unless `AUDIT_SECRET_KEY` is explicitly supplied.

## Technology

Python, Pydantic, optional FastAPI/Uvicorn, and dependency-free HTML/CSS/JavaScript. The static interface is intended for current evergreen desktop and mobile browsers.

## License

MIT. See [LICENSE](LICENSE).
