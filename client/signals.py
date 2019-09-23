from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import ClientProfile
from django.core.mail import send_mail
from django.conf import settings
import random


@receiver(m2m_changed)
def driver_added(action, instance, pk_set, model, **kwargs):
    if model == Group:
        if action == 'post_add':
            group_name = Group.objects.get(id=next(iter(pk_set))).name
            if group_name == 'client':
                code = random.randint(1000, 9999)
                ClientProfile.objects.create(user=instance, verificationCode=code)
                send_mail(
                    'Profile Verification',
                    'Your Verification code is %s' % code,
                    settings.EMAIL_HOST_USER,
                    [instance.email],
                    fail_silently=True
                )
