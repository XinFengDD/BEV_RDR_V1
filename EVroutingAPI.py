import requests,os,sys,json
import numpy as np
from datetime import datetime
import urllib.parse as urlparse
from VehConfig import CC_dict
from APIConf import APIconfig
from RDRV0Rating import *
from Credential import *
import geopy.distance
os.environ['REQUESTS_CA_BUNDLE']=os.path.join(os.path.dirname(sys.argv[0]),'cacert.pem')
#from tomtom_apikey import api_key


import googlemaps
gmaps = googlemaps.Client(key=Credential['googlemap']['key'])
def locationrating(CS_coord,Route_coord):
    distance=geopy.distance.geodesic(CS_coord, Route_coord).km
    locationscore = 4-0.25*distance
    return locationscore

def FindChargeStationnearby(lat1,lon1,RDR=5,maxCSpt = 5):
    params = {"latitude": lat1, "longitude": lon1, "output": "json", "compact": True, "verbose": False, "maxresults": maxCSpt, "distance":RDR,"distanceunit":"miles"}
    data = requests.get(Credential['OpenChargemap']['endpoint'], params = params, headers={"X-API-Key" : Credential['OpenChargemap']['key']})
    if data.status_code == 200:
        CSlist = json.loads(data.text)
        CSTitle = []
        CSlocation = []
        OutletNumber=[]
        try:
            for CS in CSlist:
                CSTitle.append(CS['AddressInfo']['Title'])
                CSlocation.append((CS['AddressInfo']['Latitude'],CS['AddressInfo']['Longitude']))
                OutletNumber.append(len(CS['Connections']))
            return CSTitle, CSlocation,OutletNumber
        except ValueError:
                print("Error, No charge station is found nearby! ")
    else:
        print("Error, API status code = ",data.status_code)

