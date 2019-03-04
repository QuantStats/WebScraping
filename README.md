The script `HotelScrape.py` scrapes hotel data from the popular hotel reservation site: https://www.booking.com/.

The demonstrated example uses Hong Kong (destination) and 21 October-09 November 2019 (stay period) as inputs.

The scraped hotel data is saved in a `csv` file (see `hotel_prices.csv` for a sample) as a list of hotels with their key info: rating, star, and (total) price in the user local currency for the stay period. The user local currency is dependent on the IP address when running the scrape.

The default scrape runs from the first to the last page of all available listings. Alternatively, one can also comment out parts of the code to scrape up to a maximum number of pages only. Instructions to do so are given in the script.

Using _Task Scheduler_ in Windows or _Cron_ in Unix/Linux, one can schedule the scrape to run daily to gather a large amount of data over many days. A possible application of this can be done by a tourist planning to visit a certain destination wanting to collect hotel prices days before the trip.

The print output after a run of the script is shown below:

![alt text](https://github.com/QuantStats/WebScraping/blob/master/HotelList.png)
