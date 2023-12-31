import hashlib

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils import timezone

from accounts.managers import UserManager
from accounts.validators import (
    validate_username,
    validate_name,
    validate_birth_date
)


class User(AbstractUser):
    username = models.CharField(max_length=50,
                                unique=True,
                                validators=[validate_username])
    email = models.EmailField(unique=True,
                              max_length=255)
    first_name = models.CharField(max_length=50,
                                  validators=[validate_name])
    last_name = models.CharField(max_length=50,
                                 validators=[validate_name])

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        self.username = self.username.lower()
        super().save(*args, **kwargs)


class Profile(models.Model):
    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.URLField(max_length=255, blank=True)
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(validators=[validate_birth_date])
    bio = models.TextField()
    info = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.user} \'s profile'

    def create_gravatar(self):
        md5_hash = hashlib.md5(self.user.email.encode('utf-8')).hexdigest()
        gravatar_url = f'https://www.gravatar.com/avatar/{md5_hash}?d=identicon&s={200}'
        self.avatar = gravatar_url

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)
        if not self.avatar:
            self.create_gravatar()
        super().save(*args, **kwargs)


def get_random_token():
    pass


class AbstractToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, default='', unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.token = get_random_string(length=32)
        super(AbstractToken, self).save(*args, **kwargs)

    def verify_token(self):
        validate_expiration = timezone.localtime(self.created) < timezone.now() - timezone.timedelta(days=1)
        return validate_expiration

class ActivateToken(AbstractToken):
    def __str__(self):
        return f'{self.user}\'s activate token'

    class Meta:
        verbose_name_plural = 'Activation Tokens'


class PasswordsResetToken(AbstractToken):
    def __str__(self):
        return f'{self.user}\'s password reset token'

    class Meta:
        verbose_name_plural = 'Password reset Tokens'
