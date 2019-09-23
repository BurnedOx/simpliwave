from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import EmployeeProfile


@receiver(m2m_changed)
def driver_added(action, instance, pk_set, model, **kwargs):
    if model == Group:
        if action == 'post_add':
            group_name = Group.objects.get(id=next(iter(pk_set))).name
            if group_name == 'employee':
                EmployeeProfile.objects.create(user=instance, employeeId=instance.username)
