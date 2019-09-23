from django.views.generic import View
from employee.models import Certificate
from client.models import ProjectInvoice
from .utils import render_to_pdf


class GenerateCertificate(View):
    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        certificate = Certificate.objects.get(code=code)
        date = certificate.date

        context = {
            'certificate_id': code,
            'student_name': certificate.work.student.name,
            'project': certificate.work.project.name,
            'client': certificate.work.project.client.name,
            'domain': certificate.work.project.domain.name,
            'role': certificate.role,
            'date': '%s %s, %s' % (months[date.month - 1], date.day, date.year),
        }

        pdf = render_to_pdf('certificate/certificate.html', context)
        return pdf


class GenerateProjectInvoice(View):
    def get(self, request, *args, **kwargs):
        invoice_id = kwargs['invoice_id']
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        invoice = ProjectInvoice.objects.get(id=invoice_id)
        date = invoice.date

        cgst = 9
        sgst = 9
        cgst_amount = invoice.project.amount*(cgst/100)
        sgst_amount = invoice.project.amount*(sgst/100)
        short_date = '%s/%s/%s' % (date.day, date.month, date.year)
        long_date = '%s %s, %s' % (months[date.month-1], date.day, date.year)

        context = {
            'invoice_id': invoice_id,
            'client': invoice.project.client.name,
            'domain': invoice.project.domain.name,
            'package': invoice.project.package.name,
            'amount': invoice.project.amount,
            'cgst': cgst,
            'cgst_amount': cgst_amount,
            'sgst': sgst,
            'sgst_amount': sgst_amount,
            'total_price': invoice.project.amount + cgst_amount + sgst_amount,
            'short_date': short_date,
            'long_date': long_date
        }

        pdf = render_to_pdf('invoice/project_invoice.html', context)
        return pdf
