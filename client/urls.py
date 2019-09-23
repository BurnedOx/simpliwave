from rest_framework import routers
from django.urls import path
from .views import *

route = routers.DefaultRouter()

route.register(r'user', UserView, base_name='client_user')
route.register(r'profile', ProfileView, base_name='client_profile')
route.register(r'domain', DomainView, base_name='domain')
route.register(r'package', PackageView, base_name='package')
route.register(r'project', ProjectView, base_name='project')
route.register(r'internship', InternshipView, base_name='internship')
route.register(r'p-invoice', ProjectInvoiceView, base_name='p-invoice')

urlpatterns = [
    path('verify/', VerifyView.as_view()),
    path('project/<pk>/status', ProjectStatusView.as_view()),
    path('project/<project_id>/progress', ProjectProgressView.as_view()),
    path('user-update/', UpdateUser.as_view()),
]

urlpatterns += route.urls
