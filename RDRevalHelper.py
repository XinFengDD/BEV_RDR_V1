from tkinter import *
from tkinter import filedialog
import json,math
import os,sys
from scipy.stats import norm
from datetime import datetime
import numpy as np
from EVroutingAPI import *
from VehConfig import *
from RDRV0Rating import *
from RDRPloter import *
import pandas as pd

os.environ['REQUESTS_CA_BUNDLE']=os.path.join(os.path.dirname(sys.argv[0]),'cacert.pem')
from Credential import *



def extract(input):
    start=input[0].get()
    end=input[1].get()
    SOC=float(input[2].get())
    MinBL=float(input[3].get())
    Vehicle=input[4].get()
    RTTraffic= "true" if input[11].cget('text')=="RT Traffic On" else "false"
    return start,end,SOC,MinBL,Vehicle,RTTraffic

def obtainGPS_gmap(POI):
    geocode_result = gmaps.geocode(POI)
    return geocode_result[0]['geometry']['location']


def SelectFolder(Entry,output_map):
    of_root = Tk()
    of_root.withdraw()
    DataLogger_path='..\\V0'
    csv_path = filedialog.askdirectory(initialdir=DataLogger_path)
    print(csv_path)
    Entry.delete(0,END)
    Entry.insert(0,csv_path)

def findChargeinfo(csvfile):
    csvfile["Tdiff"] = csvfile['TripTime']
    csvfile["Tdiff"] = csvfile['Tdiff'].shift(periods=-1)- csvfile["TripTime"].shift(periods=1)
    csvfile["Tdiff"] =csvfile["Tdiff"].astype('timedelta64[s]')
    switch = csvfile[(csvfile['Tdiff'])>60]
    #switch.index = switch.index + 1
    switch=pd.concat([csvfile.head(1), switch], ignore_index=True)
    switch=switch.append(csvfile.tail(1))
    switch['SOC_diff'] = switch['SOC_%'].diff(-1)
    TOTAL_Driving_SOC = switch[switch['SOC_diff'] > 0]['SOC_diff'].sum()
    TOTAL_Charging_SOC = switch[switch['SOC_diff'] < 0]['SOC_diff'].sum()

    switch["Tdiff"]=switch["TripTime"]
    switch["Tdiff"] = switch['Tdiff'].shift(periods=-1)- switch["TripTime"]
    switch["Tdiff"] =switch["Tdiff"].astype('timedelta64[s]')
    TOTAL_Charging_Dur=switch[switch['SOC_diff'] < 0]['Tdiff'].sum()/3600
    return TOTAL_Driving_SOC, TOTAL_Charging_SOC, TOTAL_Charging_Dur

