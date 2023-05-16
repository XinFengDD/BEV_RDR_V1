APIconfig={
    'OpenChargemap':{
        'endpoint':'https://api.openchargemap.io/v3/poi/?',
        'key':''
    },
    'googlemap':{
        'endpoint':'',
        'key':''
    },
    'TomTom':{
        'endpoint':'https://api.tomtom.com/routing/1/calculateLongDistanceEVRoute/',
        'endpoint_iso':'https://api.tomtom.com/routing/1/calculateReachableRange/',
        'key':'',
        'path':["drive_km",
                "drive_hour",
                "batteryConsum",
                "arrival_perc",
                "charge_energy",
                "charge_duration",
                "charge_cost",
                "name",
                "departure_perc",
                #"instruction",
                "location"
                ]
    },
    'Iternio':{
        'endpoint':'https://api.iternio.com/1/plan?',
        'key':'',
        'IterniobaseUrllight': "https://api.iternio.com/1/plan_light?",
        'realtime_weather': 'False',
        'realtime_traffic':'True',
        'realtime_chargers':'True',
        'path_steps':False,
        'path_polyline':False,

        'allow_toll':True,
        'allow_border':True,
        'adjust_speed':False,

        #'outside_temp':20,
        #'wind_speed':0,
        #'wind_dir':'head',
        'road_condition':'normal',
        'find_alts':False,
        'find_next_charger_alts':False,
        'exclude_ids':0,
        'network_preferences':{},
        'preferred_charge_cost_multiplier':0.7,
        'nonpreferred_charge_cost_addition':0,
        'allowed_dbs':'ocm',
        'group_preferences':{},
        'access_groups':[],
        'path':["lat",
                "lon",
                "soc_perc [SoC %]",
                "cons_per_km [Wh/km]",
                "speed [km/h]",
                "remaining_time [s]",
                "remaining_dist [km]",
                "instruction",
                "speed_limit [m/s]",
                "elevation [m]",
                "path_distance [m]",
                "jam_factor [0-4]",
                "instruction_obj",
                "unknown1",
                "unknown2",
                ]
    },
    'HERE':{
        'endpoint':'https://router.hereapi.com/v8/routes?',
        'key':''
    },
}