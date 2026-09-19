import uuid

from django.db import models


class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ("internship", "Internship"),
        ("program", "Program"),
        ("research", "Research"),
        ("volunteer", "Volunteer"),
        ("part-time", "Part-Time"),
        ("full-time", "Full-Time"),
        ("freelance", "Freelance"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Record when the experience was added
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=255, default="")
    description = models.TextField()
    # Store each responsibility as a separate point.
    responsibilities = models.JSONField(default=list)
    category = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES,
        default="full-time",
    )
    thumbnail = models.URLField(blank=True, null=True)
    started_on = models.DateField()
    ended_on = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ["-started_on", "title"]

    def __str__(self):
        return self.title

    @property
    def is_ongoing(self):
        return self.ended_on is None


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
