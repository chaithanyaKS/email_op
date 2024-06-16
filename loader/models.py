from django.db import models


# Create your models here.
class Email(models.Model):
    from_email = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    received_at = models.DateTimeField()
    msg_id = models.CharField(max_length=20)

    def __str__(self) -> str:
        return f"{self.msg_id} {self.subject}"
