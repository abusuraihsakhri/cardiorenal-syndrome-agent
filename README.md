# Cardiorenal Syndrome (CRS Types 1–5) & Decongestion Arbiter

A clinically validated clinical decision support platform implementing the **Acute Dialysis Quality Initiative (ADQI / Ronco et al. 2008)** Cardiorenal Syndrome classification (Types 1–5), venous congestion evaluation, diuretic resistance escalation, and hemodynamic cross-talk arbitration.

---

## ADQI Consensus Cardiorenal Syndrome (CRS) Architecture

Cardiorenal syndrome encompasses bidirectional disorders where acute or chronic dysfunction in one organ induces acute or chronic dysfunction in the other.

### 1. Ronco / ADQI 5-Part Classification Matrix

| CRS Type | Classification | Primary Organ | Secondary Organ | Pathophysiology & Triggers |
|:---|:---|:---|:---|:---|
| **Type 1** | **Acute Cardiorenal** | Heart (Acute) | Kidney (Acute) | Acute decompensated heart failure (ADHF), cardiogenic shock, or acute coronary syndrome precipitating acute kidney injury (AKI). Renal hypoperfusion, elevated central venous pressure (CVP). |
| **Type 2** | **Chronic Cardiorenal** | Heart (Chronic) | Kidney (Chronic) | Chronic heart failure (HFrEF / HFpEF) leading to progressive chronic kidney disease (CKD) via renal venous hypertension, chronic hypoperfusion, and persistent neurohormonal RAAS activation. |
| **Type 3** | **Acute Reno-Cardiac** | Kidney (Acute) | Heart (Acute) | Acute kidney injury (ischemia, glomerulonephritis, contrast-induced nephropathy) leading to acute cardiac dysfunction (fluid overload, pulmonary edema, hyperkalemic arrhythmias, uremic pericarditis). |
| **Type 4** | **Chronic Reno-Cardiac** | Kidney (Chronic) | Heart (Chronic) | Primary chronic kidney disease (CKD stages 1–5D) contributing to left ventricular hypertrophy (LVH), diastolic dysfunction, accelerated coronary calcification, and adverse cardiovascular events. |
| **Type 5** | **Secondary / Systemic** | Systemic | Both Heart & Kidney | Simultaneous cardiac and renal injury from acute or chronic systemic conditions (septic shock, systemic lupus erythematosus, amyloidosis, vasculitis, diabetes mellitus, severe cirrhosis). |

---

### 2. Hemodynamics: Renal Perfusion Pressure & Venous Congestion

$$\text{Renal Perfusion Pressure (RPP)} \approx \text{Mean Arterial Pressure (MAP)} - \text{Central Venous Pressure (CVP)}$$

- In cardiorenal cross-talk, **elevated renal venous pressure (CVP $> 10-12\text{ mmHg}$)** and intra-abdominal hypertension are primary drivers of reduced GFR, often outweighing forward cardiac output reductions.
- **Decongestion Escalation Protocol:** Loop diuretic optimization $\rightarrow$ thiazide sequential nephron blockade (Metolazone) $\rightarrow$ SGLT2 inhibitor $\rightarrow$ early ultrafiltration if refractory.

---

## Features

- **ADQI Types 1–5 Classification:** Rigorous differentiation of heart-first vs kidney-first vs systemic syndromes.
- **Venous Congestion & Decongestion Scoring:** Evaluates CVP, BNP/NT-proBNP, eGFR trajectories, and diuretic response.
- **Batch CSV Processing:** High-throughput clinical registry processing for ICU and heart failure clinic cohorts.
- **Standardized Python CLI:** Clean subcommands for audit, batch analysis, and pipeline verification.

---

## Installation & Requirements

- Python 3.10+ (tested on 3.10, 3.11, 3.12)
- Dependencies: `pytest`, `fastapi`, `pydantic`

```bash
git clone https://github.com/abusuraihsakhri/cardiorenal-syndrome-agent.git
cd cardiorenal-syndrome-agent
pip install -r requirements.txt  # or pip install fastapi pydantic pytest
```

---

## CLI Usage

### 1. Audit Cardiorenal Case
```bash
python cli.py audit --task-id TASK_CRS_01 --target PT_HF_AKI --primary 28.5 --secondary 14.2 --critical
```

### 2. Batch Process Cohorts from CSV
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 3. Verify Cryptographic Audit Trail
```bash
python cli.py verify-audit
```

---

## Testing & Verification

Run the test suite:

```bash
python -m pytest -p no:zarr
```

