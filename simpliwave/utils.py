from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.auth.models import Group, User
from django.conf import settings
from django.core.mail import send_mail
from rest_framework import exceptions
import random


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def get_roll(grp_name):
    try:
        roll = Group.objects.get_or_create(name=grp_name)[0]
        return roll
    except:
        return None


def update_email(user, profile, email):
    if User.objects.filter(email__iexact=email):
        raise exceptions.ValidationError('Email address already exists')
    else:
        code = random.randint(1000, 9999)
        user.username = email
        user.email = email
        user.save()
        profile.verificationCode = code
        profile.status = 'Unverified'
        profile.save()
        send_mail(
            'Profile Verification',
            'Your Verification code is %s' % code,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=True
        )


def password_update(user, old, new):
    if not user.check_password(old):
        raise exceptions.ValidationError("Your old password didn't match you can try forgot password")
    else:
        user.set_password(new)
        user.save()
