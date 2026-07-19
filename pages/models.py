from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} from {self.name}"


class OpportunitySubmission(models.Model):
    class OpportunityType(models.TextChoices):
        SCHOLARSHIP = "scholarship", "Scholarship"
        INTERNSHIP = "internship", "Internship"
        JOB = "job", "Job"
        FELLOWSHIP = "fellowship", "Fellowship"
        EXCHANGE_PROGRAM = "exchange_program", "Exchange Program"
        COMPETITION = "competition", "Competition"
        TRAINING = "training", "Training"

    submitter_name = models.CharField(max_length=120)
    submitter_email = models.EmailField()
    title = models.CharField(max_length=255)
    organization = models.CharField(max_length=180)
    opportunity_type = models.CharField(
        max_length=32,
        choices=OpportunityType.choices,
    )
    official_link = models.URLField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
