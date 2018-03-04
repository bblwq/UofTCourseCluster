import urllib3
import json
from bs4 import BeautifulSoup
import pickle

urllib3.disable_warnings()

page_url = 'https://fas.calendar.utoronto.ca/search-courses'
course_url = 'https://fas.calendar.utoronto.ca'
dataset = {}

for page in range(0, 438):
    print('Page: ', page)
    http = urllib3.PoolManager()
    request = http.request('GET', page_url, fields={'page': str(page)})
    html = BeautifulSoup(request.data, 'html.parser')
    courses = html.find('table').find('tbody').find_all('tr')
    
    for course in courses:
        fields = course.find_all('td')
        code = fields[0].find('a')
        print(code)
        title = fields[1].text
        description_field = fields[2].find('p')
        if description_field is None:
            description = fields[2].text.replace('\n',' ')
        else:
            description = description_field.text

        prerequisites = []
        exclusions = []
        for i in range(3,len(fields)):
            if 'views-field-field-prerequisite1' in fields[i]['class']:
                if not fields[i].find('p') is None:
                    course_list = fields[i].find('p').find_all('a')
                    if len(course_list) == 0:
                        prerequisites.append(fields[i].find('p').text)
                    else:
                        for course in course_list:
                            prerequisites.append(course.string)
            
            if 'views-field-field-exclusion1' in fields[i]['class']:
                if not fields[i].find('p') is None:
                    course_list = fields[i].find('p').find_all('a')
                    for course in course_list:
                        exclusions.append(course.string)
        
        URL = course_url + code['href']
        request = http.request('GET', URL)
        html = BeautifulSoup(request.data, 'html.parser')
        if html.find('div', class_='field field-name-field-distribution-req field-type-list-text field-label-inline clearfix') is None:
            distribution_req = ''
        else:
            distribution_req = html.find('div', class_='field field-name-field-distribution-req field-type-list-text field-label-inline clearfix').find('div', class_='field-items').find('div', class_='field-item even').text
        if html.find('div', class_='field field-name-field-breadth-req field-type-list-text field-label-inline clearfix') is None:
            breadth_req = ''
        else:
            breadth_req = html.find('div', class_='field field-name-field-breadth-req field-type-list-text field-label-inline clearfix').find('div', class_='field-items').find('div', class_='field-item even').text
        if html.find('div', class_='field field-name-field-section-link field-type-text-with-summary field-label-inline clearfix') is None:
            program_area = ''
        else:
            program_area = html.find('div', class_='field field-name-field-section-link field-type-text-with-summary field-label-inline clearfix').find('div', class_='field-items').find('div', class_='field-item even').find('p').find('a').text        
        
        dataset[code.text] = {'Title':title.strip(),'Description':description.strip(),'Prerequisite':prerequisites,'Exclusion':exclusions,'Distribution Requirements':distribution_req,'Breadth Requirements':breadth_req,'Program Area Section':program_area}

with open('course_repo.txt', 'w') as outfile:
    json.dump(dataset, outfile)
#pickle.dump(dataset, open('course_repo.p', 'wb'))