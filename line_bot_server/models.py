from django.core.validators import MaxLengthValidator, RegexValidator
from django.db import models


class User(models.Model):
    user_id = models.CharField(primary_key=True, unique=True, max_length=33, validators=[RegexValidator(r"U[0-9a-f]{32}")])
    type = models.IntegerField(choices=((-1, "deleted"), (0, "user"), (1, "admin")))
    status = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"id: {self.user_id}, type: {self.type}, status: {self.status}"  # type: ignore
