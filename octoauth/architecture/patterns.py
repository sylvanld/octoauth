import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Callable, Dict, Set

from pydantic import BaseModel

LOGGER = logging.getLogger(__name__)


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
