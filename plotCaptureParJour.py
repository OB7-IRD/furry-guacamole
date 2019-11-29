
import pandas as pd
import logbookcontrol as jp
import os



import plotly.express as px

dataFileClassic = "France_OA_427_FLUX_AVDTH_1216_0117.mdb"
dataFileERS = "AVDTH_20170223144519.mdb"
databaseFileClassic = os.getcwd() + "\\" + dataFileClassic
databaseFileERS = os.getcwd() + "\\" + dataFileERS
avdth_classic = jp.AVDTH(databaseFileClassic)
avdth_ers = jp.AVDTH(databaseFileERS)

ers_ids = avdth_ers.find_all_ers_id()
ers_id = ers_ids[0]

avdth_trip = avdth_classic.find_trip(ers_id)
ers_trip = avdth_ers.find_trip(ers_id)

ers_catches = pd.DataFrame( avdth_ers.list_all_catches_from_trip(ers_trip['C_BAT'], ers_trip['D_DBQ']))
    
avdth_catches = pd.DataFrame( avdth_classic.list_all_catches_from_trip(avdth_trip['C_BAT'], avdth_trip['D_DBQ']))    

#print(avdth_catches)

ers_grouped = pd.DataFrame({'sum' : ers_catches.groupby( [ "D_ACT", "C_ESP"] )["V_POIDS_CAPT"].agg("sum"), 'source':"ers"}).reset_index()
#    display(ers_grouped)

avdth_grouped = pd.DataFrame({'sum' : avdth_catches.groupby( [ "D_ACT", "C_ESP"] )["V_POIDS_CAPT"].sum(),
                                  'source':"avdth"}).reset_index()
all_catches = ers_grouped.append(avdth_grouped)
    
#print(all_catches)

all_catches['C_ESP'] = [avdth_ers.get_specie_label(specie) for specie in all_catches['C_ESP']]
    
fig = px.bar(all_catches, x="sum", y="D_ACT", color='C_ESP', barmode='stack', orientation='h',  facet_col='source', labels=dict(sum="Poids capturés", D_ACT="Date d'activités", C_ESP="Espèce"))

fig.show()