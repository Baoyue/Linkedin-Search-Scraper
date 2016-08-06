#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests  
import re  
import json  
from bs4 import BeautifulSoup, Comment
from lxml import html
import urllib2
from time import sleep
import csv

newPageData = {}
myfile = open('searchList.csv', 'wb')
myfile.write('\xEF\xBB\xBF')
f = csv.writer(myfile)
f.writerow(["name", "location", "industry", "currentTitle", "currentCompany", "experienceDuration1", "companyLocation1", "previousTitle", "previousCompany", "experienceDuration2", "companyLocation2", "education1", "degree1", "major1", "GPA1", "eduDuration1", "education2", "degree2", "major2", "GPA2", "eduDuration2"])
myfile.close()

def login(s):
    USERNAME = "YOUR USERNAME"
    PASSWORD = "YOUR PASSWORD"

    r = s.get('https://www.linkedin.com/uas/login')  
       
    soup = BeautifulSoup(r.text, "lxml")  
    soup = soup.find(id="login")       
  
    loginCsrfParam = soup.find('input', id = 'loginCsrfParam-login')['value']  
    csrfToken = soup.find('input', id = 'csrfToken-login')['value']  
    sourceAlias = soup.find('input', id = 'sourceAlias-login')['value']  
    isJsEnabled = soup.find('input',attrs={"name" :'isJsEnabled'})['value']  
    source_app = soup.find('input', attrs={"name" :'source_app'})['value']  
    tryCount = soup.find('input', id = 'tryCount')['value']  
    clickedSuggestion = soup.find('input', id = 'clickedSuggestion')['value']  
    signin = soup.find('input', attrs={"name" :'signin'})['value']  
    session_redirect = soup.find('input', attrs={"name" :'session_redirect'})['value']  
    trk = soup.find('input', attrs={"name" :'trk'})['value']  
    fromEmail = soup.find('input', attrs={"name" :'fromEmail'})['value']  
   
    payload = {  
        'isJsEnabled':isJsEnabled,  
        'source_app':source_app,  
        'tryCount':tryCount,  
        'clickedSuggestion':clickedSuggestion,  
        'session_key':USERNAME,  
        'session_password':PASSWORD,  
        'signin':signin,  
        'session_redirect':session_redirect,  
        'trk':trk,  
        'loginCsrfParam':loginCsrfParam,  
        'fromEmail':fromEmail,  
        'csrfToken':csrfToken,  
        'sourceAlias':sourceAlias  
    }  
  
    s.post('https://www.linkedin.com/uas/login-submit', data=payload)  
    return s  
  
  
def getPersons(code_json):  
    person_json = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["results"]  

    person_list = []  
    for person_item in person_json:
        if "person" in person_item:
            person = person_item["person"]  
            if "link_nprofile_view_4" in person:
                profileLink = person["link_nprofile_view_4"].encode('utf-8')
                person_list.append("%s\n" % (profileLink))  
    return person_list

  
def getNextPageURL(code_json):  
    resultPagination = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["baseData"]["resultPagination"]  
       
    soup = BeautifulSoup(html.text, "lxml") 

    orig = soup.find('input', attrs={"name" :'orig'})['value']
    rsid = code_json["content"]["page"]["voltron_unified_search_json"]["search"]["link_group_search_cluster"]
    rsid = re.search('(?<=rsid=)(\d+)', rsid)
    rsid = rsid.group(0)
    pageKey = soup.find('input', attrs={"name" :'pageKey'})['value']
    trkInfo = soup.find('input', attrs={"name" :'trkInfo'})['value']

    newPageData = {

        'orig': orig,
        'rsid': rsid,
        'pageKey': pageKey,
        'trkInfo': trkInfo
    }

    if "nextPage" in resultPagination:  
        newURL = 'https://www.linkedin.com' + resultPagination["nextPage"]["pageURL"]
        return newURL
    else:  
        nextPageURL = "NULL"  
  
    return nextPageURL 

