
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

ers_activities = pd.DataFrame( avdth_ers.list_all_activities_from_trip(ers_trip['C_BAT'], ers_trip['D_DBQ']))

avdth_activities = pd.DataFrame( avdth_classic.list_all_activities_from_trip(avdth_trip['C_BAT'], avdth_trip['D_DBQ']))
ers_grouped = pd.DataFrame({'count' : ers_activities.groupby( [ "D_ACT", "C_OPERA"] ).size(), 'source':"ers"}).reset_index()
print(ers_grouped)

avdth_grouped = pd.DataFrame({'count' : avdth_activities.groupby( [ "D_ACT", "C_OPERA"] ).size(),
                              'source':"avdth"}).reset_index()
all_activities = ers_grouped.append(avdth_grouped)
all_activities['C_OPERA'] = [avdth_ers.get_operation_label(op) for op in all_activities['C_OPERA']]


fig = px.bar(all_activities, x="count", y="D_ACT", color='C_OPERA', barmode='stack', height=600, orientation='h',  facet_col='source', labels=dict(count="Nombre d'activités", D_ACT="Date d'activités", C_OPERA="Opération"))
fig.show()