def OpenLog(Entry,output_map,API_Summary,Fig1):
    of_root = Tk()
    of_root.withdraw()
    DataLogger_path='..\\V1\\log'
    file_path = filedialog.askopenfilename(initialdir=DataLogger_path,filetypes=(("CSV files", "*.csv"),("Excel files", "*.xlsx"),("All files", "*.*")) )
    print(file_path)
    if(file_path): 
        Entry[6].delete(0,END)
        Entry[6].insert(0,file_path)
        Entry[4].delete(0,END)
        Entry[4].insert(0,'EC4')
        Entry[5].delete(0,END)
        Entry[5].insert(0,'Energy_km')
        Entry[7].delete(0,END)
        Entry[7].insert(0,'Retent On')
        Entry[8].delete(0,END)
        Entry[8].insert(0,file_path)

    if( file_path.endswith(".csv") ): 
        #DLfilepath=os.path.dirname(file_path)
        print ("loading csv trip log file...")

        with open(file_path) as f:
            #channels=Logchannels
            #csvfile = pd.read_csv(f,header=0,usecols =channels)
            csvfile = pd.read_csv(f,header=0)
            EndOdo=csvfile['ODOMETER'].max()
            StartOdo=csvfile['ODOMETER'].min()
            TDistance=EndOdo-StartOdo

            csvfile['Distance']=csvfile['ODOMETER']-StartOdo
            csvfile['TripMinute']=pd.to_datetime(csvfile['HEAD_COLL_TIMS'],utc=True)
            triptime=[]
            for index, row in csvfile.iterrows():
                triptime.append(row['TripMinute']+pd.Timedelta(seconds=row['SECONDS']))
            csvfile['TripTime']=triptime
            csvfile=csvfile.sort_values(by=['TripTime'])
            Startmin=(csvfile['TripTime'].min())
            Endmin=csvfile['TripTime'].max()
            TRIP_DURATION=pd.Timedelta(Endmin-Startmin)
            TRIP_DURATION_H=TRIP_DURATION.total_seconds()/3600

            TOTAL_Driving_SOC,TOTAL_Charging_SOC,TOTAL_Charging_Dur = findChargeinfo(csvfile)

        plotselection=Entry[5].get()

        if plotselection=='Energy_km':
            ConsumptionPlot(csvfile[['Distance','SOC_%']],Fig1)
        elif plotselection=='Speed_km':
            SpeedPlot(csvfile[['Distance','SPEED_PER_SEC']],Fig1)
        elif plotselection=='Speed_time':
            SpeedPlotTime(csvfile[['TripTime','SPEED_PER_SEC']],Fig1)
        elif plotselection=='Elevation_km':
            ElevationPlot(csvfile[['Distance','ALTITUDE','OUTSIDE_TEMPERATURE_C']],Fig1)
        elif plotselection=='Histogram':
            Histoplot(csvfile[['SPEED_MODE_PER_MINUTE','SOC_%','HEAD_COLL_TIMS']],Fig1)
        elif plotselection=='SOC_time':
            TimeSeriesPlot(csvfile[['TripTime','SPEED_PER_SEC','SOC_%']],Fig1)
        elif plotselection=='Anxiety':
            Anxietyplot(csvfile[['TripMinute','SOC_%','HEAD_COLL_TIMS']],Fig1)

        csvfile=csvfile.dropna().reindex()

        Pstart, Pend,InitSOC= LoadCSV(csvfile,output_map)
        TripUpdate(Pstart,Pend, InitSOC,Entry)

        #TOTAL_DELTA_SOC, TRIP_DURATION_H = TripExtract()
        logN=4
        API_Summary['SOC'][logN].config(text="{:.1f}".format(TOTAL_Driving_SOC*.463))
        API_Summary['DDur'][logN].config(text="{:.1f}".format(TRIP_DURATION_H))
        API_Summary['ChDur'][logN].config(text="{:.1f}".format(TOTAL_Charging_Dur))
        API_Summary['Dis'][logN].config(text="{:.1f}".format(TDistance))
    elif file_path.endswith(".xlsx"): 
        print ("loading test matrix file...")
        with open(file_path) as f:
            testmatrix=pd.read_excel(file_path, index_col=None) 
            if testmatrix.shape[0]>0:
                textinfo=[]
                cities=[]
                for idx in testmatrix.index:
                    cities.append(findCoord(testmatrix['start'][idx]))
                    cities.append(findCoord(testmatrix['end'][idx]))
                    textinfo.append("Charge Station: initial SOC:{:.1f}".format(float(testmatrix["SOC_%"][idx])))
                    output_map.set_marker(cities[idx*2][0],cities[idx*2][1], text=textinfo[idx],marker_color_circle="blue")
                    output_map.set_marker(cities[idx*2+1][0],cities[idx*2+1][1], text=textinfo[idx],marker_color_circle="green")
            disp_lat=cities[1][0]
            disp_lng=cities[1][1]
            output_map.set_position(disp_lat,disp_lng)
            zoomlevel=5
            output_map.set_zoom(zoomlevel)
    else: 
        print("incorrect file format")


def TripUpdate(Pstart, Pend, InitSOC,Entry):
    for i in range(4):
        Entry[i].delete(0, END)
    
    Entry[0].insert(0,','.join(map(str,Pstart)))
    Entry[1].insert(0,','.join(map(str,Pend)))
    Entry[2].insert(0,str(InitSOC))
    Entry[3].insert(0,"10")

