# This files contains your custom actions which can be used to run
# custom Python code.

from typing import Text, List, Any, Dict
import socket

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

# Connection to Raspberry Pi
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("raspberrypi", 5000))

ALLOWED_FLAVOUR = ["strawberry", "orange", "blackcurrant"]


class ValidateSimplePickForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_pick_form"

    def validate_flavour(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `flavour` value."""

        if slot_value.lower() not in ALLOWED_FLAVOUR:
            dispatcher.utter_message(text=f"We only have strawberry, orange, and blackcurrant candies.")
            return {"flavour": None}
        
        return {"flavour": slot_value}
    
class ValidateSimpleSortForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_sort_form"

    def validate_flavour(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `flavour` value."""

        if slot_value.lower() not in ALLOWED_FLAVOUR:
            dispatcher.utter_message(text=f"We only have strawberry, orange, and blackcurrant candies.")
            return {"flavour": None}
        
        return {"flavour": slot_value}
    
class ActionResetCandySlot(Action):
    def name(self) -> Text:
        return "action_reset_candy_slot"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [SlotSet("flavour", None)]
    
class ActionSortCandy(Action):
    def name(self) -> Text:
        return "action_sort_candy"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        s.send(f"SortCandy {tracker.get_slot('flavour')}".encode())
    
class ActionPickCandy(Action):
    def name(self) -> Text:
        return "action_pick_candy"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        s.send(f"PickCandy {tracker.get_slot('flavour')}".encode())

class ActionPickCup(Action):
    def name(self) -> Text:
        return "action_pick_cup"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        s.send(f"PickCup cup".encode())
