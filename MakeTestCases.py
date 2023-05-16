import random
import itertools
import pandas as pd
import numpy as np
cities = [
    "London",
    "Madrid",
    "Rome",
    "Paris",
    "Berlin",
    "Athens",
    "Vienna",
    "Milan",
    "Barcelona",
    "Naples",
    "Warsaw",
    "Hamburg",
    "Budapest",
    "Prague",
    "Munich",
    "Valencia",
    "Copenhagen",
    "Bucharest",
    "Amsterdam",
    "Brussels",
    "Stockholm",
    "Dublin",
    "Stuttgart",
    "Frankfurt",
    "Lisbon",
    "Helsinki",
    "Lyon",
    "Porto",
    "Glasgow",
    "Bologna",
    "Poznań",
    "Kraków",
    "Antwerp",
    "Seville",
    "Riga",
    "Turin",
    "Gdańsk",
    "Marseille",
    "Vilnius",
    "Tallinn",
    "Katowice",
    "Nice",
    "Rotterdam",
    "Malaga",
    "Cardiff",
    "Mannheim",
    "Brno",
    "Murcia",
    "Dortmund",
    "Essen"
]

combinations = list(itertools.combinations(cities, 2))

VinBook=pd.DataFrame(combinations)
VinBook['SOC_%']= np.random.randint(35, 100, VinBook.shape[0])
VinBook['MinBL']= np.random.randint(10, 25, VinBook.shape[0])
VinBook['RTTraffic']=np.random.randint(0, 1, VinBook.shape[0])
VinBook.to_csv("log\\city_combinations.csv", index=False,header=['start','end','SOC','MinBL','RTTraffic'])