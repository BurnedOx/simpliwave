from django.db import models
from django.contrib.auth.models import User
from client.models import Project, ClientProfile
from student.models import ProjectCompose, StudentProfile
from django.conf import settings
import datetime
from chat.models import Message
from django.core.cache import cache

# Create your models here.


class EmployeeId(models.Model):
    empId = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.empId


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.TextField(blank=True, null=True)
    contact = models.CharField(max_length=20, blank=True, null=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    skills = models.TextField(blank=True, null=True)
    projectHistory = models.TextField(blank=True, null=True)
    employeeId = models.OneToOneField(EmployeeId, on_delete=models.CASCADE, null=True, blank=True)

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


progress_choices = (
    ('Backlog', 'backlog'),
    ('In-Progress', 'in_progress'),
    ('Ready for Review', 'ready_for_review'),
    ('Completed', 'completed'),
)


class Milestone(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    topic = models.CharField(max_length=250)
    progress = models.CharField(max_length=100, choices=progress_choices, default='In-Progress')

    def __str__(self):
        return f'{self.topic} - {self.progress}'


class Result(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    role = models.CharField(max_length=250, blank=True, null=True)
    creditPercentage = models.IntegerField(default=0)

    @property
    def name(self):
        return self.student.user.username

    @property
    def domain(self):
        return self.project.domain

    def __str__(self):
        return self.name


project_status_choices = (
    ('In-Progress', 'in_progress'),
    ('Completed', 'completed'),
)


class ProjectManagement(models.Model):
    name = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE)
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    student = models.ManyToManyField(StudentProfile, blank=True)
    messages = models.ManyToManyField(Message, blank=True)
    milestones = models.ManyToManyField(Milestone, blank=True)
    results = models.ManyToManyField(Result, blank=True)
    status = models.CharField(max_length=50, choices=project_status_choices, default='In-Progress')

    def __str__(self):
        return self.name


class FileManagement(models.Model):
    employee = models.ForeignKey(EmployeeProfile, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    work = models.ManyToManyField(ProjectCompose, blank=True)
    file = models.FileField(blank=True, null=True)

    def __str__(self):
        return self.project


class Certificate(models.Model):
    work = models.ForeignKey(ProjectCompose, on_delete=models.CASCADE)
    code = models.CharField(max_length=250)
    date = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=250)

    def __str__(self):
        return self.code
