import django_filters
from django.contrib.auth import get_user_model

from events.models import Event

User = get_user_model()


class EventFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="lte")
    organized_by_me = django_filters.BooleanFilter(method="filter_organized_by_me")
    participated_by_me = django_filters.BooleanFilter(method="filter_participated_by_me")

    class Meta:
        model = Event
        fields = ["start_date", "end_date", "organized_by_me", "participated_by_me"]

    def filter_organized_by_me(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(organizer=user)
            else:
                return queryset.exclude(organizer=user)
        return queryset.none()

    def filter_participated_by_me(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(participants=user)
            else:
                return queryset.exclude(participants=user)
        return queryset.none()
