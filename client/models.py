from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import datetime
from django.core.cache import cache

# Create your models here.

profile_status = (
    ('Verified', 'verified'),
    ('Unverified', 'unverified'),
)


class ClientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True, null=True)
    verificationCode = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    status = models.CharField(max_length=15, choices=profile_status, default='Unverified')

    def __str__(self):
        return self.user.username

    @property
    def name(self):
        name = self.user.first_name
        if self.user.last_name != '':
            name += ' ' + self.user.last_name
        return name

    @property
    def email(self):
        return self.user.email

    def last_seen(self):
        return cache.get('last_seen_%s' % self.user.username)

    @property
    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            if now > (self.last_seen() + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)):
                return False
            else:
                return True
        else:
            return False


class Domain(models.Model):
    name = models.CharField(max_length=50)
    base_price = models.FloatField()

    def __str__(self):
        return self.name


package_choices = (
    ('Gold', 'gold'),
    ('Silver', 'silver'),
    ('Bronze', 'bronze')
)


class Package(models.Model):
    name = models.CharField(choices=package_choices, max_length=10)
    price = models.FloatField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


status_choices = (
    ('Approved', 'approved'),
    ('Pending', 'pending'),
    ('Closed', 'closed')
)


class Project(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    applyDueDate = models.DateField(auto_now=True, blank=True, null=True)
    weeks = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    detailsFile = models.FileField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')

    def __str__(self):
        return self.name

    @property
    def amount(self):
        return self.domain.base_price + self.package.price


stipend_type_choices = (
    ('Week', 'week'),
    ('Month', 'month')
)


class Internship(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    domain = models.CharField(max_length=200)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    stipend = models.IntegerField()
    stipend_type = models.CharField(choices=stipend_type_choices, max_length=10)
    applyDueDate = models.DateField()
    about = models.TextField(blank=True, null=True)
    skillsRequired = models.CharField(max_length=200, blank=True, null=True)
    responsibility = models.CharField(max_length=200, blank=True, null=True)
    numberOfPeople = models.IntegerField(blank=True, null=True)
    numberOfMonths = models.IntegerField()
    status = models.CharField(max_length=10, choices=status_choices, default='Pending')

    def __str__(self):
        return self.name


class ProjectInvoice(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
