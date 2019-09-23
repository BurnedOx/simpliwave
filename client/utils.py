from .models import ProjectInvoice, Project
import random


def generateId(model):
    new_id = random.randint(1, 100000)
    if model.objects.filter(id__iexact=new_id):
        generateId(model)
    else:
        return new_id


def create_invoice(projectId):
    project = Project.objects.get(id=projectId)
    invoice_id = generateId(ProjectInvoice)
    ProjectInvoice.objects.get_or_create(id=invoice_id, project=project)


def unique_name(name, instance, count=0):
    name = name.replace(' ', '')
    if instance.objects.filter(name__iexact=name):
        count = count+1
        name = f'{name}_{count}'
        unique_name(name, instance, count)
    return f'{name}_{count}'
