import re
import uuid
from datetime import date
from openstates.scrape import State
from openstates.metadata.models import (
    State as modelState,
    Chamber,
)

from .bills import CABillScraper


class CA(State):
    division_id = "ocd-division/country:ca"
    classification = "legislature"
    name = "Canada"
    legislature_name = "Parliament"
    url = "https://www.parl.ca/"
    scrapers = {
        "bills": CABillScraper,
        # "events": A2EventScraper,
    }

    # This is nonense, just a placeholder
    org_id = uuid.uuid4()
    org_id = f"ocd-organization/{org_id}"
    metadata = modelState(
        name="UK",
        abbr="uk",
        capital="None",
        capital_tz="America/Central",
        fips="48",
        unicameral=True,
        legislature_name="Parliament",
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
            "identifier": "44",
            "name": "2023-24 Session",
            "start_date": "2023-01-01",
            "end_date": "2024-12-31",
            "active": True,
        },
    ]
    ignored_scraped_sessions = []

    def get_session_list(self):
        return ["44"]
