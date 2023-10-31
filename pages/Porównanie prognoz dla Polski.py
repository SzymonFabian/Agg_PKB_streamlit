import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
from traitlets import default
from io import StringIO
from io import BytesIO
from zipfile import ZipFile
import urllib.request
from streamlit_option_menu import option_menu



def rok(x):
    return x.year


st.set_page_config(layout="wide")
#####################################
#PRZYGOTOWANIE DANYCH
#####################################

#####################
#NBP
#####################
#Ważne żeby zakładki w excelu były ułożone równo tak żeby najnowsza była na początku (piersza po lewej)
link1="https://github.com/SzymonFabian/Agg_PKB_streamlit/raw/main/data/NBP.zip"
url = urllib.request.urlopen(link1)
with ZipFile(BytesIO(url.read())) as my_zip_file:
    for contained_file in my_zip_file.namelist():
        fzip=my_zip_file.open(contained_file)
        data=fzip.read()
        
NBP_g = ()
x = pd.ExcelFile(data)
x = sorted(list(x.sheet_names),reverse=False)
for i in x:
    tmp_df = pd.read_excel(data, sheet_name=i)
    tmp_df = tmp_df.rename(columns={"Unnamed: 0": "Zmienna"})
    tmp_df = tmp_df.iloc[:,[0,tmp_df.shape[1]-4,tmp_df.shape[1]-3,tmp_df.shape[1]-2,tmp_df.shape[1]-1]]
    tmp_df.index = tmp_df["Zmienna"]
    tmp_df = tmp_df.drop('Zmienna', axis=1)
    tmp_df = tmp_df.T
    tmp_df = tmp_df.iloc[:,[0,4,5,6,7,8,9,10,11,13,14]]
    tmp_df = tmp_df.set_axis(['CPI','PKB','Popyt_krajowy','PCR','GCR','ITR','wklad_eks_netto','XTR','MTR','LN','UR'], axis=1)
    tmp_df["Prognoza"] = "NBP - {}".format(i)
    tmp_df["Rok"] = tmp_df.index
    #nie jestem pewny czy dobrze liczę udział zapasów w dynamice PKB
    tmp_df["Zapasy"] = tmp_df["PKB"] - (tmp_df["Popyt_krajowy"] + tmp_df["wklad_eks_netto"])
    tmp_df = tmp_df.round(1)

    NBP_g = NBP_g + tuple((tmp_df,))

#####################
#KE
#####################
#Ważne żeby zakładki w excelu były ułożone równo tak żeby najnowsza była na początku (piersza po lewej)
link2="https://github.com/SzymonFabian/Agg_PKB_streamlit/raw/main/data/KE.zip"
url = urllib.request.urlopen(link2)
with ZipFile(BytesIO(url.read())) as my_zip_file:
    for contained_file in my_zip_file.namelist():
        fzip=my_zip_file.open(contained_file)
        data=fzip.read()

KE_g = ()
x = pd.ExcelFile(data)
x = sorted(list(x.sheet_names),reverse=False)
for i in x:
    tmp_df = pd.read_excel(data, sheet_name=i)
    tmp_df.index = tmp_df["Kategoria"]
    tmp_df = tmp_df.drop('Kategoria',axis=1)
    tmp_df = tmp_df.T
    tmp_df = tmp_df.iloc[:,[0,1,2,3,4,5,7,8,9,10,11,16]]
    tmp_df = tmp_df.set_axis(["PKB","PCR","GCR","ITR","XTR","MTR","Popyt_krajowy","Zapasy","wklad_eks_netto","LN","UR","CPI"], axis=1)
    tmp_df = tmp_df.round(1)
    tmp_df["Rok"] = tmp_df.index
    tmp_df["Prognoza"] = "KE - {}".format(i)
    

    KE_g = KE_g + tuple((tmp_df,))


#####################
#MF
#####################
link3="https://github.com/SzymonFabian/Agg_PKB_streamlit/raw/main/data/MF.zip"
url = urllib.request.urlopen(link3)
with ZipFile(BytesIO(url.read())) as my_zip_file:
    for contained_file in my_zip_file.namelist():
        fzip=my_zip_file.open(contained_file)
        data=fzip.read()


MF_g = ()
x = pd.ExcelFile(data)
x = sorted(list(x.sheet_names),reverse=False)
for i in x:
    tmp_df = pd.read_excel(data, sheet_name=i)
    tmp_df["Prognoza"] = "MF - {}".format(i)
    tmp_df = tmp_df.round(1)
    MF_g = MF_g + tuple((tmp_df,))


