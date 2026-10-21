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

## Updated interface

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

## GitHub and Streamlit deployment

Create a repository with the naming convention requested by your teacher, such as `IADAI202-1000330-Phreya-Shethwala`. Upload the extracted contents, preserving the `data` and `.streamlit` folders. The ZIP is a delivery package; the repository must contain its extracted files. The included Parquet file is below GitHub's 100 MB per-file limit. Do not upload `.venv`, caches or the original 832 MB CSV.

In Streamlit Community Cloud, connect the GitHub account, select the repository and branch, use `app.py` as the entry point, and choose Python 3.13 in advanced settings if available. Deploy and open the app. Test filters and downloads on the live deployment.

**Live app URL:** Add the actual URL here after deployment. This package has not been published to a user account.

**Screenshots:** After launching, capture Overview, Stays & facilities and Charges & payment. Save them under `screenshots/` and add their actual Markdown image links here before submission. Screenshots are not bundled because browser installation was unavailable in the build environment.

## References

- Dataset: supplied Hospital_Inpatient_Discharges__SPARCS_De-Identified___2021_20231012.zip.
- New York State SPARCS: https://www.health.ny.gov/statistics/sparcs/
- AHRQ CCSR: https://hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp
- Streamlit: https://docs.streamlit.io/
- Plotly: https://plotly.com/python/

These are background/technical reference links; no external research findings have been fabricated. Add your own short, cited domain research for the problem-understanding criterion.
