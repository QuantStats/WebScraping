import pandas as pd
import re
import os
import calendar
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException

class HotelScraper():
    scrape_url = 'https://www.booking.com'
    gecko_path = r'C:/Users/admin/Desktop/geckodriver-v0.24.0-win64/geckodriver.exe'

    def __init__(self, destination, checkin_date=None, checkout_date=None, output='./scraper_outputs/', write_source=False):
        self.destination = destination
        
        if not(checkin_date):
            self.checkin_date = re.search(r'\d{4}-\d{2}-\d{2}', str(pd.Timestamp.now())).group(0)
        else:
            self.checkin_date = checkin_date
            
        if not(checkout_date):
            self.checkout_date = re.search(r'\d{4}-\d{2}-\d{2}', str(pd.Timestamp.now()+pd.Timedelta(days=1))).group(0)
        else:
            self.checkout_date = checkout_date

        self.output = output
        self.write_source = write_source

        self.__destination_save = re.sub(r'/s+', '_', destination.strip().lower())
        
        self.__output_dict = dict()
        
    #the main function to perform the scrape
    def scrape_dict(self, html_bs):
        hotel_name_tag = 'sr-hotel__name'

        rating_tag = 'bui-review-score__badge'

        star_tag = 'bk-icon-wrapper bk-icon-stars star_track'

        price_tag = 'bui-price-display__value prco-inline-block-maker-helper'
        
        for entry in html_bs.find_all(['span', 'div', 'i'], {'class': [hotel_name_tag, rating_tag, star_tag, price_tag]}):
        
            #assign hotel name as a dictionary key and create a list that
            #contains key information about the hotel, the list in is this order for storage
            #0: Rating, 1: Star, 2: Price
            match = re.search(r'sr-hotel__name', str(entry))
            if match:
                temp_key = (entry.text).strip('\n')

                #some initializations for the subdictionary values
                self.__output_dict[temp_key] = ['']*3

                     
            #assign rating
            match = re.search(r'bui-review-score__badge', str(entry))
            if match:
                temp_value = re.sub(r'\s+', '', entry.text)
                self.__output_dict[temp_key][0] = temp_value

            #assign star
            match = re.search(r'bk-icon-wrapper bk-icon-stars star_track', str(entry))
            if match:
                temp_value = entry.text.strip()
                temp_value = re.search(r'\d', temp_value)[0] #some text-processing to extract a number
                self.__output_dict[temp_key][1] = temp_value
                
            #assign price
            match = re.search(r'bui-price-display__value prco-inline-block-maker-helper', str(entry)) 
            if match:
                #this is needed because some hotels don't provide a price
                if str(entry):
                    temp_value = entry.text.strip()
                    temp_value = temp_value.replace(u'\xa0', '')    #some text-processing to remove unicode
                    temp_value = temp_value.replace(',', '')    #remove comma in price
                    temp_value = re.search(r'\d+', temp_value)[0]   #some text-processing to extract a number
                    self.__output_dict[temp_key][2] = temp_value
                    
    #main get_scrape() ends here
    
    def click_next_month(month, year, driver):
        month = str(month)
        year = str(year)
        calendar_list = driver.find_elements_by_class_name('bui-calendar__month')
        
        cond = True
        while cond:
            count = 0
            for j in calendar_list:
                month_text = str(j.get_attribute('innerText'))
                count+=1
                if month_text == month+' '+year:
                    cond = False
                    break
                if count == 2:
                    driver.find_element_by_css_selector('div.bui-calendar__control:nth-child(2) > svg:nth-child(1)').click()
                    calendar_list = driver.find_elements_by_class_name('bui-calendar__month')

    def get_scrape(self):
        stime = pd.Timestamp.now()
        
        url = HotelScraper.scrape_url
        driver = webdriver.Firefox(executable_path=HotelScraper.gecko_path)
        driver.get(url)
        
        #click on the currency
        driver.implicitly_wait(7)
        driver.find_element_by_css_selector('a[aria-controls="currency_selector_popover"]').click()
        driver.implicitly_wait(3)
        driver.find_element_by_css_selector('li[class="currency_hotel_currency"]').click()
        
        try:
           cal_icon = driver.find_elements_by_css_selector('.xp__dates__checkin > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1) > svg:nth-child(1) > g:nth-child(2) > path:nth-child(1)')
           cal_icon = cal_icon[0]
        except IndexError:
           try:
               cal_icon = driver.find_elements_by_css_selector('.xp__dates__checkin > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > span:nth-child(1)')
               cal_icon = cal_icon[0]
           except IndexError:
               try:
                   cal_icon = driver.find_elements_by_css_selector('.xp__dates__checkin > div:nth-child(1) > div:nth-child(1) > div:nth-child(1)')
                   cal_icon = cal_icon[0]
               except IndexError:
                   pass
        finally:           
                cal_icon.click()

        #ndate_to_checkin/ndate_to_checkout: date as a string enclosed by double quotation marks, e.g. "2019-10-21"
        ndate_to_checkin = '"'+self.checkin_date+'"'
        ndate_to_checkout = '"'+self.checkout_date+'"'

        #navigating the calendar
        calendar_list = driver.find_elements_by_class_name('bui-calendar__month')
        
        checkin_datetime = pd.to_datetime(self.checkin_date)
        month_to_checkin = list(calendar.month_name)[checkin_datetime.month]
        year_to_checkin = str(checkin_datetime.year)
        
        checkout_datetime = pd.to_datetime(self.checkout_date)
        month_to_checkout = list(calendar.month_name)[checkout_datetime.month]
        year_to_checkout = str(checkout_datetime.year)

        #click on the navigate to next month until the check-in month is found
        HotelScraper.click_next_month(month_to_checkin, year_to_checkin, driver)
        
        #click on the check-in dates
        driver.find_element_by_css_selector('td[data-date='+ndate_to_checkin+']').click()

        #click on the navigate to next month until the check-out month is found
        HotelScraper.click_next_month(month_to_checkout, year_to_checkout, driver)
        
        #click on the check-out dates
        driver.find_element_by_css_selector('td[data-date='+ndate_to_checkout+']').click()
        
        #key in the destination and click the search button
        driver.find_element_by_css_selector('input#ss').send_keys(self.destination)
        driver.find_element_by_css_selector('button.sb-searchbox__button').click()
        
        #save source if needed
        if self.write_source:
            try:
                with open(self.__destination_save+'_source'+'.txt', 'w', encoding='utf-8') as outfile:
                    outfile.write(BeautifulSoup(driver.page_source, 'lxml').prettify())
                    
            except:
                print(self.destination+' write source error. Skipping write...')
                pass

        while True:
            try:
                html = driver.page_source
                if not(html):
                    break
                html_bs = BeautifulSoup(html, 'lxml')
                self.scrape_dict(html_bs)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.bui-pagination__link.paging-next')))
                driver.find_element_by_css_selector('a.bui-pagination__link.paging-next').click()

            except (NoSuchElementException, ElementClickInterceptedException, TimeoutException) as e:
                break

        #save the dictionary to a panda dataframe
        pdtable = pd.DataFrame.from_dict(self.__output_dict, orient='index', columns=['Rating', 'Star', 'Price'])

        #save the data in csv format
        try:
            os.mkdir(self.output)
        except FileExistsError:
            pass
        
        pdtable.to_csv(self.output+self.__destination_save+'.csv')

        #terminate the browser
        os.system('tskill plugin-container')
        driver.close()
        driver.quit()
        
        ftime = pd.Timestamp.now()

        print('Scrape for '+self.destination+' from '+self.checkin_date+' to '+self.checkout_date+' had completed in '+str((ftime-stime)/pd.Timedelta(minutes=1))+' minutes.'+' Start time: '+str(stime)+', End time: '+str(ftime))
