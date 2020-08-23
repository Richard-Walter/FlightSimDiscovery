import re
import csv

# validate latitude and longitude constants
SIGN = '[\+-]?'
DECIMALS = '(\.[0-9]+)?'
ZEROS = '(\.0+)?'

LATITUDE =  f'{SIGN}(90{ZEROS}|[1-8]\d{DECIMALS}|\d{DECIMALS})'
LONGITUDE = f'{SIGN}(180{ZEROS}|1[0-7]\d{DECIMALS}|[1-9]\d{DECIMALS}|\d{DECIMALS})'

LAT_REGEX = f'\({LATITUDE}\)'
LONG_REGEX = f'\({LATITUDE}\)'

lat_pattern = re.compile(LAT_REGEX)
long_pattern = re.compile(LONG_REGEX)

def validate_latitude(value):
    return lat_pattern.search(value)

def validate_longitude(value):
    return long_pattern.search(value)

if __name__ == '__main__':

    # generate countries dictionary
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