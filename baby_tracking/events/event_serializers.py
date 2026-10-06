from rest_framework import serializers

class BaseEventSerializer(serializers.Serializer):
    created_at = serializers.DateTimeField()
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True, default=None)

class BottleFeedSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=0, max_value=500,)
    contents = serializers.ChoiceField(choices=["formula", "breast_milk"])
    

class BreastFeedSerializer(serializers.Serializer):
    left_time = serializers.IntegerField(min_value=0)
    right_time = serializers.IntegerField(min_value=0)
    

class DiaperSerializer(serializers.Serializer):
    contents = serializers.ChoiceField(choices=["wet", "dirty", "dry"])
    colour = serializers.ChoiceField(choices=["black", "green", "yellow", "red", "black"], required=False)
    composition = serializers.ChoiceField(choices=["runny", "mucousy", "mushy", "solid", "pebbles"], required=False)
    blowout = serializers.BooleanField(required=False)
    diaper_rash = serializers.BooleanField(required=False)
    