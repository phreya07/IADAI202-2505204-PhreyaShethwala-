# MediScope Hospital Inpatient Dashboard

MediScope is a Streamlit dashboard built for the Mathematics for AI-II summative assessment, Scenario 2. It helps hospital administrators and operations managers explore how diagnoses, severity, age, facility and primary payment relate to recorded length of stay and financial measures.

## Why this app was built

Large discharge files are difficult to interpret by reading individual rows. This app turns the supplied SPARCS data into filtered comparisons, summary metrics and interactive charts that can support questions about hospital utilisation and financial patterns. The results describe associations; they are not clinical advice or hospital quality rankings.

## Included dataset

The complete user-supplied 2021 New York State SPARCS de-identified dataset is included as `data/hospital.parquet`: 2,101,588 discharge records and 205 facility names. There is no sampling or synthetic data. The original CSV was approximately 832 MB; relevant columns are stored in compressed Parquet to keep deployment practical. One record is a discharge, not necessarily a distinct patient. No external download, API key or database is required.

## Run on Windows

Install 64-bit Python 3.13. Extract this ZIP first, open the extracted MediScope folder in VS Code, and open its terminal. Run each command separately:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL shown in the terminal, usually http://localhost:8501. Keep the terminal open. Press Ctrl+C there to stop the app. No PowerShell activation command or execution-policy change is necessary.

For later runs, only the final command is needed. If you see a missing-data message, verify that `data/hospital.parquet` and `data/quality.json` are inside the extracted project folder.

## Other systems

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Research questions

1. Which diagnoses have the longest average recorded stays?
2. Which age groups have the highest average charges?
3. How do hospital charges vary by severity?
4. Which facilities and counties have longer average stays?
5. How do primary payment groups differ in volume and average charges?

## Background research and design decisions

New York State describes SPARCS as a discharge-data system containing information on patient characteristics, diagnoses, treatments, services and charges [1, 2]. This makes it suitable for comparing groups of hospital stays. I chose a dashboard so users can narrow these records to a hospital, county or patient group instead of searching through the original file.

AHRQ explains that CCSR groups diagnosis codes into clinically meaningful categories and supports analysis of healthcare utilisation, costs and outcomes [3]. This supports comparing average stays by diagnosis. The app uses the diagnosis descriptions already supplied in the dataset; it does not apply a new version of the CCSR mapping.

AHRQ also distinguishes hospital charges, the amounts billed, from costs, the expenses of providing services [4]. For this reason, the dashboard labels charges and costs separately. Neither is presented as the amount paid by a patient or insurer.

My interpretation is that longer stays and higher discharge volumes can help administrators identify areas for further capacity review. These comparisons do not show that a hospital is inefficient: patient severity, diagnoses and specialist services must also be considered.

## Research questions and findings

The following results were calculated from all 2,101,588 supplied discharge records, with no demographic or hospital filters. For ranked diagnosis, county and facility comparisons, I used a minimum of **30 records per group** to reduce the influence of very small groups. This is a practical display threshold, not a statistical guarantee. Set the app's advanced minimum-group setting to 30 to reproduce the diagnosis and county rankings. The app defaults to 1 so small filtered selections remain visible.

### 1. Which diagnoses are associated with the longest average stays?

Among diagnosis groups with at least 30 records, **spinal cord injury, subsequent encounter** had the highest average recorded stay at **27.62 days across 176 discharges**. Short gestation, low birth weight and fetal growth retardation followed at **27.47 days across 307 discharges**, then respiratory distress syndrome at **26.19 days across 311 discharges**.

This identifies diagnosis groups that may need closer review of bed use and discharge planning. It does not establish the medical reason for longer stays. The Overview diagnosis chart shows the comparison, including group record counts on hover.

### 2. Which age groups have the highest average hospital charges?

| Age group | Discharge records | Average charges per discharge USD |
|---|---:|---:|
| 50 to 69 | 584,480 | $90,103.61 |
| 70 or Older | 619,644 | $87,031.25 |
| 30 to 49 | 415,681 | $58,971.44 |
| 18 to 29 | 192,051 | $47,658.69 |
| 0 to 17 | 289,732 | $47,628.26 |

The **50 to 69** group had the highest average charges. This can guide further financial analysis of the services used by different age groups. It does not mean age itself causes higher charges; diagnoses, procedures and severity may differ. The age comparison appears in Charges & payment.

### 3. How do charges vary across severity levels?

| Recorded severity | Discharge records | Average charges per discharge USD |
|---|---:|---:|
| Minor | 638,227 | $36,690.95 |
| Moderate | 760,535 | $54,647.65 |
| Major | 499,474 | $90,426.68 |
| Extreme | 200,802 | $217,898.27 |
| Unknown | 2,550 | $62,351.05 |

