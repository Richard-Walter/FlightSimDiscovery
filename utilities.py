# -*- coding: utf-8 -*-
import re
import csv
import os
from flask import Flask
from openpyxl import Workbook
import codecs
from math import cos, asin, sqrt
from flightsimdiscovery import db
from flightsimdiscovery.config import Config

# validate latitude and longitude constants
lat_pattern = re.compile(r"^(\+|-)?(?:90(?:(?:\.0{1,18})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,18})?))$")
long_pattern = re.compile(r"^(\+|-)?(?:180(?:(?:\.0{1,18})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,18})?))$")
poi_start_pattern_compile = re.compile(r'\[{3}(\+|-)?\d\d')
poi_pattern = r'\[{3}.+"31FD54F7\w+\\"'
lat_long_pattern = r'\[{3}(\+|-)?(\d{1,3}\.\d+),((\+|-)?\d{1,3}\.\d+)]'
location_pattern = r'\[{2}\\"Location\\",\[\\("[^\]]+)'
category_pattern = r'\[{2}\\"Category\\",\[\\("[^\]]+)'
continent_pattern = r'\[{1}\\"Continent\\",\[\\("[^\]]+)'
notes_pattern = r'\[{1}\\"Notes\\",\[\\("[^\]]+)'

region_details = {
    'Africa - Eastern': [-5.188246, 35.136011, 6],
    'Africa - Middle': [2.099101, 17.294214, 6],
    'Africa - Northern': [26.028232, 16.503199, 6],
    'Africa - Southern': [-23.988214, 23.401357, 6],
    'Africa - Western': [12, 3, 6],
    'America - Central': [17.4, -91, 7],
    'America - Northern': [44.35528, -99.99917, 5],
    'America - South': [-19.24773, -61.52741, 4.5],
    'Antartica': [-75.250973, -0.071389, 4],
    'Asia - Central': [45.3, 63.9, 5],
    'Asia - Eastern': [39.286757, 112.064601, 5],
    'Asia - South-eastern': [11.998224, 120.656442, 5],
    'Asia - Southern': [26.9, 72.2, 5],
    'Asia - Western': [32.811895, 40.661186, 5],
    'Caribbean': [19.593216, -68.968228, 6],
    'Europe - Eastern': [50, 30, 5],
    'Europe - Northern': [59.155256, 16.123697, 6],
    'Europe - Southern': [45.160168, 15.1362, 6],
    'Europe - Western': [52.261223, 11.669846, 5],
    'Oceania': [-22.696926, 161.591196, 5],
}

