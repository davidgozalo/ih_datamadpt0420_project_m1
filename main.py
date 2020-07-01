#1. Data acquisition,
#2. Input requirements
#3. Operations
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import requests
import re
#1 Data acquisition
#Tables
#Importing data from db into a df
sqlitedb_path = './data/raw/raw_data_project_m1.db'
engine = create_engine(f'sqlite:///{sqlitedb_path}')
tables=pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table'", engine)
# Importing each table data from db into df
df_personal = pd.read_sql("SELECT * FROM personal_info", engine)
df_country = pd.read_sql("SELECT * FROM country_info", engine)
df_career = pd.read_sql("SELECT * FROM career_info", engine)
df_poll_info = pd.read_sql("SELECT * FROM poll_info", engine)
#I create a data frame per table
#This function cleans gender data (in the df_personal df)
def set_gender(x):
    x1=x.lower()
    if x1[0]=="m":
        return "male"
    if x1[0]=="f":
        return "female"
df_personal['gender'] = df_personal['gender'].apply(set_gender)
#This merges all the dataframes into a single big one
df_personal_country = pd.merge(df_personal, df_country,how="inner", on='uuid')
df_personal_country_career=pd.merge(df_personal_country, df_career,how="inner", on='uuid')
df_personal_country_career_poll_info=pd.merge(df_personal_country_career, df_poll_info,how="inner", on='uuid')
#I select only the variables that I am going to use in the final step
df_basic = df_personal_country_career_poll_info[["uuid","country_code","normalized_job_code","gender"]]
#I import data to get the job description
response = requests.get('http://api.dataatwork.org/v1/jobs/autocomplete?contains=data')
json_data = response.json()
job_data = pd.DataFrame(json_data)
#I select the columns I need from job_data
job_basic_data = job_data[["uuid","normalized_job_title"]]
#I rename the columns so that I can later merge on them
job_basic_data_renamed=job_basic_data.rename(columns={"uuid":"normalized_job_code"})
#df_basic_clean1 means that 1s phase of cleaning is incorporating the normalized job description
df_basic_clean1=pd.merge(df_basic, job_basic_data_renamed,how="left", on='normalized_job_code')
# I assume that no info on job means that the individual has no job
df_basic_clean1["normalized_job_title"].fillna("no job", inplace = True)
# I import data to  get country description
page = requests.get("https://ec.europa.eu/eurostat/statistics-explained/index.php/Glossary:Country_codes")
from bs4 import BeautifulSoup
soup = BeautifulSoup(page.content, 'html.parser')
soup = BeautifulSoup(page.content, 'html.parser')
list=soup.find_all('td')
a=len(list)
dictionary={}
lista=[]
for i in range (a):
    w=soup.find_all('td')[i].get_text()
    #print(i,w)
    ws= re.sub("\n", "", w)
    wws=re.sub(" ","",ws)
    if len(ws)>=4:
        lista.append(wws)
    else:
        pass
indexlista = []
valuelista = []
count = 0
for item in lista:
    count = count + 1
    if count % 2 == 0:
        itemclean = item.replace("(", "")
        itemclean2 = itemclean.replace(")", "")
        indexlista.append(itemclean2)

    else:
        valuelista.append(item)
dfObj = pd.DataFrame(valuelista, index=indexlista)
df_new = dfObj.reset_index()
df_new.columns = ['code','country']
df_new.rename(columns={'code':'country_code'}, inplace=True)
df_new['country_code'].replace('EL','GR', inplace=True)
df_new['country_code'].replace('UK','GB', inplace=True)
#df_basic_clean2 means that 2nd phase of cleaning is incorporating the country description
df_basic_clean2=pd.merge(df_basic_clean1, df_new,how="left", on='country_code')
#I take the columns that I need from the final calculatuions
df_sumary=df_basic_clean2.groupby(["country", "normalized_job_title", "gender"]).count().reset_index()
df_sumary_basic=df_sumary[["country", "normalized_job_title", "gender", "uuid"]]
#Example of total display as a final result
print(df_sumary_basic)
#Ordered
df_sumary_basic.sort_values("uuid", axis = 0, ascending = False,
                 inplace = False, na_position ='last')
#Example of a final result based on input
normalized_job_title="no job"
country="Belgium"
sumary_job = df_sumary_basic[(df_sumary_basic["normalized_job_title"] == normalized_job_title)|(df_sumary_basic["country"] == country)]
print(sumary_job)