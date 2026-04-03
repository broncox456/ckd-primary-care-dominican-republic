# Peravia CKD Epidemiology

**Real-world clinical and sociodemographic analysis of chronic kidney disease in primary care in the Dominican Republic**

## Overview

This project analyzes real-world data collected during a chronic kidney disease (CKD) screening initiative conducted in Peravia, Dominican Republic.

The repository integrates two complementary datasets into a reproducible epidemiological workflow:

- a **clinical screening dataset** from primary care UNAPS consultations
- a **sociodemographic dataset** capturing social determinants of health in a linked patient subset

Rather than forcing a simplistic merge, the workflow was designed to reflect the reality of field-collected healthcare data, including inconsistencies across instruments, and to handle them using transparent quality-control procedures.

## Clinical relevance

CKD is often underdiagnosed in low-resource settings, where early detection, timely nephrology referral, and long-term follow-up remain limited.

This project is clinically relevant because it explores:

- CKD burden in primary care
- distribution of hypertension and diabetes
- geographic concentration of screened patients
- social barriers affecting access to care
- nephrology follow-up patterns in a linked subcohort

The goal was not only to describe the data, but to build a structured and reproducible healthcare analytics workflow grounded in nephrology and population health.

## Study design

### Main clinical cohort
- **Source:** UNAPS primary care screening dataset
- **Sample size:** 400 patients
- **Focus:** clinical characterization and CKD-related variables

### Nested sociodemographic subcohort
- **Source:** structured social survey dataset
- **Sample size:** 50 linked patients
- **Purpose:** contextual analysis of access to care, social barriers, and healthcare utilization

## Data integration strategy

The sociodemographic dataset was linked to the clinical dataset through a derived numeric identifier extracted from the original UNAPS patient ID.

Because the datasets were collected independently, overlapping variables were validated after linkage. Inconsistencies were detected in some shared fields, especially age.

To preserve methodological integrity:

- original data were not overwritten
- quality-control flags were introduced
- the social analysis was restricted to a filtered subset when necessary
- all major linkage decisions were documented

This approach prioritizes transparency over artificial data correction.

## Workflow

The repository follows a reproducible pipeline:

1. **Data audit**
   - file inspection
   - sheet detection
   - structure review
   - ID overlap exploration

2. **Cleaning**
   - column normalization
   - text standardization
   - categorical harmonization
   - numeric conversion
   - ID standardization

3. **Subcohort construction**
   - ID transformation
   - linkage validation
   - overlap review

4. **Quality control**
   - detection of age discrepancies
   - inconsistency flagging
   - creation of a filtered analytical subset

5. **Descriptive analysis**
   - prevalence summaries
   - CKD classification distribution
   - sex and locality distribution
   - sociodemographic summaries

6. **Figure generation**
   - age distribution
   - CKD classification
   - hypertension and diabetes frequency
   - top localities
   - insurance access
   - economic barriers
   - educational level

## Key findings

### Main clinical cohort (n = 400)
- **Mean age:** 51.6 years
- **Female proportion:** 57.3%
- **Hypertension prevalence:** 29.5%
- **Diabetes prevalence:** 26.0%

### CKD burden
- **Patients with CKD:** 35.5%

Distribution:
- Normal function: 64.5%
- KDIGO 1–2: 12.0%
- KDIGO 3a–3b: 10.0%
- KDIGO 4: 4.5%
- KDIGO 5: 9.0%

### Geographic concentration
Highest patient concentration was observed in:
- Baní (n = 108)
- Nizao (n = 53)
- Matanzas (n = 41)

### Sociodemographic subcohort
- **Successfully linked patients:** 50
- **Quality-filtered analytical subset:** 14

Findings from the filtered social subset:
- **Insurance access:** 64.3%
- **Mean nephrology visits per year:** 2.14

## Repository structure

```text
peravia-ckd-epidemiology/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── 01_data_audit.py
│   ├── 02_clean_unaps.py
│   ├── 03_clean_sociodemographic.py
│   ├── 04_build_subcohort.py
│   ├── 05_descriptive_analysis.py
│   └── 06_generate_figures.py
├── results/
│   ├── tables/
│   ├── figures/
│   └── reports/
├── docs/
├── logs/
├── README.md
└── requirements.txt

```text

Main outputs

Tables
results/tables/clinical_summary.csv
results/tables/ckd_distribution.csv
results/tables/sex_distribution.csv
results/tables/locality_distribution.csv
results/tables/subcohort_quality_summary.csv
results/tables/subcohort_summary_clean.csv
results/tables/linked_subcohort_preview.csv
Reports
results/reports/data_audit_report.txt
results/reports/subcohort_build_report.txt
Figures
results/figures/age_distribution_main_cohort.png
results/figures/ckd_classification_distribution.png
results/figures/diabetes_status_main_cohort.png
results/figures/hypertension_status_main_cohort.png
results/figures/top_localities_main_cohort.png
results/figures/insurance_access_subcohort.png
results/figures/economic_barriers_subcohort.png
results/figures/educational_level_subcohort.png
Tools and environment
Python for data audit, cleaning, linkage, analysis, and figure generation
PowerShell for execution and logging
Excel files as source datasets

Main libraries:

pandas
numpy
matplotlib
openpyxl
Methodological note

This project intentionally preserves real-world data imperfections.

Instead of forcing artificial consistency between independently collected datasets, the analysis:

identifies inconsistencies
documents them
controls for them analytically

This increases the credibility of the repository and better reflects how real healthcare data behave outside ideal research settings.

Limitations
Small effective sample size in the filtered social subset
Inconsistencies across independently collected datasets
Descriptive and exploratory design
No inferential or predictive modeling included in the current version

These limitations are acknowledged and handled explicitly within the workflow.

Final assessment

This repository represents a serious healthcare data science project with clinical relevance, real-world complexity, and a reproducible structure. It is suitable for GitHub portfolio use after final cleanup of unnecessary files.

Cristian Arias, MD
Nephrologist | Internal Medicine Specialist
Healthcare Data Science & Bioinformatics