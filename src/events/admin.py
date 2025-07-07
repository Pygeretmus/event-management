from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from events.models import Event, EventRegistration


class EventRegistrationInline(admin.TabularInline):
    model = EventRegistration
    extra = 0
    readonly_fields = ("user_link",)
    fields = ("user_link",)

    def has_add_permission(self, request, obj=None):
        return False

    def user_link(self, obj):
        if obj.user:
            url = reverse("admin:users_customusermodel_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user)
        return "-"

    user_link.short_description = "User"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "date",
        "location",
        "organizer_display",
        "date",
    )

    list_filter = (
        "date",
        "organizer",
        "date",
    )

    search_fields = (
        "title",
        "description",
        "location",
        "organizer__username",
        "organizer__first_name",
        "organizer__last_name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-date",)

    fieldsets = (
        (
            "General",
            {
                "fields": ("title", "description", "organizer"),
                "classes": ("wide",),
            },
        ),
        (
            "Date and location",
            {
                "fields": ("date", "location"),
                "classes": ("wide",),
            },
        ),
        (
            "Service information",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    inlines = [EventRegistrationInline]

    def organizer_display(self, obj):
        url = reverse("admin:users_customusermodel_change", args=[obj.organizer.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none;">' "{}</a>",
            url,
            obj.organizer,
        )

    organizer_display.short_description = "Organizer"
    organizer_display.admin_order_field = "organizer"


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "user_display", "event_display")

    list_filter = (
        "event__date",
        "event__location",
    )

    search_fields = ("user__username", "user__first_name", "user__last_name", "event__title", "event__location")

    ordering = ("-event__date",)

    def user_display(self, obj):
        url = reverse("admin:users_customusermodel_change", args=[obj.user.pk])
        return format_html(
            '<a href="{}" style="text-decoration: none;">' "{}</a>",
            url,
            obj.user,
        )

    user_display.short_description = "User"
    user_display.admin_order_field = "user"

    def event_display(self, obj):
        url = reverse("admin:events_event_change", args=[obj.event.pk])
        return format_html('<a href="{}" style="text-decoration: none;">' "{}</a>", url, obj.event.title)

    event_display.short_description = "Event"
    event_display.admin_order_field = "event"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "event")
