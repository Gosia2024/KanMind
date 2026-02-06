from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    """
    Custom user manager for creating users with email as the unique identifier.
    Required by Django when using a custom User model (AbstractBaseUser).
    """
    def create_user(self, email, fullname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not fullname:
            raise ValueError("Fullname is required")

        email = self.normalize_email(email)
        user = self.model(email=email, fullname=fullname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, fullname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email=email, fullname=fullname, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model.
    - Uses email as USERNAME_FIELD (login via email).
    - Stores fullname for display purposes.
    """
    email = models.EmailField(unique=True)
    fullname = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]
    def __str__(self):
        return self.email
