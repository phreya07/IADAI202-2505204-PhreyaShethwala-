"""Run from project root: python -m unittest discover -s tests -v"""
import unittest
from pathlib import Path
import pandas as pd
from streamlit.testing.v1 import AppTest
from prepare_data import clean
ROOT=Path(__file__).resolve().parents[1]
class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.at=AppTest.from_file(str(ROOT/'app.py'),default_timeout=180).run()
        cls.at.text_input[0].set_value('Phreya')
        cls.at.button[0].click().run()
    def test_01_full_dataset(self):
        at=self.at
        self.assertEqual(len(at.exception),0)
        self.assertEqual(at.metric[0].value,'2,101,588')
        self.assertEqual(at.metric[3].value,'205')
        self.assertEqual(len(at.get('plotly_chart')),9)
    def test_02_filter_and_reset(self):
        at=self.at
        at.multiselect[0].set_value(['New York City']).run()
        self.assertEqual(len(at.exception),0)
        source=pd.read_parquet(ROOT/'data/hospital.parquet',columns=['Hospital Service Area'])
        self.assertEqual(at.metric[0].value,f'{(source.iloc[:,0]=="New York City").sum():,}')
        at.button[0].click().run()
        self.assertEqual(at.metric[0].value,'2,101,588')
    def test_03_empty_cohort(self):
        at=self.at
        source=pd.read_parquet(ROOT/'data/hospital.parquet')
        counts=source.groupby('Facility Name',observed=True)['Length of Stay'].max()
        facility=counts[counts<119].index[0]
        at.multiselect[2].set_value([facility]).run()
        at.slider[0].set_range(119,119).run()
        self.assertEqual(len(at.exception),0)
        self.assertTrue(any('No records' in x.value for x in at.warning))
        at.button[0].click().run()
    def test_04_small_cohort(self):
        at=self.at
        at.slider[0].set_range(119,120).run()
        self.assertEqual(len(at.exception),0)
        at.button[0].click().run()
    def test_05_welcome(self):
        fresh=AppTest.from_file(str(ROOT/'app.py'),default_timeout=180).run()
        self.assertEqual(len(fresh.metric),0)
        fresh.button[0].click().run()
        self.assertTrue(len(fresh.error)>0)
        fresh.text_input[0].set_value('Test user')
        fresh.button[0].click().run()
        self.assertEqual(len(fresh.exception),0)
        self.assertEqual(len(fresh.metric),4)
    def test_06_cleaning(self):
        source=pd.read_parquet(ROOT/'data/hospital.parquet').head(4).astype(object)
        source['Length of Stay']=['120+','-3','invalid','0']
        source['Total Charges']=['$1,250.50','5','10','-4']
        result=clean(source)
        self.assertEqual(len(result),2)
        self.assertTrue(result.iloc[0]['Stay Capped'])
        self.assertEqual(result.iloc[0]['Length of Stay'],120)
        self.assertEqual(result.iloc[0]['Total Charges'],1250.5)
        self.assertTrue(pd.isna(result.iloc[1]['Total Charges']))
if __name__=='__main__':unittest.main()