class GADP_RDR_V0:
    def __init__(self, start,end,SOC,MinBL,Vehicle,traffic="true"):
        self.now = datetime.now()
        self.start= start
        self.end=end
        self.SOC=SOC
        self.MinBL=MinBL
        self.Vehicle=Vehicle
        self.traffic=traffic


    def CalConsumW(self,velocity,distance,vehicle):
        ConsumEnergy=distance/1000*0.621*np.interp(velocity, CC_dict[vehicle]['V0']['CCspd'], CC_dict[vehicle]['V0']['CCrate'])
        return ConsumEnergy

    def CalculateEC(self,directions_result,vehicle):
        TripW=0
        for step in directions_result['steps']:
            velocity=step['distance']['value']/step['duration']['value']*2.237
            ConsumW=self.CalConsumW(velocity,step['distance']['value'],vehicle)
            TripW=TripW+ConsumW
        return TripW

    def V0_EV(self):
        directions_result = gmaps.directions(self.start,self.end,departure_time=self.now)

        AuxLoss=CC_dict[self.Vehicle]['V0']['VehEELoss']+CC_dict[self.Vehicle]['V0']['HVACLoss']+CC_dict[self.Vehicle]['V0']['AgeCharging']+CC_dict[self.Vehicle]['V0']['VehLoad']
        ExternalImpact=CC_dict[self.Vehicle]['V0']['TrafficImpact']+CC_dict[self.Vehicle]['V0']['WindImpact']+CC_dict[self.Vehicle]['V0']['TempImpact'] 
        TripW=self.CalculateEC(directions_result[0]['legs'][0],self.Vehicle)*(1+AuxLoss+ExternalImpact)
        SOCdrop=TripW/1000/CC_dict[self.Vehicle]['BatterySize']*100
        FinalSOC = self.SOC-SOCdrop if SOCdrop<self.SOC else 0
        duration=directions_result[0]['legs'][0]['duration']['value']/3600
        duration_in_traffic=directions_result[0]['legs'][0]['duration_in_traffic']['value']/3600
        distance=directions_result[0]['legs'][0]['distance']['value']/1000
        chargeTime=0
        Gmap_pathinfo=directions_result[0]['legs'][0]['steps']
        chargeinfo = self.findCS(Gmap_pathinfo)
        return [TripW/1000,duration_in_traffic,distance,chargeTime] , Gmap_pathinfo, chargeinfo                                               

    def findCS(self,pathsinfo):
        TripW = 0
        startsearch={}
        endsearch={}
        idx = 0
        pathlen=len(pathsinfo)
        chargeinfo=[]
        while idx <pathlen:
            while (self.SOC>self.MinBL+5) and (idx <pathlen):
                velocity=pathsinfo[idx]['distance']['value']/pathsinfo[idx]['duration']['value']*2.237
                ConsumW=self.CalConsumW(velocity,pathsinfo[idx]['distance']['value'],self.Vehicle)
                SOCdrop=ConsumW/1000/CC_dict[self.Vehicle]['BatterySize']*100
                self.SOC -=SOCdrop
                idx +=1
            lat = pathsinfo[idx-1]['end_location']['lat']
            lng = pathsinfo[idx-1]['end_location']['lng']
            CSTitle, CSlocation,OutletNumber=FindChargeStationnearby(lat,lng,5,10)
            if len(CSTitle)<1:
                CSTitle, CSlocation,OutletNumber=FindChargeStationnearby(pathsinfo[idx-1]['start_location']['lat'],pathsinfo[idx-1]['start_location']['lng'],10,10)
            maxscore,Selectedlocation,SelectedTitle = self.RefineChargeStations(CSTitle, CSlocation,OutletNumber,(lat,lng))
            ChargeSOC,ChargeDuration = self.Charging(Selectedlocation)
            chargeinfo.append({'name':SelectedTitle,'location':Selectedlocation,'chscore':maxscore,'chargeSOC':ChargeSOC,'chargedur':ChargeDuration})
        return chargeinfo
    
    def RefineChargeStations(self, CSTitle, CSlocation, OutletNumber,route_coord ):
        score = []
        for idx, Title in enumerate(CSTitle):
            networkscore = networkrating(Title.casefold())
            outletscore=outletrating(OutletNumber[idx])
            locationscore=locationrating(CSlocation[idx],route_coord)
            score.append(networkscore+outletscore+locationscore)
        selectedidx=score.index(max(score))
        return max(score),CSlocation[selectedidx],CSTitle[selectedidx]

    def Charging(self, Selectedlocation):
        targetSOC=80
        ChargeSOC=targetSOC - self.SOC
        chargePower = 80
        ChargeDuration = ChargeSOC*CC_dict[self.Vehicle]['BatterySize']/chargePower
        self.SOC=targetSOC
        return ChargeSOC,ChargeDuration

