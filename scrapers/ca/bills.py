import json
import pytz
import dateutil

from openstates.scrape import Scraper, Bill, VoteEvent

import datetime as dt


class CABillScraper(Scraper):
    _tz = pytz.timezone("America/Toronto")

    def scrape(self, session):
        url = "https://www.parl.ca/legisinfo/en/bills/json"
        response = self.get(url).content
        rows = json.loads(response)

        for row in rows:
            yield from self.scrape_bill(session, row)

    def scrape_bill(self, session, row):
        session_id = f"{row['ParliamentNumber']}-{row['SessionNumber']}"
        bill_num = row["NumberCode"]

        # the big bulk JSON doesn't have all the statuses / sponsors filled in
        json_url = f"https://www.parl.ca/LegisInfo/en/bill/{session_id}/{bill_num}/json"
        response = self.get(json_url).content
        row = json.loads(response)[0]

        chamber = "lower" if "House" in row["OriginatingChamberNameEn"] else "upper"

        bill = Bill(
            bill_num,
            legislative_session=session,
            chamber=chamber,
            title=row["ShortTitleEn"]
            if row["ShortTitleEn"] != ""
            else row["LongTitleEn"],
            classification="bill",
        )

        if row["ShortTitleEn"]:
            bill.add_title(row["LongTitleEn"])

        bill.add_sponsorship(
            row["SponsorPersonName"],
            classification="primary",
            entity_type="person",
            primary=True,
        )

        if row["ShortLegislativeSummaryEn"]:
            bill.add_abstract(row["ShortLegislativeSummaryEn"], "Short Summary")

        bill_url = (
            f"https://www.parl.ca/legisinfo/en/bill/{session_id}/{row['NumberCode']}"
        )
        bill.add_source(bill_url)
        bill.add_source(json_url)

        self.scrape_versions(bill, row)
        self.scrape_actions(bill, row)
        yield from self.scrape_votes(bill, row, chamber)

        if row["SimilarBills"]:
            self.scrape_similar(bill, row["SimilarBills"])

        yield bill

    def scrape_actions(self, bill: Bill, row: dict):
        for stage in row["BillStages"]["HouseBillStages"]:
            self.scrape_stages(bill, stage, "lower")
        for stage in row["BillStages"]["SenateBillStages"]:
            self.scrape_stages(bill, stage, "upper")
        for stage in row["BillStages"]["RoyalAssent"]:
            self.scrape_stages(bill, stage, "executive")

    def scrape_similar(self, bill: Bill, rows: dict):
        for row in rows:
            bill.add_related_bill(
                row["NumberCode"],
                f"{row['ParliamentNumber']}-{row['SessionNumber']}",
                "related",
            )

    def scrape_stages(self, bill: Bill, stage: dict, chamber: str):
        for e in stage["SignificantEvents"]:
            self.info(e["EventNameEn"])
            when = dateutil.parser.parse(e["EventDateTime"])
            when = self._tz.localize(when)
            bill.add_action(
                e["EventNameEn"],
                when,
                chamber=chamber,
                classification=[],  # TODO classifier
            )

    def scrape_versions(self, bill: Bill, row: dict):
        # https://www.parl.ca/Content/Bills/441/Government/C-51/C-51_4/C-51_4.PDF
        bill_num = row["NumberCode"]
        session_id = f"{row['ParliamentNumber']}{row['SessionNumber']}"

        if row["ReceivedRoyalAssent"]:
            bill.add_version_link(
                "Royal Assent",
                f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_4/{bill_num}_4.PDF",
                media_type="applicaton/pdf",
                on_duplicate="ignore",
            )

        if row["PassedFirstChamberThirdReading"]:
            bill.add_version_link(
                "Third Reading",
                f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_3/{bill_num}_3.PDF",
                media_type="applicaton/pdf",
                on_duplicate="ignore",
            )

        if row["PassedFirstChamberFirstReading"]:
            bill.add_version_link(
                "First Reading",
                f"https://www.parl.ca/Content/Bills/{session_id}/Government/{bill_num}/{bill_num}_1/{bill_num}_1.PDF",
                media_type="applicaton/pdf",
                on_duplicate="ignore",
            )

    def scrape_votes(self, bill: Bill, row: dict, bill_chamber: str):
        for vote in row["HouseVoteDetails"]:
            yield from self.scrape_vote(
                bill,
                vote,
                "lower",
                row["NumberCode"],
                bill_chamber,
                row["ParliamentNumber"],
                row["SessionNumber"],
            )
        for vote in row["SenateVoteDetails"]:
            yield from self.scrape_vote(
                bill,
                vote,
                "upper",
                row["NumberCode"],
                bill_chamber,
                row["ParliamentNumber"],
                row["SessionNumber"],
            )

    def scrape_vote(
        self,
        bill: Bill,
        row: dict,
        chamber: str,
        bill_id: str,
        bill_chamber: str,
        session: str,
        sitting: str,
    ):
        when = dateutil.parser.parse(row["DecisionDateTime"])
        when = self._tz.localize(when)

        vote_id = f"{bill_id}-{row['DivisionNumber']}"

        session_id = f"{session}-{sitting}"

        vote = VoteEvent(
            bill=bill_id,
            bill_chamber=bill_chamber,
            chamber=chamber,
            identifier=vote_id,
            legislative_session=session_id,
            motion_text=row["DivisionSubjectEn"],
            result="pass" if row["IsAgreedTo"] else "fail",
            start_date=when,
            classification="passage",  # NOTE This is wrong but we don't have an other here...
        )

        if chamber == "upper":
            # url = f"https://sencanada.ca/en/in-the-chamber/votes/details/627679/{session_id}"
            self.warning("Found a senate vote! Write the parsing code.")
            print(row)
            return
        elif chamber == "lower":
            url = f"https://www.ourcommons.ca/Members/en/votes/{session}/{sitting}/{row['DivisionNumber']}"

        vote.add_source(url)

        vote.set_count("yes", int(row["DivisionVotesYeas"]))
        vote.set_count("no", int(row["DivisionVotesNays"]))
        vote.set_count("paired", int(row["DivisionVotePaired"]))

        yield vote


# PYTHONPATH=scrapers poetry run os-update ca bills --scrape
