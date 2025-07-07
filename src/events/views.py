from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from events.models import Event
from events.permissions import IsNotOrganizer, IsOrganizerOrReadOnly
from events.serializers import EventRegistrationSerializer, EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("date")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ("update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsOrganizerOrReadOnly()]
        if self.action == "register":
            return [IsAuthenticated(), IsNotOrganizer()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @action(detail=True, methods=["post"], serializer_class=EventRegistrationSerializer)
    def register(self, request, pk=None):
        event = self.get_object()

        serializer = self.get_serializer(data={}, context={"request": request, "event": event})
        serializer.is_valid(raise_exception=True)
        super().perform_create(serializer)

        return Response({"detail": "Registration successful."}, status=status.HTTP_201_CREATED)
