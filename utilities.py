import re
import csv

# validate latitude and longitude constants
lat_pattern = re.compile(r"^(\+|-)?(?:90(?:(?:\.0{1,10})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,10})?))$")
long_pattern = re.compile(r"^(\+|-)?(?:180(?:(?:\.0{1,10})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,10})?))$")

region_details = {
	'Africa - Eastern': [-5.188246,35.136011,6],
	'Africa - Middle': [2.099101,17.294214,6],
	'Africa - Northern': [26.028232,16.503199,6],
	'Africa - Southern': [-23.988214,23.401357,6],
	'Africa - Western': [12,3,6],
	'America - Central': [17.4,-91,7],
	'America - Northern': [44.35528,-99.99917,5],
	'America - South': [-19.24773,-61.52741,4.5],
	'Antartica': [-75.250973,-0.071389,4],
	'Asia - Central': [45.3,63.9,5],
	'Asia - Eastern': [39.286757,112.064601,5],
	'Asia - South-eastern': [11.998224,120.656442,5],
	'Asia - Southern': [26.9,72.2,5],
	'Asia - Western': [32.811895,40.661186,5],
	'Caribbean': [19.593216,-68.968228,6],
	'Europe - Eastern': [50,30,5],
	'Europe - Northern': [59.155256,16.123697,6],
	'Europe - Southern': [45.160168,15.1362,6],
	'Europe - Western': [52.261223,11.669846,5],
	'Oceania': [-22.696926,161.591196,5],
}

