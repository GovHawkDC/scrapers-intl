import json
import pytz
import dateutil
import re


from openstates.scrape import Scraper, Bill
from .session_metadata import session_metadata


class INBillScraper(Scraper):
    # TODO: Whats the tzdb code for IST?
    _tz = pytz.timezone("Asia/Kolkata")

    def scrape(self, session):
        yield from self.scrape_page(session, 1)

    def scrape_page(self, session, page_num: int):
        self.info(f"Fetching page {page_num}")

        ls_number = session_metadata[session]["ls_number"]
        rs_number = session_metadata[session]["rs_number"]

        url = f"https://sansad.in/api_rs/legislation/getBills?loksabha={ls_number}&sessionNo={rs_number}&billName=&house=&ministryName=&billType=&billCategory=&billStatus=&introductionDateFrom=&introductionDateTo=&passedInLsDateFrom=&passedInLsDateTo=&passedInRsDateFrom=&passedInRsDateTo=&page={page_num}&size=100&locale=en&sortOn=billIntroducedDate&sortBy=desc"
        response = self.get(url).content
        rows = json.loads(response)

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

            self.scrape_actions(bill, row)
            self.scrape_sponsors(bill, row)
            self.scrape_versions(bill, row)
            self.scrape_documents(bill, row)

            if row["billCategory"]:
                bill.add_subject(row["billCategory"])

            yield bill

        if rows["_metadata"]["currentPageNumber"] < rows["_metadata"]["totalPages"]:
            if page_num == 1:
                self.info(f"{rows['_metadata']['totalPages']} pages found.")
            yield from self.scrape_page(session, page_num + 1)

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
                self.strip_extra_spaces(row["ministryName"]),
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

    def strip_extra_spaces(self, val: str) -> str:
        return re.sub(r"\s+", " ", val)
