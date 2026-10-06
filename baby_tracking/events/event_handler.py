"""
This module contains helper classes the build and manage events
"""

from django.core.exceptions import ValidationError

from rest_framework import serializers

from .event_serializers import (
    DiaperSerializer,
    BottleFeedSerializer,
    BreastFeedSerializer,
)

EVENT_TYPES = {
    "bottle_feed": BottleFeedSerializer,
    "breast_feed": BreastFeedSerializer,
    "diaper": DiaperSerializer,
}


def verify_event(self, event: dict):

    event_type = event.get("type", None)

    if event_type not in EVENT_TYPES.keys():
        raise ValidationError("event type is not valid")

    serializer = EVENT_TYPES[event_type](data=event)

    if not serializer.is_valid():
        raise serializers.ValidationError({"data": serializer.errors})