countries_details = {
    'Afghanistan': ['Asia - Southern', 33.93911, 67.709953],
    'Albania': ['Europe - Southern', 41.153332, 20.168331],
    'Algeria': ['Africa - Northern', 28.033886, 1.659626],
    'American Samoa': ['Oceania', -14.270972, -170.132217],
    'Andorra': ['Europe - Southern', 42.546245, 1.601554],
    'Angola': ['Africa - Middle', -11.202692, 17.873887],
    'Anguilla': ['Caribbean', 18.220554, -63.068615],
    'Antarctica': ['Antartica', -75.250973, -0.071389],
    'Antigua and Barbuda': ['Caribbean', 17.060816, -61.796428],
    'Argentina': ['America - South', -38.416097, -63.616672],
    'Armenia': ['Middle East', 40.069099, 45.038189],
    'Aruba': ['Caribbean', 12.52111, -69.968338],
    'Australia': ['Oceania', -25.274398, 133.775136],
    'Austria': ['Europe - Western', 47.516231, 14.550072],
    'Azerbaijan': ['Middle East', 40.143105, 47.576927],
    'Bahamas': ['Caribbean', 25.03428, -77.39628],
    'Bahrain': ['Middle East', 25.930414, 50.637772],
    'Bangladesh': ['Asia - Southern', 23.684994, 90.356331],
    'Barbados': ['Caribbean', 13.193887, -59.543198],
    'Belarus': ['Europe - Eastern', 53.709807, 27.953389],
    'Belgium': ['Europe - Western', 50.503887, 4.469936],
    'Belize': ['America - Central', 17.189877, -88.49765],
    'Benin': ['Africa - Western', 9.30769, 2.315834],
    'Bermuda': ['America - Northern', 32.321384, -64.75737],
    'Bhutan': ['Asia - Southern', 27.514162, 90.433601],
    'Bolivia': ['America - South', -16.290154, -63.588653],
    'Bosnia and Herzegovina': ['Europe - Southern', 43.915886, 17.679076],
    'Botswana': ['Africa - Southern', -22.328474, 24.684866],
    'Brazil': ['America - South', -14.235004, -51.92528],
    'British Indian Ocean Territory': ['Africa - Eastern', -6.343194, 71.876519],
    'British Virgin Islands': ['Caribbean', 18.420695, -64.639968],
    'Brunei': ['Asia - South-eastern', 4.535277, 114.727669],
    'Bulgaria': ['Europe - Eastern', 42.733883, 25.48583],
    'Burkina Faso': ['Africa - Western', 12.238333, -1.561593],
    'Burundi': ['Africa - Eastern', -3.373056, 29.918886],
    'Cabo Verde': ['Africa - Western', 12.565679, 104.990963],
    'Cambodia': ['Asia - South-eastern', 7.369722, 12.354722],
    'Cameroon': ['Africa - Middle', 56.130366, -106.346771],
    'Canada': ['America - Northern', 16.002082, -24.013197],
    'Cayman Islands': ['Caribbean', 19.513469, -80.566956],
    'Central African Republic': ['Africa - Middle', 6.611111, 20.939444],
    'Chad': ['Africa - Middle', 15.454166, 18.732207],
    'Chile': ['America - South', -35.675147, -71.542969],
    'China': ['Asia - Eastern', 35.86166, 104.195397],
    'Christmas Island': ['Oceania', -10.447525, 105.690449],
    'Cocos (Keeling) Islands': ['Oceania', -12.164165, 96.870956],
    'Colombia': ['America - South', 4.570868, -74.297333],
    'Comoros': ['Africa - Eastern', -11.875001, 43.872219],
    'Congo': ['Africa - Middle', -4.038333, 21.758664],
    'Congo, Democratic Republic of the': ['Africa - Middle', -0.228021, 15.827659],
    'Cook Islands': ['Oceania', -21.236736, -159.777671],
    'Costa Rica': ['America - Central', 9.748917, -83.753428],
    'Croatia': ['Europe - Southern', 45.1, 15.2],
    'Cuba': ['Caribbean', 21.521757, -77.781167],
    'Cyprus': ['Middle East', 35.126413, 33.429859],
    'Czechia': ['Europe - Eastern', 49.817492, 15.472962],
    'Denmark': ['Europe - Northern', 56.26392, 9.501785],
    'Djibouti': ['Africa - Eastern', 11.825138, 42.590275],
    'Dominica': ['Caribbean', 15.414999, -61.370976],
    'Dominican Republic': ['Caribbean', 18.735693, -70.162651],
    'Ecuador': ['America - South', -1.831239, -78.183406],
    'Egypt': ['Africa - Northern', 26.820553, 30.802498],
    'El Salvador': ['America - Central', 13.794185, -88.89653],
    'Equatorial Guinea': ['Africa - Middle', 1.650801, 10.267895],
    'Eritrea': ['Africa - Eastern', 15.179384, 39.782334],
    'Estonia': ['Europe - Northern', 58.595272, 25.013607],
    'Eswatini': ['Africa - Southern', 9.145, 40.489673],
    'Ethiopia': ['Africa - Eastern', 8.899458, 39.844715],
    'Falkland Islands (Malvinas)': ['America - South', 61.892635, -6.911806],
    'Faroe Islands': ['Europe - Northern', -16.578193, 179.414413],
    'Fiji': ['Oceania', 61.92411, 25.748151],
    'Finland': ['Europe - Northern', 46.227638, 2.213749],
    'France': ['Europe - Western', 3.933889, -53.125782],
    'French Guiana': ['America - South', -17.679742, -149.406843],
    'French Polynesia': ['Oceania', -17.455157, -149.607942],
    'French Southern Territories': ['Africa - Eastern', -0.803689, 11.609444],
    'Gabon': ['Africa - Middle', 13.443182, -15.310139],
    'Gambia': ['Africa - Western', 31.354676, 34.308825],
    'Georgia': ['Middle East', 42.315407, 43.356892],
    'Germany': ['Europe - Western', 51.165691, 10.451526],
    'Ghana': ['Africa - Western', 7.946527, -1.023194],
    'Gibraltar': ['Europe - Southern', 36.137741, -5.345374],
    'Great Britain': ['Europe - Northern', 55.378051, -3.435973],
    'Greece': ['Europe - Southern', 39.074208, 21.824312],
    'Greenland': ['America - Northern', 71.706936, -42.604303],
    'Grenada': ['Caribbean', 12.262776, -61.604171],
    'Guadeloupe': ['Caribbean', 16.995971, -62.067641],
    'Guam': ['Oceania', 13.444304, 144.793731],
    'Guatemala': ['America - Central', 15.783471, -90.230759],
    'Guernsey': ['America - Central', 49.465691, -2.585278],
    'Guinea': ['Africa - Western', 9.945587, -9.696645],
    'Guinea-Bissau': ['Africa - Western', 11.803749, -15.180413],
    'Guyana': ['Africa - Western', 4.860416, -58.93018],
    'Haiti': ['America - South', 18.971187, -72.285215],
    'Heard Island and McDonald Islands': ['Caribbean', -53.08181, 73.504158],
    'Honduras': ['America - Central', 15.199999, -86.241905],
    'Hong Kong': ['Asia - Eastern', 22.396428, 114.109497],
    'Hungary': ['Europe - Eastern', 47.162494, 19.503304],
    'Iceland': ['Europe - Northern', 64.963051, -19.020835],
    'India': ['Asia - Southern', 20.593684, 78.96288],
    'Indonesia': ['Asia - South-eastern', -0.789275, 113.921327],
    'Iran': ['Asia - Southern', 32.427908, 53.688046],
    'Iraq': ['Middle East', 33.223191, 43.679291],
    'Ireland': ['Europe - Northern', 53.41291, -8.24389],
    'Isle of Man': ['Europe - Northern', 54.236107, -4.548056],
    'Israel': ['Middle East', 31.046051, 34.851612],
    'Italy': ['Europe - Southern', 41.87194, 12.56738],
    'Ivory Coast': ['Africa - Western', 7.539989, -5.54708],
    'Jamaica': ['Caribbean', 18.109581, -77.297508],
    'Japan': ['Asia - Eastern', 36.204824, 138.252924],
    'Jersey': ['Europe - Northern', 49.214439, -2.13125],
    'Jordan': ['Middle East', 30.585164, 36.238414],
    'Kazakhstan': ['Asia - Central', 48.019573, 66.923684],
    'Kenya': ['Africa - Eastern', -0.023559, 37.906193],
    'Kiribati': ['Oceania', -3.370417, -168.734039],
    'Kosovo': ['Europe - Southern', 42.602636, 20.902977],
    'Kuwait': ['Middle East', 29.31166, 47.481766],
    'Kyrgyzstan': ['Asia - Central', 41.20438, 74.766098],
    'Laos': ['Asia - South-eastern', 19.85627, 102.495496],
    'Latvia': ['Europe - Northern', 56.879635, 24.603189],
    'Lebanon': ['Middle East', 33.854721, 35.862285],
    'Lesotho': ['Africa - Southern', -29.609988, 28.233608],
    'Liberia': ['Africa - Western', 6.428055, -9.429499],
    'Libya': ['Africa - Northern', 26.3351, 17.228331],
    'Liechtenstein': ['Europe - Western', 47.166, 9.555373],
    'Lithuania': ['Europe - Northern', 55.169438, 23.881275],
    'Luxembourg': ['Europe - Western', 49.815273, 6.129583],
    'Macao': ['Asia - Eastern', 22.198745, 113.543873],
    'Madagascar': ['Africa - Eastern', 41.608635, 21.745275],
    'Malawi': ['Africa - Eastern', -18.766947, 46.869107],
    'Malaysia': ['Asia - South-eastern', -13.254308, 34.301525],
    'Maldives': ['Asia - Southern', 4.210484, 101.975766],
    'Mali': ['Africa - Western', 3.202778, 73.22068],
    'Malta': ['Europe - Southern', 17.570692, -3.996166],
    'Marshall Islands': ['Oceania', 35.937496, 14.375416],
    'Martinique': ['Caribbean', 7.131474, 171.184478],
    'Mauritania': ['Africa - Western', 14.641528, -61.024174],
    'Mauritius': ['Africa - Eastern', 21.00789, -10.940835],
    'Mayotte': ['Africa - Eastern', -20.348404, 57.552152],
    'Mexico': ['America - Central', 23.634501, -102.552784],
    'Moldova, Republic of': ['Europe - Eastern', 47.411631, 28.369885],
    'Monaco': ['Europe - Western', 43.750298, 7.412841],
    'Mongolia': ['Asia - Eastern', 46.862496, 103.846656],
    'Montenegro': ['Europe - Southern', 42.708678, 19.37439],
    'Montserrat': ['Caribbean', 16.742498, -62.187366],
    'Morocco': ['Africa - Northern', 31.791702, -7.09262],
    'Mozambique': ['Africa - Eastern', -18.665695, 35.529562],
    'Myanmar': ['Asia - South-eastern', 21.913965, 95.956223],
    'Namibia': ['Africa - Southern', -22.95764, 18.49041],
    'Nauru': ['Oceania', -0.522778, 166.931503],
    'Nepal': ['Asia - Southern', 28.394857, 84.124008],
    'Netherlands': ['Europe - Western', 52.132633, 5.291266],
    'New Caledonia': ['Oceania', 12.226079, -69.060087],
    'New Zealand': ['Oceania', -42.323230, 172.862215],
    'Nicaragua': ['America - Central', -40.900557, 174.885971],
    'Niger': ['Africa - Western', 12.865416, -85.207229],
    'Nigeria': ['Africa - Western', 17.607789, 8.081666],
    'Niue': ['Oceania', 9.081999, 8.675277],
    'Norfolk Island': ['Oceania', -19.054445, -169.867233],
    'North Korea': ['Asia - Eastern', -29.040835, 167.954712],
    'North Macedonia': ['Europe - Southern', 40.339852, 127.510093],
    'Northern Mariana Islands': ['Oceania', 17.33083, 145.38469],
    'Norway': ['Europe - Northern', 60.472024, 8.468946],
    'Oceania (Federated States of)': ['Oceania', 7.425554, 150.550812],
    'Oman': ['Middle East', 21.512583, 55.923255],
    'Pakistan': ['Asia - Southern', 30.375321, 69.345116],
    'Palau': ['Oceania', 7.51498, 134.58252],
    'Palestine, State of': ['Middle East', 31.952162, 35.233154],
    'Panama': ['America - Central', 8.537981, -80.782127],
    'Papua New Guinea': ['Oceania', -6.314993, 143.95555],
    'Paraguay': ['America - South', -23.442503, -58.443832],
    'Peru': ['America - South', -9.189967, -75.015152],
    'Philippines': ['Asia - South-eastern', 12.879721, 121.774017],
    'Pitcairn': ['Oceania', -24.703615, -127.439308],
    'Poland': ['Europe - Eastern', 51.919438, 19.145136],
    'Portugal': ['Europe - Southern', 39.399872, -8.224454],
    'Puerto Rico': ['Caribbean', 18.220833, -66.590149],
    'Qatar': ['Middle East', 25.354826, 51.183884],
    'Réunion': ['Africa - Eastern', -21.115141, 55.536384],
    'Romania': ['Europe - Eastern', 45.943161, 24.96676],
    'Russian Federation': ['Europe - Eastern', 61.52401, 105.318756],
    'Rwanda': ['Africa - Eastern', -1.940278, 29.873888],
    'Saint Barthélemy': ['Caribbean', -15.95, -5.71667],
    'Saint Helena': ['Africa - Western', -24.143474, -10.030696],
    'Saint Kitts and Nevis': ['Caribbean', 17.357822, -62.782998],
    'Saint Lucia': ['Caribbean', 13.909444, -60.978893],
    'Saint Pierre and Miquelon': ['America - Northern', 46.941936, -56.27111],
    'Saint Vincent and the Grenadines': ['Caribbean', 12.984305, -61.287228],
    'Samoa': ['Oceania', -13.759029, -172.104629],
    'San Marino': ['Europe - Southern', 43.94236, 12.457777],
    'Sao Tome and Principe': ['Africa - Middle', 0.18636, 6.613081],
    'Saudi Arabia': ['Middle East', 23.885942, 45.079162],
    'Senegal': ['Africa - Western', 14.497401, -14.452362],
    'Serbia': ['Europe - Southern', 44.016521, 21.005859],
    'Seychelles': ['Africa - Eastern', -4.679574, 55.491977],
    'Sierra Leone': ['Africa - Western', 8.460555, -11.779889],
    'Singapore': ['Asia - South-eastern', 1.352083, 103.819836],
    'Slovakia': ['Europe - Eastern', 48.669026, 19.699024],
    'Slovenia': ['Europe - Southern', 46.151241, 14.995463],
    'Solomon Islands': ['Oceania', -9.64571, 160.156194],
    'Somalia': ['Africa - Eastern', 5.152149, 46.199616],
    'South Africa': ['Africa - Southern', -30.559482, 22.937506],
    'South Georgia': ['America - South', -54.429579, -36.587909],
    'South Korea': ['Asia - Eastern', 35.907757, 127.766922],
    'South Sudan': ['Africa - Eastern', 6.889577, 30.747197],
    'Spain': ['Europe - Southern', 40.463667, -3.74922],
    'Sri Lanka': ['Asia - Southern', 7.873054, 80.771797],
    'Sudan': ['Africa - Northern', 12.862807, 30.217636],
    'Suriname': ['America - South', 3.919305, -56.027783],
    'Svalbard and Jan Mayen': ['Europe - Northern', 77.553604, 23.670272],
    'Swaziland': ['Africa - Southern', -26.522503, 31.465866],
    'Sweden': ['Europe - Northern', 60.128161, 18.643501],
    'Switzerland': ['Europe - Western', 46.818188, 8.227512],
    'Syria': ['Middle East', 34.802075, 38.996815],
    'Taiwan': ['Asia - Eastern', 23.69781, 120.960515],
    'Tajikistan': ['Asia - Central', 38.861034, 71.276093],
    'Tanzania': ['Africa - Eastern', -6.369028, 34.888822],
    'Thailand': ['Asia - South-eastern', 15.870032, 100.992541],
    'Timor-Leste': ['Asia - South-eastern', -8.874217, 125.727539],
    'Togo': ['Africa - Western', 8.619543, 0.824782],
    'Tokelau': ['Oceania', -8.967363, -171.855881],
    'Tonga': ['Oceania', -21.178986, -175.198242],
    'Trinidad and Tobago': ['Caribbean', 10.691803, -61.222503],
    'Tunisia': ['Africa - Northern', 33.886917, 9.537499],
    'Turkey': ['Middle East', 38.963745, 35.243322],
    'Turkmenistan': ['Asia - Central', 38.969719, 59.556278],
    'Turks and Caicos Islands': ['Caribbean', 21.694025, -71.797928],
    'Tuvalu': ['Oceania', -7.109535, 177.64933],
    'U.S. Virgin Islands': ['Caribbean', 18.335765, -64.896335],
    'Uganda': ['Africa - Eastern', 1.373333, 32.290275],
    'Ukraine': ['Europe - Eastern', 48.379433, 31.16558],
    'United Arab Emirates': ['Middle East', 23.424076, 53.847818],
    'United States of America': ['America - Northern', 37.09024, -95.712891],
    'Uruguay': ['America - South', -32.522779, -55.765835],
    'Uzbekistan': ['Asia - Central', 41.377491, 64.585262],
    'Vanuatu': ['Oceania', -15.376706, 166.959158],
    'Venezuela': ['America - South', 6.42375, -66.58973],
    'Vietnam': ['Asia - South-eastern', 14.058324, 108.277199],
    'Wallis and Futuna': ['Oceania', -13.768752, -177.156097],
    'Western Sahara': ['Africa - Northern', 24.215527, -12.885834],
    'Yemen': ['Middle East', 15.552727, 48.516388],
    'Zambia': ['Africa - Southern', -13.133897, 27.849332],
    'Zimbabwe': ['Africa - Southern', -19.015438, 29.154857],
}

