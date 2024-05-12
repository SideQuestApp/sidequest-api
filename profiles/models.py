import os
from django.db import models
from common.models import AbstractBaseModel
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Regular User"""
        if not email:
            raise ValueError('Users must have a valid email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Admin User"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin, AbstractBaseModel):
    """
    * Custom User Model
    * Uses email as default field instead of username
    """
    email = models.CharField(max_length=70, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=70)
    dob = models.CharField(null=True)
    phone_number = models.CharField(max_length=20)
    level = models.IntegerField(default=1)
    title = models.CharField(max_length=40, null=True)
    xp = models.IntegerField(default=0)
    xp_to_lvl_up = models.IntegerField(default=100)
    premium = models.BooleanField(default=os.environ['DEBUG'])
    profile_img = models.ImageField(null=True, upload_to='profile_imgs/')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'

    @property
    def full_name(self):
        """
        * Display full name of the user
        """
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.email} - {self.full_name}"

    def change_xp_to_lvl_up(self):
        """
        * Changes the xp needed for level up
        * Sub-Quadratic Growth (We might change it later)
        """
        if self.level < 21:
            self.xp_to_lvl_up = int(50 * (self.level ** 1.2))

    def level_up(self):
        """
        * Increment user level by one
        * Tranger XP for the next lvl
        """
        if self.level < 20:
            self.level += 1
        # Transfer the xp to the next level
        if self.xp >= self.xp_to_lvl_up:
            self.xp = self.xp - self.xp_to_lvl_up
        self.change_xp_to_lvl_up()