def LoadCSV(input,output_map):
    coordlist=input[['LATITUDE','LONGITUDE']].values.tolist()
    textinfo=[]
    output_map.delete_all_marker()
    output_map.delete_all_path()
    output_map.set_path(coordlist,width=5)
    Pstart=coordlist[0]
    Pend=coordlist[-1]
    SOClist=input['SOC_%'].values.tolist()
    textinfo.append("Initial SOC percent:{:.1f}".format(SOClist[0]))
    start_lat=coordlist[0][0]
    start_lng=coordlist[0][1]
    output_map.set_marker(start_lat,start_lng, text=textinfo[0],marker_color_circle="blue")
    end_lat=coordlist[-1][0]
    end_lng=coordlist[-1][1]
    textinfo.append("End SOC percent:{:.1f}".format(SOClist[-1]))
    output_map.set_marker(end_lat,end_lng, text=textinfo[1],marker_color_circle="green")
    #find charging spot
    input["SOCdiff"] = input['SOC_%'].diff(periods=7)
    Charging = input[(input["SOCdiff"]>0.3)&(input["SPEED_MODE_PER_MINUTE"]==0)&(input["SPEED_PER_SEC"]==0)]
    Charging.drop_duplicates('LATITUDE', inplace = True)
    Charging=Charging.reset_index()
    if Charging.shape[0]>0:
        for idx in Charging.index:
            textinfo.append("Charge Station: initial SOC:{:.1f}".format(float(Charging["SOC_%"][idx])))
            output_map.set_marker(Charging['LATITUDE'][idx],Charging['LONGITUDE'][idx], text=textinfo[idx+1],marker_color_circle="red")
    disp_lat=(Pstart[0]+Pend[0])/2
    disp_lng=(Pstart[1]+Pend[1])/2
    output_map.set_position(disp_lat,disp_lng)
    zoomlevel=8
    output_map.set_zoom(zoomlevel)
    return Pstart,Pend, SOClist[0]

def ShowChargeStation(input,output):
    location=input.get().split(" ")
    lat = float(location[0])
    lng = float(location[1])
    CSTitle, CSlocation=FindChargeStationnearby(lat,lng)
    print(CSTitle)
    marker_2=[]
    for i in range(len(CSlocation)):
        marker_2.append(output.set_marker(CSlocation[i][0],CSlocation[i][1], text=CSTitle[i],marker_color_circle="green"))
        
    output.set_zoom(11)
    return marker_2
    


def ChRatupdate(IteChRat,TTChRat,output,weight =10):
    ItTripChRat=sum(IteChRat)/len(IteChRat)*weight/10 if len(IteChRat)>0 else 0
    
    TTTripChRat=sum(TTChRat)/len(TTChRat)*weight/10 if len(TTChRat)>0 else 0
    output[0].config(text="{:.1f}".format(TTTripChRat))
    output[1].config(text="{:.1f}".format(ItTripChRat))

def TTRatupdate(IteChRat,TTChRat,outputarray,output,TTweight=10,ChWeight=10):
    output_SOC_Log=float(output['SOC'][4].cget("text"))
    output_dis_Log=float(output['Dis'][4].cget("text"))
    output_TTRat=output['TTRat']
    ItChRat=sum(IteChRat)/len(IteChRat)
    TTChRat=sum(TTChRat)/len(TTChRat)
    ItDrRat = norm(loc = output_SOC_Log , scale = .15*output_SOC_Log).pdf(outputarray[0][1])
    TTDrRat = norm(loc = output_SOC_Log , scale = .15*output_SOC_Log).pdf(outputarray[0][0])
    #ItDrRat=(1-abs(outputarray[0][1]/output_SOC_Log-1))*output_dis_Log/20
    #TTDrRat=(1-abs(outputarray[0][0]/output_SOC_Log-1))*output_dis_Log/20
    ItTTRat = ItChRat*ChWeight/10+ItDrRat*output_dis_Log*TTweight/10
    TTTTRat = TTChRat*ChWeight/10+TTDrRat*output_dis_Log*TTweight/10
    output_TTRat[0].config(text="{:.1f}".format(TTTTRat))
    output_TTRat[1].config(text="{:.1f}".format(ItTTRat))

def SOCupdate(result,output,decimal=2):
    for i in range(len(result)):
        if decimal == 2:
            output[i].config(text="{:.2f}".format(result[i]))
        elif decimal ==1:
            output[i].config(text="{:.1f}".format(result[i]))
        else:  
            output[i].config(text="{:.0f}".format(result[i]))

def isfloat(num):
    try:
        float(num[0])
        float(num[1])
        return True
    except ValueError:
        return False

def findCoord(start):
    if isinstance(start, str):
        Pstart=start.split(",")
    elif isinstance(start, tuple):
        Pstart=start
    else:
        print("start point coordination error")
        return
    if isfloat(Pstart):
        start_coord=[float(Pstart[0]),float(Pstart[1])]
    else:
        location1=obtainGPS_gmap(start)
        start_coord = [location1['lat'], location1['lng']]
    return start_coord