countries_by_region = {
    'Asia - Southern': ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Iran', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka'],
    'Europe - Southern': ['Albania', 'Andorra', 'Bosnia and Herzegovina', 'Croatia', 'Gibraltar', 'Greece', 'Italy', 'Kosovo', 'Malta', 'Montenegro',
                          'North Macedonia', 'Portugal', 'San Marino', 'Serbia', 'Slovenia', 'Spain'],
    'Africa - Northern': ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Sudan', 'Tunisia', 'Western Sahara'],
    'Oceania': ['American Samoa', 'Australia', 'Christmas Island', 'Cocos (Keeling) Islands', 'Cook Islands', 'Fiji', 'French Polynesia', 'Guam',
                'Kiribati', 'Marshall Islands', 'Nauru', 'New Caledonia', 'New Zealand', 'Niue', 'Norfolk Island', 'Northern Mariana Islands',
                'Oceania (Federated States of)', 'Palau', 'Papua New Guinea', 'Pitcairn', 'Samoa', 'Solomon Islands', 'Tokelau', 'Tonga', 'Tuvalu',
                'Vanuatu', 'Wallis and Futuna'],
    'Africa - Middle': ['Angola', 'Cameroon', 'Central African Republic', 'Chad', 'Congo', 'Congo, Democratic Republic of the', 'Equatorial Guinea',
                        'Gabon', 'Sao Tome and Principe'],
    'Caribbean': ['Anguilla', 'Antigua and Barbuda', 'Aruba', 'Bahamas', 'Barbados', 'British Virgin Islands', 'Cayman Islands', 'Cuba', 'Dominica',
                  'Dominican Republic', 'Grenada', 'Guadeloupe', 'Heard Island and McDonald Islands', 'Jamaica', 'Martinique', 'Montserrat',
                  'Puerto Rico', 'Saint Barthélemy', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines',
                  'Trinidad and Tobago', 'Turks and Caicos Islands', 'U.S. Virgin Islands'],
    'Antartica': ['Antarctica'],
    'America - South': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Falkland Islands (Malvinas)', 'French Guiana', 'Haiti',
                        'Paraguay', 'Peru', 'South Georgia', 'Suriname', 'Uruguay', 'Venezuela'],
    'Middle East': ['Armenia', 'Azerbaijan', 'Bahrain', 'Cyprus', 'Georgia', 'Iraq', 'Israel', 'Jordan', 'Kuwait', 'Lebanon', 'Oman',
                    'Palestine, State of', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'United Arab Emirates', 'Yemen'],
    'Europe - Western': ['Austria', 'Belgium', 'France', 'Germany', 'Liechtenstein', 'Luxembourg', 'Monaco', 'Netherlands', 'Switzerland'],
    'Europe - Eastern': ['Belarus', 'Bulgaria', 'Czechia', 'Hungary', 'Moldova, Republic of', 'Poland', 'Romania', 'Russian Federation', 'Slovakia',
                         'Ukraine'],
    'America - Central': ['Belize', 'Costa Rica', 'El Salvador', 'Guatemala', 'Guernsey', 'Honduras', 'Mexico', 'Nicaragua', 'Panama'],
    'Africa - Western': ['Benin', 'Burkina Faso', 'Cabo Verde', "Côte d'Ivoire", 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Liberia',
                         'Mali', 'Mauritania', 'Niger', 'Nigeria', 'Saint Helena', 'Senegal', 'Sierra Leone', 'Togo'],
    'America - Northern': ['Bermuda', 'Canada', 'Greenland', 'Saint Pierre and Miquelon', 'United States of America'],
    'Africa - Southern': ['Botswana', 'Eswatini', 'Lesotho', 'Namibia', 'South Africa', 'Swaziland', 'Zambia', 'Zimbabwe'],
    'Africa - Eastern': ['British Indian Ocean Territory', 'Burundi', 'Comoros', 'Djibouti', 'Eritrea', 'Ethiopia', 'French Southern Territories',
                         'Kenya', 'Madagascar', 'Malawi', 'Mauritius', 'Mayotte', 'Mozambique', 'Réunion', 'Rwanda', 'Seychelles', 'Somalia',
                         'South Sudan', 'Tanzania', 'Uganda'],
    'Asia - South-eastern': ['Brunei', 'Cambodia', 'Indonesia', 'Laos', 'Malaysia', 'Myanmar', 'Philippines', 'Singapore', 'Thailand', 'Timor-Leste',
                             'Vietnam'],
    'Asia - Eastern': ['China', 'Hong Kong', 'Japan', 'Macao', 'Mongolia', 'North Korea', 'South Korea', 'Taiwan'],
    'Europe - Northern': ['Denmark', 'Estonia', 'Faroe Islands', 'Finland', 'Great Britain', 'Iceland', 'Ireland', 'Isle of Man', 'Jersey', 'Latvia',
                          'Lithuania', 'Norway', 'Svalbard and Jan Mayen', 'Sweden'],
    'Asia - Central': ['Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Uzbekistan'],
}

