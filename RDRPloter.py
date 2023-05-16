import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from APIConf import APIconfig

def get_tripinfo(section):        
    travelTime = section['summary']['duration']/3600
    travelkm = section['summary']['length']/1000
    
    if 'consumption' in  section['summary']:
        departurecharge=section['departure']['charge']
        arrivalcharge=section['arrival']['charge']
        travelEnergy =departurecharge-arrivalcharge
        
        if 'postActions' in section:
            chargeTime = section['postActions'][0]['duration']/3600
            chargeEnergy =section['postActions'][0]['targetCharge']-section['postActions'][0]['arrivalCharge']
        else:
            chargeTime = 0
            chargeEnergy =0
    else:
        print("special travel type, such as ferry")
    return [travelkm,travelTime-chargeTime,travelEnergy,arrivalcharge,chargeEnergy,chargeTime,departurecharge]


def PlotSig(IternioPathinfo,TTSummary,HEREsummary,Fig1):
    SignalName=APIconfig["Iternio"]["path"]
    IternioInfo=[]
    TomTomInfo=[]
    HEREInfo=[]
    for data in IternioPathinfo:
        IternioInfo.append(pd.DataFrame(data,columns =APIconfig["Iternio"]["path"]))
    Iteroutput=["speed [km/h]","cons_per_km [Wh/km]","remaining_dist [km]","soc_perc [SoC %]"]
    IterInfo=pd.concat(IternioInfo)
    for data in TTSummary[4]:
        del data['location']
        TomTomInfo.append(pd.DataFrame(data,index=[0],columns =APIconfig["TomTom"]["path"][:-1]))
    totaldistance =0
    HERETripData=[]
    for HEREdata in HEREsummary[5]:
        secdata= get_tripinfo(HEREdata)
        HERETripData.append([totaldistance,secdata[6]/46.3*100])
        totaldistance +=secdata[0]
        HERETripData.append([totaldistance,secdata[3]/46.3*100])
        
        #HEREInfo.append(pd.DataFrame(secdata,index=[0],columns =['drive_km','drive_hour','batteryConsum','arrival_perc','charge_energy','charge_duration','departure_perc','mileage']))
        #TomTomInfo.append(pd.DataFrame.from_dict(data))
    TTInfo=pd.concat(TomTomInfo).reset_index()
    InitialSOC=TTInfo['arrival_perc']+TTInfo['batteryConsum']/46.3*100
    new_row = pd.DataFrame({'drive_km':0, 'arrival_perc':InitialSOC, 'departure_perc':InitialSOC},index =[0])
    TTInfo = pd.concat([new_row, TTInfo]).reset_index(drop = True)
    #TTInfo['soc_perc [SoC %]']=TTInfo['batteryConsum']/CC_dict['EC4']['BatterySize']*100
    TToutput=['drive_km','batteryConsum','arrival_perc','departure_perc']
    PlotAPIData(IterInfo[Iteroutput],TTInfo[TToutput],Fig1,HERETripData)

def PlotAPIData(IterData,TTData,Figure,HEREData=[]):

    '''
    Figure.clf()
    ax1 = Figure.add_subplot(2,1,1)
    item1 = IterData.columns[0]
    Vmin = IterData[item1].min()
    Vmax = IterData[item1].max()

    ax1.set_xlabel(item1)
    ax1.set_ylabel('Occurance')

    n = 30
    step = (Vmax - Vmin)/(n-1)
    bin_x = np.arange(Vmin, Vmax+2*step, step)
    ax1=plt.hist(IterData[item1],bins=bin_x)
    #Figure.suptitle('1D Histogram')
    Figure.canvas._tkcanvas.pack(side= "top", fill= "x", expand=True)
    #SigPlot1.get_tk_widget().grid(row=1, sticky="nesw")
    Figure.canvas.draw()
    '''
    item3 = IterData.columns[2]
    TDistance = IterData[item3].max()
    IterData['mileage']=TDistance-IterData[item3]
    ax1 = Figure.add_subplot(2,1,1)

    ax1.set_xlabel('mileage [km]')
    ax1.set_ylabel('SOC_%')
    #data_resampled.plot('cons_per_km [Wh/km]')
    IterData.plot(x='mileage',y='soc_perc [SoC %]',ax=ax1,zorder=2,label="Iternio Estimate")
    Tomtomdata=[]
    distance=0
    for index, row in TTData.iterrows():
        distance=row['drive_km']+distance
        Tomtomdata.append({'mileage':distance,'soc_perc [SoC %]':row['arrival_perc']})
        Tomtomdata.append({'mileage':distance+0.001,'soc_perc [SoC %]':row['departure_perc']})
    FinalTTdata=pd.DataFrame(Tomtomdata).iloc[1:-1]
    FinalTTdata.plot(x='mileage',y='soc_perc [SoC %]', ax=ax1, zorder=3, linestyle='dashed',marker='o',  label='TomTom Estimate')
    if len(HEREData)>0:
        FinalHEREdata=pd.DataFrame(HEREData,columns =['mileage','soc_perc [SoC %]'])

        FinalHEREdata.plot(x='mileage',y='soc_perc [SoC %]', ax=ax1, zorder=4, linestyle='dotted',marker='x',  label='HERE Estimate')
        
    Figure.suptitle('SOC')
    Figure.canvas._tkcanvas.pack(side= "top", fill= "x", expand=True)
    Figure.canvas.draw()

    ax2 = Figure.add_subplot(2,1,2)
    


    ax2.set_xlabel('mileage [km]')
    ax2.set_ylabel('cons_per_km [Wh/km]')

    IterData.plot(x='mileage',y='cons_per_km [Wh/km]',ax=ax2,zorder=2,label="Iternio Estimate")
    Figure.suptitle('BEV Trip Log Vs Estimated SOC')
    Figure.canvas._tkcanvas.pack(side= "bottom", fill= "x", expand=True)
    Figure.canvas.draw()

