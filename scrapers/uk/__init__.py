import re
import uuid
from datetime import date
from openstates.scrape import State
from openstates.metadata.models import (
    State as modelState,
    Chamber,
)

from .bills import UKBillScraper

# from .events import A2EventScraper

class UK(State):
    division_id = "ocd-division/country:uk"
    classification = "legislature"
    name = "United Kingdom"
    legislature_name = "Parliament"
    url = "https://www.parliament.uk/"
    scrapers = {
        "bills": UKBillScraper,
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
        legislature_name="Parliament of the United Kingdom",
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
    legislative_sessions = [
        {
            "_scraped_name": "2024",
            "classification": "primary",
            "identifier": "2024",
            "name": "2024 Session",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "active": True,
        },
    ]
    ignored_scraped_sessions = []

    def get_session_list(self):
        return ["2024"]
