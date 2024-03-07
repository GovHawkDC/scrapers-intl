import json
import pytz
import dateutil

from openstates.scrape import Scraper, Bill

import datetime as dt


class AUBillScraper(Scraper):
    _tz = pytz.timezone("Europe/Dublin")

    def scrape(self, session):
        yield {}