class Eval_Tomtom:
    def __init__(self, start,end,SOC,MinBL,Vehicle,traffic="true",travelmode="car",avoidfeatures="unpavedRoads"):
        self.now = datetime.now()
        # Building the request URL
        self.baseUrl = Credential["TomTom"]["endpoint"]
        self.isoUrl = Credential["TomTom"]["endpoint_iso"]
        self.Tomtomoutput="RoutingAPI\TrailRoute_output.json"
        self.routeType = "fastest"                        # Fastest route
        self.traffic = traffic                            # To include Traffic information
        self.travelMode = travelmode                         # Travel by car
        self.avoid = avoidfeatures                       # Avoid unpaved roads
        self.departAt = self.now.strftime("%Y-%m-%dT%H:%M:%S")
        self.vehicleCommercial = "false"                   # Commercial vehicle 
        self.api_key=Credential["TomTom"]["key"]
        self.start=str(start[0])+","+str(start[1])
        self.end=str(end[0])+","+str(end[1])
        self.batterysize=CC_dict[Vehicle]['BatterySize']
        CombinCurve = lambda x, y : str(x)+','+str(y/10*CC_dict[Vehicle]['CCCoeff'])+':'
        ECureve = ''.join(map(lambda x, y: CombinCurve(x,y), CC_dict[Vehicle]['CCspd'], CC_dict[Vehicle]['CCrate']))
        self.ECurve=ECureve[:-1]
        self.currentChargeInkWh=SOC*self.batterysize/100
        self.minChargeAtDestinationInkWh=MinBL*self.batterysize/100
        self.chargePara=CC_dict[Vehicle]['ChargeParaTT']

    def get_direction(self):
        requestEVParams = (
            urlparse.quote(self.start) + ":" + urlparse.quote(self.end) 
            + "/json?vehicleEngineType=electric"
            + "&traffic=" + self.traffic
            #+ "&travelMode=" + self.travelMode
            #+ "&avoid=" + self.avoid 
            + "&constantSpeedConsumptionInkWhPerHundredkm=" + self.ECurve
            + "&maxChargeInkWh="+str(self.batterysize)
            + "&currentChargeInkWh="+str(self.currentChargeInkWh)
            + "&minChargeAtDestinationInkWh="+str(self.minChargeAtDestinationInkWh)
            + "&minChargeAtChargingStopsInkWh="+str(self.minChargeAtDestinationInkWh)
            + "&departAt=" + urlparse.quote(self.departAt)
            )

        self.requestUrl = self.baseUrl + requestEVParams + "&key=" + self.api_key
        # Sending the request
        response = requests.post(self.requestUrl, json=self.chargePara)
        if(response.status_code == 200):
            # Get response's JSON
            jsonResult = response.json()
            # Read summary of the first route
            routeSummary = jsonResult['routes'][0]['summary']
            
            # Read ETA
            # eta = routeSummary['arrivalTime']
            travelEnergy = routeSummary['batteryConsumptionInkWh']
            if 'totalChargingTimeInSeconds' in routeSummary.keys():
                chargetime = routeSummary['totalChargingTimeInSeconds'] 
            else:
                chargetime=0
            travelTime = (routeSummary['travelTimeInSeconds']-chargetime) / 3600
            chargeTime = (chargetime) / 3600
            travelkm=routeSummary['lengthInMeters']/1000
            chargeinfo, chargeScore=self.get_chargeinfo(jsonResult['routes'][0]['legs'])
            routinginfo=self.get_routinginfo(jsonResult['routes'][0]['legs'])
            
        else:
            travelEnergy=0
            travelTime=0
            travelkm=0
            chargeTime=0
            chargeinfo=[]
            routinginfo=[]
            chargeScore=[]
            print("Tomtom EV API Error")
        return [travelEnergy,travelTime,travelkm,chargeTime,chargeinfo,routinginfo,chargeScore]

    def get_chargeinfo(self,steps):
        charging=[]
        chargeScore=[]
        for j in range(len(steps)):
            charginginfo={}

            charginginfo["drive_km"]=steps[j]["summary"]["lengthInMeters"]/1000
            charginginfo["drive_hour"]=steps[j]["summary"]["travelTimeInSeconds"]/3600
            charginginfo["batteryConsum"]=steps[j]["summary"]["batteryConsumptionInkWh"]
            charginginfo["arrival_perc"]=steps[j]["summary"]["remainingChargeAtArrivalInkWh"]/self.batterysize*100
            
            if j<(len(steps)-1):
                chargeleg=steps[j]["summary"]["chargingInformationAtEndOfLeg"]
                charginginfo["charge_energy"]=chargeleg["targetChargeInkWh"]-steps[j]["summary"]["remainingChargeAtArrivalInkWh"]
                charginginfo["charge_duration"]=chargeleg["chargingTimeInSeconds"]
                charginginfo["charge_cost"]=0
                charginginfo["name"]=chargeleg["chargingParkName"]
                charginginfo["departure_perc"]=chargeleg["targetChargeInkWh"]/self.batterysize*100
                charginginfo["charger"]=chargeleg
                chargeScore.append(self.ChargeRate(charginginfo["name"],steps[j]['points'][-1]))
            else:
                charginginfo["charge_energy"]=0
                charginginfo["charge_duration"]=0
                charginginfo["charge_cost"]=0
                charginginfo["name"]='NA'
                charginginfo["departure_perc"]=0
                charginginfo["charger"]='NA'

            charginginfo["location"]=(steps[j]["points"][-1]['latitude'],steps[j]["points"][-1]['longitude'])
            charging.append(charginginfo)
        return charging, chargeScore

    def get_routinginfo(self,steps):
        routing=[]
        for step in steps:
            leg=[]
            leg=list(map(lambda x :(x['latitude'],x['longitude']) , step['points']))
            leg.append(leg)
            routing.append(leg)
        return routing

    def get_pathinfo(self,steps):
        Info=[]
        for i in range(len(steps)-1):
            Info.append(steps[i]['path'])
        return Info

    def get_Isoline(self,location):
        requestIsoParams = (
            urlparse.quote(location)  
            + "/json?vehicleEngineType=electric"
            + "&traffic=" + self.traffic
            #+ "&travelMode=" + self.travelMode
            #+ "&avoid=" + self.avoid 
            + "&constantSpeedConsumptionInkWhPerHundredkm=" + self.ECurve
            + "&maxChargeInkWh="+str(self.batterysize)
            + "&currentChargeInkWh="+str(self.currentChargeInkWh)
            + "&minChargeAtDestinationInkWh="+str(self.minChargeAtDestinationInkWh)
            + "&minChargeAtChargingStopsInkWh="+str(self.minChargeAtDestinationInkWh)
            + "&departAt=" + urlparse.quote(self.departAt)
            )

        self.requestUrl = self.isoUrl + requestIsoParams + "&key=" + self.api_key
        # Sending the request
        response = requests.post(self.requestUrl, json=self.chargePara)
        if(response.status_code == 200):
            # Get response's JSON
            jsonResult = response.json()

            polygoninfo=self.get_routinginfo(jsonResult['routes'][0]['legs'])
            
        else:
            polygoninfo=[]
        return [polygoninfo]
    
    def ChargeRate(self,name,coords):
        networkscore = networkrating(name.casefold())
        CSTitle, CSlocation , connects_number = FindChargeStationnearby(coords['latitude'],coords['longitude'],0.3)
        
        outlet_number= connects_number[0] if len(connects_number)>0 else 0
        outletscore=outletrating(outlet_number)
        return networkscore+outletscore