def APICompare(input,API_Summary,output_map,Fig1):
    output_SOC=API_Summary['SOC']
    output_dur=API_Summary['DDur']
    output_Chdur=API_Summary['ChDur']
    output_dis=API_Summary['Dis']
    output_ChRat=API_Summary['ChRat']
    output_map.delete_all_marker()
    output_map.delete_all_path()
    start,end,SOC,MinBL,Vehicle, RTTraffic=extract(input)
    result=[]
    start_coord=findCoord(start)
    end_coord=findCoord(end)

    EVrouting_TT=Eval_Tomtom(start_coord,end_coord,SOC,MinBL,Vehicle,RTTraffic)
    EVrouting_Iternio=Eval_Iternio(start_coord,end_coord,SOC,MinBL,Vehicle,RTTraffic)
    EVrouting_HERE=Eval_HERE(start_coord,end_coord,SOC,MinBL,Vehicle,RTTraffic)
    EVrouting_GADP_V0=GADP_RDR_V0(start,end,SOC,MinBL,Vehicle)
    TTsummary=EVrouting_TT.get_direction()
    Iterniosummary, IternioPathinfo = EVrouting_Iternio.get_direction()
    V0Summary, Gmapinfo,V0Chargeinfo = EVrouting_GADP_V0.V0_EV()
    HEREsummary=EVrouting_HERE.get_direction()
    result.append(TTsummary[:4])
    result.append(Iterniosummary[:4])
    result.append(V0Summary)
    result.append(HEREsummary[:4])
    outputarray=np.array(result).T

    SOCupdate(outputarray[0],output_SOC,1)
    SOCupdate(outputarray[1],output_dur)
    SOCupdate(outputarray[2],output_dis,0)
    SOCupdate(outputarray[3],output_Chdur)


    marker=[]
    marker.append(output_map.set_address(start, marker=True, text=start))

    path=[]
    for Iterniowaypoints in Iterniosummary[5]:
        path.append(output_map.set_path(Iterniowaypoints[0:-1:50],width=5))
    for TTwaypoints in TTsummary[5]:
        path.append(output_map.set_path(TTwaypoints[0:-1:50],color="brown",width=5))

    print("Charge direction from Iternio")
    IteChRat=[]
    for cs in Iterniosummary[4]:
        rating =IternioChrating(cs["charger"])
        IteChRat.append(rating)
        textinfo="arrival perc:{:.1f} %, depart perc:{:.1f} %, charge energy: {:.1f} kWh, charge dur: {:.1f} h, CS Rating: {:.0f}".format(cs["arrival_perc"],cs["departure_perc"],cs["charge_energy"],cs["charge_duration"]/3600,rating)
        marker.append(output_map.set_position(cs["location"][0],cs["location"][1], marker=True, text=textinfo,marker_color_circle="blue"))
    json_data1 = json.dumps(Iterniosummary[4],indent=4)

    print(json_data1)
    print("*********************************************************")
    print("Charge direction from TomTom")
    TTChRat=[]
    for cs in TTsummary[4]:
        if cs["charger"]=='NA':
            rating =0
        else:
            rating=TTChrating(cs["charger"])
            TTChRat.append(rating)
        textinfo="arrival perc:{:.1f} %, depart perc:{:.1f} %, charge energy: {:.1f} kWh, charge dur: {:.1f} h, CS Rating: {:.0f}".format(cs["arrival_perc"],cs["departure_perc"],cs["charge_energy"],cs["charge_duration"]/3600,rating)
        marker.append(output_map.set_position(cs["location"][0],cs["location"][1], marker=True, text=textinfo,marker_color_circle="yellow"))

    marker.append(output_map.set_address(end, marker=True, text=end,marker_color_circle="green"))
    print("*********************************************************")
    for HERECS in HEREsummary[5]:
        HERECSlat=HERECS['arrival']['place']['location']['lat']
        HERECSlngt=HERECS['arrival']['place']['location']['lng']
        HEREarrivalcharge=HERECS['arrival']['charge']
        HEREDepartCharge= HERECS["postActions"][0]['targetCharge'] if "postActions" in HERECS else 0
        HEREcharge = HERECS["postActions"][0]['targetCharge']-HERECS["postActions"][0]['arrivalCharge'] if "postActions" in HERECS else 0
        HEREchargeDur=HERECS["postActions"][0]['duration']/3600 if "postActions" in HERECS else 0
        textinfo="arrival perc:{:.1f} %, depart perc:{:.1f} %, charge energy: {:.1f} kWh, charge dur: {:.1f} h".format(HEREarrivalcharge,HEREDepartCharge,HEREcharge,HEREchargeDur)
        marker.append(output_map.set_position(HERECSlat,HERECSlngt, marker=True, text=textinfo,marker_color_circle="purple"))

    print("*********************************************************")
    if False:
        for V0CS in V0Chargeinfo:
            V0CSlat=V0CS['location'][0]
            V0CSlng=V0CS['location'][1]
            #cs["arrival_perc"],cs["departure_perc"],cs["charge_energy"],cs["charge_duration"]/3600,rating
            #textinfo="arrival perc:{:.1f} %, depart perc:{:.1f} %, charge energy: {:.1f} kWh, charge dur: {:.1f} h, CS Rating: {:.0f}".format(cs["arrival_perc"],cs["departure_perc"],cs["charge_energy"],cs["charge_duration"]/3600,rating)
            textinfo="V0"
            marker.append(output_map.set_position(V0CSlat,V0CSlng, marker=True, text=textinfo,marker_color_circle="grey"))


    ChRatupdate(IteChRat,TTChRat,output_ChRat,int(input[9].get()))
    try: 
        SOCDrop = float(API_Summary['SOC'][4].cget("text"))
        TTRatupdate(IteChRat,TTChRat,outputarray,API_Summary,int(input[10].get()),int(input[9].get()))
    except:
        pass
        

    PlotSig(IternioPathinfo,TTsummary,HEREsummary,Fig1)

    json_data2 = json.dumps(TTsummary[4],indent=4)
    print(json_data2)

    disp_lat=(start_coord[0]+end_coord[0])/2
    disp_lng=(start_coord[1]+end_coord[1])/2
    output_map.set_position(disp_lat,disp_lng)
    zoomlevel=round(17.256-1.443*math.log(TTsummary[2]*2.5))
    output_map.set_zoom(zoomlevel)
    return marker