def ConsumptionPlot(data, Figure):
    data=data.drop_duplicates(subset=['Distance'])
    TDistance=int(data['Distance'].max())
    data.set_index('Distance',inplace =True)

    Xresampled = list(range(0,TDistance))
    data_resampled = data.reindex(data.index.union(Xresampled)).interpolate('values').loc[Xresampled]
    data_resampled['cons_per_km [Wh/km]']=-data_resampled['SOC_%'].diff()*463
    data_resampled=data_resampled.iloc[1:]

    Signplot(data_resampled,Figure)

def SpeedPlot(data, Figure):
    data=data.drop_duplicates(subset=['Distance'])
    TDistance=int(data['Distance'].max())
    data.set_index('Distance',inplace =True)

    Xresampled = list(range(0,TDistance))
    data_resampled = data.reindex(data.index.union(Xresampled)).interpolate('values').loc[Xresampled]
    data_resampled['Accel [m/s2]']=data_resampled['SPEED_PER_SEC'].diff()
    data_resampled=data_resampled.iloc[1:]

    Signplot(data_resampled,Figure)

def SpeedPlotTime(data, Figure):


    data['SpeedDiff']=data['SPEED_PER_SEC'].diff()
    data['TimeDiff']=data['TripTime'].diff().dt.total_seconds()
    data=data.iloc[1:]
    data['Accel [m/s2]']=data['SpeedDiff']/data['TimeDiff']
    data.rename(columns={'SPEED_PER_SEC':'Speed [km/h]'}, inplace=True)
    TimeSeriesPlot(data[['TripTime','Speed [km/h]','Accel [m/s2]']],Figure)

def ElevationPlot(data, Figure):
    data=data.drop_duplicates(subset=['Distance'])
    TDistance=int(data['Distance'].max())
    data.set_index('Distance',inplace =True)

    Xresampled = list(range(0,TDistance))
    data_resampled = data.reindex(data.index.union(Xresampled)).interpolate('values').loc[Xresampled]

    Signplot(data_resampled,Figure)

def TimeSeriesPlot(data, Figure):
    x1label=data.columns[0]
    y1label=data.columns[1]
    x2label=data.columns[0]
    y2label=data.columns[2]
    Figure.clf()
    ax1 = Figure.add_subplot(2,1,1)

    ax1.set_xlabel(x1label)
    ax1.set_ylabel(y1label)

    data.plot(x=x1label,y=y1label,ax=ax1,zorder=3,label="Trip Log")
    #Figure.suptitle('1D Histogram')
    Figure.canvas._tkcanvas.pack(side= "top", fill= "x", expand=True)
    Figure.canvas.draw()

    ax2 = Figure.add_subplot(2,1,2)

    ax2.set_xlabel(x2label)
    ax2.set_ylabel(y2label)
    #data_resampled.plot(y=y2label,ax=ax2,zorder=3,ylim=(-200,600),label="Trip Log")
    data.plot(x=x2label,y=y2label,ax=ax2,zorder=3,label="Trip Log")
    Figure.suptitle('Time Series')
    Figure.canvas._tkcanvas.pack(side= "bottom", fill= "x", expand=True)
    Figure.canvas.draw()