class Eval_Iternio:
    def __init__(self, start,end,SOC,MinBL,Vehicle,traffic=APIconfig["Iternio"]["realtime_traffic"],travelmode="car",avoidfeatures="unpavedRoads",):
        self.now = datetime.now()
        # Building the request URL
        #self.baseUrl =Credential["Iternio"]["IterniobaseUrllight"]
        self.baseUrl =Credential["Iternio"]["endpoint"]
        self.api_key=Credential["Iternio"]["key"]
        self.start_lat=start[0]
        self.start_lon=start[1]
        self.end_lat=end[0]
        self.end_lon=end[1]
        self.batterysize=CC_dict[Vehicle]['BatterySize']
        self.EVConfig=CC_dict[Vehicle]['ParaIternio']['IternioEVConfig']
        self.SOC=SOC
        self.Econsump=CC_dict[Vehicle]['ParaIternio']['ref_consumption']*CC_dict[Vehicle]['CCCoeff']
        self.minSOCAtDestination=MinBL
        self.RTWeather=APIconfig["Iternio"]["realtime_weather"]
        self.RTTraffic=traffic
        self.RTCharger=APIconfig["Iternio"]["realtime_chargers"]
        self.max_soc_perc=100


    def get_direction(self):
        IternioEVStatus='initial_soc_perc=%d'%(self.SOC)+'&realtime_weather='+self.RTWeather+'&realtime_traffic='+self.RTTraffic+'&realtime_chargers='+self.RTCharger+'&charger_soc_perc='+str(self.minSOCAtDestination)+'&arrival_soc_perc='+str(self.minSOCAtDestination)+'&ref_consumption='+str(self.Econsump)+'&charger_max_soc_perc='+str(self.max_soc_perc)
        Iterniodestination ='destinations=[{"lat":%f,"lon":%f}, {"lat":%f, "lon":%f}]&'%(self.start_lat,self.start_lon,self.end_lat,self.end_lon)
        IterniorequestParams = (self.EVConfig+Iterniodestination+IternioEVStatus)
        IterniorequestUrl = self.baseUrl + IterniorequestParams + "&api_key=" + self.api_key
        Iternioresponse = requests.get(IterniorequestUrl)
        if(Iternioresponse.status_code == 200):
            # Get response's JSON
            IterniojsonResult = Iternioresponse.json()
            TripResults=IterniojsonResult['result']['routes'][0]
            travelEnergy = TripResults['total_energy_used']
            travelTime = TripResults['total_drive_duration']/3600
            travelkm=TripResults['total_dist']/1000
            chargeinfo , chargingscore=self.get_chargeinfo(TripResults['steps'])
            routinginfo=self.get_routinginfo(TripResults['steps'])
            chargeTime=TripResults['total_charge_duration']/3600
            pathinfo=self.get_pathinfo(TripResults['steps'])
        else:
            travelEnergy=0
            travelTime=0
            travelkm=0
            chargeTime=0
            chargeinfo=[]
            routinginfo=[]
            pathinfo=[]
            chargingscore=[]
            print("Iternioa API Error")
        return [travelEnergy,travelTime,travelkm,chargeTime,chargeinfo,routinginfo, chargingscore],pathinfo

    def get_chargeinfo(self,steps):
        charging=[]
        chargingscore=[]
        for j in range(1,len(steps)-1):
            charginginfo={}
            try: 
                charginginfo["charge_energy"]=steps[j]["charge_energy"]
                charginginfo["charge_duration"]=steps[j]["charge_duration"]
                charginginfo["charge_cost"]=steps[j]["charge_cost"]
                charginginfo["name"]=steps[j]["name"]
                charginginfo["location"]=(steps[j]["lat"],steps[j]["lon"])
                charginginfo["arrival_perc"]=steps[j]["arrival_perc"]
                charginginfo["departure_perc"]=steps[j]["departure_perc"]
                charginginfo["charger"]=steps[j]["charger"]
                charginginfo["outlet_num"]=len(steps[j]["charger"]["outlets"])
                charging.append(charginginfo)
                chargingscore.append(self.ChargeRate(charginginfo["name"],charginginfo["outlet_num"]))
            except (KeyError):
                charginginfo["charge_energy"]=0
                charginginfo["charge_duration"]=0
                charginginfo["charge_cost"]=0
                charginginfo["name"]=steps[j]["name"]
                charginginfo["location"]=(steps[j]["lat"],steps[j]["lon"])
                charginginfo["arrival_perc"]=steps[j]["arrival_perc"]
                charginginfo["departure_perc"]=steps[j]["departure_perc"]
                charginginfo["charger"]=''
                charging.append(charginginfo)
        return charging, chargingscore

    def get_routinginfo(self,steps):
        routing=[]
        for i in range(len(steps)-1):
            leg=[]
            leg=list(map(lambda x :(x[0],x[1]) , steps[i]['path']))
            leg.append(leg)
            routing.append(leg)
        return routing

    def get_pathinfo(self,steps):
        Info=[]
        for i in range(len(steps)-1):
            Info.append(steps[i]['path'])
        return Info
    
    def ChargeRate(self,name,outlet_number):
        networkscore = networkrating(name.casefold())
        outletscore=outletrating(outlet_number)
        return networkscore+outletscore
    
