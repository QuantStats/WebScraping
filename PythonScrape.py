import re
import os
from bs4 import BeautifulSoup
from selenium import webdriver

#original url
##original_url = "https://www.booking.com/searchresults.en-us.html?label=gen173nr-1FCAEoggI46AdIM1gEaKEBiAEBmAExuAEIyAEP2AEB6AEB-\
##AECiAIBqAID&sid=e6e7b8c369323453b7bedf599396e14c&sb=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com\
##%2Findex.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaKEBiAEBmAExuAEIyAEP2AEB6AEB-AECiAIBqAID%3Bsid\
##%3De6e7b8c369323453b7bedf599396e14c%3Bsb_price_type%3Dtotal\
##%26%3B&ss=Seoul&is_ski_area=0&ssne=Seoul&ssne_untouched=Seoul&dest_id=-\
##716583&dest_type=city&checkin_year=2019&checkin_month=3&checkin_monthday=27&checkout_year=2019&checkout_month=3&checkout\
##_monthday=28&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1"

#url pre-text
url = 'https://www.booking.com/searchresults.en-us.html?label=gen173nr-1FCAEoggI46AdIM1gEaKEBiAEBmAExuAEIyAEP2AEB6AEB-\
AECiAIBqAID&sid=e6e7b8c369323453b7bedf599396e14c&sb=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com\
%2Findex.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaKEBiAEBmAExuAEIyAEP2AEB6AEB-AECiAIBqAID%3Bsid\
%3De6e7b8c369323453b7bedf599396e14c%3Bsb_price_type%3Dtotal\
%26%3B&ss='

#combination texts
destination = 'Seoul'

checkin_year = 2019
checkin_month = 3
checkin_monthday = 27

checkout_year = 2019
checkout_month = 3
checkout_monthday = 28

#final url after combination
url = url+destination+'&is_ski_area=0&ssne='+destination+\
      '&ssne_untouched='+destination+'&dest_id=-716583&dest\
_type=city&checkin_year='+str(checkin_year)+'&checkin_month='+\
str(checkin_month)+'&checkin_monthday='+str(checkin_monthday)+\
'&checkout_year='+str(checkout_year)+'&checkout_month='+\
str(checkout_month)+'&checkout_monthday='+str(checkout_monthday)+\
'&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1'


driver = webdriver.Firefox(executable_path=r'C:\Users\your_path_here\geckodriver-v0.24.0-win64\geckodriver.exe')
driver.get(url)

html = driver.page_source
html = BeautifulSoup(html, 'lxml')

#comment out to save the html code as a text file if necessary
##with open('hotel.txt', 'w', encoding='utf-8') as outfile:
##    outfile.write(html.prettify())


def my_scrape():
    for entry in html.find_all(['span', 'div', 'i'], {'class': ['sr-hotel__name', 'bui-review-score__badge', 'bk-icon-wrapper bk-icon-stars star_track', 'strike-it-red_anim change-text-color-gray']}):
    
        #assign hotel name as a dictionary key and create a subdictionary that
        #contains key information about the hotel
        match = re.search(r'sr-hotel__name', str(entry))
        if match:
            temp_key = (entry.text).strip('\n')
            hotel_dict[temp_key] = dict()

            #some initializations for the subdictionary values
            hotel_dict[temp_key]['Rating'] = 'NA'
            hotel_dict[temp_key]['Stars'] = 'NA'
            hotel_dict[temp_key]['Price'] = 'NA'
                 
        #assign hotel rating
        match = re.search(r'bui-review-score__badge', str(entry))
        if match:
            temp_value = re.sub(r'\s+', '', entry.text)
            hotel_dict[temp_key]['Rating'] = temp_value

        #assign hotel stars
        match = re.search(r'bk-icon-wrapper bk-icon-stars star_track', str(entry))
        if match:
            temp_value = entry.text.strip()
            temp_value = re.search(r'\d', temp_value)[0] #some text-processing to extract a number
            hotel_dict[temp_key]['Stars'] = temp_value
            
        #assign hotel price
        match = re.search(r'strike-it-red_anim change-text-color-gray', str(entry)) 
        if match:
            #this is needed because some hotels don't provide prices
            if str(entry):
                temp_value = entry.span.string.strip()
                temp_value = temp_value.replace(u'\xa0', '')    #some text-processing to remove unicode
                hotel_dict[temp_key]['Price'] = temp_value
    
hotel_dict = dict()    

#number of pages to scrape
pages = 10

for k in range(0, pages):
    html = driver.page_source
    if not(html):
        break
    html = BeautifulSoup(html, 'lxml')
    my_scrape()
    driver.find_element_by_css_selector('a.bui-pagination__link.paging-next').click()    

print('Total number of hotels found: '+str(len(hotel_dict)))

for keys, values in hotel_dict.items():
    print(keys, ': ', values)

os.system('tskill plugin-container')
driver.quit()