countries_details = {
	'Afghanistan': ['Asia - Southern', 33.93911,67.709953],
	'Albania': ['Europe - Southern', 41.153332,20.168331],
	'Algeria': ['Africa - Northern', 28.033886,1.659626],
	'American Samoa': ['Oceania', -14.270972,-170.132217],
	'Andorra': ['Europe - Southern', 42.546245,1.601554],
	'Angola': ['Africa - Middle', -11.202692,17.873887],
	'Anguilla': ['Caribbean', 18.220554,-63.068615],
	'Antarctica': ['Antartica', -75.250973,-0.071389],
	'Antigua and Barbuda': ['Caribbean', 17.060816,-61.796428],
	'Argentina': ['America - South', -38.416097,-63.616672],
	'Armenia': ['Middle East', 40.069099,45.038189],
	'Aruba': ['Caribbean', 12.52111,-69.968338],
	'Australia': ['Oceania', -25.274398,133.775136],
	'Austria': ['Europe - Western', 47.516231,14.550072],
	'Azerbaijan': ['Middle East', 40.143105,47.576927],
	'Bahamas': ['Caribbean', 25.03428,-77.39628],
	'Bahrain': ['Middle East', 25.930414,50.637772],
	'Bangladesh': ['Asia - Southern', 23.684994,90.356331],
	'Barbados': ['Caribbean', 13.193887,-59.543198],
	'Belarus': ['Europe - Eastern', 53.709807,27.953389],
	'Belgium': ['Europe - Western', 50.503887,4.469936],
	'Belize': ['America - Central', 17.189877,-88.49765],
	'Benin': ['Africa - Western', 9.30769,2.315834],
	'Bermuda': ['America - Northern', 32.321384,-64.75737],
	'Bhutan': ['Asia - Southern', 27.514162,90.433601],
	'Bolivia': ['America - South', -16.290154,-63.588653],
	'Bosnia and Herzegovina': ['Europe - Southern', 43.915886,17.679076],
	'Botswana': ['Africa - Southern', -22.328474,24.684866],
	'Brazil': ['America - South', -14.235004,-51.92528],
	'British Indian Ocean Territory': ['Africa - Eastern', -6.343194,71.876519],
	'British Virgin Islands': ['Caribbean', 18.420695,-64.639968],
	'Brunei': ['Asia - South-eastern', 4.535277,114.727669],
	'Bulgaria': ['Europe - Eastern', 42.733883,25.48583],
	'Burkina Faso': ['Africa - Western', 12.238333,-1.561593],
	'Burundi': ['Africa - Eastern', -3.373056,29.918886],
	'Cabo Verde': ['Africa - Western', 12.565679,104.990963],
	'Cambodia': ['Asia - South-eastern', 7.369722,12.354722],
	'Cameroon': ['Africa - Middle', 56.130366,-106.346771],
	'Canada': ['America - Northern', 16.002082,-24.013197],
	'Cayman Islands': ['Caribbean', 19.513469,-80.566956],
	'Central African Republic': ['Africa - Middle', 6.611111,20.939444],
	'Chad': ['Africa - Middle', 15.454166,18.732207],
	'Chile': ['America - South', -35.675147,-71.542969],
	'China': ['Asia - Eastern', 35.86166,104.195397],
	'Christmas Island': ['Oceania', -10.447525,105.690449],
	'Cocos (Keeling) Islands': ['Oceania', -12.164165,96.870956],
	'Colombia': ['America - South', 4.570868,-74.297333],
	'Comoros': ['Africa - Eastern', -11.875001,43.872219],
	'Congo': ['Africa - Middle', -4.038333,21.758664],
	'Congo, Democratic Republic of the': ['Africa - Middle', -0.228021,15.827659],
	'Cook Islands': ['Oceania', -21.236736,-159.777671],
	'Costa Rica': ['America - Central', 9.748917,-83.753428],
	'Croatia': ['Europe - Southern', 45.1,15.2],
	'Cuba': ['Caribbean', 21.521757,-77.781167],
	'Cyprus': ['Middle East', 35.126413,33.429859],
	'Czechia': ['Europe - Eastern', 49.817492,15.472962],
	'Denmark': ['Europe - Northern', 56.26392,9.501785],
	'Djibouti': ['Africa - Eastern', 11.825138,42.590275],
	'Dominica': ['Caribbean', 15.414999,-61.370976],
	'Dominican Republic': ['Caribbean', 18.735693,-70.162651],
	'Ecuador': ['America - South', -1.831239,-78.183406],
	'Egypt': ['Africa - Northern', 26.820553,30.802498],
	'El Salvador': ['America - Central', 13.794185,-88.89653],
	'Equatorial Guinea': ['Africa - Middle', 1.650801,10.267895],
	'Eritrea': ['Africa - Eastern', 15.179384,39.782334],
	'Estonia': ['Europe - Northern', 58.595272,25.013607],
	'Eswatini': ['Africa - Southern', 9.145,40.489673],
	'Ethiopia': ['Africa - Eastern', -51.796253,39.782334],
	'Falkland Islands (Malvinas)': ['America - South', 61.892635,-6.911806],
	'Faroe Islands': ['Europe - Northern', -16.578193,179.414413],
	'Fiji': ['Oceania', 61.92411,25.748151],
	'Finland': ['Europe - Northern', 46.227638,2.213749],
	'France': ['Europe - Western', 3.933889,-53.125782],
	'French Guiana': ['America - South', -17.679742,-149.406843],
	'French Oceania': ['Oceania', -49.280366,69.348557],
	'French Southern Territories': ['Africa - Eastern', -0.803689,11.609444],
	'Gabon': ['Africa - Middle', 13.443182,-15.310139],
	'Gambia': ['Africa - Western', 31.354676,34.308825],
	'Georgia': ['Middle East', 42.315407,43.356892],
	'Germany': ['Europe - Western', 51.165691,10.451526],
	'Ghana': ['Africa - Western', 7.946527,-1.023194],
	'Gibraltar': ['Europe - Southern', 36.137741,-5.345374],
	'Great Britain': ['Europe - Northern', 55.378051,-3.435973],
	'Greece': ['Europe - Southern', 39.074208,21.824312],
	'Greenland': ['America - Northern', 71.706936,-42.604303],
	'Grenada': ['Caribbean', 12.262776,-61.604171],
	'Guadeloupe': ['Caribbean', 16.995971,-62.067641],
	'Guam': ['Oceania', 13.444304,144.793731],
	'Guatemala': ['America - Central', 15.783471,-90.230759],
	'Guernsey': ['America - Central', 49.465691,-2.585278],
	'Guinea': ['Africa - Western', 9.945587,-9.696645],
	'Guinea-Bissau': ['Africa - Western', 11.803749,-15.180413],
	'Guyana': ['Africa - Western', 4.860416,-58.93018],
	'Haiti': ['America - South', 18.971187,-72.285215],
	'Heard Island and McDonald Islands': ['Caribbean', -53.08181,73.504158],
	'Honduras': ['America - Central', 15.199999,-86.241905],
	'Hong Kong': ['Asia - Eastern', 22.396428,114.109497],
	'Hungary': ['Europe - Eastern', 47.162494,19.503304],
	'Iceland': ['Europe - Northern', 64.963051,-19.020835],
	'India': ['Asia - Southern', 20.593684,78.96288],
	'Indonesia': ['Asia - South-eastern', -0.789275,113.921327],
	'Iran': ['Asia - Southern', 32.427908,53.688046],
	'Iraq': ['Middle East', 33.223191,43.679291],
	'Ireland': ['Europe - Northern', 53.41291,-8.24389],
	'Isle of Man': ['Europe - Northern', 54.236107,-4.548056],
	'Israel': ['Middle East', 31.046051,34.851612],
	'Italy': ['Europe - Southern', 41.87194,12.56738],
	'Ivory Coast': ['Africa - Western', 7.539989,-5.54708],
	'Jamaica': ['Caribbean', 18.109581,-77.297508],
	'Japan': ['Asia - Eastern', 36.204824,138.252924],
	'Jersey': ['Europe - Northern', 49.214439,-2.13125],
	'Jordan': ['Middle East', 30.585164,36.238414],
	'Kazakhstan': ['Asia - Central', 48.019573,66.923684],
	'Kenya': ['Africa - Eastern', -0.023559,37.906193],
	'Kiribati': ['Oceania', -3.370417,-168.734039],
	'Kosovo': ['Europe - Southern', 42.602636,20.902977],
	'Kuwait': ['Middle East', 29.31166,47.481766],
	'Kyrgyzstan': ['Asia - Central', 41.20438,74.766098],
	'Laos': ['Asia - South-eastern', 19.85627,102.495496],
	'Latvia': ['Europe - Northern', 56.879635,24.603189],
	'Lebanon': ['Middle East', 33.854721,35.862285],
	'Lesotho': ['Africa - Southern', -29.609988,28.233608],
	'Liberia': ['Africa - Western', 6.428055,-9.429499],
	'Libya': ['Africa - Northern', 26.3351,17.228331],
	'Liechtenstein': ['Europe - Western', 47.166,9.555373],
	'Lithuania': ['Europe - Northern', 55.169438,23.881275],
	'Luxembourg': ['Europe - Western', 49.815273,6.129583],
	'Macao': ['Asia - Eastern', 22.198745,113.543873],
	'Madagascar': ['Africa - Eastern', 41.608635,21.745275],
	'Malawi': ['Africa - Eastern', -18.766947,46.869107],
	'Malaysia': ['Asia - South-eastern', -13.254308,34.301525],
	'Maldives': ['Asia - Southern', 4.210484,101.975766],
	'Mali': ['Africa - Western', 3.202778,73.22068],
	'Malta': ['Europe - Southern', 17.570692,-3.996166],
	'Marshall Islands': ['Oceania', 35.937496,14.375416],
	'Martinique': ['Caribbean', 7.131474,171.184478],
	'Mauritania': ['Africa - Western', 14.641528,-61.024174],
	'Mauritius': ['Africa - Eastern', 21.00789,-10.940835],
	'Mayotte': ['Africa - Eastern', -20.348404,57.552152],
	'Mexico': ['America - Central', 23.634501,-102.552784],
	'Moldova, Republic of': ['Europe - Eastern', 47.411631,28.369885],
	'Monaco': ['Europe - Western', 43.750298,7.412841],
	'Mongolia': ['Asia - Eastern', 46.862496,103.846656],
	'Montenegro': ['Europe - Southern', 42.708678,19.37439],
	'Montserrat': ['Caribbean', 16.742498,-62.187366],
	'Morocco': ['Africa - Northern', 31.791702,-7.09262],
	'Mozambique': ['Africa - Eastern', -18.665695,35.529562],
	'Myanmar': ['Asia - South-eastern', 21.913965,95.956223],
	'Namibia': ['Africa - Southern', -22.95764,18.49041],
	'Nauru': ['Oceania', -0.522778,166.931503],
	'Nepal': ['Asia - Southern', 28.394857,84.124008],
	'Netherlands': ['Europe - Western', 52.132633,5.291266],
	'New Caledonia': ['Oceania', 12.226079,-69.060087],
	'New Zealand': ['Oceania', -20.904305,165.618042],
	'Nicaragua': ['America - Central', -40.900557,174.885971],
	'Niger': ['Africa - Western', 12.865416,-85.207229],
	'Nigeria': ['Africa - Western', 17.607789,8.081666],
	'Niue': ['Oceania', 9.081999,8.675277],
	'Norfolk Island': ['Oceania', -19.054445,-169.867233],
	'North Korea': ['Asia - Eastern', -29.040835,167.954712],
	'North Macedonia': ['Europe - Southern', 40.339852,127.510093],
	'Northern Mariana Islands': ['Oceania', 17.33083,145.38469],
	'Norway': ['Europe - Northern', 60.472024,8.468946],
	'Oceania (Federated States of)': ['Oceania', 7.425554,150.550812],
	'Oman': ['Middle East', 21.512583,55.923255],
	'Pakistan': ['Asia - Southern', 30.375321,69.345116],
	'Palau': ['Oceania', 7.51498,134.58252],
	'Palestine, State of': ['Middle East', 31.952162,35.233154],
	'Panama': ['America - Central', 8.537981,-80.782127],
	'Papua New Guinea': ['Oceania', -6.314993,143.95555],
	'Paraguay': ['America - South', -23.442503,-58.443832],
	'Peru': ['America - South', -9.189967,-75.015152],
	'Philippines': ['Asia - South-eastern', 12.879721,121.774017],
	'Pitcairn': ['Oceania', -24.703615,-127.439308],
	'Poland': ['Europe - Eastern', 51.919438,19.145136],
	'Portugal': ['Europe - Southern', 39.399872,-8.224454],
	'Puerto Rico': ['Caribbean', 18.220833,-66.590149],
	'Qatar': ['Middle East', 25.354826,51.183884],
	'Réunion': ['Africa - Eastern', -21.115141,55.536384],
	'Romania': ['Europe - Eastern', 45.943161,24.96676],
	'Russian Federation': ['Europe - Eastern', 61.52401,105.318756],
	'Rwanda': ['Africa - Eastern', -1.940278,29.873888],
	'Saint Barthélemy': ['Caribbean', -15.95,-5.71667],
	'Saint Helena': ['Africa - Western', -24.143474,-10.030696],
	'Saint Kitts and Nevis': ['Caribbean', 17.357822,-62.782998],
	'Saint Lucia': ['Caribbean', 13.909444,-60.978893],
	'Saint Pierre and Miquelon': ['America - Northern', 46.941936,-56.27111],
	'Saint Vincent and the Grenadines': ['Caribbean', 12.984305,-61.287228],
	'Samoa': ['Oceania', -13.759029,-172.104629],
	'San Marino': ['Europe - Southern', 43.94236,12.457777],
	'Sao Tome and Principe': ['Africa - Middle', 0.18636,6.613081],
	'Saudi Arabia': ['Middle East', 23.885942,45.079162],
	'Senegal': ['Africa - Western', 14.497401,-14.452362],
	'Serbia': ['Europe - Southern', 44.016521,21.005859],
	'Seychelles': ['Africa - Eastern', -4.679574,55.491977],
	'Sierra Leone': ['Africa - Western', 8.460555,-11.779889],
	'Singapore': ['Asia - South-eastern', 1.352083,103.819836],
	'Slovakia': ['Europe - Eastern', 48.669026,19.699024],
	'Slovenia': ['Europe - Southern', 46.151241,14.995463],
	'Solomon Islands': ['Oceania', -9.64571,160.156194],
	'Somalia': ['Africa - Eastern', 5.152149,46.199616],
	'South Africa': ['Africa - Southern', -30.559482,22.937506],
	'South Georgia': ['America - South', -54.429579,-36.587909],
	'South Korea': ['Asia - Eastern', 35.907757,127.766922],
	'South Sudan': ['Africa - Eastern', 6.889577,30.747197],
	'Spain': ['Europe - Southern', 40.463667,-3.74922],
	'Sri Lanka': ['Asia - Southern', 7.873054,80.771797],
	'Sudan': ['Africa - Northern', 12.862807,30.217636],
	'Suriname': ['America - South', 3.919305,-56.027783],
	'Svalbard and Jan Mayen': ['Europe - Northern', 77.553604,23.670272],
	'Swaziland': ['Africa - Southern', -26.522503,31.465866],
	'Sweden': ['Europe - Northern', 60.128161,18.643501],
	'Switzerland': ['Europe - Western', 46.818188,8.227512],
	'Syria': ['Middle East', 34.802075,38.996815],
	'Taiwan': ['Asia - Eastern', 23.69781,120.960515],
	'Tajikistan': ['Asia - Central', 38.861034,71.276093],
	'Tanzania': ['Africa - Eastern', -6.369028,34.888822],
	'Thailand': ['Asia - South-eastern', 15.870032,100.992541],
	'Timor-Leste': ['Asia - South-eastern', -8.874217,125.727539],
	'Togo': ['Africa - Western', 8.619543,0.824782],
	'Tokelau': ['Oceania', -8.967363,-171.855881],
	'Tonga': ['Oceania', -21.178986,-175.198242],
	'Trinidad and Tobago': ['Caribbean', 10.691803,-61.222503],
	'Tunisia': ['Africa - Northern', 33.886917,9.537499],
	'Turkey': ['Middle East', 38.963745,35.243322],
	'Turkmenistan': ['Asia - Central', 38.969719,59.556278],
	'Turks and Caicos Islands': ['Caribbean', 21.694025,-71.797928],
	'Tuvalu': ['Oceania', -7.109535,177.64933],
	'U.S. Virgin Islands': ['Caribbean', 18.335765,-64.896335],
	'Uganda': ['Africa - Eastern', 1.373333,32.290275],
	'Ukraine': ['Europe - Eastern', 48.379433,31.16558],
	'United Arab Emirates': ['Middle East', 23.424076,53.847818],
	'United States of America': ['America - Northern', 37.09024,-95.712891],
	'Uruguay': ['America - South', -32.522779,-55.765835],
	'Uzbekistan': ['Asia - Central', 41.377491,64.585262],
	'Vanuatu': ['Oceania', -15.376706,166.959158],
	'Venezuela': ['America - South', 6.42375,-66.58973],
	'VietNam': ['Asia - South-eastern', 14.058324,108.277199],
	'Wallis and Futuna': ['Oceania', -13.768752,-177.156097],
	'Western Sahara': ['Africa - Northern', 24.215527,-12.885834],
	'Yemen': ['Middle East', 15.552727,48.516388],
	'Zambia': ['Africa - Southern', -13.133897,27.849332],
	'Zimbabwe': ['Africa - Southern', -19.015438,29.154857],
}

