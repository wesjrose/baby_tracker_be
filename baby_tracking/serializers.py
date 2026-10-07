from django.core.exceptions import ValidationError

from rest_framework import serializers

from .models import Baby, BabyEvent


class BabySerializer(serializers.ModelSerializer):

    class Meta:
        model = Baby
        fields = ["name"]

    def create(self, validated_data):
        return Baby.objects.create(**validated_data)


class BaseEventSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    notes = serializers.CharField(
        max_length=1000, required=False, allow_blank=True, default=""
    )


class BottleFeedDataSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0, max_value=500)
    contents = serializers.ChoiceField(choices=["formula", "breast_milk"])


class BottleFeedSerializer(BaseEventSerializer):
    data = BottleFeedDataSerializer()


class BreastFeedDataSerializer(serializers.Serializer):
    left_time = serializers.IntegerField(min_value=0)
    right_time = serializers.IntegerField(min_value=0)


class BreastFeedSerializer(BaseEventSerializer):
    data = BreastFeedDataSerializer()


class DiaperDataSerializer(serializers.Serializer):
    contents = serializers.ChoiceField(choices=["wet", "dirty", "dry"])
    colour = serializers.ChoiceField(
        choices=["black", "green", "yellow", "red"], required=False
    )
    composition = serializers.ChoiceField(
        choices=["runny", "mucousy", "mushy", "solid", "pebbles"], required=False
    )
    blowout = serializers.BooleanField(required=False)
    diaper_rash = serializers.BooleanField(required=False)


class DiaperSerializer(BaseEventSerializer):
    data = DiaperDataSerializer()


EVENT_TYPES = {
    "bottle_feed": BottleFeedSerializer,
    "breast_feed": BreastFeedSerializer,
    "diaper": DiaperSerializer,
}


class GetEventsSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=EVENT_TYPES)
    asc = serializers.BooleanField()


def get_event_serializer(event: dict):

    event_type = event.get("type", None)
    if event_type not in EVENT_TYPES:
        raise ValidationError(f"{event_type} is not a valid event type")
    return EVENT_TYPES[event_type](data=event)


class EventSerializer(serializers.ModelSerializer):

    baby_id = serializers.PrimaryKeyRelatedField(source="baby", read_only=True)

    class Meta:
        model = BabyEvent
        fields = ["id", "created_at", "notes", "data", "baby_id"]
