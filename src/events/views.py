from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from events.models import Event
from events.permissions import IsOrganizerOrReadOnly
from events.serializers import EventSerializer


class EventListCreateView(ListCreateAPIView):
    queryset = Event.objects.all().order_by("date")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)


class EventDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOrganizerOrReadOnly]
