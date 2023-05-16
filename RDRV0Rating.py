from VehConfig import *

def networkrating(chargernetwork):
    if any(s.casefold() in chargernetwork for s in Rating['ChargerNetwork'][3]):
        netscore =3
    elif any(s.casefold() in chargernetwork for s in Rating['ChargerNetwork'][2]):
        netscore =2
    else :
        netscore =1
    return netscore


def outletrating(connects_number):
    if connects_number  <= Rating['NB_Outlet'][2]:
        connect_score =1
    elif  connects_number <= Rating['NB_Outlet'][3]:
        connect_score = 2
    elif  connects_number <= Rating['NB_Outlet'][4]:
        connect_score =3
    else :
        connect_score =4
    return connect_score

def TTChrating(chargerinfo):
    connects_number=0
    connect_score=0
    grading =0
    powerscore=0
    netscore=0

    '''
    chargerPower =chargerinfo["chargingConnectionInfo"]["chargingPowerInkW"]
    if  chargerPower >=Rating['Power'][4]:
        grading = 4
    elif chargerPower >=Rating['Power'][3]:
        grading =3
    elif chargerPower >=Rating['Power'][2]:
        grading =2
    else :
        grading =1
    
    if connects_number  <= Rating['NB_Outlet'][2]:
        connect_score =1
    elif connects_number <= Rating['NB_Outlet'][3]:
        connect_score = 2
    elif connects_number <= Rating['NB_Outlet'][4]:
        connect_score =3
    else :
        connect_score =4
    '''
    chargernetwork = chargerinfo["chargingParkName"].casefold()

    return grading+outletrating(connects_number)+networkrating(chargernetwork)

def IternioChrating(chargerinfo):
    connects_number=0
    connect_score=0
    grading =0
    powerscore=0
    netscore=0
    for outlet in chargerinfo["outlets"]:
        if outlet['status']=='OPERATIONAL':
            connects_number += 1
            if  outlet['power']>=Rating['Power'][4]:
                powerscore +=4
            elif outlet['power']>=Rating['Power'][3] :
                powerscore +=3
            elif outlet['power']>=Rating['Power'][2] :
                powerscore +=2
            else :
                powerscore +=1
    '''
    if powerscore <=Rating['Grading'][2]:
        grading =1
    elif powerscore <=Rating['Grading'][3]:
        grading =2
    elif powerscore <=Rating['Grading'][4]:
        grading =3
    else :
        grading =4
    
    if connects_number  <= Rating['NB_Outlet'][2]:
        connect_score =1
    elif  connects_number <= Rating['NB_Outlet'][3]:
        connect_score = 2
    elif  connects_number <= Rating['NB_Outlet'][4]:
        connect_score =3
    else :
        connect_score =4

    '''
    chargernetwork = chargerinfo['network_name'].casefold()
    return grading+outletrating(connects_number)+networkrating(chargernetwork)