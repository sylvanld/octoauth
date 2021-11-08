import json
import logging
from collections import defaultdict
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Callable, Dict, Set

from pydantic import BaseModel

FILE_HANDLER = RotatingFileHandler("octoauth.events.log")
FILE_HANDLER.setLevel(logging.DEBUG)

LOGGER = logging.getLogger("octoauth.events")
LOGGER.addHandler(FILE_HANDLER)


class EventBus:
    subscribers: Dict[str, Set[Callable]]

    def __init__(self):
        self.subscribers = defaultdict(set)

    def subscribe(self, event: str, subscriber: Callable):
        self.subscribers[event].add(subscriber)

    def unsubscribe(self, event: str, subscriber: Callable):
        self.subscribers[event].remove(subscriber)

    def publish(self, event: str, data: BaseModel):
        LOGGER.error(
            "%s",
            json.dumps(
                {
                    "event": event,
                    "date": datetime.now().isoformat(),
                    "data": data.dict(),
                },
                indent=4,
            ),
        )
        for subscriber in self.subscribers[event]:
            subscriber(data)


event_bus = EventBus()


def publish_event(event_name: str):
    """
    Decorator used to publish event with data equals to output of decorated function.
    """

    def wrapped(func):
        def wrapper(*args, **kwargs):
            output = func(*args, **kwargs)
            event_bus.publish(event_name, output)
            return output

        return wrapper

    return wrapped
