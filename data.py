import csv

csv.register_dialect('custom_csv', delimiter=';')
cities = set()

with open('cities_list.csv', encoding='utf-8') as file:
    reader = csv.reader(file, 'custom_csv')
    for city in list(reader)[1:]:
        cities.add(city[0].lower())

sex = {'мужской': 2, 'женский': 1}
sex_reverse = {2: 'мужской', 1: 'женский'}

relation = {'замужем/женат': 4, 'не замужем/не женат': 1,
            'есть друг/есть подруга': 2, 'в активном поиске': 6}
relation_reverse = {4: 'замужем/женат', 1: 'не замужем/не женат',
                    2: 'есть друг/есть подруга', 6: 'в активном поиске'}
