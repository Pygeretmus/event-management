import django_filters

from events.models import Event


class EventFilter(django_filters.FilterSet):
    start_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="date", lookup_expr="lte")

    class Meta:
        model = Event
        fields = ["start_date", "end_date"]
