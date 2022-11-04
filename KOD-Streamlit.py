from audioop import reverse
from sqlite3 import Date
from xmlrpc.client import DateTime
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import plotly.graph_objects as go



#df = pd.read_excel(r'd:\HUKP\Desktop\Workspace\Raporty\Porównanie_wzrostu_shiny\Dataset_agg.xlsx', sheet_name="Data")


url = 'https://raw.githubusercontent.com/SzymonFabian/Agg_PKB_streamlit/main/Dataset_agg.csv'
df = pd.read_csv(url, index_col=0, sep=";")



#dodwanie po 100 do każdej wartości
for i in range(1,len(df.columns)):
    for j in range(0,df.shape[0]):
        df.iloc[j,i] = df.iloc[j,i]+100
    

#df.index = df["Country"]

#df_1 = df.drop(columns=["Country"]).T
df_1 = df.T

st.title("Zagregowany PKB")

st.markdown("""
    Przedstawienie zagregowanego PKB dla Polski i pozostałych państw UE.

""")


st.sidebar.header("Filtry")
selected_year_start = st.sidebar.selectbox("poczatek",list(reversed(range(2001,2023))))
selected_year_end = st.sidebar.selectbox("koniec",list(reversed(range(2001,2023))))

wybrane_lata = [str(y) for y in range(selected_year_start, selected_year_end + 1)]

df_2 = df_1[df_1.index.isin(wybrane_lata)]



#co rysujemy dla całego zbioru
dd = (df_2.prod(axis=0)/(100**(df_2.shape[0]-1)))-100
cc = pd.DataFrame({"values" : dd,"Country":dd.index}).sort_values(by=['values'], ascending=False)


cc["kolor"] = ""
cc["cale"] = ""
for j,i in enumerate(cc["Country"]):
    if i == "Poland":
        cc["kolor"][j] = "red"
    elif i == "European Union" or i =="Euro area":
        cc["kolor"][j] = "blue"
    else:
        cc["kolor"][j] = "grey"
    cc["cale"][j] = round(cc["values"][j],1)


# Sidebar 
sorted_country = sorted(cc["Country"])
selected_country = st.sidebar.multiselect('Kraj', sorted_country, sorted_country)


#kraje = ("Poland", "Germany","Lithuania","Denmark","Italy","Slovenia")

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





























