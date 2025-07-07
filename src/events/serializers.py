from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from events.models import Event, EventRegistration


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


class CurrentEventDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["event"]

    def __repr__(self):
        return "%s()" % self.__class__.__name__


class EventRegistrationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    event = serializers.HiddenField(default=CurrentEventDefault())

    class Meta:
        model = EventRegistration
        fields = ["user", "event"]
        validators = [
            UniqueTogetherValidator(
                queryset=EventRegistration.objects.all(),
                fields=("user", "event"),
                message="You are already registered for this event.",
            )
        ]
