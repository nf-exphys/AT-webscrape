# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 11:54:31 2022

@author: Nick.Foreman
"""

# THIS SCRIPT ATTEMPTS TO SCRAPE COMPLETION DATA ON THE APPALACIAN TRAIL
# IN ORDER TO BETTER UNDERSTAND WHEN PEOPLE START, WHERE THEY COME FROM, ETC.
# TO DO THIS, I USE SELENIUM TO ACCESS THE WEB PAGES AND LOOP THROUGH THEM TO
# EXTRACT DATA ABOUT THE INDIVIDUALS

# https://appalachiantrail.org/miler-listings-year/2018/page/2/


#%% Set up modules & lists, connect to Chrome

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import re
from time import sleep
import pandas as pd

# this is the general format of the URL to search
# url = "https://appalachiantrail.org/miler-listings-year/2018/page/1/"

#This is the range of years that I'm interested in looping through to get data
year = list(range(2018, 2022, 1))

#For now, we don't know how many pages there will be, so assume 2 per year. 
    #Will adjust for each year accordingly later in the script
page_nums = list(range(1, 3, 1))

# If you get an error about versions not matching between ChromeDriver and Chrome,
# Go to https://chromedriver.chromium.org/downloads and download the correct version

#This connects the script to Google Chrome using selenium
ser = Service("C:/Users/Nick.Foreman/Desktop/chromedriver.exe") #this specifies the executable path
driver = webdriver.Chrome(service = ser)

#%% Create function to extract data from site HTML

def extract_person_data(html_str):

#replace "test" with iteration of split_html
        
    #first get useful data, ignore HTML
    full_str = html_str.split(">\n", 1)[1]
    
    #split each person on the semi-colon to separate name from location/route
        #also removes leading/lagging whitespace
    name_str = full_str.split(";", 1)[0].strip()
    loc_str = full_str.split(";", 1)[1].strip()
    
    #
    if name_str is None:
        print("No name found")
    
    #If participant isn't from US, ignore that person and don't store their data
    #If they are from the US, process their data and return as a list
    if re.search("USA", loc_str) is None:
    
        return None
    
    else:
                   
        try:
            state = re.search("^[A-Z]{2}", loc_str).group(0)
            
        except AttributeError:
            print("State set to None")
            state = None
        
        #use regex to find direction
        try:
            direction = re.search(",\s([a-zA-Z]*)\s</a", loc_str).group(1)
        except AttributeError:
            print("No hiking direction found")
            direction = None
            
        #now store all of the results 
        #res_df = pd.DataFrame(columns=())
        
        res = [name_str, state, direction]
        res = pd.DataFrame([res], columns=(['Name', 'State', 'Direction']))
        
        return(res)

#%% Function to find number of pages for a year

def pages_per_year(page_html):
    
    #We need to know how many pages there are per year.
    #There should be about 10 of them
    #To do this, scrape the HTML of the first page to find the number of pages
    
    #find something that's close to the page number
    possible_pages = re.findall("page\/\d{1,2}", page_html)
    
    #now loop through and convert the list of strings to an integer
    poss_page_nums = []
    
    for i in possible_pages:
        #remove text and convert to int
        poss_page_nums.append(int(i.replace('page/', '')))
       
    #once it'e just integers, find the highest one
        #this will tell you how many times to loop through a given year
    max_page = max(poss_page_nums) 
    
    return(max_page)

#%% Create a function that extracts HTML for a given year 
    #and uses it to get data from each person

def scrape_AT_data(year):
    
    current_year = str(year)
    
    # set the URL for first page of a given year
    url = "https://appalachiantrail.org/miler-listings-year/" + current_year + "/page/" + str(1) + "/"
    
    #navigate to that URL
    driver.get(url)
    
    #then get the associated HTML
    page_html = driver.page_source
    
    #Figure out number of pages for a year
    max_page = pages_per_year(page_html)
    page_statement = "Max pages for this year is " + str(max_page)
    print(page_statement)
    
    #this is a list of page numbers
    #page_nums = range(1, max_page+1, 1)
    
    #this is a list set up to be iterated over to get page numbers
    page_iter = range(0, max_page, 1)
    
    #This is the dataframe for results in a given year
    year_df = pd.DataFrame([], columns=(['Name', 'State', 'Direction', 'year']))

    #Loop through each page for a given year and get data
    for j in page_iter: 
        
        current_year = str(year)
        page_num = str(page_iter[j] + 1)
        
        
        url = "https://appalachiantrail.org/miler-listings-year/" + current_year + "/page/" + page_num + "/"    
        
        print(url)
        
        #get HTML
        driver.get(url)
        sleep(5) #add a 5 second delay to make sure page loads
        page_html = driver.page_source
        
        #test file to fine tune regex
       #file = open("Desktop\html_ATresults.txt", "w")
       #file.write(page_html)
       #file.close() 
        
        #get rid of everything before miler-listings
            #string now starts with the names
        trimmed_html = page_html.split("<div id=\"miler-listings\">\n<div>\n<div>\n")[1]
           
        #get rid of everything after small-container
        trimmed_html = trimmed_html.split("<div class=\"container small-container\">", 1)[0]
     
        #file = open("Desktop\html_ATresults.txt", "w")
        #file.write(trimmed_html)
        #file.close()   
     
        #now split HTML up into each person
        split_html = trimmed_html.split("</div>\n<div>")
        
        #test = split_html[15]
        #print(test)
        
        #df to store results for each page
        df = pd.DataFrame([], columns=(['Name', 'State', 'Direction']))
        
        #go through each person on the page and extract their data
        for m in split_html:
            
            #print(m)
            
            #get results for each person as a list
            res = extract_person_data(m)
            
            #store that list in a data frame
            df = df.append(res)
        
        #Adds a year column
        df['year'] = current_year
        
        #Removes duplicate rows
            #Duplicates exist because they're in the HTML, but it's easier to remove
            #them here after formatting is trimmed down
            #Might be able to improve regular expression to make this obsolete
        df = df.drop_duplicates(keep = 'first')
        
        #Adds the dataframe from the current loop iteration to the existing results for that year
        year_df = year_df.append(df)
        
    #Set up file path
    storage_folder = "Desktop/Code/AT_throughhike/data/"
    sheet_name = "AT_res_" + current_year + ".csv"
    file_path = storage_folder + sheet_name
       
    #Save results as a CSV
    year_df.to_csv(file_path, index = False, columns = ['Name', 'State', 'Direction', 'year'])
    
#%% Scrape data for a set of 10 years

#list from 2010 - 2019
years = list(range(2010,2020))

list(map(scrape_AT_data, years))

#%% Exit 
driver.close()