def SortTimeStamp(csvfile):
    csvfile['TripMinute']=pd.to_datetime(csvfile['HEAD_COLL_TIMS'],utc=True)
    triptime=[]
    for index, row in csvfile.iterrows():
        triptime.append(row['TripMinute']+pd.Timedelta(seconds=row['SECONDS']))
    csvfile['TripTime']=triptime
    csvfile=csvfile.sort_values(by=['TripTime']).dropna()
    return csvfile.reset_index()

def readfile(directory_path):
    # Create an empty list to store the DataFrames
    dataframes = []
    charginginfo=[]
    filenames=[]
    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)
            # Read the CSV file into a DataFrame and append it to the list
            #df = pd.read_csv(file_path,header=0,usecols =Logchannels)
            df = pd.read_csv(file_path)
            df=SortTimeStamp(df)
            charginginfo.append([findChargeinfo(df)])
            dataframes.append(df.iloc[[0, -1], :])
            filenames.append(os.path.splitext(filename)[0])
    # Print the list of DataFrames
    return dataframes, charginginfo,filenames

def testextract(data):
    start=(data['LATITUDE'].head(1),data['LONGITUDE'].head(1))
    end=(data['LATITUDE'].tail(1),data['LONGITUDE'].tail(1))
    SOC=(data['SOC_%'].head(1),data['SOC_%'].tail(1))
    Odometer=(data['ODOMETER'].head(1),data['ODOMETER'].tail(1))
    return start,end,SOC,Odometer

def getMatricsinfo(input):
    file_path=input[8].get()
    vehicle=input[4].get()
    ch_weight=int(input[9].get())
    dr_weight=int(input[10].get())
    return file_path, vehicle, ch_weight, dr_weight

def exportfile(TTsummary,Iterniosummary,HEREsummary,idx,path='result',V0summary=''):
    TTjson = json.dumps(TTsummary, indent=4)
    with open("%s\Charge_TT_%d.json"%(path,idx), "w") as outfile:
        outfile.write(TTjson)
    Iterniojson = json.dumps(Iterniosummary, indent=4)
    with open("%s\Charge_Iternio_%d.json"%(path,idx), "w") as outfile:
        outfile.write(Iterniojson)
    HEREjson = json.dumps(HEREsummary, indent=4)
    with open("%s\Charge_HERE_%d.json"%(path,idx), "w") as outfile:
        outfile.write(HEREjson)
    if V0summary !='':
        V0json = json.dumps(V0summary, indent=4)
        with open("%s\Charge_V0_%d.json"%(path,idx), "w") as outfile:
            outfile.write(V0json)
    print("BEV trip tested: %d"%(idx))


