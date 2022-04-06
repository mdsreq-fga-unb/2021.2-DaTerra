from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core import validators
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail


class UserManager(BaseUserManager):
    def _create_user(self, cpf, complete_name, birthday_date, email, cellphone, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not cpf:
            raise ValueError(_('There must be a CPF'))
        email = self.normalize_email(email)
        user = self.model(
            cpf=cpf, complete_name=complete_name,
            birthday_date=birthday_date, email=email,
            cellphone=cellphone,
            is_staff=is_staff, is_active=True, is_superuser=is_superuser,
            last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_user(self, cpf, email=None, password=None, **extra_fields):
        return self._create_user(cpf, email, password, False, False, **extra_fields)

    def create_superuser(self, cpf, complete_name, birthday_date, email, cellphone, password, **extra_fields):
        user=self._create_user(cpf, complete_name, birthday_date, email, cellphone, password, True, True, **extra_fields)
        user.is_active=True
        user.save(using=self._db)
        return user

STATE_CHOICES = (
    ('DF', 'distrito federal'),
    ('SP', 'são paulo'),
)



class User(AbstractBaseUser, PermissionsMixin):
    cpf = models.CharField(_('cpf'), max_length=30, unique=True)
    complete_name = models.CharField(_('complete name'), max_length=30)
    birthday_date = models.DateField(_('birthday_date'))
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    cellphone = models.CharField(_('cellphone'), max_length=30)
    city = models.CharField(_('city'), max_length=255, default='não informado')
    state = models.CharField(max_length=255, choices=STATE_CHOICES, default='DF')
    
    is_staff = models.BooleanField(_('staff status'), default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True, help_text=_('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'))
    is_trusty = models.BooleanField(_('trusty'), default=False, help_text=_('Designates whether this user has confirmed his account.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'cpf'
    REQUIRED_FIELDS = ['complete_name', 'email', 'cellphone', 'birthday_date']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.complete_name

    def get_short_name(self):
        return self.complete_name.split(' ')[0]

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])