countries_by_region = {
	'Asia - Southern': ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Iran', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka'],
	'Europe - Southern': ['Albania', 'Andorra', 'Bosnia and Herzegovina', 'Croatia', 'Gibraltar', 'Greece', 'Italy', 'Kosovo', 'Malta', 'Montenegro', 'North Macedonia', 'Portugal', 'San Marino', 'Serbia', 'Slovenia', 'Spain'],
	'Africa - Northern': ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Sudan', 'Tunisia', 'Western Sahara'],
	'Oceania': ['American Samoa', 'Australia', 'Christmas Island', 'Cocos (Keeling) Islands', 'Cook Islands', 'Fiji', 'French Oceania', 'Guam', 'Kiribati', 'Marshall Islands', 'Nauru', 'New Caledonia', 'New Zealand', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Oceania (Federated States of)', 'Palau', 'Papua New Guinea', 'Pitcairn', 'Samoa', 'Solomon Islands', 'Tokelau', 'Tonga', 'Tuvalu', 'Vanuatu', 'Wallis and Futuna'],
	'Africa - Middle': ['Angola', 'Cameroon', 'Central African Republic', 'Chad', 'Congo', 'Congo, Democratic Republic of the', 'Equatorial Guinea', 'Gabon', 'Sao Tome and Principe'],
	'Caribbean': ['Anguilla', 'Antigua and Barbuda', 'Aruba', 'Bahamas', 'Barbados', 'British Virgin Islands', 'Cayman Islands', 'Cuba', 'Dominica', 'Dominican Republic', 'Grenada', 'Guadeloupe', 'Heard Island and McDonald Islands', 'Jamaica', 'Martinique', 'Montserrat', 'Puerto Rico', 'Saint Barthélemy', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'Turks and Caicos Islands', 'U.S. Virgin Islands'],
	'Antartica': ['Antarctica'],
	'America - South': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Falkland Islands (Malvinas)', 'French Guiana', 'Haiti', 'Paraguay', 'Peru', 'South Georgia', 'Suriname', 'Uruguay', 'Venezuela'],
	'Middle East': ['Armenia', 'Azerbaijan', 'Bahrain', 'Cyprus', 'Georgia', 'Iraq', 'Israel', 'Jordan', 'Kuwait', 'Lebanon', 'Oman', 'Palestine, State of', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'United Arab Emirates', 'Yemen'],
	'Europe - Western': ['Austria', 'Belgium', 'France', 'Germany', 'Liechtenstein', 'Luxembourg', 'Monaco', 'Netherlands', 'Switzerland'],
	'Europe - Eastern': ['Belarus', 'Bulgaria', 'Czechia', 'Hungary', 'Moldova, Republic of', 'Poland', 'Romania', 'Russian Federation', 'Slovakia', 'Ukraine'],
	'America - Central': ['Belize', 'Costa Rica', 'El Salvador', 'Guatemala', 'Guernsey', 'Honduras', 'Mexico', 'Nicaragua', 'Panama'],
	'Africa - Western': ['Benin', 'Burkina Faso', 'Cabo Verde', "Côte d'Ivoire", 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Liberia', 'Mali', 'Mauritania', 'Niger', 'Nigeria', 'Saint Helena', 'Senegal', 'Sierra Leone', 'Togo'],
	'America - Northern': ['Bermuda', 'Canada', 'Greenland', 'Saint Pierre and Miquelon', 'United States of America'],
	'Africa - Southern': ['Botswana', 'Eswatini', 'Lesotho', 'Namibia', 'South Africa', 'Swaziland', 'Zambia', 'Zimbabwe'],
	'Africa - Eastern': ['British Indian Ocean Territory', 'Burundi', 'Comoros', 'Djibouti', 'Eritrea', 'Ethiopia', 'French Southern Territories', 'Kenya', 'Madagascar', 'Malawi', 'Mauritius', 'Mayotte', 'Mozambique', 'Réunion', 'Rwanda', 'Seychelles', 'Somalia', 'South Sudan', 'Tanzania', 'Uganda'],
	'Asia - South-eastern': ['Brunei', 'Cambodia', 'Indonesia', 'Laos', 'Malaysia', 'Myanmar', 'Philippines', 'Singapore', 'Thailand', 'Timor-Leste', 'VietNam'],
	'Asia - Eastern': ['China', 'Hong Kong', 'Japan', 'Macao', 'Mongolia', 'North Korea', 'South Korea', 'Taiwan'],
	'Europe - Northern': ['Denmark', 'Estonia', 'Faroe Islands', 'Finland', 'Great Britain', 'Iceland', 'Ireland', 'Isle of Man', 'Jersey', 'Latvia', 'Lithuania', 'Norway', 'Svalbard and Jan Mayen', 'Sweden'],
	'Asia - Central': ['Kazakhstan', 'Kyrgyzstan', 'Tajikistan', 'Turkmenistan', 'Uzbekistan'],
}

categoryList = [ 
	"Building",
	"Bush Strips",
	"Canyon",
	"City/town",
	"Dessert",
	"Helipads",
	"Infrastructure",
	"Interesting",
	"Island",
	"Lake",
	"Mountain",
	"National Park",
	"Other",
	"Reef",
	"River",
	"Seaports",
	"Seaports",
	"Volcano",
	"Waterfall",
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

    with open('Countries centroid.csv') as csv_file:
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

    with open("Countries_dict.txt", "w") as text_file:
        text_file.write(region_dict)

    # generate region dictionary
    region_dict = 'region_details = {' + '\n'

    with open('Regions centroid.csv') as csv_file:
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

    with open("Regions_dict.txt", "w") as text_file:
        text_file.write(region_dict)


    # generate Javascript ccuntry_region dict
    python_region_dict = {}

    with open('Countries centroid.csv') as csv_file:

        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # lets create a python dictionary first
                python_region_dict.setdefault(str(row[3]).strip(),[]).append(str(row[0]))
            
    js_dict = 'var region_country = {' + '\n'

    for region, country_list in python_region_dict.items():
            # print(region)
            line_details = str(country_list) 
            js_dict += '\t\'' + region + '\': ' + line_details + ',' + '\n'
            line_count += 1

    js_dict += '}'

    with open("JS_Regions_dict.txt", "w") as text_file:
        text_file.write(js_dict)    

if __name__ == '__main__':

    # pass
    generate_csvs() 

    # test get_country_region
    # print(get_country_region('Australia'))
    # print(get_region_list)
    # print(get_country_list())

    #test lattitude
    # lat_value = 34
    # validity = validate_lat(str(lat_value))

    # # test longitude
    # long_value = 220.3423
    # validity = validate_long(str(long_value))
