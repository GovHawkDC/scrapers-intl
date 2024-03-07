import json
import pytz
import dateutil

from openstates.scrape import Scraper, Bill

import datetime as dt

class UKBillScraper(Scraper):

    _tz = pytz.timezone("Europe/London")

    def scrape(self, session):
        url = f"https://bills-api.parliament.uk/api/v1/Bills?CurrentHouse=All&Session={session}"
        response = self.get(url).content
        rows = json.loads(response)

        for row in rows["items"]:
            yield from self.scrape_bill(session, row["billId"])


    def scrape_bill(self, session, bill_id: int):
        url = f"https://bills-api.parliament.uk/api/v1/Bills/{bill_id}"
        response = self.get(url).content
        row = json.loads(response)

        print(row)

        chamber = "upper" if row['originatingHouse'] == "Lords" else "lower"

        # hack, UK bills don't have an id as such
        bill_num = f"{row['originatingHouse']} {row['billId']}"
        bill = Bill(
            bill_num,
            legislative_session=session,
            chamber=chamber,
            title=row["shortTitle"],
            classification="bill",
        )

        bill.add_title(row['longTitle'])
            
        if row['summary']:
            bill.add_abstract(row['summary'])

        for sponsor in row['sponsors']:
            bill.add_sponsorship(
                name=sponsor['member']['name'],
                classification="primary",
                entity_type="person",
                primary=True
            )

        # TODO: promoters = cosponsors?
            
        self.scrape_actions(bill, bill_id)
        self.scrape_versions(bill, bill_id)

        web_url = f"https://bills.parliament.uk/bills/{bill_id}"
        bill.add_source(web_url)

        yield bill


    def scrape_actions(self, bill: Bill, bill_id: int) -> None:
        url = f"https://bills-api.parliament.uk/api/v1/Bills/{bill_id}/Stages"
        response = self.get(url).content
        rows = json.loads(response)

        for row in rows['items']:
            chamber = "upper" if row['house'] == "Lords" else "lower"

            if row['stageSittings']:
                when = dateutil.parser.parse(row['stageSittings'][0]['date'])
                when = self._tz.localize(when)
                bill.add_action(
                    description=row["description"],
                    date=when,
                    chamber=chamber,
                    classification=None,
                )

    def scrape_versions(self, bill: Bill, bill_id: int) -> None:
        url = f"https://bills-api.parliament.uk/api/v1/Bills/{bill_id}/Publications"
        response = self.get(url).content
        rows = json.loads(response)

        for row in rows['publications']:
            version_date = dateutil.parser.parse(row['displayDate'])
            version_date = self._tz.localize(version_date)

            if row['publicationType']['id'] == 5:
                for v in row['files']:
                    bill.add_version_link(
                        note=row['title'],
                        url=f"https://bills.parliament.uk/publications/{row['id']}/documents/{v['id']}",
                        date=version_date.strftime("%Y-%m-%d"),
                        media_type=v['contentType'],
                        on_duplicate="ignore"
                    )
                for v in row['links']:
                    bill.add_version_link(
                        note=row['title'],
                        url=v['url'],
                        media_type=v['contentType'],
                        on_duplicate="ignore"
                    )
            else:
                self.info(f"Saving doc, docid {row['publicationType']['id']}")
                for v in row['links']:
                    bill.add_document_link(
                        note=row['title'],
                        url=v['url'],
                        media_type=v['contentType'],
                        on_duplicate="ignore"
                    )