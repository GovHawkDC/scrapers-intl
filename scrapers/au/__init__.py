import json
import dateutil
import datetime
import uuid
import requests
import re
from datetime import date
from openstates.scrape import State
from openstates.metadata.models import (
    State as modelState,
    Chamber,
)

from .bills import AUBillScraper

# from .events import A2EventScraper


class AU(State):
    division_id = "ocd-division/country:au"
    classification = "legislature"
    name = "Australia"
    legislature_name = "Parliament"
    url = "https://www.aph.gov.au/"
    scrapers = {
        "bills": AUBillScraper,
        # "events": A2EventScraper,
    }

    org_id = uuid.uuid4()
    org_id = f"ocd-organization/{org_id}"
    metadata = modelState(
        name="UK",
        abbr="uk",
        capital="None",
        capital_tz="America/Central",
        fips="48",
        unicameral=True,
        legislature_name="Oireachtas",
        legislature_organization_id="ocd-organization/8ab77a54-0646-413c-a63a-dc85154282b8",
        executive_name="Executive",
        executive_organization_id="ocd-organization/4c8c2a9c-f33c-476d-bf81-266eb72193f8",
        division_id="ocd-division/country:uk",
        jurisdiction_id="ocd-division/country:uk/government",
        url="https://www.parliament.uk/",
        legislature=Chamber(
            chamber_type="upper",
            name="House of Lords",
            organization_id=org_id,
            num_seats=31,
            title="Lord",
            districts=[]
            # districts=simple_numbered_districts(
            #     "ocd-division/country:us/state:tx", "upper", 31
            # ),
        ),
    )
    # https://bills.parliament.uk/
    legislative_sessions = [
        {
            "classification": "primary",
            "identifier": "47",
            "name": "47",
            "start_date": "2023-01-01",
            "end_date": "2024-12-31",
            "active": True,
        },
        {
            "classification": "primary",
            "identifier": "46",
            "name": "46",
            "start_date": "2022-07-24",
            "end_date": "2019-07-01",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "45",
            "name": "45",
            "start_date": "2019-06-30",
            "end_date": "2016-08-29",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "44",
            "name": "44",
            "start_date": "2016-08-28",
            "end_date": "2013-11-11",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "43",
            "name": "43",
            "start_date": "2013-11-10",
            "end_date": "2010-09-27",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "42",
            "name": "42",
            "start_date": "2010-09-26",
            "end_date": "2008-02-11",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "41",
            "name": "41",
            "start_date": "2008-02-10",
            "end_date": "2004-11-15",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "40",
            "name": "40",
            "start_date": "2004-11-14",
            "end_date": "2002-02-11",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "39",
            "name": "39",
            "start_date": "2002-02-10",
            "end_date": "1998-11-09",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "38",
            "name": "38",
            "start_date": "1998-11-08",
            "end_date": "1996-04-29",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "37",
            "name": "37",
            "start_date": "1996-04-28",
            "end_date": "1993-05-03",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "36",
            "name": "36",
            "start_date": "1993-05-02",
            "end_date": "1990-05-07",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "35",
            "name": "35",
            "start_date": "1990-05-06",
            "end_date": "1987-09-13",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "34",
            "name": "34",
            "start_date": "1987-09-12",
            "end_date": "1985-02-20",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "33",
            "name": "33",
            "start_date": "1985-02-19",
            "end_date": "1983-04-23",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "32",
            "name": "32",
            "start_date": "1983-04-22",
            "end_date": "1980-11-24",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "31",
            "name": "31",
            "start_date": "1980-11-23",
            "end_date": "1978-02-20",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "30",
            "name": "30",
            "start_date": "1978-02-19",
            "end_date": "1976-02-16",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "29",
            "name": "29",
            "start_date": "1976-02-15",
            "end_date": "1974-07-08",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "28",
            "name": "28",
            "start_date": "1974-07-07",
            "end_date": "1973-02-26",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "27",
            "name": "27",
            "start_date": "1973-02-25",
            "end_date": "1969-11-24",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "26",
            "name": "26",
            "start_date": "1969-11-23",
            "end_date": "1967-02-20",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "25",
            "name": "25",
            "start_date": "1967-02-19",
            "end_date": "1964-02-24",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "24",
            "name": "24",
            "start_date": "1964-02-23",
            "end_date": "1962-02-19",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "23",
            "name": "23",
            "start_date": "1962-02-18",
            "end_date": "1959-02-16",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "22",
            "name": "22",
            "start_date": "1959-02-15",
            "end_date": "1956-02-14",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "21",
            "name": "21",
            "start_date": "1956-02-13",
            "end_date": "1954-08-03",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "20",
            "name": "20",
            "start_date": "1954-08-02",
            "end_date": "1951-06-11",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "19",
            "name": "19",
            "start_date": "1951-06-10",
            "end_date": "1950-02-21",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "18",
            "name": "18",
            "start_date": "1950-02-20",
            "end_date": "1946-11-05",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "17",
            "name": "17",
            "start_date": "1946-11-04",
            "end_date": "1943-09-22",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "16",
            "name": "16",
            "start_date": "1943-09-21",
            "end_date": "1940-11-19",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "15",
            "name": "15",
            "start_date": "1940-11-18",
            "end_date": "1937-11-29",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "14",
            "name": "14",
            "start_date": "1937-11-28",
            "end_date": "1934-10-22",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "13",
            "name": "13",
            "start_date": "1934-10-21",
            "end_date": "1932-02-16",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "12",
            "name": "12",
            "start_date": "1932-02-15",
            "end_date": "1929-11-19",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "11",
            "name": "11",
            "start_date": "1929-11-18",
            "end_date": "1929-02-05",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "10",
            "name": "10",
            "start_date": "1929-02-04",
            "end_date": "1926-01-12",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "9",
            "name": "9",
            "start_date": "1926-01-11",
            "end_date": "1923-02-27",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "8",
            "name": "8",
            "start_date": "1923-02-26",
            "end_date": "1920-02-25",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "7",
            "name": "7",
            "start_date": "1920-02-24",
            "end_date": "1917-06-13",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "6",
            "name": "6",
            "start_date": "1917-06-12",
            "end_date": "1914-10-07",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "5",
            "name": "5",
            "start_date": "1914-10-06",
            "end_date": "1913-07-08",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "4",
            "name": "4",
            "start_date": "1913-07-07",
            "end_date": "1910-06-30",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "3",
            "name": "3",
            "start_date": "1910-06-29",
            "end_date": "1907-02-19",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "2",
            "name": "2",
            "start_date": "1907-02-18",
            "end_date": "1904-03-01",
            "active": False,
        },
        {
            "classification": "primary",
            "identifier": "1",
            "name": "1",
            "start_date": "1904-02-29",
            "end_date": "1901-05-08",
            "active": False,
        },
    ]
    ignored_scraped_sessions = []

    def get_session_list(self):
        url = "https://www.aph.gov.au/ParliamentNumbers.svc/GetDates"
        page = requests.get(url).content
        rows = json.loads(page)
        sessions = []
        for row in rows["d"]:
            sessions.append(str(row["ParliamentNumber"]))
            # here's a utility function to translate from the sessions API to 
            # our session object
            # if row["DateTo"]:
            #     self.print_session(row)

        return sessions

    def print_session(self, row):
        s = {
            "classification": "primary",
            "identifier": str(row["ParliamentNumber"]),
            "name": str(row["ParliamentNumber"]),
            "start_date": self.parse_date(row["DateTo"]).strftime("%Y-%m-%d"),
            "end_date": self.parse_date(row["DateFrom"]).strftime("%Y-%m-%d"),
            "active": False,
        }
        print(s)
        print(",")

    def parse_date(self, datestr: str):
        datestr = re.findall(r"\/Date\((.*?)\)\/", datestr)[0]
        day = datestr.split("+")[0]
        tzoffset = datestr.split("+")[1]
        date = datetime.datetime.fromtimestamp(int(day) / 1000)
        return date