Average charges increased across the four named severity levels. Extreme-severity records had much higher average charges than minor-severity records. This supports looking at severity when reviewing financial differences between facilities. Unknown is a separate missing/unspecified category, not an additional severity level. The severity box plot shows the distribution, while the financial table reports means.

### 4. Which facilities and counties have longer average stays?

Among groups with at least 30 records, **Columbia County** had the highest average recorded stay at **7.40 days across 3,320 discharges**. Across all eligible facilities, **Blythedale Children's Hospital** had the highest average at **57.34 days across 389 discharges**, followed by **Henry J. Carter Specialty Hospital**, at **45.79 days across 524 discharges**.

These results suggest that facility type and case mix should be investigated before drawing operational conclusions. The comparison is not a ranking of hospital quality. In Stays & facilities, the county bar chart ranks average stays, the facility bar chart ranks discharge volume, and the heatmap compares stays for the 15 highest-volume selected facilities. To inspect a specialist facility outside that heatmap, select it in the Hospital filter or export a facility summary in Data explorer. The facility findings above come from the full facility summary, not the volume ranking.

### 5. How do primary payment groups differ in volume and average charges?

**Medicare** was the largest primary payment group, with **826,250 discharge records**, followed by **Medicaid**, with **646,300**. Their average charges were **$87,975.99** and **$62,511.64**, respectively. **Miscellaneous/Other** had the highest average charges at **$96,817.39**, across **22,526 discharges**.

The payment charts show the discharge share and average charges of each primary payment group. These patterns can help users investigate how patient mix differs across groups. They do not show insurer reimbursement, patient out-of-pocket spending or an effect caused by the payment type.

### Overall interpretation

The results show differences in recorded stays and billed charges across clinical, demographic, geographical and payment groups. Diagnosis and severity comparisons give useful context for interpreting facility results. The dashboard supports investigation; it does not explain the causes of those differences or recommend clinical treatment.

## Interface and user journey

A separate welcome screen asks for a first name and role before opening the dashboard. These values remain only in Streamlit session state. Filters cascade: selecting an upstream group clears downstream choices and offers only compatible values. The default minimum comparison count is one, so small selections remain visible. The research questions stay in this README rather than in the main dashboard.

## Features

- Consistent navy and teal healthcare theme with five tabs.
- Eight categorical filters, a stay range and minimum comparison-group size.
- Four summary cards that update with the selected cohort.
- Nine interactive visuals: diagnosis stays, stay distribution (one-day bins), facility volume, county stays, facility/county heatmap, severity box plots, age charges, payment share and payment charges.
- Hover details and built-in Plotly chart controls.
- Exact full-cohort severity quartiles instead of sampled box plots.
- Record browser with pagination and CSV exports; complete grouped-summary export.
- Clear no-results state and one-click filter reset.
- Cleaning statistics, formulas, limitations and reference links.

## Data preparation and integration

`prepare_data.py` reads the original ZIP/CSV in chunks with Pandas, retains the relevant columns, cleans them and writes a compact Parquet file plus a quality report. `app.py` loads this file with PyArrow, applies one shared cohort mask and uses Pandas aggregations to produce Plotly charts displayed by Streamlit. Streamlit caches the source data. No patient-identifying data is introduced.

Cleaning rules:

- Convert currency strings to numbers; negative/unparseable financial amounts become missing.
- Exclude missing, invalid or negative length-of-stay records; zero-day stays remain.
- Preserve `120+` as a cap flag and use 120 as the numeric lower bound.
- Strip whitespace and label missing categorical values Unknown.
- Use the supplied readable CCSR diagnosis descriptions.
- Retain repeated rows: no unique encounter key is supplied, so identical rows may be distinct discharges.
- Retain legitimate extreme values. Box plots hide outlier dots without deleting those records.
- Omit unused fields such as birth weight rather than trying to impute them.

To reproduce the included dataset:

```powershell
.\.venv\Scripts\python.exe prepare_data.py "C:\path\to\Hospital_Inpatient_Discharges__SPARCS_De-Identified___2021_20231012.zip"
```

## Formulas and interpretation

Average stay is total recorded days divided by discharge records. Financial averages exclude missing values of the relevant financial column. Payment share is group discharges divided by all filtered discharges. The minimum group size affects comparative bars and the heatmap; it does not change overall distributions or totals. Financial data are US dollars. Charges, costs and reimbursements are different concepts; actual payments are not available.

The overview starts at 5.7 average recorded days and about $73,305 average charges for all 2,101,588 records. These are descriptive baseline figures, not benchmarks for judging hospitals. More severe cases and different diagnosis mixes can change comparisons.

