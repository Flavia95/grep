# extract from the main database the data on periconceptional drugs

import pandas as pd
import csv
import numpy as np
from pandas import DataFrame

db_miscarriage = pd.read_csv("miscarriage_database.csv")

db_miscarriage_drug=db_miscarriage[['id','type_of_miscarriage','periconceptional_drug_1','periconceptional_drug_2','periconceptional_drug_3','periconceptional_drug_4']]

melted= pd.melt(db_miscarriage_drug, id_vars=['id','type_of_miscarriage'], value_vars =['periconceptional_drug_1','periconceptional_drug_2','periconceptional_drug_3','periconceptional_drug_4'],var_name='number_of_pcd',value_name='periconceptional_drug')

drug_chem_agent = csv.reader(open('drug_pa.csv', 'r'))

dictionary_chem_agent = {}

for row in drug_chem_agent:
    k, v = row
    dictionary_chem_agent[k] = v


melted['chem_agent'] = melted['periconceptional_drug'].map(dictionary_chem_agent)

drug_smiles = csv.reader(open('drug_smile.csv', 'r'))

dictionary_smiles = {}

for row in drug_smiles:
    k, v = row
    dictionary_smiles[k]= v

melted['smiles'] = melted['periconceptional_drug'].map(dictionary_smiles)

melted_complete = melted.replace(np.nan,'NA', regex=True)

melted_complete.to_csv('/home/"InsertYourDirectoryName"/drug_script/periconceptional_drug.csv')



