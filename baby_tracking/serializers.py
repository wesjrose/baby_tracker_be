from rest_framework import serializers

from .models import Baby

class BabySerializer(serializers.ModelSerializer):

    class Meta:
        model = Baby
        fields = ["name"]

    def create(self, validated_data):
        return Baby.objects.create(**validated_data)