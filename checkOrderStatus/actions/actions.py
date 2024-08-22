from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json
import urllib.request


class ActionCheckOrderStatus(Action):
    def name(self) -> Text:
        return "check_order_status"

    def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # hard-coded balance for tutorial purposes. in production this
        # would be retrieved from a database or an API
        order_number = tracker.get_slot("orderNumber")
        email = tracker.get_slot("email")
        status = 'HARD CODE STATUS {} {}'.format(order_number, email)
        url = "https://rental.stg.travelwifi.io/api/mobile/app_version"
        order_found = False
        app_version = ''
        try:
            res = urllib.request.urlopen(
                urllib.request.Request(
                    url=url,
                    headers={'Accept': 'application/json'},
                    method='GET'
                ),
                timeout=5
            )
            app_version = res.read().decode("utf-8")
        except Exception as err:
            order_found = False
        url = "https://rental.stg.travelwifi.io/en/order/currentStatus?order_number={}&email={}".format(order_number,
                                                                                                        email)
        try:
            res = urllib.request.urlopen(
                urllib.request.Request(
                    url=url,
                    headers={
                        'Accept': 'application/json',
                        'X-Inertia': 'true',
                        'X-Inertia-Version': app_version
                    },
                    method='GET'
                ),
                timeout=30
            )
            order = json.loads(res.read())
            order_found = True
            status = order['props']['order']['status']
        except Exception as err:
            order_found = False
        # tracker.slots['orderFound'] = order_found
        return [SlotSet("status", status), SlotSet("order_found", order_found)]
