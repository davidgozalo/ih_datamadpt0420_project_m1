#1. Data acquisition,
#2. Input requirements
#3. Operations
import pandas as pd
from sqlalchemy import create_engine
import requests
import re
from bs4 import BeautifulSoup
mode=0
country_sel=0
#1 Data acquisition
#Tables
#Importing data from db into a df
sqlitedb_path = './data/raw/raw_data_project_m1.db'
engine = create_engine(f'sqlite:///{sqlitedb_path}')
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
df_job_data = pd.DataFrame(json_data)
#I select the columns I need from job_data
df_job_basic_data = df_job_data[["uuid","normalized_job_title"]]
#I rename the columns so that I can later merge on them
df_job_basic_data_renamed=df_job_basic_data.rename(columns={"uuid":"normalized_job_code"})
#df_basic_clean1 means that 1s phase of cleaning is incorporating the normalized job description
df_basic_clean1=pd.merge(df_basic, df_job_basic_data_renamed,how="left", on='normalized_job_code')
# I assume that no info on job means that the individual has no job
df_basic_clean1["normalized_job_title"].fillna("no job", inplace = True)
# I import data to  get country description
page = requests.get("https://ec.europa.eu/eurostat/statistics-explained/index.php/Glossary:Country_codes")
soup = BeautifulSoup(page.content, 'html.parser')
soup = BeautifulSoup(page.content, 'html.parser')
list=soup.find_all('td')
n_elements=len(list)
lista=[]
for i in range (n_elements):
    w=soup.find_all('td')[i].get_text()
    #print(i,w)
    ws= re.sub("\n", "", w)
    wws=re.sub(" ","",ws)
    wwws=re.sub("[0-9]","",wws)
    wwwws=re.sub("[\[\]]","",wwws)
    wwwwws=re.sub("[\*]","",wwwws)
    if len(ws)>=4:
        lista.append(wwwwws)
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
df_countries = pd.DataFrame(valuelista, index=indexlista)
df_countries = df_countries.reset_index()
df_countries.columns = ['code','country']
df_countries.rename(columns={'code':'country_code'}, inplace=True)
df_countries['country_code'].replace('EL','GR', inplace=True)
df_countries['country_code'].replace('UK','GB', inplace=True)
#df_basic_clean2 means that 2nd phase of cleaning is incorporating the country description
df_basic_clean2=pd.merge(df_basic_clean1, df_countries,how="left", on='country_code')
#I take the columns that I need from the final calculatuions
df_sumary=df_basic_clean2.groupby(["country", "normalized_job_title", "gender"]).count().reset_index()
df_sumary_basic=df_sumary[["country", "normalized_job_title", "gender", "uuid"]]
#2. Input requirements
# At this point we should run the input choices
df_show=pd.merge(df_countries, df_sumary_basic,how="right", on='country')
df_show_unique_country=df_show['country'].unique()
df_show_unique_country_code=df_show["country_code"].unique()
country_list =df_show_unique_country.tolist()
country_code_list =df_show_unique_country_code.tolist()
country_code_list_lower=[x.lower() for x in country_code_list]
country_list_lower=[x.lower() for x in country_list]
df_show_list=pd.DataFrame({'country': country_list, 'country_code': country_code_list})
possible_mode_values=["country","all","ALL","COUNTRY","All","Country"]
parameter1=0
mode=0
while True:
    mode=input(f"Do you want all data or do you want to choose a country?")
    try:
        if mode in possible_mode_values:
            parameter1=mode
            print (f"We will show you {mode} data")
            break
    except ValueError:
        print (f"{mode} is not a valid answer")
        print ('Just say "all" or "country", please')
        continue
    else:
        print (f"{mode} is not a valid answer")
        print ('Just say "all" or "country", please')
possible_country_values= []
for item in country_code_list:
    value=item
    value_lower=item.lower()
    value_capitalized=item.capitalize()
    possible_country_values.append(value)
    possible_country_values.append(value_lower)
    possible_country_values.append(value_capitalized)