def Signplot(data_resampled,Figure):
    x1label=data_resampled.index.name
    y1label=data_resampled.columns[0]
    x2label=data_resampled.index.name
    y2label=data_resampled.columns[1]
    Figure.clf()
    ax1 = Figure.add_subplot(2,1,1)

    ax1.set_xlabel(x1label)
    ax1.set_ylabel(y1label)

    data_resampled.plot(y=y1label,ax=ax1,zorder=3,label="Trip Log")
    #Figure.suptitle('1D Histogram')
    Figure.canvas._tkcanvas.pack(side= "top", fill= "x", expand=True)
    Figure.canvas.draw()

    ax2 = Figure.add_subplot(2,1,2)

    ax2.set_xlabel(x2label)
    ax2.set_ylabel(y2label)
    #data_resampled.plot(y=y2label,ax=ax2,zorder=3,ylim=(-200,600),label="Trip Log")
    data_resampled.plot(y=y2label,ax=ax2,zorder=3,label="Trip Log")
    Figure.suptitle('Trip Mileage Based Data')
    Figure.canvas._tkcanvas.pack(side= "bottom", fill= "x", expand=True)
    Figure.canvas.draw()

def Anxietyplot(data,Figure):
    data=data.drop_duplicates(subset=['TripMinute'])
    x1label='Time [min]'
    y1label='Used SOC [%]'
    data[x1label]=data['TripMinute']-data['TripMinute'].min()
    data[x1label]=data[x1label].dt.total_seconds()/60

    data[y1label]=100-data['SOC_%']


    Figure.clf()
    ax1 = Figure.add_subplot(2,1,1)
    n = 40
    Tmin = data[x1label].min()
    Tmax = data[x1label].max()
    step = (Tmax - Tmin)/(n-1)
    bin_x = np.arange(Tmin, Tmax+2*step, step)

    Vmin = data[y1label].min()
    Vmax = data[y1label].max()

    ax1.set_xlabel(x1label)
    ax1.set_ylabel(y1label)


    step = (Vmax - Vmin)/(n-1)
    bin_y1 = np.arange(Vmin, Vmax+2*step, step)
    my_cmap = plt.cm.jet
    my_cmap.set_under('w',1)
    ax1=plt.hist2d(data[x1label],data[y1label],bins=(bin_x,bin_y1),cmin = 1,cmap=my_cmap)

    Figure.canvas._tkcanvas.pack(side= "top", fill= "x", expand=True)
    Figure.canvas.draw()
    
    ax2 = Figure.add_subplot(2,1,2)
    x2label=x1label
    y2label='Anxiet idx'
    data[y2label]=data[y1label].apply(lambda x: 0 if x<70 else x*x/100)

    ax2.set_xlabel(x2label)
    ax2.set_ylabel(y2label)
    m = 40
    A2min = data[y2label].min()
    A2max = data[y2label].max()
    step = (A2max - A2min)/(m-1)
    bin_y2 = np.arange(A2min, A2max+2*step, step)
    my_cmap = plt.cm.jet
    my_cmap.set_under('w',1)
    ax1=plt.hist2d(data[x2label],data[y2label],bins=(bin_x,bin_y2),cmin = 1,cmap=my_cmap)

    Figure.canvas._tkcanvas.pack(side= "bottom", fill= "x", expand=True)
    Figure.canvas.draw()
    
def Histoplot(data,Figure):
    data=data.drop_duplicates(subset=['HEAD_COLL_TIMS'])
    x1label=data.columns[0]
    x2label=data.columns[1]

    Figure.clf()
    ax1 = Figure.add_subplot(2,1,1)

    Vmin = data[x1label].min()
    Vmax = data[x1label].max()

    ax1.set_xlabel(x1label)
    ax1.set_ylabel('Minute')

    n = 40
    step = (Vmax - Vmin)/(n-1)
    bin_x = np.arange(Vmin, Vmax+2*step, step)
    ax1=plt.hist(data[x1label],bins=bin_x)
    Figure.canvas._tkcanvas.pack(side= "top", fill= "x", expand=True)
    Figure.canvas.draw()

    ax2 = Figure.add_subplot(2,1,2)

    ax2.set_xlabel(x2label)
    ax2.set_ylabel('Minute')
    m = 50
    step = (Vmax - Vmin)/(m-1)
    bin_x2 = np.arange(Vmin, Vmax+2*step, step)
    ax1=plt.hist(data[x2label],bins=bin_x2)
    Figure.suptitle('Trip Histogram')
    Figure.canvas._tkcanvas.pack(side= "bottom", fill= "x", expand=True)
    Figure.canvas.draw()