def MatrixTest(input,output_map,API_Summary,Figure1):
    file_path, Vehicle, ch_weight, dr_weight =getMatricsinfo(input)

    result=[]
    score=[]
    print ("loading test matrix file...")
    with open(file_path) as f:
        testmatrix=pd.read_excel(file_path, index_col=None) 
        if testmatrix.shape[0]>0:
            textinfo=[]
            cities=[]
            for idx in testmatrix.index:
                start_coord = findCoord(testmatrix['start'][idx])
                end_coord=findCoord(testmatrix['end'][idx])
                SOC=float(testmatrix["SOC_%"][idx])
                MinBL=float(testmatrix["MinBL"][idx])

                EVrouting_TT=Eval_Tomtom(start_coord,end_coord,SOC,MinBL,Vehicle)
                EVrouting_Iternio=Eval_Iternio(start_coord,end_coord,SOC,MinBL,Vehicle)
                EVrouting_HERE=Eval_HERE(start_coord,end_coord,SOC,MinBL,Vehicle)

                TTsummary=EVrouting_TT.get_direction()
                Iterniosummary, IternioPathinfo=EVrouting_Iternio.get_direction()
                HEREsummary = EVrouting_HERE.get_direction()
                #EVrouting_GADP_V0=GADP_RDR_V0(start_coord,end_coord,SOC,MinBL,Vehicle)
                #V0Summary, Gmapinfo, Chargeinfo =EVrouting_GADP_V0.V0_EV()
                
                TTChScore = sum(TTsummary[6])/len(TTsummary[6])*ch_weight/10 if len(TTsummary[6])>0 else 3
                result.append(TTsummary[:4])
                score.append([TTChScore,idx])
                ItChScore = sum(Iterniosummary[6])/len(Iterniosummary[6])*ch_weight/10 if len(Iterniosummary[6])>0 else 3
                result.append(Iterniosummary[:4])
                score.append([ItChScore,idx])
                #result.append(V0Summary)
                HEREChScore = sum(HEREsummary[6])/len(HEREsummary[6])*ch_weight/10 if len(HEREsummary[6])>0 else 3
                result.append(HEREsummary[:4])
                score.append([HEREChScore,idx])
                exportfile(TTsummary[4],Iterniosummary[4],HEREsummary[5],idx)
                
                
            headerlist="E(kWh),Drv_T(h),Dis(km),Chg_T(h),Ch_Score,Trip_Index"
            outputarray=np.concatenate([result,score],axis=1)
            #outputresult=pd.DataFrame(result)
            output_file = "result\matrixtest_output.csv"
            np.savetxt(output_file, outputarray, delimiter=',', header=headerlist)
            #outputresult.to_csv(output_file)
            print("Results are exported to",output_file)

def V0ChargeScore(V0Chargeinfo):
    CSnumber=len(V0Chargeinfo)
    if CSnumber>0:
        V0total = 0
        for V0CS in V0Chargeinfo:
            V0total+=V0CS['chscore']
        return V0total/CSnumber
    else:
        return 3
        
