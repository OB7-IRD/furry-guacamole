
import pandas as pd
import logbookcontrol as jp
import os, math



import plotly.express as px


def convert_lat_pos(quadrant, latitude):
    if quadrant == 3 or quadrant == 2:
        latitude *= -1
    return math.floor(latitude/100.) + ((latitude/100.) % 1 / 60 * 100)
    

def convert_long_pos(quadrant, longitude):
    if quadrant == 3 or quadrant == 4:
        longitude *= -1    
    return math.floor(longitude/100.) + ((longitude/100.) % 1 / 60 * 100)

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

ers_activities = pd.DataFrame( avdth_ers.list_all_activities_from_trip(ers_trip['C_BAT'], ers_trip['D_DBQ']),
                             columns=['C_BAT','D_DBQ','D_ACT','N_ACT','V_LAT','V_LON', 'Q_ACT','D_ACT_FULL','ID_ACT', "V_CAPT", "C_OPERA"]
                             )

ers_activities['latitude'] = [convert_lat_pos(q,l) for l,q in zip(ers_activities['V_LAT'],ers_activities['Q_ACT'])]
ers_activities['longitude'] = [convert_long_pos(q,l) for l,q in zip(ers_activities['V_LON'],ers_activities['Q_ACT'])]
ers_activities['C_OPERA'] = [avdth_ers.get_operation_label(op) for op in ers_activities['C_OPERA']]
ers_activities['source'] = ["ers" for x in ers_activities['C_OPERA']]

avdth_activities = pd.DataFrame( avdth_classic.list_all_activities_from_trip(avdth_trip['C_BAT'], avdth_trip['D_DBQ']),
                                 columns=['C_BAT','D_DBQ','D_ACT','N_ACT','V_LAT','V_LON', 'Q_ACT','D_ACT_FULL','ID_ACT', "V_CAPT",  "C_OPERA"]
                                 )

avdth_activities['latitude'] = [convert_lat_pos(q,l) for l,q in zip(avdth_activities['V_LAT'],avdth_activities['Q_ACT'])]
avdth_activities['longitude'] = [convert_long_pos(q,l) for l,q in zip(avdth_activities['V_LON'],avdth_activities['Q_ACT'])]

avdth_activities['C_OPERA'] = [avdth_ers.get_operation_label(op) for op in avdth_activities['C_OPERA']]
avdth_activities['source'] = ["avdth" for x in avdth_activities['C_OPERA'] ]


all_activities = ers_activities.append(avdth_activities)

fig = px.scatter_mapbox(all_activities, lat="latitude", lon="longitude", color="source", hover_name="D_ACT_FULL", hover_data=["V_CAPT", "C_OPERA", "source"],
                         zoom=3, height=600)

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()
