from django.shortcuts import render, get_object_or_404

from drf_spectacular.utils import extend_schema, PolymorphicProxySerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (
    BabySerializer,
    BottleFeedSerializer,
    BreastFeedSerializer,
    DiaperSerializer,
    get_event_serializer,
    EVENT_TYPES,
    GetEventsSerializer,
    EventSerializer,
)
from .models import GuardianMapping, BabyEvent, Baby
from .permissions import isGuardian

EVENT_SCHEMA = PolymorphicProxySerializer(
    component_name="NewEvent",
    serializers=EVENT_TYPES,
    resource_type_field_name="type",
)

# Create your views here.

# TODO: create baby


# TODO: add user to the baby (will need tokenized version to check)


class BabyView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(request=BabySerializer, responses={201: BabySerializer})
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

    @extend_schema(request=EVENT_SCHEMA, responses={201: EVENT_SCHEMA})
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

    @extend_schema(
        parameters=[GetEventsSerializer],
        responses=EventSerializer(many=True),
    )
    def get(self, request, baby_id):
        """
        This endpoint will return a list of the matching events
        """

        params_serializer = GetEventsSerializer(data=request.query_params)
        params_serializer.is_valid(raise_exception=True)
        params = params_serializer.data

        baby = get_object_or_404(Baby, pk=baby_id)
        self.check_object_permissions(request, baby)
        ordering = "created_at" if params["asc"] else "-created_at"

        events = BabyEvent.objects.filter(baby=baby, type_in=params["type"]).order_by(
            ordering
        )

        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
