from .models import Certificate, ProjectCompose


def create_certificate(result, role):
    work = ProjectCompose.objects.get(student=result.student, project=result.project)

    try:
        Certificate.objects.get(work=work)
    except Certificate.DoesNotExist:
        domain_code = ''
        for string in work.project.domain.name.split(' '):
            domain_code += string[0]

        try:
            unique_id = Certificate.objects.latest("id").id + 1
        except Certificate.DoesNotExist:
            unique_id = 1

        certificate_id = f'SW-{domain_code}-{unique_id}'

        Certificate.objects.create(id=unique_id, work=work, code=certificate_id, role=role)


def share_credit(percentage, project, student):
    sharable_credit = project.amount / 2
    credit = (sharable_credit * (percentage / 100))

    student.credit = student.credit + credit
    student.save()
