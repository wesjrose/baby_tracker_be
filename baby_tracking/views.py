from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    BabySerializer,
    BottleFeedSerializer,
    BreastFeedSerializer,
    DiaperSerializer,
)
from .models import GuardianMapping, BabyEvent, Baby
from .permissions import isGuardian

EVENT_TYPES = {
    "bottle_feed": BottleFeedSerializer,
    "breast_feed": BreastFeedSerializer,
    "diaper": DiaperSerializer,
}


def get_event_serializer(event: dict):

    event_type = event.get("type", None)
    if event_type not in EVENT_TYPES:
        raise ValidationError(f"{event_type} is not a valid event type")
    return EVENT_TYPES[event_type](data=event)


# Create your views here.

# TODO: create baby


# TODO: add user to the baby (will need tokenized version to check)


class BabyView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """This is the endpoint for creating a new baby. The baby will be
        assigned to the user that creates the baby.
        """

        serializer = BabySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        baby = serializer.save()

        GuardianMapping.objects.create(baby=baby, guardian=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventView(APIView):

    permission_classes = [IsAuthenticated, isGuardian]

    def post(self, request, baby_id):
        baby = get_object_or_404(Baby, pk=baby_id)
        self.check_object_permissions(request, baby)

        data = request.data
        serializer = get_event_serializer(data)
        serializer.is_valid(raise_exception=True)

        event = BabyEvent.objects.create(
            type=data["type"],
            baby=baby,
            notes=data.get("notes", None),
            created_at=data["created_at"],
            data=data["data"],
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
