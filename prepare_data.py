"""Build compact, reproducible data from the supplied SPARCS CSV or ZIP."""
from pathlib import Path
import sys, zipfile, json
import pandas as pd
COLUMNS=['Hospital Service Area','Hospital County','Facility Name','Age Group','Gender','Race','Ethnicity','Length of Stay','Type of Admission','Patient Disposition','Discharge Year','CCSR Diagnosis Code','CCSR Diagnosis Description','APR Severity of Illness Description','APR Risk of Mortality','Payment Typology 1','Emergency Department Indicator','Total Charges','Total Costs']
def clean(df):
    df=df.copy()
    raw=df['Length of Stay'].astype('string').str.strip()
    df['Stay Capped']=raw.str.contains(r'\+',na=False)
    df['Length of Stay']=pd.to_numeric(raw.str.replace('+','',regex=False),errors='coerce')
    for c in ['Total Charges','Total Costs']:
        df[c]=pd.to_numeric(df[c].astype('string').str.replace(r'[$,]','',regex=True),errors='coerce')
        df.loc[df[c]<0,c]=float('nan')
    for c in COLUMNS:
        if c not in ['Length of Stay','Total Charges','Total Costs','Discharge Year']:
            df[c]=df[c].astype('string').str.strip().fillna('Unknown').replace('','Unknown')
    df=df[df['Length of Stay'].notna() & (df['Length of Stay']>=0)].copy()
    return df
if __name__=='__main__':
    source=Path(sys.argv[1]); out=Path(__file__).parent/'data';out.mkdir(exist_ok=True)
    handle=source
    if source.suffix=='.zip':
        archive=zipfile.ZipFile(source);handle=archive.open(next(n for n in archive.namelist() if n.endswith('.csv')))
    frames=[]; original=0
    for chunk in pd.read_csv(handle,usecols=COLUMNS,dtype='string',chunksize=150000):
        original+=len(chunk);frames.append(clean(chunk))
    d=pd.concat(frames,ignore_index=True)
    for c in d.select_dtypes(include=['string']).columns:d[c]=d[c].astype('category')
    d.to_parquet(out/'hospital.parquet',index=False,compression='zstd')
    stats={'source_rows':original,'retained_rows':len(d),'excluded_invalid_stays':original-len(d),'capped_stays':int(d['Stay Capped'].sum()),'missing_charges':int(d['Total Charges'].isna().sum()),'missing_costs':int(d['Total Costs'].isna().sum()),'facilities':int(d['Facility Name'].nunique()),'mean_stay':float(d['Length of Stay'].mean()),'mean_charges':float(d['Total Charges'].mean()),'source_file':source.name}
    (out/'quality.json').write_text(json.dumps(stats,indent=2));print(stats)