#####################################
#ŁĄCZENIE DANYCH
#####################################
KE = pd.concat(KE_g, axis=0, ignore_index=True)
NBP = pd.concat(NBP_g, axis = 0, ignore_index=True)
MF = pd.concat(MF_g, axis=0, ignore_index=True)
df = pd.concat([KE,NBP,MF])



##########################################################
#STREAMLIT
##########################################################


st.title("Porównanie prognoz")


st.markdown("""
    Przedstawienie prognoz głównych instytucji: **KE** (Komisji Europejskiej), **NBP** (Narodowego Banku Polskiego), **MF** (Ministerstwa Finansów). \n
    Analizowane zmienne są w ujęciu realnym.
""")
with st.sidebar:
    selected = option_menu(
        menu_title = "Porównanie:", 
        options = ["Dynamik", "Wkładu we wzrost"],
        menu_icon = "cast",
        default_index = 0,
        orientation = "horizontal"
    )
st.sidebar.markdown("""-------""")


if selected == "Dynamik": 

    st.markdown("""
    Wykres przedstawia prognozy dynamiki dla wybranej zmiennej (%, r/r).
    """)

    #wycięto bezrobocie
    zmienne = ["PKB","CPI","Konsumpcja prywatna","Konsumpcja publiczna","Inwestycje","Eksport","Import","Zatrudnienie"]
    wybor_zmiennej = st.sidebar.selectbox("Zmienna",zmienne)



    wybor_prognozy_NBP = st.sidebar.multiselect("Wybór prognozy NBP",sorted(NBP["Prognoza"].unique().tolist(), reverse=True),sorted(NBP["Prognoza"].unique().tolist(), reverse=True)[0])
    #wybor_prognozy_KE = st.sidebar.multiselect("Wybór prognozy KE",y,sorted(y,reverse=False)[0])
    wybor_prognozy_MF = st.sidebar.multiselect("Wybór prognozy MF",sorted(MF["Prognoza"].unique().tolist(), reverse=True),sorted(MF["Prognoza"].unique().tolist(), reverse=True)[0])

    


    if wybor_zmiennej in ("PKB","CPI"):
                #usuwanie z listy KE prognozy Summer i Winter bo nie ma w nich pokazanych wkładów we wzrost
        y=KE["Prognoza"].unique()
        wybor_prognozy_KE = st.sidebar.multiselect("Wybór prognozy KE",y,sorted(y,reverse=False)[0])
    else:
                #usuwanie z listy KE prognozy Summer i Winter bo nie ma w nich pokazanych wkładów we wzrost
        y=KE[(KE["XTR"].notnull().values)]["Prognoza"].unique()
        wybor_prognozy_KE = st.sidebar.multiselect("Wybór prognozy KE",y,sorted(y,reverse=False)[0])



    wybor_prognozy = wybor_prognozy_NBP + wybor_prognozy_KE + wybor_prognozy_MF 
    #####################################
    #WYBÓR DANYCH
    #####################################


    dict = {
        "PKB": "PKB",
        "Konsumpcja prywatna":"PCR",
        "Konumpcja publiczna":"GCR",
        "Inwestycje":"ITR",
        "Eksport": "XTR",
        "Import":"MTR",
        "Zatrudnienie":"LN",
        "Bezrobocie":"UR",
        "CPI":"CPI"
    }
    wybrana_zmienna = dict.get(wybor_zmiennej) 

    ttt = list()

    for j,i in enumerate(df.loc[:,"Prognoza"].str[:2]):
        if i == "KE":
            ttt.append("blue") 
        elif i =="NB":
            ttt.append("green") 
        elif i =="MF":
            ttt.append("red") 
    df["Kolor"] = ttt

    Numer = list(range(1,2))

    for i in range(1, len(df["Prognoza"])):
        if df["Kolor"].iloc[i] != df["Kolor"].iloc[i-1]:
                Numer.append(1)
        else:
            if df["Prognoza"].iloc[i] == df["Prognoza"].iloc[i-1]:
                Numer.append(Numer[i-1])
            else:
                Numer.append(Numer[i-1]+1)

    df["Numer"] = Numer
    df["kolor"] = df["Kolor"] + df["Numer"].astype(str)


    tmp = {'kolor': ['green1','green2','green3','green4','red1','red2','red3','red4','blue1','blue2','blue3','blue4'],
         'hex': ['#91d17d','#6bd14b','#2ea30a','#185c04','#eb8888','#de5757','#d11515','#5e0606','#9699eb','#575bde','#0e15cf','#060963']}
    hex = pd.DataFrame(data=tmp)
    df = df.merge(hex, on='kolor', how='left')



    dynamiki = df[[wybrana_zmienna,"Prognoza","Rok","hex"]][df.Prognoza.isin(wybor_prognozy)]
    dynamiki["Rok"] = pd.to_datetime(dynamiki["Rok"], format='%Y')

    

    fig = px.line(dynamiki , x="Rok", y=wybrana_zmienna, color='Prognoza', text=wybrana_zmienna, symbol="Prognoza",width=1000, height=500)
    fig.update_traces(textposition="bottom right")
    fig.update_xaxes(dtick="M12")

    for i in range(len(fig['data'])):
        fig['data'][i]['line']['color'] =dynamiki["hex"].unique()[i]

    st.plotly_chart(fig, use_container_width=False)

    st.sidebar.caption('*CPI w przypadku KE to HICP')


