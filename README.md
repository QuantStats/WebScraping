The script 'PythonScrape.py' scrapes hotel data from the popular hotel reservation site: https://www.booking.com/.

The demonstarted example uses Seoul (destination) and 27-28 March 2019 (stay period) as the inputs.

The output prints a dictionary of hotels with their key info: stars, ratings, and (total) price for the stay period.

The default scrape runs from the first to the last page of all available listings.

Alternatively, one can also comment out parts of the code to scrape up to a maximum number of pages only. Instructions to do so are given in the script.

Using Task Scheduler in Windows or Cron in Unix/Linux, one can schedule the scrape to run daily to gather a large amount of data over many days.
