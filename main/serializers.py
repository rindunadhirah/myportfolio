from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class StarInformationMixin:
    """Provide reusable star information for portfolio serializers."""

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            return False

        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(
            user.username for user in obj.starred_by.all()
        )


class ProjectSerializer(
    StarInformationMixin,
    serializers.ModelSerializer,
):
    """Validate and represent Project API data."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "context",
            "role",
            "contributions",
            "technologies",
            "project_url",
            "image_path",
            "started_on",
            "ended_on",
            "achievement",
            "is_featured",
            "created_at",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]

    def validate_title(self, value):
        value = strip_tags(value).strip()

        if not value:
            raise serializers.ValidationError(
                "Project title cannot be empty."
            )

        return value

    def validate_summary(self, value):
        return strip_tags(value).strip()

    def validate_context(self, value):
        return strip_tags(value).strip()

    def validate_role(self, value):
        return strip_tags(value).strip()

    def validate_achievement(self, value):
        return strip_tags(value).strip()

    def validate_contributions(self, value):
        return self._clean_text_list(value, "contributions")

    def validate_technologies(self, value):
        return self._clean_text_list(value, "technologies")

    def validate(self, attrs):
        attrs = super().validate(attrs)
        started_on = attrs.get(
            "started_on",
            getattr(self.instance, "started_on", None),
        )
        ended_on = attrs.get(
            "ended_on",
            getattr(self.instance, "ended_on", None),
        )

        if started_on and ended_on and ended_on < started_on:
            raise serializers.ValidationError(
                {
                    "ended_on": (
                        "End date cannot be earlier than start date."
                    )
                }
            )

        return attrs

    @staticmethod
    def _clean_text_list(value, field_name):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                f"{field_name.capitalize()} must be a list."
            )

        return [
            strip_tags(str(item)).strip()
            for item in value
            if strip_tags(str(item)).strip()
        ]


class ExperienceSerializer(
    StarInformationMixin,
    serializers.ModelSerializer,
):
    """Validate and represent Experience API data."""

    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()
    is_ongoing = serializers.SerializerMethodField()
    category_label = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        fields = [
            "id",
            "title",
            "organization",
            "description",
            "responsibilities",
            "category",
            "category_label",
            "thumbnail",
            "started_on",
            "ended_on",
            "is_ongoing",
            "created_at",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]
        read_only_fields = [
            "id",
            "is_ongoing",
            "created_at",
            "star_count",
            "is_starred",
            "starred_by_names",
        ]

    def validate_title(self, value):
        value = strip_tags(value).strip()

        if not value:
            raise serializers.ValidationError(
                "Role title cannot be empty."
            )

        return value

    def validate_organization(self, value):
        return strip_tags(value).strip()

    def validate_description(self, value):
        return strip_tags(value).strip()

    def validate_responsibilities(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Responsibilities must be a list."
            )

        responsibilities = [
            strip_tags(str(item)).strip()
            for item in value
            if strip_tags(str(item)).strip()
        ]

        if not responsibilities:
            raise serializers.ValidationError(
                "Add at least one responsibility."
            )

        return responsibilities

    def validate(self, attrs):
        attrs = super().validate(attrs)
        started_on = attrs.get(
            "started_on",
            getattr(self.instance, "started_on", None),
        )
        ended_on = attrs.get(
            "ended_on",
            getattr(self.instance, "ended_on", None),
        )

        if started_on and ended_on and ended_on < started_on:
            raise serializers.ValidationError(
                {
                    "ended_on": (
                        "End date cannot be earlier than start date."
                    )
                }
            )

        return attrs

    def get_is_ongoing(self, obj):
        return obj.is_ongoing

    def get_category_label(self, obj):
        return obj.get_category_display()
