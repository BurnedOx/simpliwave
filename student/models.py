from django.db import models
from django.contrib.auth.models import User
from client.models import Domain, Project, Internship
from django.conf import settings
import datetime
from django.core.cache import cache
import math

# Create your models here.

profile_status = (
    ('Verified', 'verified'),
    ('Unverified', 'unverified'),
)


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True, null=True)
    verificationCode = models.CharField(max_length=10, blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    skills = models.TextField(blank=True, null=True)
    projectHistory = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=15, choices=profile_status, default='Unverified')
    credits = models.IntegerField(default=0)

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


class NameApprove(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250, blank=True, null=True)
    status = models.CharField(max_length=20,
                              choices=(('Pending', 'pending'), ('Accepted', 'accepted'), ('Rejected', 'rejected')),
                              default='Pending'
                              )

    @property
    def old_name(self):
        return self.student.name


class Resume(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=20)
    lastName = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    linkedIn = models.URLField(blank=True, null=True)
    altLink = models.URLField(blank=True, null=True)
    objectives = models.TextField(blank=True, null=True)
    experiences = models.TextField(blank=True, null=True)
    education = models.TextField(blank=True, null=True)
    skills = models.CharField(max_length=500, blank=True, null=True)
    activities = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.firstName} {self.lastName} - {self.objectives}'


project_apply_choices = (
    ('Applied', 'applied'),
    ('Approved', 'approved'),
    ('Rejected', 'rejected')
)


class ProjectApply(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='Applied', choices=project_apply_choices)

    def __str__(self):
        return f'{self.student} - {self.project}'


internship_apply_choices = (
    ('Applied', 'applied'),
    ('Approved', 'approved'),
    ('Hired', 'hired')
)


class InternshipApply(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, default='Applied', choices=internship_apply_choices)

    def __str__(self):
        return f'{self.student} - {self.internship}'


class ProjectCompose(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f'{self.project.name} - {self.student.user.username}'


class Experience(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    projectComposed = models.ManyToManyField(Project, blank=True)

    def __str__(self):
        return f'{self.student} - {self.domain}'

    @property
    def countOfProjects(self):
        count = len(self.projectComposed.all())
        return count

    @property
    def label(self):
        return math.ceil(self.countOfProjects/5)


class Ranking(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    rank = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.student} - {self.domain}'

    class Meta:
        ordering = ('rank',)


class CodeSharing(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    code = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.id