continents_by_region = {
    'Asia': ['Asia - Southern', 'Middle East', 'Asia - South-eastern', 'Asia - Eastern', 'Asia - Central'],
    'Europe': ['Europe - Southern', 'Europe - Western', 'Europe - Eastern', 'Europe - Northern'],
    'Africa': ['Africa - Northern', 'Africa - Middle', 'Africa - Western', 'Africa - Southern', 'Africa - Eastern'],
    'Oceania': ['Oceania'],
    'South America': ['America - South'],
    'North America': ['Caribbean', 'America - Northern', 'America - Central']
}

categoryList = [
    "Airport (Bush Strip)",
    "Airport (Famous/Interesting)",
    "Beach",
    "Canyon",
    "City/Town",
    "Megacity",
    "Desert",
    "Island",
    "Lake",
    "Mountain",
    "National Park",
    "Reef",
    "Region",
    "River",
    "Seaport",
    "Valley",
    "Volcano",
    "Waterfall",
    "World Heritage",
    "Landmark: Historical",
    "Landmark: Man-Made",
    "Landmark: Geological (Other)",
    "Special Interest",
    "Other",
]


def get_country_list():
    countryList = []
    for region in countries_by_region:
        regions_countries = countries_by_region[region]
        countryList.extend(regions_countries)

    return sorted(countryList)