if selected == "Wkładu we wzrost":

    st.markdown("""
    Wykres przedstawia prognozowane wkłady we wzrost PKB (%, r/r) trzech głównych kategorii : Popytu krajowego, Zapasów i Eksportu netto.
    """)

    #usuwanie z listy KE prognozy Summer i Winter bo nie ma w nich pokazanych wkładów we wzrost
    y=KE["Prognoza"].unique()
    yy=[]
    for i in y:
        if not 'Winter'  in i:
            yy.append(i)
    yyy=[]
    for i in yy:
        if not 'Summer'  in i:
            yyy.append(i)


    wybor_prognozy_NBP = st.sidebar.multiselect("Wybór prognozy NBP",sorted(NBP["Prognoza"].unique().tolist(), reverse=True),sorted(NBP["Prognoza"].unique().tolist(), reverse=True)[0])
    wybor_prognozy_KE = st.sidebar.multiselect("Wybór prognozy KE",yyy,sorted(yyy,reverse=False)[0])
    wybor_prognozy_MF = st.sidebar.multiselect("Wybór prognozy MF",sorted(MF["Prognoza"].unique().tolist(), reverse=True),sorted(MF["Prognoza"].unique().tolist(), reverse=True)[0])

    


    wybor_prognozy = wybor_prognozy_NBP + wybor_prognozy_KE + wybor_prognozy_MF 


            

    
    wklad = df[['PKB','Popyt_krajowy','Zapasy','wklad_eks_netto',"Prognoza","Rok"]][df.Prognoza.isin(wybor_prognozy)]
    wklad["Rok"] = pd.to_datetime(wklad["Rok"], format='%Y')

    wklad["Rok"] = wklad["Rok"].apply(rok)


    fig = go.Figure()



    categories = wklad["Prognoza"].unique()

    for j, i in enumerate(categories):
            kk = wklad[wklad["Prognoza"] == i]
            if j == 0:

                    fig.add_trace(
                            go.Bar(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["Popyt_krajowy"],marker_color='#2e59a8', name = "Popyt krajowy",text =kk["Popyt_krajowy"]),
                    )

                    fig.add_trace(
                            go.Bar(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["Zapasy"],marker_color='#73a2c6', name = "Zapasy",text =kk["Zapasy"]),
                    )

                    fig.add_trace(
                            go.Bar(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["wklad_eks_netto"],marker_color='#c5eddf', name = "Eksport netto",text =kk["wklad_eks_netto"]),
                    )
                    fig.add_trace(go.Scatter(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["PKB"],
                        mode='markers',
                        name='PKB',marker_color="Red"))

            else:
                    fig.add_trace(
                            go.Bar(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["Popyt_krajowy"],marker_color='#2e59a8', name = "Popyt krajowy", showlegend=False,text =kk["Popyt_krajowy"]),
                    )

                    fig.add_trace(
                            go.Bar(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["Zapasy"],marker_color='#73a2c6', name = "Zapasy", showlegend=False,text =kk["Zapasy"]),
                    )

                    fig.add_trace(
                            go.Bar(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["wklad_eks_netto"],marker_color='#c5eddf', name = "Eksport netto", showlegend=False,text =kk["wklad_eks_netto"]),
                    )
                    fig.add_trace(go.Scatter(x=[kk["Rok"], [i]*len(kk["Rok"])], y=kk["PKB"],
                        mode='markers',
                        name='PKB', showlegend=False,marker_color="Red"))

                    

    fig.update_layout(
        xaxis=dict(title_text="Rok"),
        yaxis=dict(title_text="mln PLN"),
        barmode='relative',
    )

    fig.update_layout(
        xaxis_title="Rok",
        yaxis_title="%",
        legend_title="",
        font=dict(
            family="times new roman",
            size=12,
            color="Black"
        ),height=600, width=300*len(categories)
    )
        

    st.plotly_chart(fig, use_container_width=False)


