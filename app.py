from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

ROOT=Path(__file__).parent
st.set_page_config(page_title='MediScope | Hospital Intelligence',page_icon='✚',layout='wide')
st.markdown('''<style>
.block-container{padding-top:2rem;max-width:1500px}h1,h2,h3{letter-spacing:-.035em}h1{font-size:2.7rem!important} [data-testid="stMetric"]{background:white;border:1px solid #dce5ed;border-radius:14px;padding:18px 20px} [data-testid="stMetricLabel"]{color:#64778b} [data-testid="stMetricValue"]{color:#123f57;font-size:1.9rem} .eyebrow{color:#087f8c;font-size:.8rem;font-weight:700;letter-spacing:.16em}.intro{color:#60758a;font-size:1.05rem;max-width:850px}.banner{background:#123f57;color:white;border-radius:18px;padding:24px 30px;margin-bottom:24px}.banner p{color:#cfdee8;margin:0}.banner h3{color:white;margin:0 0 8px} [data-testid="stSidebar"]{border-right:1px solid #dce5ed} .stPlotlyChart{border:1px solid #e1e8f0;border-radius:14px;overflow:hidden}div[data-testid="stTabs"] button{font-weight:600}footer{visibility:hidden}
</style>''',unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stAppViewContainer"]{background:radial-gradient(ellipse at top right,#e4f5f2 0,transparent 45%),#f3f6fb}
.banner{background:linear-gradient(120deg,#102f48,#146476);box-shadow:0 12px 30px #123f5715}
[data-testid="stMetric"]{border-top:4px solid #20b8a5;box-shadow:0 8px 22px #18324b08}
[data-testid="stTabs"] [role="tablist"]{background:#fff;padding:8px;border-radius:14px;gap:6px}
[data-testid="stTabs"] [aria-selected="true"]{background:#e1f5f0;border-radius:9px;color:#096b65}
.welcome-art{background:linear-gradient(145deg,#12334f,#087f8c);border-radius:28px;padding:50px 36px;color:white;min-height:370px}
.welcome-art h2{color:white;font-size:2.3rem}.welcome-art p{color:#cce8e5}.symbol{font-size:80px;line-height:1.4}.feature{background:#ffffff18;border:1px solid #ffffff30;border-radius:14px;padding:14px;margin-top:14px}
</style>""",unsafe_allow_html=True)
if not st.session_state.get('entered',False):
    st.markdown('<div class="eyebrow">✚ MEDISCOPE · HOSPITAL INTELLIGENCE</div>',unsafe_allow_html=True)
    st.write('')
    left,right=st.columns([1.1,1],gap='large')
    with left:
        st.markdown('<div class="welcome-art"><div class="symbol">🏥 🩺</div><h2>See the story<br>behind every stay.</h2><p>Your workspace for exploring New York hospital care.</p><div class="feature">📊 Interactive comparisons &nbsp; · &nbsp; 🔎 Explore your data</div><div class="feature">⏱️ Length of stay &nbsp; · &nbsp; 💳 Charges and payment</div></div>',unsafe_allow_html=True)
    with right:
        st.title('Welcome to MediScope')
        st.write('Make this workspace yours, then explore the dashboard.')
        with st.form('welcome'):
            name=st.text_input('Your name',max_chars=50,placeholder='Enter your first name')
            role=st.selectbox('I am exploring as a…',['Student / researcher','Hospital administrator','Operations analyst','Other'])
            submitted=st.form_submit_button('Continue →',type='primary',width='stretch')
        st.caption('Your name is used only for this session. No account is created.')
        if submitted:
            if not name.strip():st.error('Please enter your name to continue.')
            else:
                st.session_state.update(entered=True,visitor=name.strip(),role=role)
                st.rerun()
    st.stop()
COLORS=['#087f8c','#39a9a1','#6c83b5','#dfaa53','#a275a8','#536e86']
@st.cache_data(show_spinner='Loading hospital records…')
def load():
    return pd.read_parquet(ROOT/'data/hospital.parquet')
try:
    data=load();quality=json.loads((ROOT/'data/quality.json').read_text())
except (OSError,ValueError,ImportError) as e:
    st.error('The bundled data could not be loaded. Extract the complete project and install requirements.txt. See README.md for data preparation instructions.');st.stop()

def reset():
    for k in list(st.session_state):
        if k.startswith('filter_'): del st.session_state[k]
with st.sidebar:
    st.markdown('## ✚ MediScope')
    st.caption('HOSPITAL INTELLIGENCE · 2021')
    st.divider();st.markdown('### Explore your cohort')
    st.caption('Leave a selection empty to include all values.')
    selections={}
    option_mask=pd.Series(True,index=data.index)
    filter_columns=['Hospital Service Area','Hospital County','Facility Name','Age Group','Gender','APR Severity of Illness Description','Payment Typology 1','CCSR Diagnosis Description']
    def clear_following(column):
        for following in filter_columns[filter_columns.index(column)+1:]:
            st.session_state.pop('filter_'+following,None)
    for c,label in [('Hospital Service Area','Service area'),('Hospital County','County'),('Facility Name','Hospital'),('Age Group','Age group'),('Gender','Gender'),('APR Severity of Illness Description','Severity'),('Payment Typology 1','Primary payment'),('CCSR Diagnosis Description','Diagnosis')]:
        options=sorted(data.loc[option_mask,c].unique().tolist())
        selections[c]=st.multiselect(label,options,key='filter_'+c,on_change=clear_following,args=(c,))
        if selections[c]:option_mask &= data[c].isin(selections[c])
    stay=st.slider('Recorded stay (days)',0,120,(0,120),key='filter_stay')
    with st.expander('⚙️ Advanced comparison settings'):
        minimum=st.select_slider('Minimum records per comparison group',options=[1,10,30,50,100],value=1,key='filter_minimum')
    st.button('Reset filters',on_click=reset,width='stretch')
    st.divider();st.caption('SPARCS · New York State\n\nDischarge records, not unique patients.')
mask=data['Length of Stay'].between(*stay)
for c,values in selections.items():
    if values:mask &= data[c].isin(values)
d=data.loc[mask]
st.markdown('<div class="eyebrow">MEDISCOPE / INPATIENT ANALYTICS</div>',unsafe_allow_html=True)
st.title('🏥 Your hospital overview')
st.caption('Welcome, '+st.session_state.get('visitor','')+' 👋')

st.caption(f'2021 discharge year  •  {len(d):,} of {len(data):,} records selected  •  Full dataset included')
if d.empty:
    st.warning('No records match these filters. Broaden your selections or use Reset filters.');st.stop()
a,b,c,e=st.columns(4)
a.metric('📋 Discharge records',f'{len(d):,}')
b.metric('⏱️ Average recorded stay',f'{d["Length of Stay"].mean():.1f} days')
c.metric('💳 Average charges',f'${d["Total Charges"].mean():,.0f}' if d['Total Charges'].notna().any() else 'Unavailable')
e.metric('🏥 Hospitals represented',f'{d["Facility Name"].nunique():,}')
st.caption('Charges are billed amounts, not actual costs or payments. Recorded stays of 120+ are represented as 120 days; averages are lower-bound estimates.')

def chart(fig,key):
    fig.update_layout(template='plotly_white',font=dict(family='Arial',color='#28455c'),colorway=COLORS,margin=dict(l=25,r=25,t=55,b=30),paper_bgcolor='white',plot_bgcolor='white',height=fig.layout.height or 420,title_font_size=17,legend_title_text='')
    st.plotly_chart(fig,width='stretch',key=key,config={'displaylogo':False})
def summary(col):
    return d.groupby(col,observed=True).agg(Records=('Length of Stay','size'),Average_stay=('Length of Stay','mean'),Average_charges=('Total Charges','mean'),Average_costs=('Total Costs','mean')).reset_index()
def eligible(col):
    return summary(col).query('Records >= @minimum')

overview,clinical,finance,explorer,about=st.tabs(['📊 Overview','🩺 Stays & facilities','💳 Charges & payment','🔎 Data explorer','ℹ️ Methodology'])
with overview:
    st.markdown('<div class="banner"><h3>📊 Care patterns at a glance</h3><p>Choose a hospital or patient group to explore its stays and charges.</p></div>',unsafe_allow_html=True)
    l,r=st.columns(2)
    with l:
        s=eligible('CCSR Diagnosis Description').nlargest(10,'Average_stay').sort_values('Average_stay')
        if len(s):
            fig=px.bar(s,x='Average_stay',y='CCSR Diagnosis Description',orientation='h',hover_data=['Records'],title='Which diagnoses have the longest stays?',labels={'Average_stay':'Average recorded stay (days)','CCSR Diagnosis Description':'Diagnosis'},color_discrete_sequence=COLORS)
            fig.update_yaxes(tickfont_size=10);chart(fig,'diagnoses')
            top=s.iloc[-1];st.caption(f'{top["CCSR Diagnosis Description"]}: {top.Average_stay:.1f} days across {int(top.Records):,} records. Minimum group size: {minimum}.')
        else:st.info('No diagnosis meets the minimum group size.')
    with r:
        counts=d['Length of Stay'].value_counts().sort_index().rename_axis('Recorded stay').reset_index(name='Records')
        chart(px.bar(counts,x='Recorded stay',y='Records',title='How are recorded stays distributed?',labels={'Recorded stay':'Recorded stay (days)'},color_discrete_sequence=COLORS),'stayhist')
        st.caption(f'Median stay: {d["Length of Stay"].median():.0f} days. {d["Stay Capped"].sum():,} selected stays are recorded as 120+ days.')
with clinical:
    st.subheader('Length of stay and hospital utilisation')
    l,r=st.columns(2)
    with l:
        s=eligible('Facility Name').nlargest(15,'Records').sort_values('Records')
        chart(px.bar(s,x='Records',y='Facility Name',orientation='h',title='Highest-volume facilities in this cohort',hover_data=['Average_stay'],labels={'Facility Name':'Facility'},color_discrete_sequence=COLORS),'facilities')
    with r:
        s=eligible('Hospital County').nlargest(15,'Average_stay').sort_values('Average_stay')
        chart(px.bar(s,x='Average_stay',y='Hospital County',orientation='h',title='Counties with longer average stays',hover_data=['Records'],labels={'Average_stay':'Average recorded stay (days)','Hospital County':'County'},color_discrete_sequence=COLORS),'counties')
    top=d['Facility Name'].value_counts().head(15).index
    h=d[d['Facility Name'].isin(top)].groupby(['Facility Name','Hospital County'],observed=True)['Length of Stay'].agg(['mean','size']).reset_index()
    h=h[h['size']>=minimum]
    if len(h):
        matrix=h.pivot_table(index='Facility Name',columns='Hospital County',values='mean',observed=True)
        fig=px.imshow(matrix,aspect='auto',color_continuous_scale='Teal',title='Average recorded stay by facility and county',labels={'color':'Days','x':'County','y':'Facility'})
        fig.update_layout(height=550);chart(fig,'heatmap')
        st.caption('Shows the 15 highest-volume selected facilities. Blank cells indicate absent or insufficient records. A facility generally belongs to one county; blank combinations are expected.')
    else:st.info('No facility/county groups meet the minimum record count.')
    counties=eligible('Hospital County')
    if len(counties):
        row=counties.loc[counties.Average_stay.idxmax()]
        st.info(f"Among eligible counties, {row['Hospital County']} has the longest average recorded stay: {row.Average_stay:.1f} days ({int(row.Records):,} discharges). Review diagnoses and severity before considering operational changes.")
with finance:
    st.subheader('Charges, costs and primary payment')
    st.caption('All financial figures are in US dollars. Missing or invalid financial values are excluded only from financial calculations.')
    l,r=st.columns(2)
    order=['Minor','Moderate','Major','Extreme','Unknown']
    with l:
        # Exact quantiles: no downsampling of financial distributions.
        fig=go.Figure()
        for severity in order:
            values=d.loc[d['APR Severity of Illness Description']==severity,'Total Charges'].dropna()
            if not len(values):continue
            q1,median,q3=values.quantile([.25,.5,.75]);iqr=q3-q1
            inside=values[values.between(q1-1.5*iqr,q3+1.5*iqr)]
            fig.add_trace(go.Box(name=severity,q1=[q1],median=[median],q3=[q3],lowerfence=[inside.min()],upperfence=[inside.max()],boxpoints=False))
        fig.update_layout(title='How do charges vary by severity?',yaxis_title='Total charges (USD)',showlegend=False);chart(fig,'severity')
        st.caption('Boxes use exact cohort quartiles. Whiskers end at observed values within 1.5 IQR; outlier dots are hidden, but valid high charges remain in calculations.')
    with r:
        s=eligible('Age Group')
        chart(px.bar(s,x='Age Group',y='Average_charges',title='Average charges by age group',hover_data=['Records'],labels={'Average_charges':'Average charges (USD)'},category_orders={'Age Group':['0 to 17','18 to 29','30 to 49','50 to 69','70 or Older']},color_discrete_sequence=COLORS),'age')
    l,r=st.columns(2)
    with l:
        s=summary('Payment Typology 1')
        chart(px.pie(s,names='Payment Typology 1',values='Records',hole=.6,title='Discharge share by primary payment',color_discrete_sequence=COLORS),'payment')
    with r:
        s=eligible('Payment Typology 1').sort_values('Average_charges')
        chart(px.bar(s,x='Average_charges',y='Payment Typology 1',orientation='h',title='Average charges by primary payment',hover_data=['Records','Average_costs'],labels={'Average_charges':'Average charges (USD)','Payment Typology 1':'Primary payment'},color_discrete_sequence=COLORS),'billing')
    st.markdown('### Financial comparison')
    s=summary('APR Severity of Illness Description')
    st.dataframe(s.rename(columns={'APR Severity of Illness Description':'Severity','Average_stay':'Average stay (days)','Average_charges':'Average charges ($)','Average_costs':'Average costs ($)'}),hide_index=True,width='stretch')
    st.caption('Payment comparisons do not measure reimbursement, profitability or the causal effect of insurance.')
    st.markdown('### Findings for the selected cohort')
    ages=eligible('Age Group').dropna(subset=['Average_charges'])
    payments=eligible('Payment Typology 1').dropna(subset=['Average_charges'])
    severity=eligible('APR Severity of Illness Description').dropna(subset=['Average_charges'])
    if len(ages):
        row=ages.loc[ages.Average_charges.idxmax()]
        st.write(f"Highest average charges by age: **{row['Age Group']}**, ${row.Average_charges:,.0f} across {int(row.Records):,} discharges.")
    if len(severity):
        row=severity.loc[severity.Average_charges.idxmax()]
        st.write(f"Highest average charges by severity: **{row['APR Severity of Illness Description']}**, ${row.Average_charges:,.0f} across {int(row.Records):,} discharges.")
    if len(payments):
        row=payments.loc[payments.Average_charges.idxmax()]
        st.write(f"Highest average charges by primary payment: **{row['Payment Typology 1']}**, ${row.Average_charges:,.0f} across {int(row.Records):,} discharges. Investigate diagnosis and severity mix before attributing this difference to payment type.")
with explorer:
    st.subheader('Explore the underlying records')
    st.caption('Preview and downloads are limited to 10,000 rows per page to keep the app responsive. All charts use the full filtered cohort.')
    page=st.number_input('Data page',min_value=1,max_value=max(1,int(np.ceil(len(d)/10000))),value=1,step=1)
    preview=d.iloc[(page-1)*10000:page*10000]
    st.dataframe(preview,hide_index=True,width='stretch',height=420)
    st.download_button('Download this data page (CSV)',preview.to_csv(index=False).encode(),f'mediscope_records_page_{page}.csv','text/csv')
    group=st.selectbox('Summarise and export by',['Hospital County','Facility Name','CCSR Diagnosis Description','Age Group','APR Severity of Illness Description','Payment Typology 1'])
    grouped=summary(group)
    st.dataframe(grouped,hide_index=True,width='stretch')
    st.download_button('Download complete filtered summary',grouped.to_csv(index=False).encode(),'mediscope_summary.csv','text/csv')
with about:
    st.subheader('Purpose and intended use')
    st.write('MediScope helps hospital administrators and operations teams compare inpatient utilisation, length of stay and financial patterns. It is a descriptive educational dashboard for Mathematics for AI-II, Scenario 2.')
    st.markdown('### Dataset and scope')
    st.write('Source: user-supplied New York State SPARCS de-identified hospital inpatient discharge dataset, discharge year 2021; filename dated 2023-10-12. One row represents a discharge, not a unique patient. No synthetic records or sampling are used.')
    st.markdown('### Cleaning and quality checks')
    st.json(quality)
    st.write('Currency commas and dollar symbols are removed before numeric conversion. Negative or unparseable financial values become missing. Invalid or negative stays are excluded. Missing categorical fields become Unknown. Existing readable CCSR diagnosis descriptions are used; no invented code mappings are added. Only relevant analysis columns are retained; birth weight and other unused fields are omitted.')
    st.write('Identical discharge rows are retained because no unique encounter identifier is supplied; dropping them could remove distinct admissions. Valid extreme charges and stays are retained. Zero-day stays remain valid.')
    st.markdown('### Calculations')
    st.write('Average stay = sum of valid recorded stay days / discharge records. Financial averages use non-missing values of the relevant financial column. Discharge share = payment-group records / filtered discharge records. Comparative bars and the heatmap respect the selected minimum group size; overall distributions and totals include every selected record.')
    st.markdown('### Limitations')
    st.write('Stays marked 120+ are treated as 120, so mean stays underestimate their true duration. There are no exact admission/discharge dates or stable patient identifiers: monthly trends and readmission rates cannot be calculated. Facility comparisons are not adjusted for diagnosis, severity or patient mix. Charges are not costs or payments, and cost differences do not establish quality of care. Findings apply to these 2021 records and are not current hospital performance ratings.')
    st.markdown('### Research and technical references')
    st.markdown('- [New York State SPARCS information](https://www.health.ny.gov/statistics/sparcs/)\n- [AHRQ CCSR diagnosis categories](https://hcup-us.ahrq.gov/toolssoftware/ccsr/dxccsr.jsp)\n- [Streamlit documentation](https://docs.streamlit.io/)\n- [Plotly Python documentation](https://plotly.com/python/)')
    st.caption('References are provided for further reading; dataset calculations use the supplied file. No live external data connection is required.')
st.divider();st.caption('MediScope  •  New York inpatient discharges, 2021  •  Educational analytics')