def Simulation(db_E):
    input=db_E[8]
    chweight=int(db_E[9].get())
    drweight=int(db_E[10].get())
    Vehicle=db_E[4].get()
    MinBL=float(db_E[3].get())

    reducedlog, chargeinfo,filenames =readfile(input.get())
    result=[]
    score=[]
    for idx, test in enumerate(reducedlog):

        start,end,SOC,Odometer=testextract(test)
        start_coord=findCoord(start)
        end_coord=findCoord(end)

        EVrouting_TT=Eval_Tomtom(start_coord,end_coord,SOC[0][0],MinBL,Vehicle)
        EVrouting_Iternio=Eval_Iternio(start_coord,end_coord,SOC[0][0],MinBL,Vehicle)
        EVrouting_HERE=Eval_HERE(start_coord,end_coord,SOC[0][0],MinBL,Vehicle)
        TTsummary=EVrouting_TT.get_direction()
        Iterniosummary, IternioPathinfo=EVrouting_Iternio.get_direction()
        EVrouting_GADP_V0=GADP_RDR_V0(start,end,SOC[0][0],MinBL,Vehicle)
        V0Summary, Gmapinfo,V0Chargeinfo=EVrouting_GADP_V0.V0_EV()
        HEREsummary = EVrouting_HERE.get_direction()
        result.append(TTsummary[:4])
        result.append(Iterniosummary[:4])
        result.append(V0Summary)
        result.append(HEREsummary[:4])
        
        
        TTTripDrRat=10
        ItTripDrRat=10
        [(TOTAL_Driving_SOC,TOTAL_Charging_SOC,TOTAL_Charging_Dur)] = chargeinfo[idx]
        output_SOC_Log=TOTAL_Driving_SOC*CC_dict[Vehicle]['BatterySize']/100 #SOC[0][0]-SOC[1].tolist()[0]
        output_dis_Log=Odometer[1].tolist()[0]-Odometer[0][0]
        ItTripDrRat = norm(loc = output_SOC_Log , scale = .15*output_SOC_Log).pdf(Iterniosummary[0])*output_dis_Log
        TTTripDrRat = norm(loc = output_SOC_Log , scale = .15*output_SOC_Log).pdf(TTsummary[0])*output_dis_Log
        V0DrRat =norm(loc = output_SOC_Log , scale = .15*output_SOC_Log).pdf(V0Summary[0])*output_dis_Log
        

        HEREDrRat =norm(loc = output_SOC_Log , scale = .15*output_SOC_Log).pdf(HEREsummary[0])*output_dis_Log
        

        TTTripChRat = sum(TTsummary[6])/len(TTsummary[6]) if len(TTsummary[6])>0 else 3
        ItTripChRat = sum(Iterniosummary[6])/len(Iterniosummary[6]) if len(Iterniosummary[6])>0 else 3
        V0ChScore = V0ChargeScore(V0Chargeinfo)
        HEREChScore = sum(HEREsummary[6])/len(HEREsummary[6])  if len(HEREsummary[6])>0 else 3

        ItTTScore = ItTripChRat*chweight/10+ItTripDrRat*drweight/10
        TTTTScore = TTTripChRat*chweight/10+TTTripDrRat*drweight/10
        V0Score = V0ChScore*chweight/10+V0DrRat*drweight/10
        HETTScore = HEREChScore*chweight/10+HEREDrRat*drweight/10
        score.append([TTTripChRat,TTTripDrRat,TTTTScore,idx])
        score.append([ItTripChRat,ItTripDrRat,ItTTScore,idx])
        score.append([V0ChScore,V0DrRat,V0Score,idx])
        score.append([HEREChScore,HEREDrRat,HETTScore,idx])
        exportfile(TTsummary[4],Iterniosummary[4],HEREsummary[5],idx,'log',V0Chargeinfo)
    headerlist="E(kWh),Drv_T(h),Dis(km),Chg_T(h),Ch_Score,Dr_Score,Trip_Score,Trip_Index"
    outputarray=np.concatenate([result,score],axis=1)
    #result=pd.DataFrame(outputarray,columns=headerlist)
    output_file = "log\output.csv"
    np.savetxt(output_file, outputarray, delimiter=',', header=headerlist)
    #result.to_csv(output_file, delimiter=",")
    print("Results are exported to",output_file)


def update_vehicle(input,output):
   output.delete(0,END)
   output.insert(0,input)

def update_plot(input,output,Fig1):
    output[5].delete(0,END)
    output[5].insert(0,input)

    
    file_path=output[6].get()
    
    if file_path!='' and file_path.endswith(".csv"):
        DLfilepath=os.path.dirname(file_path)
        print ("loading csv file..."+DLfilepath)
        with open(file_path) as f:
            channels=['LATITUDE','LONGITUDE','SOC_%','ODOMETER','ALTITUDE','SPEED_PER_SEC','SPEED_MODE_PER_MINUTE','HEAD_COLL_TIMS','SECONDS','OUTSIDE_TEMPERATURE_C']
            csvfile = pd.read_csv(f,header=0,usecols =channels)
            EndOdo=csvfile['ODOMETER'].max()
            StartOdo=csvfile['ODOMETER'].min()

            TDistance=EndOdo-StartOdo
            csvfile['Distance']=csvfile['ODOMETER']-StartOdo
            csvfile['TripMinute']=pd.to_datetime(csvfile['HEAD_COLL_TIMS'],utc=True)
            triptime=[]
            for index, row in csvfile.iterrows():
                triptime.append(row['TripMinute']+pd.Timedelta(seconds=row['SECONDS']))
            csvfile['TripTime']=triptime
            csvfile=csvfile.sort_values(by=['TripTime'])
            Startmin=(csvfile['TripTime'].min())
            Endmin=csvfile['TripTime'].max()
            TRIP_DURATION_H=str(Endmin-Endmin)
            plotselection=output[5].get()
        if plotselection=='Energy_km':
            ConsumptionPlot(csvfile[['Distance','SOC_%']],Fig1)
        elif plotselection=='Speed_km':
            SpeedPlot(csvfile[['Distance','SPEED_PER_SEC']],Fig1)
        elif plotselection=='Speed_time':
            SpeedPlotTime(csvfile[['TripTime','SPEED_PER_SEC']],Fig1)
        elif plotselection=='Elevation_km':
            ElevationPlot(csvfile[['Distance','ALTITUDE','OUTSIDE_TEMPERATURE_C']],Fig1)
        elif plotselection=='Histogram':
            Histoplot(csvfile[['SPEED_MODE_PER_MINUTE','SOC_%','HEAD_COLL_TIMS']],Fig1)
        elif plotselection=='SOC_time':
            TimeSeriesPlot(csvfile[['TripTime','SPEED_PER_SEC','SOC_%']],Fig1)
        elif plotselection=='Anxiety':
            Anxietyplot(csvfile[['TripMinute','SOC_%','HEAD_COLL_TIMS']],Fig1)
    #Figure.clf()
    #Figure.canvas.draw()

