import json
import pytz
import dateutil

from openstates.scrape import Scraper, Bill

import datetime as dt


class INBillScraper(Scraper):
    # TODO: Whats the tzdb code for IST?
    _tz = pytz.timezone("Asia/Kolkata")

    def scrape(self, session):
        url = "https://sansad.in/api_rs/legislation/getBills?billName=&house=&ministryName=&mpCode=&billType=Government&billCategory=&billStatus=&introductionDateFrom=&introductionDateTo=&passedInLsDateFrom=&passedInLsDateTo=&passedInRsDateFrom=&passedInRsDateTo=&page=1&size=50&locale=en&sortOn=billIntroducedDate&sortBy=desc"
        response = self.get(url).content
        rows = json.loads(response)

        # TODO: metadata

        for row in rows["records"]:
            bill_num = f"{row['billYear']} {row['billNumber']}"

            chamber = (
                "lower" if row["billIntroducedInHouse"] == "Lok Sabha" else "upper"
            )

            bill = Bill(
                bill_num,
                legislative_session=session,
                chamber=chamber,
                title=row["billName"],
                classification="bill",
            )

            bill.add_source("https://sansad.in/rs/legislation/bills")

            # todo errataFile reportFile billSynopsisFile billGazettedFile

            self.scrape_actions(bill, row)
            self.scrape_sponsors(bill, row)
            self.scrape_versions(bill, row)

            if row["billCategory"]:
                bill.add_subject(row["billCategory"])

            yield bill

    def scrape_actions(self, bill: Bill, row: dict):
        chamber = "lower" if row["billIntroducedInHouse"] == "Lok Sabha" else "upper"
        actions = [
            {
                "key": "billIntroducedDate",
                "name": "Introduced",
                "actor": chamber,
                "classification": ["introduction"],
            },
            {
                "key": "billPassedInLSDate",
                "name": "Passed Lok Sabha",
                "actor": "lower",
                "classification": ["passage"],
            },
            {
                "key": "billPassedInRSDate",
                "name": "Passed Rajya Sabha",
                "actor": "upper",
                "classification": ["passage"],
            },
            {
                "key": "billAssentedDate",
                "name": "Assented",
                "actor": "executive",
                "classification": ["executive-signature"],
            },
        ]

        for action in actions:
            if row[action["key"]] is not None:
                when = dateutil.parser.parse(row[action["key"]])
                when = self._tz.localize(when)

                bill.add_action(
                    action["name"],
                    date=when,
                    organization=action["actor"],
                    classification=action["classification"],
                )

        if row["billAssentedDate"] and row["actNo"] and row["actYear"]:
            when = dateutil.parser.parse(row["billAssentedDate"])
            when = self._tz.localize(when)

            bill.add_action(
                f"Act No. {row['actNo'].strip()} of {row['actYear']}",
                date=when,
                organization="executive",
                classification=["became-law"],
            )

    def scrape_documents(self, bill: Bill, row: dict):
        version_keys = {
            "errataFile": "Errata",
            "reportFile": "Report",
            "billGazettedFile": "Gazette",
            "billSynopsisFile": "Synopsis",
        }
        for key, version_name in version_keys.items():
            if row[key] != None:
                bill.add_document_link(
                    version_name,
                    row[key],
                    media_type="application/pdf",
                    on_duplicate="ignore",
                )

    def scrape_sponsors(self, bill: Bill, row: dict):
        chamber = "lower" if row["billIntroducedInHouse"] == "Lok Sabha" else "upper"

        if row["billIntroducedBy"]:
            bill.add_sponsorship(
                row["billIntroducedBy"],
                entity_type="person",
                primary=True,
                chamber=chamber,
                classification="primary",
            )
        else:
            bill.add_sponsorship(
                row["ministryName"],
                entity_type="organization",
                primary=True,
                classification="primary",
            )

    def scrape_versions(self, bill: Bill, row: dict):
        version_keys = {
            "billIntroducedFile": "As Introduced",
            "billPassedInLSFile": "As Passed by Lok Sabha",
            "billPassedInRSFile": "As Passed by Rajya Sabha",
            "billPassedInBothHousesFile": "As Passed by Both Houses",
        }

        for key, version_name in version_keys.items():
            if row[key] != None:
                bill.add_version_link(
                    version_name,
                    row[key],
                    media_type="application/pdf",
                    on_duplicate="ignore",
                )
