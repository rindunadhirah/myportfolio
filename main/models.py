import uuid

from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("internship", "Internship"),
        ("research", "Research"),
        ("volunteer", "Volunteer"),
        ("part-time", "Part-Time"),
        ("full-time", "Full-Time"),
        ("freelance", "Freelance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="full-time",
    )
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_at is None


class Project(models.Model):
    # Main project information
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    summary = models.TextField()
    context = models.CharField(max_length=255)
    role = models.CharField(max_length=100)

    # Multiple contributions and technologies
    contributions = models.JSONField(default=list)
    technologies = models.JSONField(default=list)

    # Project media and timeline
    project_url = models.URLField()
    image_path = models.CharField(max_length=255)
    started_on = models.DateField()
    ended_on = models.DateField(blank=True, null=True)

    # Optional project highlights
    achievement = models.CharField(max_length=255, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-started_on", "title"]

    def __str__(self):
        return self.title
