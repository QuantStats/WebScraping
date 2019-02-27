import re
import os
import calendar
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

#the main function to perform the scrape
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

url = 'https://www.booking.com'
driver = webdriver.Firefox(executable_path=r'C:\your_installation_path_here\geckodriver.exe')
driver.get(url)

#list of inputs, you may change them accordingly
destination = 'Hong Kong'

day_to_checkin = '21'
month_to_checkin = 'October'
year_to_checkin = '2019'

day_to_checkout = '02'
month_to_checkout = 'November'
year_to_checkout = '2019'

cal_icon = driver.find_elements_by_css_selector('.xp__dates__checkin > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > svg:nth-child(1) > g:nth-child(2) > path:nth-child(1)')
if len(cal_icon) != 0:
    cal_icon = cal_icon[0]
    cal_icon.click()
else:
    cal_icon = driver.find_elements_by_css_selector('.xp__dates__checkin > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)')
    if len(cal_icon) != 0:
        cal_icon = cal_icon[0]
        cal_icon.click()
    else:
        cal_icon = driver.find_elements_by_css_selector('.xp__dates__checkin > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)')
        if len(cal_icon) != 0:
            cal_icon = cal_icon[0]
            cal_icon.click()

#two processes to process checkin and checkout strings for css_selector searches
#nmonth_to_checkin/nmonth_to_checkout: month in digits as a string, e.g. Octorber is '10'
#ndate_to_checkin/ndate_to_checkout: date as a string enclosed by double quotation marks, e.g. "2019-10-21"
nmonth_to_checkin = str(list(calendar.month_name).index(month_to_checkin))
ndate_to_checkin = '"'+year_to_checkin+'-'+nmonth_to_checkin+'-'+day_to_checkin+'"'

nmonth_to_checkout = str(list(calendar.month_name).index(month_to_checkout))
ndate_to_checkout = '"'+year_to_checkout+'-'+nmonth_to_checkout+'-'+day_to_checkout+'"'

#navigating the calendar
calendar_list = driver.find_elements_by_class_name('bui-calendar__month')
cond = True

#click on the navigate to next month until the check-in month is found
while cond:
    count = 0
    for j in calendar_list:
        month_text = str(j.get_attribute('innerText'))
        count+=1
        if month_text == month_to_checkin+' '+year_to_checkin:
            cond = False
            break
        if count == 2:
            driver.find_element_by_css_selector('div.bui-calendar__control:nth-child(2) > svg:nth-child(1)').click()
            calendar_list = driver.find_elements_by_class_name('bui-calendar__month')

#click on the check-in dates
driver.find_element_by_css_selector('td[data-date='+ndate_to_checkin+']').click()

#click on the navigate to next month until the check-out month is found
cond = True
while cond:
    count = 0
    for j in calendar_list:
        month_text = str(j.get_attribute('innerText'))
        count+=1
        if month_text == month_to_checkout+' '+year_to_checkout:
            cond = False
            break
        if count == 2:
            driver.find_element_by_css_selector('div.bui-calendar__control:nth-child(2) > svg:nth-child(1)').click()
            calendar_list = driver.find_elements_by_class_name('bui-calendar__month')

#click on the check-out dates
driver.find_element_by_css_selector('td[data-date='+ndate_to_checkout+']').click()

#key in the destination and click the search button
driver.find_element_by_css_selector('input#ss').send_keys(destination)
driver.find_element_by_css_selector('button.sb-searchbox__button').click()
   
hotel_dict = dict()

html = driver.page_source
html = BeautifulSoup(html, 'lxml')
with open('hotel.txt', 'w', encoding='utf-8') as outfile:
    outfile.write(html.prettify())

while True:
    try:
        html = driver.page_source
        if not(html):
            break
        html = BeautifulSoup(html, 'lxml')
        my_scrape()
        driver.find_element_by_css_selector('a.bui-pagination__link.paging-next').click()

    except NoSuchElementException:
        break
    
#alternatively, comment the previous part out and use this part if the goal is to scrape up to a maximum number of pages
#number of pages to scrape
##pages = 10   
##for k in range(0, pages):
##    html = driver.page_source
##    if not(html):
##        break
##    html = BeautifulSoup(html, 'lxml')
##    my_scrape()
##    driver.find_element_by_css_selector('a.bui-pagination__link.paging-next').click()    

print('Total number of hotels found: '+str(len(hotel_dict)))

for keys, values in hotel_dict.items():
    print(keys, ': ', values)

os.system('tskill plugin-container')
driver.quit()