def update_plot1(input, output, fig1):
    # Clear the input field and insert the new input value
    output[5].delete(0, END)
    output[5].insert(0, input)

    # Load the CSV file
    file_path = output[6].get()
    if file_path and file_path.endswith(".csv"):
        print(f"Loading CSV file: {file_path}")
        try:
            # Read the CSV file and extract the required columns
            channels = ['LATITUDE', 'LONGITUDE', 'SOC_%', 'ODOMETER', 'ALTITUDE', 'SPEED_PER_SEC', 'SPEED_MODE_PER_MINUTE', 'HEAD_COLL_TIMS', 'SECONDS', 'OUTSIDE_TEMPERATURE_C']
            df = pd.read_csv(file_path, usecols=channels)

            # Calculate trip information
            end_odo = df['ODOMETER'].max()
            start_odo = df['ODOMETER'].min()
            distance = end_odo - start_odo
            df['Distance'] = df['ODOMETER'] - start_odo
            df['TripTime'] = pd.to_datetime(df['HEAD_COLL_TIMS'], utc=True) + pd.to_timedelta(df['SECONDS'], unit='s')
            df = df.sort_values(by=['TripTime'])
            start_min = df['TripTime'].min()
            end_min = df['TripTime'].max()
            trip_duration_h = str(end_min - end_min)

            # Plot the selected data
            plot_selection = output[5].get()
            if plot_selection == 'Energy_km':
                ConsumptionPlot(df[['Distance', 'SOC_%']], fig1)
            elif plot_selection == 'Speed_km':
                SpeedPlot(df[['Distance', 'SPEED_PER_SEC']], fig1)
            elif plot_selection == 'Speed_time':
                SpeedPlotTime(df[['TripTime', 'SPEED_PER_SEC']], fig1)
            elif plot_selection == 'Elevation_km':
                ElevationPlot(df[['Distance', 'ALTITUDE', 'OUTSIDE_TEMPERATURE_C']], fig1)
            elif plot_selection == 'Histogram':
                Histoplot(df[['SPEED_MODE_PER_MINUTE', 'SOC_%', 'HEAD_COLL_TIMS']], fig1)
            elif plot_selection == 'SOC_time':
                TimeSeriesPlot(df[['TripTime', 'SPEED_PER_SEC', 'SOC_%']],fig1)
            elif plot_selection=='Anxiety':
                Anxietyplot(df[['TripMinute','SOC_%','HEAD_COLL_TIMS']],fig1)
        except:
            print("An exception occurred")



def RetentOpt(Entry,Button,Option):
    if Button.cget('text')==Option[0]:
        Button.config(text=Option[1])
        Entry.delete(0,END)
        Entry.insert(0,Option[1])
    elif Button.cget('text')==Option[1]:
        Button.config(text=Option[0])
        Entry.delete(0,END)
        Entry.insert(0,Option[0])
    else:
        pass

def clear(API_Summary,output_map,Figure,db_E):
    for i in range(5):
        API_Summary['SOC'][i].config(text=" ")
        API_Summary['DDur'][i].config(text=" ")
        API_Summary['ChDur'][i].config(text=" ")
        API_Summary['Dis'][i].config(text=" ")
        API_Summary['ChRat'][i].config(text=" ")
        API_Summary['TTRat'][i].config(text=" ")
    output_map.delete_all_marker()
    output_map.delete_all_path()
    Figure.clf()
    Figure.canvas.draw()
    for i in range(0,4):
        db_E[i].delete(0,END)
        db_E[i].insert(0,'')
    db_E[4].delete(0,END)
    db_E[4].insert(0,'EC4')
    db_E[5].delete(0,END)
    db_E[5].insert(0,'Energy_km')
    db_E[6].delete(0,END)
    db_E[6].insert(0,'')
    db_E[7].delete(0,END)
    db_E[7].insert(0,'Retent On')