## Limitations

- Stays of 120+ are top-coded, so calculated average stays are lower-bound estimates.
- No stable patient identifiers or exact admission/discharge dates are supplied. Readmission rates, unique patient totals and monthly trends cannot be calculated.
- The file covers discharge year 2021, not present-day hospital conditions.
- Results are not adjusted for case mix and do not establish causation or quality of care.
- Primary payment is the recorded primary category, not necessarily all sources of payment.
- The facility/county heatmap is naturally sparse because facilities generally belong to one county.
- Raw exports are limited to 10,000 records per page to control memory use. Grouped exports include the complete filtered cohort.
- Runtime speed depends on the host. Initial dependency installation and data load need time and sufficient memory.

## Project files

- `app.py`: dashboard.
- `prepare_data.py`: reproducible cleaning pipeline.
- `requirements.txt`: tested dependency versions.
- `.streamlit/config.toml`: theme configuration.
- `data/hospital.parquet`: full prepared analysis data.
- `data/quality.json`: source and cleaning counts.
- `tests/test_app.py`: cleaning and Streamlit interaction tests.
- `test_results.txt`: results from the delivered version.
- `SUBMISSION_CHECKLIST.md`: final assessment checklist.

## Test

From the project root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests check full-data totals, chart count, filter totals against the data, reset, empty cohorts, a narrow stay range and cleaning edge cases. Automated checks do not guarantee every future browser, package or hosting environment will behave identically.

## GitHub repository

[Open the project repository](https://github.com/phreya07/IADAI202-2505204-PhreyaShethwala-)

## Deployment instructions

Create a repository with the naming convention requested by your teacher, named `IADAI202-2505204-PhreyaShethwala-`. Upload the extracted contents, preserving the `data` and `.streamlit` folders. The ZIP is a delivery package; the repository must contain its extracted files. The included Parquet file is below GitHub's 100 MB per-file limit. Do not upload `.venv`, caches or the original 832 MB CSV.

1. Open Streamlit Community Cloud and sign in with the GitHub account that can access the repository.
2. Choose Create app and select the repository `phreya07/IADAI202-2505204-PhreyaShethwala-`.
3. Set the branch to `main` and the main file path to `app.py` if the file is at the repository root. If files are inside a subfolder, use the actual relative path instead.
4. Select a Python version compatible with requirements.txt. Local instructions use Python 3.13; automated build checks were run under Python 3.12.
5. Deploy, allow dependency installation to finish, then open the live app.
6. Test the welcome form, single and combined filters, reset, each tab, data pages and CSV downloads.
7. Copy the actual live URL into the section below. If deployment fails, inspect the build logs rather than treating the source-code upload as successful deployment.

**Live app URL:** Add the actual URL here after deployment. Replace this line with the actual Streamlit Cloud address before submission; the GitHub address above is the source repository, not the dashboard link.

**Screenshots:** After launching, capture Overview, Stays & facilities and Charges & payment. Save them under `screenshots/` and add their actual Markdown image links here before submission. Include the welcome page and show at least one working filtered view. Use only screenshots of the finished app; the supplied rubric and error screenshots are not dashboard evidence.

## References

Background sources accessed 21 October 2026:

1. New York State Department of Health. [Statewide Planning and Research Cooperative System](https://www.health.ny.gov/statistics/sparcs/). Background on the discharge-data system.
2. New York State Health Data NY. [Hospital Inpatient Discharges SPARCS De-Identified 2021](https://health.data.ny.gov/Health/Hospital-Inpatient-Discharges-SPARCS-De-Identified/tg3i-cinn). Official dataset page. All reported calculations use the supplied 2023-10-12 CSV snapshot, which may differ from later revisions on the live page.
3. AHRQ HCUP. [Clinical Classifications Software Refined for ICD-10-CM Diagnoses](https://hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp). Diagnosis grouping and analytical uses.
4. AHRQ HCUP. [Cost-to-Charge Ratio for Inpatient Files](https://hcup-us.ahrq.gov/db/ccr/ip-ccr/ip-ccr.jsp). Explanation of billed charges versus costs. This conceptual distinction is used; HCUP ratios are not applied to SPARCS data.
5. Streamlit. [Prepare and deploy your app on Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app). Deployment reference.
6. Plotly. [Python graphing library](https://plotly.com/python/). Technical reference for the interactive visuals.

## Author and assessment

**Student:** Phreya Shethwala  
**CRS:** Artificial Intelligence  
**Course:** Mathematics for AI-II  
**Assessment:** Summative Assessment, Scenario 2, Hospital Inpatient Discharges Dashboard  
**School:** Udgam School for Children

streamlit- https://htjzvjudzwaqspnrpssw7w.streamlit.app/
