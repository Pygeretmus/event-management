from django.urls import path

from events.views import EventDetailView, EventListCreateView

urlpatterns = [
    path("events/", EventListCreateView.as_view(), name="event-list"),
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
]
