import bs4
import requests
import time
from rich import print

i = 1
site = requests.get(f'https://www.ztm.waw.pl/baza-danych-pojazdow/page/{i}/')

soup = bs4.BeautifulSoup(site.text, features='html.parser')
v_list = soup.find('div', class_='grid-body').find_all('a')

max_i = soup.find_all('li', class_='page-numbers')[-2].find('a').contents[0]
max_i = int(max_i)
print(f'Max page is {max_i} and we are going to do {max_i*30+max_i+1} requests')

# print(v_list)
for i in range(max_i):
    v_list = soup.find('div', class_='grid-body').find_all('a')
    for a in v_list:
        veh = a.find_all('div')
        print(a['href'])
        v = {}
        v['internal_id'] = a['href'][-5:]
        v['number'] = veh[0].get_text()
        v['maker'] = veh[1].get_text()
        v['model'] = veh[2].get_text()
        v['operator'] = veh[3].get_text()
        v['depot'] = veh[4].get_text()

        details = requests.get(a['href'])
        soup2 = bs4.BeautifulSoup(details.text, features='html.parser')
        details = soup2.find('div', class_='vehicle-details').find_all('div', class_='vehicle-details-block')

        v['year'] = details[0].find_all('div', class_='vehicle-details-entry')[2].find_all('div')[1].get_text()
        # print(details[1].find_all('div', class_='vehicle-details-entry'))
        v['traciton_type_raw'] = details[1].find_all('div', class_='vehicle-details-entry')[0].find_all('div')[1].get_text()
        v['license_plate'] = details[1].find_all('div', class_='vehicle-details-entry')[1].find_all('div')[1].get_text()
        v['ticket_machine'] = details[3].find_all('div', class_='vehicle-details-entry')[0].find_all('div')[1].get_text()
        v['features_raw'] = details[3].find_all('div', class_='vehicle-details-entry')[1].find_all('div')[1].get_text()

        # ticket machine parsing
        if 'brak' in v['ticket_machine']:
            v['ticket_machine'] = False
        elif 'dostępny' in v['ticket_machine']:
            v['ticket_machine'] = True

        # traction type parsing
        if 'Kolej miejska' in v['traciton_type_raw']:
            v['traciton_type'] = 'rail'
        elif 'Autobus' in v['traciton_type_raw']:
            v['traciton_type'] = 'bus'
        elif 'Metro' in v['traciton_type_raw']:
            v['traciton_type'] = 'metro'
        elif 'Tramwaj' in v['traciton_type_raw']:
            v['traciton_type'] = 'tram'

        # try parsing featureset
        fset = v['features_raw'].split(', ')

        # climate controll
        if 'klimatyzacja' in fset:
            v['ac'] = True
        else:
            v['ac'] = False

        # low floor
        if 'niska podłoga' in fset:
            v['low_entry'] = True
        else:
            v['low_entry'] = False

        # announcement
        if 'zapowiadanie przystanków' in fset:
            v['voice_announcement'] = True
        else:
            v['voice_announcement'] = False

        # electrionic displays
        if 'tablice elektroniczne' in fset:
            v['electronic_displays'] = True
        else:
            v['electronic_displays'] = False

        # hot buttons
        if 'ciepłe guziki' in fset:
            v['hot_butotns'] = True
        else:
            v['hot_butotns'] = False

        # monitoring
        if 'monitoring' in fset:
            v['cctv'] = True
        else:
            v['cctv'] = False


        time.sleep(3)
        print(v)
