Logchannels=['LATITUDE','LONGITUDE','SOC_%','ODOMETER','ALTITUDE','SPEED_PER_SEC','SPEED_MODE_PER_MINUTE','HEAD_COLL_TIMS','SECONDS','OUTSIDE_TEMPERATURE_C']
Rating={'ChargerNetwork':
            {   3:  ['Tesla', 'Allego', 'Ionity', 'Electra', 'Total EV Charge', 'FastNed'],
                2:  ['e-Vadea', 'Engie', 'Power Dot', 'ZEN', 'Zero Emission Network','PROVIRIDIS', 'Lidl', 'R3']
            },
        'NB_Outlet':
            {   4: 12,
                3: 7,
                2: 3
            },
        'Grading':
            {   4:  6,
                3:  4,
                2:  2
            } ,
        'Power':
            {   4:  300,
                3:  150,
                2:  80
            }
        }            
CC_dict={
    'EC4':
    {
    'CCspd':[30,50,70,90,100,110,120,130,150],
    'CCrate':[120.5,121,142.4,176.9,198.3,223.2,250.9,281.5,351.5],
    'CCCoeff':1,
    'BatterySize':46.3,
    'V0':{
            'HVACLoss': 0.15,
            'VehEELoss':0.05,
            'VehLoad':0.05,
            'AgeCharging':0.05,
            'TrafficImpact':0.15,
            'WindImpact':0.1,
            'TempImpact':0.1,
            'CCspd':[30,50,70,90,100,110,120,130,150],
            'CCrate':[156.1,159.7,179.2,201.3,217.8,234.7,260.3,281.5,351.5],
        },
    #Reference for Iternio EV routing API https://documenter.getpostman.com/view/7396339/SWTK3YsN
    'ParaIternio':{
        'IternioEVConfig': 'car_model=citroen:ec4:21:50&',
        'ref_consumption':200,
        'fast_chargers':'ccs',
        #'charger_soc_perc':10,
        'charger_max_soc_perc':100,
        #'arrival_soc_perc':10,
        'charge_overhead':300,
        'speed_factor_perc':100,
        'max_speed':150,
        'extra_weight':0,
    },
    #Reference for TomTom EV routing API  https://developer.tomtom.com/routing-api/documentation/extended-routing/long-distance-ev-routing
    'ChargeParaTT':{
                "chargingParameters": {
                    "batteryCurve": [
                        {
                            "stateOfChargeInkWh": 1.0,
                            "maxPowerInkW": 66.4
                        },
                        {
                            "stateOfChargeInkWh": 7.0,
                            "maxPowerInkW": 101
                        },
                        {
                            "stateOfChargeInkWh": 8.0,
                            "maxPowerInkW": 96.6
                        },
                        {
                            "stateOfChargeInkWh": 14.0,
                            "maxPowerInkW": 94
                        },
                        {
                            "stateOfChargeInkWh": 27.0,
                            "maxPowerInkW": 75
                        },
                        {
                            "stateOfChargeInkWh": 35.0,
                            "maxPowerInkW": 68
                        },
                        {
                            "stateOfChargeInkWh": 36.0,
                            "maxPowerInkW": 54.5
                        },
                        {
                            "stateOfChargeInkWh": 38.0,
                            "maxPowerInkW": 44
                        },
                        {
                            "stateOfChargeInkWh": 39.0,
                            "maxPowerInkW": 33.8
                        },
                        {
                            "stateOfChargeInkWh": 43.0,
                            "maxPowerInkW": 27.5
                        },
                        {
                            "stateOfChargeInkWh": 44.0,
                            "maxPowerInkW": 16.1
                        },
                        {
                            "stateOfChargeInkWh": 46.3,
                            "maxPowerInkW": 11.1
                        }
                    ],
                    "chargingConnectors": [
                        {
                            "currentType": "AC3",
                            "plugTypes": [
                                "IEC_62196_Type_2_Outlet",
                                "IEC_62196_Type_2_Connector_Cable_Attached"
                            ],
                            "efficiency": 0.87,
                            "baseLoadInkW": 0.25,
                            "maxPowerInkW": 102.3
                        },
                        {
                            "currentType": "DC",
                            "plugTypes": [
                                "Combo_to_IEC_62196_Type_2_Base"
                            ],
                            "voltageRange": {
                                "minVoltageInV": 0,
                                "maxVoltageInV": 446
                            },
                            "efficiency": 0.87,
                            "baseLoadInkW": 0.25,
                            "maxPowerInkW": 102.3
                        },
                        {
                            "currentType": "AC1",
                            "plugTypes": [
                                "IEC_62196_Type_2_Outlet",
                                "IEC_62196_Type_2_Connector_Cable_Attached"
                            ],
                            "voltageRange": {
                                "minVoltageInV": 446,
                                "maxVoltageInV": 500
                            },
                            "efficiency": 0.87,
                            "baseLoadInkW": 0.25
                        }
                    ],
                    "chargingTimeOffsetInSec": 120
                }
            },
    #https://developer.here.com/documentation/flutter-sdk-navigate/4.13.3.0/api_reference/routing/BatterySpecifications/chargingCurve.html
    'ChargeParaHERE':{
        'chargingCurve':[0,95,10.5,95,13,92.5,13.5,85,20.5,82,20.7,75,28,70.5,33.5,61,40.8,46,43.3,21,45.9,14,46.2,10,50,6,51,2]
    
    }
    },
    
    'EC4_CV_trained':
    {
        'CCspd':[30,50,70,90,100,110,120,130,150],
        'CCrate':[156.1,159.7,179.2,201.3,217.8,234.7,260.3,281.5,351.5],
        'CCCoeff':0.8,
        'BatterySize':46.3,
        'V0':{
            'HVACLoss': 0.15,
            'VehEELoss':0.05,
            'VehLoad':0.05,
            'AgeCharging':0.05,
            'TrafficImpact':0.15,
            'WindImpact':0.1,
            'TempImpact':0.1,
            'CCspd':[30,50,70,90,100,110,120,130,150],
            'CCrate':[156.1,159.7,179.2,201.3,217.8,234.7,260.3,281.5,351.5],
        },
        #Reference for Iternio EV routing API https://documenter.getpostman.com/view/7396339/SWTK3YsN
        'ParaIternio':{
            'IternioEVConfig': 'car_model=citroen:ec4:21:50&',
            'ref_consumption':200,
            'fast_chargers':'ccs',
            #'charger_soc_perc':10,
            'charger_max_soc_perc':100,
            #'arrival_soc_perc':10,
            'charge_overhead':300,
            'speed_factor_perc':100,
            'max_speed':150,
            'extra_weight':0,
        },
        #Reference for TomTom EV routing API  https://developer.tomtom.com/routing-api/documentation/extended-routing/long-distance-ev-routing
        'ChargeParaTT':{
                        "chargingParameters": {
                            "batteryCurve": [
                                {
                                    "stateOfChargeInkWh": 1.0,
                                    "maxPowerInkW": 66.4
                                },
                                {
                                    "stateOfChargeInkWh": 7.0,
                                    "maxPowerInkW": 101
                                },
                                {
                                    "stateOfChargeInkWh": 8.0,
                                    "maxPowerInkW": 96.6
                                },
                                {
                                    "stateOfChargeInkWh": 14.0,
                                    "maxPowerInkW": 94
                                },
                                {
                                    "stateOfChargeInkWh": 27.0,
                                    "maxPowerInkW": 75
                                },
                                {
                                    "stateOfChargeInkWh": 35.0,
                                    "maxPowerInkW": 68
                                },
                                {
                                    "stateOfChargeInkWh": 36.0,
                                    "maxPowerInkW": 54.5
                                },
                                {
                                    "stateOfChargeInkWh": 38.0,
                                    "maxPowerInkW": 44
                                },
                                {
                                    "stateOfChargeInkWh": 39.0,
                                    "maxPowerInkW": 33.8
                                },
                                {
                                    "stateOfChargeInkWh": 43.0,
                                    "maxPowerInkW": 27.5
                                },
                                {
                                    "stateOfChargeInkWh": 44.0,
                                    "maxPowerInkW": 16.1
                                },
                                {
                                    "stateOfChargeInkWh": 46.3,
                                    "maxPowerInkW": 11.1
                                }
                            ],
                            "chargingConnectors": [
                                {
                                    "currentType": "AC3",
                                    "plugTypes": [
                                        "IEC_62196_Type_2_Outlet",
                                        "IEC_62196_Type_2_Connector_Cable_Attached"
                                    ],
                                    "efficiency": 0.87,
                                    "baseLoadInkW": 0.25,
                                    "maxPowerInkW": 102.3
                                },
                                {
                                    "currentType": "DC",
                                    "plugTypes": [
                                        "Combo_to_IEC_62196_Type_2_Base"
                                    ],
                                    "voltageRange": {
                                        "minVoltageInV": 0,
                                        "maxVoltageInV": 446
                                    },
                                    "efficiency": 0.87,
                                    "baseLoadInkW": 0.25,
                                    "maxPowerInkW": 102.3
                                },
                                {
                                    "currentType": "AC1",
                                    "plugTypes": [
                                        "IEC_62196_Type_2_Outlet",
                                        "IEC_62196_Type_2_Connector_Cable_Attached"
                                    ],
                                    "voltageRange": {
                                        "minVoltageInV": 446,
                                        "maxVoltageInV": 500
                                    },
                                    "efficiency": 0.87,
                                    "baseLoadInkW": 0.25
                                }
                            ],
                            "chargingTimeOffsetInSec": 120
                        }
                    },
        'ChargeParaHERE':{
        'chargingCurve':[0,95,10.5,95,13,92.5,13.5,85,20.5,82,20.7,75,28,70.5,33.5,61,40.8,46,43.3,21,45.9,14,46.2,10,50,6,51,2]
    
    }
    }
}