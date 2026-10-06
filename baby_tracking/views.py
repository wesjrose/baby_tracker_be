from django.shortcuts import render, get_object_or_404

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import BabySerializer
from .models import GuardianMapping, BabyEvent, Baby
from .permissions import isGuardian
from .events.event_handler import verify_event

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

        event = request.data

        # confirming that the event is properly formed
        verify_event(event)

        event = BabyEvent.objects.create(
            type=event["type"],
            baby=baby,
            notes=event.get("notes", None),
            created_at=event["created_at"],
            data=event,
        )
