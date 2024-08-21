from django_cassandra_engine.models import DjangoCassandraModel
from cassandra.cqlengine import columns
import uuid
import secrets
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)  # Correct UUID usage
    email = columns.Text(index=True, required=True)
    username = columns.Text(required=True)
    phone_number = columns.Text()
    password = columns.Text()
    created_at = columns.DateTime()

    def clean(self):
        if User.objects.filter(email=self.email).exists():
            raise ValidationError(_('Email already exists.'))

class Member(DjangoCassandraModel):
    email = columns.Text(primary_key=True)
    name = columns.Text()
    phone_number = columns.Text()
    password = columns.Text()
    profile_picture = columns.Text()  # Store as base64 string

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = secrets.token_urlsafe(8)
        super().save(*args, **kwargs)