for item in country_list:
    value=item
    value_lower=item.lower()
    value_capitalized=item.capitalize()
    possible_country_values.append(value)
    possible_country_values.append(value_lower)
    possible_country_values.append(value_capitalized)
if mode=="country":
    print(df_show_list.to_string(index=False))
    parameter2=0
    country_sel=0
    print ("Choose a country out of this list, please")
    while True:
        country_sel=input(f"Choose a country")
        try:
            if country_sel in possible_country_values:
                parameter2=country_sel
                break
        except ValueError:
            print (f"{country_sel} is not a valid answer")
            print ('Choose a value out of the list, please')
            continue
        else:
            print (f"{country_sel} is not a valid answer")
            print ('Choose a value out of the list, please')
else:
    pass
df_show_list["COUNTRY"] = df_show_list["country"]
df_show_list['COUNTRY'] = df_show_list['COUNTRY'].str.lower()
df_show_list["COUNTRY_CODE"] = df_show_list["country_code"]
df_show_list['COUNTRY_CODE'] = df_show_list['COUNTRY_CODE'].str.lower()
df_show_list["Country"] = df_show_list["country"]
df_show_list['Country'] = df_show_list['Country'].str.upper()
df_show_list["Country code"] = df_show_list["country_code"]
df_show_list['Country code'] = df_show_list['Country code'].str.capitalize()
#3 Results
# calculations depending on the choice of mode
if mode == "all":
    uuid_sum = df_sumary_basic["uuid"].sum()
    df_sumary["percentage"] = df_sumary["uuid"] / uuid_sum * 100
    df_sumary_basic = df_sumary[["country", "normalized_job_title", "gender", "uuid", "percentage"]]
    results = df_sumary_basic.sort_values("percentage", axis=0, ascending=False, inplace=False)
    #results_sin = results.style.hide_index()
    print(results)

if mode == "country":

    if len(country_sel) == 2 and country_sel[0].islower():
        df_sel = df_show_list.loc[df_show_list['COUNTRY_CODE'] == country_sel]
        r = df_sel.iloc[0, 0]
    if len(country_sel) == 2 and country_sel[1].isupper():
        df_sel = df_show_list.loc[df_show_list['country_code'] == country_sel]
        r = df_sel.iloc[0, 0]
    if len(country_sel) == 2 and country_sel[1].islower():
        df_sel = df_show_list.loc[df_show_list['Country_code'] == country_sel]
        r = df_sel.iloc[0, 0]
    if len(country_sel) != 2 and country_sel[0].islower():
        df_sel = df_show_list.loc[df_show_list['COUNTRY'] == country_sel]
        r = df_sel.iloc[0, 0]
    if len(country_sel) != 2 and country_sel[0].isupper() and country_sel[1].islower():
        df_sel = df_show_list.loc[df_show_list['country'] == country_sel]
        r = df_sel.iloc[0, 0]
    if len(country_sel) != 2 and country_sel[0].isupper() and country_sel[1].isupper():
        df_sel = df_show_list.loc[df_show_list['Country'] == country_sel]
        r = df_sel.iloc[0, 0]
    else:
        pass

    #print(r)

    df_sumary_country = df_sumary_basic[df_sumary_basic["country"] == r]
    uuid_sum = df_sumary_country["uuid"].sum()
    df_sumary["percentage"] = df_sumary["uuid"] / uuid_sum * 100
    df_sumary_basic = df_sumary[["country", "normalized_job_title", "gender", "uuid", "percentage"]]
    df_sumary_country = df_sumary_basic[df_sumary_basic["country"] == r]

    # df_sumary_country["percentage"]=df_sumary_country["uuid"]/uuid_sum*100
    results = df_sumary_country.sort_values("percentage", axis=0, ascending=False, inplace=False)
    #results_country = results.style.hide_index()
    print(results)
    results_country = results.to_csv(r'data/results/final_table.csv', index=False, header=True)
