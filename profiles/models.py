import os
import secrets
import string
from django.db import models
from common.models import AbstractBaseModel
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from quest.models import QuestNode


def generate_unique_token(len):
    """
    * Generates random token (LEN=6)
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(len))


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
    dob = models.CharField(max_length=10, null=True)  # ! Later convert it to DateField
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
    current_quest_node = models.ForeignKey(QuestNode, on_delete=models.CASCADE,
                                           related_name='current_node', blank=True, null=True)

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


class VerifyUserEmail(AbstractBaseModel):
    """
    * Model to generate token for a user to verify email
    * It will create a 1to1 relationship with a user upon user creation
    * Is_active will be false upon verifing the email
    * Is_active can be true if the user press forgot my password
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='verifyemail_user')
    token = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        """
        * Generates unique token upon instance creation
        """
        if not self.token:
            self.token = generate_unique_token(6)
        super().save(*args, **kwargs)

    def activate_token(self):
        """
        * Set the is_activate to true
        * Generate new token
        """
        self.is_active = True
        self.token = generate_unique_token(6)
        self.save()

    def deactivate_token(self):
        """
        * Sets the in_active to false
        """
        self.token = generate_unique_token(20)
        self.is_active = False
        self.save()