class Eval_HERE:
    def __init__(self, start,end,SOC,MinBL,Vehicle,traffic="true",):
        self.now = datetime.now()
        # Building the request URL
        self.baseUrl =Credential["HERE"]["endpoint"]
        self.api_key=Credential["HERE"]["key"]
        self.start_lat=start[0]
        self.start_lon=start[1]
        self.end_lat=end[0]
        self.end_lon=end[1]

        self.batterysize=CC_dict[Vehicle]['BatterySize']
        self.evinitialCharge=SOC*self.batterysize/100
        self.evminChargeAtDestination=MinBL*self.batterysize/100
        self.evminChargeAtChargingStation=MinBL*self.batterysize/100
        self.evmaxCharge=self.batterysize

        CombinCurve_Free = lambda x, y : str(x)+','+str(y/1000)+','
        CombinCurve_Traffic = lambda x, y : str(x)+','+str(y/1000*1.4)+','
        ECureve_Free = ''.join(map(lambda x, y: CombinCurve_Free(x,y), CC_dict[Vehicle]['CCspd'], CC_dict[Vehicle]['CCrate']))
        self.evfreeFlowSpeedTable=ECureve_Free[:-1]
        ECureve_Traffic = ''.join(map(lambda x, y: CombinCurve_Traffic(x,y), CC_dict[Vehicle]['CCspd'], CC_dict[Vehicle]['CCrate']))
        self.evtrafficSpeedTable=ECureve_Traffic[:-1]
        self.connectortype='iec62196Type2Combo'
        self.chargingCurve=','.join(map(str,CC_dict[Vehicle]['ChargeParaHERE']['chargingCurve']))

    def get_direction(self):
        HERErequestRoute='origin=%f,%f&destination=%f,%f&return=summary&transportMode=car'%(self.start_lat,self.start_lon,self.end_lat,self.end_lon)
        HERErequestEVE='&ev[freeFlowSpeedTable]=%s&ev[trafficSpeedTable]=%s&ev[initialCharge]=%f&ev[minChargeAtChargingStation]=%f&ev[minChargeAtDestination]=%f&ev[maxChargeAfterChargingStation]=%f&ev[connectorTypes]=%s'%(self.evfreeFlowSpeedTable,self.evtrafficSpeedTable,self.evinitialCharge,self.evminChargeAtChargingStation,self.evminChargeAtDestination,self.evmaxCharge,self.connectortype)
        #HERErequestEVA='&ev[auxiliaryConsumption]=1.8&ev[ascent]=9&ev[descent]=4.3&ev[makeReachable]=true'
        HERErequestEVA='&ev[makeReachable]=true'
        HERErequestEVC='&ev[maxCharge]=%f&ev[chargingCurve]=%s'%(self.evmaxCharge,self.chargingCurve)
        HERErequestUrl = self.baseUrl + HERErequestRoute +HERErequestEVE+HERErequestEVA+HERErequestEVC+ "&apikey=" + self.api_key
        HEREresponse = requests.get(HERErequestUrl)
        if(HEREresponse.status_code == 200):
            HEREjsonResult = HEREresponse.json()
            travelEnergy,travelTime,travelkm,chargeTime,chargeEnergy,chargeScore=self.get_tripinfo(HEREjsonResult['routes'][0]['sections'])
            
            return [travelEnergy,travelTime,travelkm,chargeTime,chargeEnergy,HEREjsonResult['routes'][0]['sections'],chargeScore]
        else:
            print("Fail to fetch data from HERE")
    
    def get_tripinfo(self,sections):
        travelEnergy=0
        travelTime=0
        travelkm=0
        chargeTime=0
        chargeEnergy=0
        chargeScore=[]
        #chargeinfo=[]
        for section in sections:
            
            travelTime += section['summary']['duration']/3600
            travelkm += section['summary']['length']/1000
            
            if 'consumption' in  section['summary']:
                travelEnergy +=section['departure']['charge']-section['arrival']['charge']
                if 'postActions' in section:
                    
                    chargeTime += section['postActions'][0]['duration']/3600
                    chargeEnergy +=section['postActions'][0]['targetCharge']-section['postActions'][0]['arrivalCharge']
                    if 'name' in section['arrival']['place']:
                        CSname=section['arrival']['place']['name']
                        CSlocation=section['arrival']['place']['location']
                        chargeScore.append(self.ChargeRate(CSname,CSlocation))
                    else:
                        chargeScore.append(2)
                #chargeinfo.append()
            else:
                print("special travel type, such as ferry")
        return travelEnergy,travelTime-chargeTime,travelkm,chargeTime,chargeEnergy,chargeScore

    def ChargeRate(self,name,coords):
        networkscore = networkrating(name.casefold())
        CSTitle, CSlocation , connects_number = FindChargeStationnearby(coords['lat'],coords['lng'],0.3)
        
        outlet_number= connects_number[0] if len(connects_number)>0 else 0
        outletscore=outletrating(outlet_number)
        return networkscore+outletscore