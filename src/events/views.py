from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from events.filters import EventFilter
from events.models import Event
from events.permissions import IsNotOrganizer, IsOrganizerOrReadOnly
from events.serializers import EventRegistrationSerializer, EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by("date")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ["title", "location", "organizer__username"]
    filterset_class = EventFilter

    def get_filterset(self, *args, **kwargs):
        kwargs["request"] = self.request
        return super().get_filterset(*args, **kwargs)

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

        request.user.email_user(
            subject="Event Registration", message=f"You have successfully registered for the {event.title} event"
        )
        return Response({"detail": "Registration successful."}, status=status.HTTP_201_CREATED)