def getProfile(url):
    r = s.get(url)
            
    text = r.text.encode("utf-8") 
    soup = BeautifulSoup(text, "lxml")    

    try:
        name = soup.find('span',{'class': 'full-name'}).getText().encode('utf-8')
    except AttributeError:
        name = ""
    print name
     
    try:
        location = soup.find('a', {'name': 'location'}).getText().encode('utf-8')
    except AttributeError:
        location = ""

    try:
        industry = soup.find('a', {'name': 'industry'}).getText().encode('utf-8')
    except AttributeError:
        industry = ""

    positionList = []
    try:
        for item in soup.findAll('div', id=re.compile('^experience-(\d+)-view$')):
            position = item.find('header').find('h4').find('a').getText().encode('utf-8')
            positionList.append(position)
    
    except AttributeError:
        positionList.append("")

    if len(positionList) < 1:
        positionList.append("")
    if len(positionList) < 2:
        positionList.append("")

    companyList = []   
    try:
        for item in soup.findAll('div', id=re.compile('^experience-(\d+)-view$')):
            for company in item.select('header > h5 > span > strong > a'):
                companyList.append(company.getText().encode("utf-8"))

    except AttributeError:
        companyList.append("")

    if len(companyList) < 1:
        companyList.append("")
    if len(companyList) < 2:
        companyList.append("")

    experienceDuration = []  
    duration = ""
    try:
        for item in soup.findAll('div', id=re.compile('^experience-(\d+)-view$')):
            for time in item.select('span.experience-date-locale'):
            	size = 0
                for timepoint in time.select('time'):
                    size = size + 1
                    if size == 1:
                        start = timepoint.getText().encode('utf-8')
                    if size == 2:
                        end = timepoint.getText().encode('utf-8')
                    
                if size == 1:
                    end = time.find(text=True, recursive=False).encode('ascii', 'ignore')
                    duration = start + " -" + end
                elif size == 2:
                    duration = start + " - " + end
                experienceDuration.append(duration)

    except AttributeError:
        experienceDuration.append("")

    if len(experienceDuration) < 1:
        experienceDuration.append("")
    if len(experienceDuration) < 2:
        experienceDuration.append("")

    locationList = []
    try:
        for item in soup.findAll('div', id=re.compile('^experience-(\d+)-view$')):
            for loc in item.select('span.experience-date-locale > span.locality'):
                locationList.append(loc.getText().encode('utf-8'))

    except AttributeError:
        locationList.append("")

    if len(locationList) < 1:
        locationList.append("")
    if len(locationList) < 2:
        locationList.append("")


    educationList = []
    try:
        for item in soup.findAll('div', id=re.compile('^education-(\d+)-view$')):
            university = item.find('header').find('h4').find('a').getText().encode('utf-8')
            educationList.append(university)
    
    except AttributeError:
        educationList.append("")

    if len(educationList) < 1:
        educationList.append("")
    if len(educationList) < 2:
        educationList.append("")

    degreeList = []   
    try:
        for item in soup.findAll('div', id=re.compile('^education-(\d+)-view$')):
            for degree in item.select('header > h5 > .degree'):
            	d = re.sub('(,)(.*)$', '', degree.getText().encode("utf-8"))
                degreeList.append(d)

    except AttributeError:
        degreeList.append("")

    if len(degreeList) < 1:
        degreeList.append("")
    if len(degreeList) < 2:
        degreeList.append("")

    majorList = []   
    try:
        for item in soup.findAll('div', id=re.compile('^education-(\d+)-view$')):
            for major in item.select('header > h5 > .major'):
                m = re.sub('(,)(.*)$', '', major.getText().encode("utf-8"))
                majorList.append(m)

    except AttributeError:
        majorList.append("")

    if len(majorList) < 1:
        majorList.append("")
    if len(majorList) < 2:
        majorList.append("")

    gradeList = []   
    try:
        for item in soup.findAll('div', id=re.compile('^education-(\d+)-view$')):
            for grade in item.select('header > h5 > .grade'):
                tempGPA = re.search('([0-9]*\.[0-9]+|[0-9]+)', grade.getText())
                if tempGPA:
   					gpa = tempGPA.group(1)
               	else:
               		gpa = ""
                gradeList.append(gpa)

    except AttributeError:
        gradeList.append("")

    if len(gradeList) < 1:
        gradeList.append("")
    if len(gradeList) < 2:
        gradeList.append("")

    educationDuration = []  
    
    try:
        for item in soup.findAll('div', id=re.compile('^education-(\d+)-view$')):
            for time in item.select('span.education-date'):
                count = 0
                eduStart = ""
                eduEnd = ""
                for timeSlot in time.select('time'):
                    count = count + 1
                    if count % 2 != 0:
                        eduStart = timeSlot.getText().encode("utf-8")
                    else:
                        eduEnd = timeSlot.find(text=True, recursive=False).encode('ascii', 'ignore')

                eduDuration = eduStart + " -" + eduEnd
                educationDuration.append(eduDuration)

    except AttributeError:
        educationDuration.append("")

    if len(educationDuration) < 1:
        educationDuration.append("")
    if len(educationDuration) < 2:
        educationDuration.append("")
    
        
    myfile = open('searchList.csv', 'a')
    f = csv.writer(myfile)
    f.writerow([name, location,industry,positionList[0],companyList[0],experienceDuration[0],locationList[0],positionList[1],companyList[1],experienceDuration[1],locationList[1],educationList[0],degreeList[0], majorList[0], gradeList[0],educationDuration[0],educationList[1],degreeList[1], majorList[1], gradeList[1],educationDuration[1]])
  
  
if __name__ == '__main__': 
    start_url = "YOUR CUSTOMIZED SEARCH URL"

    s = requests.session()  
    s = login(s)
        
    
    while True:

        print (start_url)
            
        if start_url == "NULL":  
            break
            
        html = s.post(start_url, data=newPageData)
        for url1 in [start_url]:
            try:
                connection1 = urllib2.urlopen(url1)
                print (connection1.getcode())
                connection1.close()
            except (urllib2.HTTPError, e):
                print (e.getcode())
           
            
        text = html.text.encode("utf-8") 

        code = re.search(r'<code id="voltron_srp_main-content" style="display:none;"><!--.+--></code>', text).group()
        code = code.replace(r'<code id="voltron_srp_main-content" style="display:none;"><!--', '')  
        code = code.replace(r'--></code>', '') 
        (code, n) = re.subn('"distance":\\\\u002d1', '"distance":-1', code)
        (code, n) = re.subn('"distanceP":\\\\u002d1', '"distanceP":-1', code)
        code_json = json.loads(code)


        start_url = getNextPageURL(code_json)  
        person_list = getPersons(code_json) 
            
        for link in person_list:  
            getProfile(link)
                
        sleep(5)  
