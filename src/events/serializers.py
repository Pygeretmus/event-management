from rest_framework import serializers

from events.models import Event


class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "date",
            "location",
            "organizer",
        ]
