import re
import csv

# validate latitude and longitude constants
lat_pattern = re.compile(r"^(\+|-)?(?:90(?:(?:\.0{1,10})?)|(?:[0-9]|[1-8][0-9])(?:(?:\.[0-9]{1,10})?))$")
long_pattern = re.compile(r"^(\+|-)?(?:180(?:(?:\.0{1,10})?)|(?:[0-9]|[1-9][0-9]|1[0-7][0-9])(?:(?:\.[0-9]{1,10})?))$")

countries_by_region = {
	'Asia - Southern': ['Afghanistan', 'Bangladesh', 'Bhutan', 'India', 'Iran', 'Maldives', 'Nepal', 'Pakistan', 'Sri Lanka'],
	'Europe - Southern ': ['Albania', 'Andorra', 'Bosnia and Herzegovina', 'Croatia', 'Gibraltar', 'Greece', 'Italy', 'Kosovo', 'Malta', 'Montenegro', 'North Macedonia', 'Portugal', 'San Marino', 'Serbia', 'Slovenia', 'Spain'],
	'Africa - Northern ': ['Algeria', 'Egypt', 'Libya', 'Morocco', 'Sudan', 'Tunisia', 'Western Sahara'],
	'Oceania': ['American Samoa', 'Australia', 'Christmas Island', 'Cocos (Keeling) Islands', 'Cook Islands', 'Fiji', 'French Oceania', 'Guam', 'Kiribati', 'Marshall Islands', 'Nauru', 'New Caledonia', 'New Zealand', 'Niue', 'Norfolk Island', 'Northern Mariana Islands', 'Oceania (Federated States of)', 'Palau', 'Papua New Guinea', 'Pitcairn', 'Samoa', 'Solomon Islands', 'Tokelau', 'Tonga', 'Tuvalu', 'Vanuatu', 'Wallis and Futuna'],
	'Africa - Middle ': ['Angola', 'Cameroon', 'Central African Republic', 'Chad', 'Congo', 'Congo, Democratic Republic of the', 'Equatorial Guinea', 'Gabon', 'Sao Tome and Principe'],
	'Caribbean': ['Anguilla', 'Antigua and Barbuda', 'Aruba', 'Bahamas', 'Barbados', 'British Virgin Islands', 'Cayman Islands', 'Cuba', 'Dominica', 'Dominican Republic', 'Grenada', 'Guadeloupe', 'Heard Island and McDonald Islands', 'Jamaica', 'Martinique', 'Montserrat', 'Puerto Rico', 'Saint Barthélemy', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Trinidad and Tobago', 'Turks and Caicos Islands', 'U.S. Virgin Islands'],
	'Antartica': ['Antarctica'],
	'America - South ': ['Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Ecuador', 'Falkland Islands (Malvinas)', 'French Guiana', 'Haiti', 'Paraguay', 'Peru', 'South Georgia', 'Suriname', 'Uruguay', 'Venezuela'],
	'Middle East': ['Armenia', 'Azerbaijan', 'Bahrain', 'Cyprus', 'Georgia', 'Iraq', 'Israel', 'Jordan', 'Kuwait', 'Lebanon', 'Oman', 'Palestine, State of', 'Qatar', 'Saudi Arabia', 'Syria', 'Turkey', 'United Arab Emirates', 'Yemen'],
	'Europe - Western ': ['Austria', 'Belgium', 'France', 'Germany', 'Liechtenstein', 'Luxembourg', 'Monaco', 'Netherlands', 'Switzerland'],
	'Europe - Eastern ': ['Belarus', 'Bulgaria', 'Czechia', 'Hungary', 'Moldova, Republic of', 'Poland', 'Romania', 'Russian Federation', 'Slovakia', 'Ukraine'],
	'America - Central ': ['Belize', 'Costa Rica', 'El Salvador', 'Guatemala', 'Guernsey', 'Honduras', 'Mexico', 'Nicaragua', 'Panama'],
	'Africa - Western ': ['Benin', 'Burkina Faso', 'Cabo Verde', "Côte d'Ivoire", 'Gambia', 'Ghana', 'Guinea', 'Guinea-Bissau', 'Guyana', 'Liberia', 'Mali', 'Mauritania', 'Niger', 'Nigeria', 'Saint Helena', 'Senegal', 'Sierra Leone', 'Togo'],
	'America - Northern ': ['Bermuda', 'Canada', 'Greenland', 'Saint Pierre and Miquelon', 'United States of America'],
	'Africa - Southern': ['Botswana', 'Eswatini', 'Lesotho', 'Namibia', 'South Africa', 'Swaziland', 'Zambia', 'Zimbabwe'],
	'Africa - Eastern ': ['British Indian Ocean Territory', 'Burundi', 'Comoros', 'Djibouti', 'Eritrea', 'Ethiopia', 'French Southern Territories', 'Kenya', 'Madagascar', 'Malawi', 'Mauritius', 'Mayotte', 'Mozambique', 'Réunion', 'Rwanda', 'Seychelles', 'Somalia', 'South Sudan', 'Tanzania', 'Uganda'],
	'Asia - South-eastern ': ['Brunei', 'Cambodia', 'Indonesia', 'Laos', 'Malaysia', 'Myanmar', 'Philippines', 'Singapore', 'Thailand', 'Timor-Leste', 'VietNam'],
	'Asia - Eastern': ['China', 'Hong Kong', 'Japan', 'Macao', 'Mongolia', 'North Korea', 'South Korea', 'Taiwan'],
	'Europe - Northern ': ['Denmark', 'Estonia', 'Faroe Islands', 'Finland', 'Great Britain', 'Iceland', 'Ireland', 'Isle of Man', 'Jersey', 'Latvia', 'Lithuania', 'Norway', 'Svalbard and Jan Mayen', 'Sweden'],
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
                region_details = '[\'' + str(row[3]) + '\', ' + str(row[4]) + ',' + str(row[5]) + '],' + '\n'
                region_dict += '\t\'' + str(row[0]) + '\': ' + region_details
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
                region_details = '[' + str(row[1]) + ',' + str(row[2]) + ',' + str(row[3]) + '],' + '\n'
                region_dict += '\t\'' + str(row[0]) + '\': ' + region_details
                line_count += 1
    region_dict += '}'

    with open("Regions_dict.txt", "w") as text_file:
        text_file.write(region_dict)

     # generate category javscript array
    cat_array = 'const categoryList = [ ' + '\n'

    with open('Category List.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                print(f'Column names are {", ".join(row)}')
                line_count += 1
            else:
                # create dictionary
                cat_details = '"' + str(row[0]) + '",' + '\n'
                cat_array += '\t' + cat_details
                line_count += 1
    cat_array += '];'

    with open("Category List.txt", "w") as text_file:
        text_file.write(cat_array)


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
                python_region_dict.setdefault(str(row[3]),[]).append(str(row[0]))
                
    # print(python_region_dict)


    js_dict = 'var region_country = {' + '\n'

    for region, country_list in python_region_dict.items():
            # print(region)
            line_details = str(country_list) 
            js_dict += '\t\'' + region + '\': ' + line_details + ',' + '\n'
            line_count += 1

    js_dict += '}'

    print(js_dict)

    with open("JS_Regions_dict.txt", "w") as text_file:
        text_file.write(js_dict)    

if __name__ == '__main__':

    # generate_csvs() 

    # test get_country_region
    print(get_country_region('Australia'))

    #test lattitude
    # lat_value = 34
    # validity = validate_lat(str(lat_value))

    # # test longitude
    # long_value = 220.3423
    # validity = validate_long(str(long_value))
