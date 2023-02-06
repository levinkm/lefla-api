from enum import unique
from tokenize import blank_re
import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
# import phonenumbers

class myAccountManager(BaseUserManager):
    def create_user(self,email,username,password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError("users must have a username")
        # if not phonenumber:
        #     raise ValueError("Users must have their phone numbers ")   

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            # phonenumber = phonenumber

        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,username,password):
        user = self.create_user(
            email = self.normalize_email(email),
            password = password,
            username = username,
            # phonenumber = phonenumber

        ) 
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return 'user created'



class Accounts(AbstractBaseUser):
    id = models.CharField(max_length=100, primary_key=True, unique=True, default=uuid.uuid4)
    email = models.EmailField(verbose_name='email', max_length=80, unique=True)
    username = models.CharField(unique=True, max_length=50)
    phonenumber = PhoneNumberField(blank = True, null = True)
    parent_phonenumber = PhoneNumberField( blank = True, null = True)
    fullname = models.CharField(blank=True, max_length=50)
    picture = models.ImageField(upload_to='Landlords',null=True,blank=True)
    otp = models.CharField(max_length=7, null=True,blank=True)
    is_email_verified = models.BooleanField( default=False)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_landlord = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = myAccountManager()

    class Meta:
        verbose_name = ("User")
        verbose_name_plural = ("Users")

    def __str__(self) -> str:
        return self.email

    def has_perm(self,perm,obj=None):
        return self.is_admin

    def has_module_perms(self,app_label):
        return True

    # def save(self, *args, **kwargs):
    #     if self.is_landlord:




