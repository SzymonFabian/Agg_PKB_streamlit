
import pandas as pd
import streamlit as st
import altair as alt
import plotly.graph_objects as go
from traitlets import default


st.set_page_config(layout="wide")
url = 'https://raw.githubusercontent.com/SzymonFabian/Agg_PKB_streamlit/main/Dataset_agg.csv'
df_org = pd.read_csv(url, index_col=0, sep=";")



df_k = df_org

#dodwanie po 100 do każdej wartości
for i in range(0,len(df_k.columns)):
    for j in range(0,df_k.shape[0]):
        df_k.iloc[j,i] = df_k.iloc[j,i]+100
    

#df.index = df["Country"]

#df_1 = df.drop(columns=["Country"]).T
df_1 = df_k.T

st.title("Skumulowany wzrost PKB w latach 2001-2023 (prognoza)")

st.markdown("""
    Wykres prezentuje ranking skumulowanego tempa wzrostu realnego PKB w wybranych krajach w wybranym zakresie lat. \n
    Źródło: Eurostat, Bank Światowy, Komisja Europejska (prognoza dla krajów UE), Międzynarodowy Fundusz Walutowy (prognoza dla krajów spoza UE).
""")


st.sidebar.header("Filtry")
selected_year_start = st.sidebar.selectbox("poczatek",list(reversed(range(2001,2023))))
selected_year_end = st.sidebar.selectbox("koniec",list(reversed(range(2001,2023))))

wybrane_lata = [str(y) for y in range(selected_year_start, selected_year_end + 1)]

df_2 = df_1[df_1.index.isin(wybrane_lata)]



#co rysujemy dla całego zbioru
dd = (df_2.prod(axis=0)/(100**(df_2.shape[0]-1)))-100
cc = pd.DataFrame({"values" : dd,"Country":dd.index}).sort_values(by=['values'], ascending=False)


st.sidebar.markdown(""" Wybrane grupy:  """)
UE = ('European Union','Euro area','Belgium','Bulgaria','Czechia','Denmark','Germany','Estonia','Ireland','Greece','Spain','France',
        'Croatia','Italy','Cyprus','Latvia','Lithuania','Luxembourg','Hungary','Malta','Netherlands','Austria','Poland','Portugal',
        'Romania','Slovenia','Slovakia','Finland','Sweden')

G7= ("Canada", "France", "Germany", "Italy", "Japan", "United Kingdom", "United States")

BRICS = ("Brazil","Russian Federation","India","China","South Africa")



cc["kolor"] = ""
cc["cale"] = ""
for j,i in enumerate(cc["Country"]):
    if i == "Poland":
        cc["kolor"][j] = "red"
    elif i == "European Union" or i =="Euro area":
        cc["kolor"][j] = "blue"
    elif i in (BRICS):
        cc["kolor"][j] = "silver"
    else:
        cc["kolor"][j] = "grey"
    cc["cale"][j] = round(cc["values"][j],1)


# Sidebar 


sorted_country = sorted(cc["Country"])
zaznaczone = sorted(cc["Country"])


UE_selected = st.sidebar.checkbox("UE")
G7_selected = st.sidebar.checkbox("G7")
BRICS_selected = st.sidebar.checkbox("BRICS")

if UE_selected and not G7_selected and not BRICS_selected:
    zaznaczone = UE
elif G7_selected and not UE_selected  and not BRICS_selected:
    zaznaczone = G7
elif UE_selected and G7_selected  and not BRICS_selected:
    zaznaczone = UE+G7
elif BRICS_selected and not UE_selected and not G7_selected:
    zaznaczone = BRICS
elif BRICS_selected and UE_selected  and not G7_selected:
    zaznaczone = BRICS+UE
elif BRICS_selected and G7_selected  and not UE_selected :
    zaznaczone = BRICS+G7
elif BRICS_selected and G7_selected  and  UE_selected :
    zaznaczone = BRICS+G7+UE

selected_country = st.sidebar.multiselect('Wybrane państwa', sorted_country, zaznaczone)


ff = cc[cc.Country.isin(selected_country)]



layout = go.Layout(
    autosize=False,
    width=1000,
    height=550)


fig = go.Figure(
    go.Bar(x=ff['Country'],
                y=ff['values'],
                marker={'color': ff['kolor']},text=ff['cale']), 
    layout=layout
)


st.plotly_chart(fig, use_container_width=False)

df_cc = df_k
for i in range(0,len(df_k.columns)):
    for j in range(0,df_k.shape[0]):
        df_cc .iloc[j,i] = (df_cc .iloc[j,i]-100)/100

df_cc["Country"] = df_cc.index

df_tmp = df_cc[df_cc.Country.isin(selected_country)]

df_pokaz = df_tmp.drop(columns=["Country"])



st.dataframe(df_pokaz.style.format("{:.1%}"))

from io import BytesIO
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=True, sheet_name='Skumulowany_wzrost_PKB')
    workbook = writer.book
    worksheet = writer.sheets['Skumulowany_wzrost_PKB']
    format1 = workbook.add_format({'num_format': '0.00'}) 
    worksheet.set_column('A:A', None, format1)  
    writer.save()
    processed_data = output.getvalue()
    return processed_data

df_temp_2 = df_pokaz
for i in range(0,len(df_temp_2.columns)):
    for j in range(0,df_temp_2.shape[0]):
        df_temp_2.iloc[j,i] = df_pokaz.iloc[j,i]*100

df_xlsx = to_excel(df_temp_2)

st.download_button(label='📥 Pobierz wybraną tabelę',
                                data=df_xlsx ,
                                file_name= 'Skumulowany_wzrost_PKB.xlsx')
























