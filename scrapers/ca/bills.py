import json
import pytz
import dateutil

from openstates.scrape import Scraper, Bill

import datetime as dt

class CABillScraper(Scraper):
    _tz = pytz.timezone("Europe/Dublin")

    def scrape(self, session):
        url = "https://www.parl.ca/legisinfo/en/bills/json"
        response = self.get(url).content
        rows = json.loads(response)

        for row in rows:
            yield from self.scrape_bill(session, row)

    def scrape_bill(self, session, row):

        chamber = "lower" if "House" in row['BillDocumentTypeNameEn'] else "upper"

        bill_num = row['NumberCode']

        bill = Bill(
            bill_num,
            legislative_session=session,
            chamber=chamber,
            title=row["ShortTitleEn"] if row['ShortTitleEn'] != "" else row['LongTitleEn'],
            classification="bill",
        )

        if row['ShortTitleEn']:
            bill.add_title(row['LongTitleEn'])

        session_id = f"{row['ParliamentNumber']}-{row['SessionNumber']}"

        bill_url = f"https://www.parl.ca/legisinfo/en/bill/{session_id}/{row['NumberCode']}"
        bill.add_source(bill_url)

        self.scrape_versions(bill, row)

        yield bill

    def scrape_versions(self, bill: Bill, row: dict):
        # https://www.parl.ca/Content/Bills/441/Government/C-51/C-51_4/C-51_4.PDF
        bill_num = row['NumberCode']
        session_id =  f"{row['ParliamentNumber']}{row['SessionNumber']}"

        if row['ReceivedRoyalAssent']:
            bill.add_version_link(
                "Royal Assent",
                f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_4/{bill_num}_4.PDF",
                media_type="applicaton/pdf",
                on_duplicate="ignore"
            )

        if row['PassedFirstChamberThirdReading']:
            bill.add_version_link(
                "Third Reading",
                f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_3/{bill_num}_3.PDF",
                media_type="applicaton/pdf",
                on_duplicate="ignore"
            )

        if row['PassedFirstChamberFirstReading']:
            bill.add_version_link(
                "First Reading",
                f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_1/{bill_num}_1.PDF",
                media_type="applicaton/pdf",
                on_duplicate="ignore"
            )

        # if bill['PassedFirstChamberSecondReading']:
        #     bill.add_version_link(
        #         "Second Reading",
        #         f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_2/{bill_num}_2.PDF",
        #         media_type="applicaton/pdf",
        #         on_duplicate="ignore"
        #     )
# PYTHONPATH=scrapers poetry run os-update ca bills --scrape