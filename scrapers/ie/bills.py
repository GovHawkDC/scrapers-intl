import json
import pytz
import dateutil

from openstates.scrape import Scraper, Bill

import datetime as dt

class IEBillScraper(Scraper):
    _tz = pytz.timezone("Europe/Dublin")

    def scrape(self, session):
        url = "https://api.oireachtas.ie/v1/legislation?bill_status=Current,Withdrawn,Enacted,Rejected,Defeated,Lapsed&bill_source=Government,Private%20Member&date_start=1900-01-01&date_end=2099-01-01&limit=10&chamber_id=&lang=en"
        response = self.get(url).content
        rows = json.loads(response)

        for row in rows['results']:
            # print(row)
            row = row['bill']
            bill_num = f"{row['billYear']} {row['billNo']}"
            # todo - legislature for government
            chamber = "lower" if row['originHouse']['showAs'] == "Dáil Éireann" else "upper"
            bill = Bill(
                bill_num,
                legislative_session=session,
                chamber=chamber,
                title=row["shortTitleEn"],
                classification="bill",
            )

            for sponsor in row['sponsors']:
                sponsor = sponsor['sponsor']
                sponsor_name = sponsor['as']['showAs'] if sponsor['as']['showAs'] else sponsor['by']['showAs']
                bill.add_sponsorship(
                    name=sponsor_name,
                    primary=sponsor['isPrimary'],
                    classification="primary" if sponsor['isPrimary'] else "cosponsor",
                    entity_type="person" 
                )

            for version in row['versions']:
                version = version['version']
                bill.add_version_link(
                    version['showAs'],
                    version['formats']['pdf']['uri'],
                    media_type="application/pdf",
                )

            for stage in row['stages']:
                stage = stage['event']
                when = dateutil.parser.parse(stage['dates'][0]['date'])
                when = self._tz.localize(when)
                actor = "lower" if stage['chamber']['chamberCode'] == "dial" else "upper"
                bill.add_action(
                    description=stage['showAs'],
                    date=when,
                    chamber=actor,
                    classification=None,
                )


            # todo: strip html
            bill.add_title(row['longTitleEn'])

            bill.add_source(row['originHouseURI'])
            yield bill