def get_region_list():
    region_list = countries_by_region.keys()
    return sorted(region_list)


def get_category_list():
    return categoryList


def get_country_region(country):
    for region in countries_by_region:
        if country in countries_by_region[region]:
            return region


def validate_lat(value):
    print(value)
    match = lat_pattern.search(value.strip())
    print(match)
    return match


def validate_long(value):
    print(value)
    match = long_pattern.search(value.strip())
    print(match)
    return match


def generate_csvs():
    region_dict = 'countries_details = {' + '\n'

    print(os.getcwd());
    with open('flightsimdiscovery\\data\\Countries centroid.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # create dictionary
                region_details = '[\'' + str(row[3]).strip() + '\', ' + str(row[4]).strip() + ',' + str(row[5]).strip() + '],' + '\n'
                region_dict += '\t\'' + str(row[0]).strip() + '\': ' + region_details
                line_count += 1
    region_dict += '}'

    with open("flightsimdiscovery\\output\\Countries_dict.txt", "w") as text_file:
        text_file.write(region_dict)

    # generate region dictionary
    region_dict = 'region_details = {' + '\n'

    with open('flightsimdiscovery\\data\\Regions centroid.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # create dictionary
                region_details = '[' + str(row[1]).strip() + ',' + str(row[2]).strip() + ',' + str(row[3]).strip() + '],' + '\n'
                region_dict += '\t\'' + str(row[0]).strip() + '\': ' + region_details
                line_count += 1
    region_dict += '}'

    with open("flightsimdiscovery\\output\\Regions_dict.txt", "w") as text_file:
        text_file.write(region_dict)

    # generate Javascript ccuntry_region dict
    python_region_dict = {}

    with open('flightsimdiscovery\\data\\Countries centroid.csv') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # lets create a python dictionary first
                python_region_dict.setdefault(str(row[3]).strip(), []).append(str(row[0]))

    js_dict = 'var region_country = {' + '\n'

    for region, country_list in python_region_dict.items():
        # print(region)
        line_details = str(country_list)
        js_dict += '\t\'' + region + '\': ' + line_details + ',' + '\n'
        line_count += 1

    js_dict += '}'

    with open("flightsimdiscovery\\output\\JS_Regions_dict.txt", "w") as text_file:
        text_file.write(js_dict)


def create_pois_csv():
    # read in raw txt file and create a spaced file for each poi for regex to work with
    with open("flightsimdiscovery\\data\\FSDiscovery locations raw.txt", encoding="utf8") as myfile:
        # with open("poi_spaced_output.txt", encoding="utf8") as myfile:
        data = myfile.read()
        # write raw output file that has each poi on a new line
        f = codecs.open("flightsimdiscovery\\output\\poi_spaced_output.txt", "w", "utf-8-sig", )
        start_poi_matches = list(poi_start_pattern_compile.finditer(data))
        print(start_poi_matches)

        for count, match in enumerate(start_poi_matches):
            # print(start_poi_matches[count + 1])
            if count + 1 < len(start_poi_matches):
                start_string = match.span()[0]
                end_string = start_poi_matches[count + 1].span()[0]

                line = data[start_string:end_string]
                f.write(line)
                f.write("\n")
                f.write("\n")

        f.close()

    with open("flightsimdiscovery\\output\\poi_spaced_output.txt", encoding="utf8") as myfile:
        data = myfile.read()

    raw_poi_matches = re.findall(poi_pattern, data)

    workbook = Workbook()
    sheet = workbook.active
    sheet['A1'] = 'NAME'
    sheet['B1'] = 'CATEGORY'
    sheet['C1'] = 'LATITUDE'
    sheet['D1'] = 'LONGITUDE'
    sheet['E1'] = 'COUNTRY'
    sheet['F1'] = 'REGION'
    sheet['G1'] = 'DESCRITPION'

    row = 2
    us_states = [

        'Ohio',
        'Kentucky',
        'West Virginia',
        'New York',
        'New Hampshire',
        'Vermont',
        'Maine',
        'Cahokia Mounds State Historic Site Illinois',
        'Michigan',
        'Pennsylvania',
        'Delaware',
        'DC',
        'Georgia (US)',
        'North Carolina',
        'Tennessee',
        'Virginia',
        'Florida',
        'Utah',
        'Arizona',
        'New Mexico',
        'Nevada',
        'Wyoming',
        'Montana',
        'California',
        'Oregon',
        'Washington',
        'Colorado',
        'Idaho',
        'South Dakota',
        'North Dakota',
        'Minnesota',
        'Missouri',
        'Hawaii',
        'Alaska'
    ]

    for count, match in enumerate(raw_poi_matches, start=2):

        update_notes_with_category = False

        # notes category
        notes_match = re.search(notes_pattern, match)
        if notes_match:
            # print(notes_match.group())

            notes = notes_match.group(1)
            notes = notes.replace("u0027", "'")
            notes = notes.strip('"').strip('\\')
            notes = notes.replace("\\\\\\", "")
            notes = notes.replace("\\\'s", "\'s")

            print('Notes: ' + notes)
        else:
            notes = ""
            print('Notes: ' + notes)
            update_notes_with_category = True
        print('\n', row)
        sheet['G' + str(row)] = notes

        # extract category
        category_match = re.search(category_pattern, match)
        if category_match:
            # print(category_match.group())
            category = category_match.group(1).strip('"').strip('\\').strip()

            if update_notes_with_category:
                sheet['G' + str(row)] = category

            # re-organise categories
            if category in ['Town', 'City', 'Town/City', 'CIty', 'Towns', 'County', 'State Park', 'State Capital', 'Beach Town', 'Beach/Town',
                            'Botanical Garden',
                            'Capital/National Park/Islands', 'City (Abandoned)', 'City/Geolical Landmark', 'City/Isthmus', 'City/Lake/Mountains',
                            'Cliffs/Caverns', 'Ghost Town', 'Island/State Park', 'Municipality', 'Nature Preserve', 'Nature Reserve', 'Peninsula',
                            'Scenic Byway', 'Abandoned Town', 'arcipelago', 'Oasis', 'Town/Peninsula', 'Achipelago']:
                continue

            if 'UNESCO' in category:
                category = 'World Heritage'
            elif 'Canyon' in category:
                category = 'Canyon'
            elif 'Island' in category:
                category = 'Island'
            elif 'Islands' in category:
                category = 'Island'
            elif 'Lake' in category:
                category = 'Lake'
            elif 'Mountain' in category:
                category = 'Mountain'
            elif 'National Park' in category:
                category = 'National Park'
            elif 'Historical Landmark' in category:
                category = 'Landmark: Historical'
            elif 'Lakes' in category:
                category = 'Lake'
            elif 'Megacity/Capital' in category:
                category = 'Megacity'
            elif 'Mountains' in category:
                category = 'Mountain'
            elif 'Prison Camp' in category:
                category = 'Special Interest'
            elif 'Valley' in category:
                category = 'Valley'
            elif 'Village' in category:
                category = 'Village'
            elif 'Volcanos' in category:
                category = 'Volcano'
            elif 'Volcano' in category:
                category = 'Volcano'
            elif 'Waterfall' in category:
                category = 'Waterfall'
            elif 'Waterfalls' in category:
                category = 'Waterfall'
            elif 'Landmark' in category:
                category = 'Landmark: Geological (Other)'
            elif 'Salt Flat' in category:
                category = 'Landmark: Geological (Other)'
            elif 'Archipelago' in category:
                category = 'Landmark: Geological (Other)'
            elif 'Atoll' in category:
                category = 'Landmark: Geological (Other)'
            elif 'Bay' in category:
                category = 'Landmark: Geological (Other)'
            elif 'Dam' in category:
                category = 'Landmark: Man-Made'
            elif 'Capital' in category:
                category = 'Capital City'

            print('Category: ' + category)
            sheet['B' + str(row)] = category

        # extract location
        location_match = re.search(location_pattern, match)
        if location_match:
            # print(location_match.group())
            location = location_match.group(1).strip('"')
            location = location.strip('\\')
            location = location.replace("*", "")
            location.strip()
            location = location.replace("u0027", "'")
            location = location.replace("u0026", "@")
            location = location.replace("\\\\\\", "")
            location = location.replace("\\\'s", "\'s")
            location = location.replace("\\\'l", "\'l")
            name = location.split(", ")[0]
            name = name.replace("Nat'l", 'National')
            print('Name: ' + name)
            # sheet['"A' + str(row) + '"'] = name
            sheet['A' + str(row)] = name

        # extract latitude and lngitude
        latt_long_match = re.search(lat_long_pattern, match)
        # print('\n')
        if latt_long_match:
            # print(latt_long_match.group())
            latitude_sign = latt_long_match.group(1)
            latitude = latt_long_match.group(2)
            if latitude_sign:
                latitude = latitude_sign + latt_long_match.group(2)
            longitude = latt_long_match.group(3)
            print('Lattitude: ' + latitude)
            print('Longitude: ' + longitude)
            sheet['C' + str(row)] = latitude
            sheet['D' + str(row)] = longitude

        # extract country from location
        country = location.split(", ")[-1].strip()
        if country in us_states:
            country = "United States of America"
        elif country == 'Canda':
            country = "Canada"
        elif country == 'Peru (also Bolivia)':
            country = "Peru"
        elif country == 'Argentina (also Brazil)':
            country = "Argentina"
        elif country == 'UK/Argentina':
            country = "Great Britain"
        elif country == 'St. Lucia':
            country = "Saint Lucia"
        elif country == 'St. Barts (Barthelemy)':
            country = "Saint Barthélemy"
        elif country == 'US Virgin Islands':
            country = "U.S. Virgin Islands"
        elif country == 'St. Maarten/Saint Martin':
            country = 'Netherlands'
        elif country == 'St. Vincent and the Grenadines':
            country = 'Saint Vincent and the Grenadines'
        elif country == 'St. Kitts and Nevis':
            country = 'Saint Kitts and Nevis'
        elif country == 'the Netherlands':
            country = 'Netherlands'
        elif country == 'England':
            country = 'Great Britain'
        elif country == 'Scotland':
            country = 'Great Britain'
        elif country == 'Wales':
            country = 'Great Britain'
        elif country == 'Isle of Man':
            country = 'Great Britain'
        elif country == 'Northern Ireland':
            country = 'Great Britain'
        elif country == 'Italy (also Austria)':
            country = 'Italy'
        elif country == 'Vatican City (Holy See)':
            country = 'Italy'
        elif country == 'Russia':
            country = 'Russian Federation'
        elif country == 'Moldova':
            country = 'Moldova, Republic of'
        elif country == 'United Arab Emirates (UAE)':
            country = 'United Arab Emirates'
        elif country == 'Pakistan (also China)':
            country = 'Pakistan'
        elif country == 'Tibet':
            country = 'China'
        elif country == 'China?':
            country = 'China'
        elif country == 'Okinawa. Japan':
            country = 'Japan'
        elif country == 'South Korea/North Korea':
            country = 'South Korea'
        elif country == 'Vietnam':
            country = 'Vietnam'
        elif country == 'Vietnam (also China)':
            country = 'Vietnam'
        elif country == 'Myanmar (Burma)':
            country = 'Myanmar'
        elif country == 'Somoa':
            country = 'Samoa'
        elif country == 'Pitcairn Islands':
            country = 'Pitcairn'
        elif country == 'South Africa (also Botswana)':
            country = 'South Africa'
        elif country == 'Zambia (also Zimbabwe)':
            country = 'Zambia'
        elif country == 'The Gambia':
            country = 'Gambia'
        elif country == 'Eswatini (Swaziland)':
            country = 'Swaziland'
        elif country == 'Cape Verde':
            country = 'Cabo Verde'
        elif country == 'Bonaire':
            country = 'Netherlands'
        elif country == 'Curaçao':
            country = 'Netherlands'
        elif country == "Jostedalsbreen Nat'l Park":
            country = 'Norway'
        elif country == "Macau":
            country = 'Macao'
        elif country == "St. Helena":
            country = 'Great Britain'
        elif country == "Tristan da Cunha":
            country = 'Great Britain'
        elif country == "North Macedonia (also Albania)":
            country = 'North Macedonia'
        elif "Bosnia" in country:
            country = 'Bosnia and Herzegovina'
        elif "Saba" in country:
            country = 'Netherlands'
        elif country == "Turks and Caicos":
            country = 'Great Britain'

        print('Country: ' + country)
        sheet['E' + str(row)] = country
        sheet['E' + str(row)] = country

        # # extract category
        # continent_match = re.search(continent_pattern, match)
        # if continent_match:
        #     # print(continent_match.group())
        #     region = continent_match.group(1).strip('"').strip('\\')
        #

        sheet['F' + str(row)] = get_country_region(country)

        row += 1

    workbook.save(filename="flightsimdiscovery\\output\\poi_database.xlsx")


# return closest airport to a latlng value
def get_nearest_airport(airports, waypoint):

    def distance_between_points(lat1, lon1, lat2, lon2):
        p = 0.017453292519943295
        a = 0.5 - cos((lat2 - lat1) * p) / 2 + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
        return 12742 * asin(sqrt(a))

    nearest_airport_data = min(airports, key=lambda p: distance_between_points(p['lat'], p['lon'], waypoint['lat'], waypoint['lon']))
    # print('Closest airport: ', nearest_airport_data)

    if nearest_airport_data['Airport_Name'].strip() == waypoint['airport_name'].strip():
        altered_airport_list = [item for item in airports if item['Airport_Name'].strip() != waypoint['airport_name'].strip()]
        # print('Altered: ', altered_airport_list)
        nearest_airport_data = get_nearest_airport(altered_airport_list, waypoint)

    return nearest_airport_data




if __name__ == '__main__':
    pass

    # create empty database

    # tempDataList = [{'Airport_Name': 'Name1', 'lat': 39.7612992, 'lon': -86.1519681},
    #                 {'Airport_Name': 'Name2', 'lat': 39.762241, 'lon': -86.158436},
    #                 {'Airport_Name': 'Name3', 'lat': 39.7622292, 'lon': -86.1578917}]
    #
    # point = {'airport_name': 'Wollongong','lat': 39.7622290, 'lon': -86.1519750}
    #
    # print('Original: ', tempDataList)
    #
    # closest_airport = get_nearest_airport(tempDataList, point)
    # print('Next Closest airport: ', closest_airport)

    # generate_csvs()
    # create_pois_csv()

    # test get_country_region
    # print(get_country_region('Australia'))
    # print(get_region_list)
    # print(get_country_list())

    # test lattitude
    # lat_value = 34
    # validity = validate_lat(str(lat_value))

    # # test longitude
    # long_value = 220.3423
    # validity = validate_long(str(long_value))
