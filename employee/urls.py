from rest_framework import routers
from django.urls import path
from .views import *

route = routers.DefaultRouter()

route.register(r'user', UserView, base_name='employee_user')
route.register(r'emp-id', EmployeeIdView, base_name='employee_id')
route.register(r'profile', ProfileView, base_name='employee_profile')
route.register(r'project-manage', ProjectManagementView, base_name='project-manage')
route.register(r'file-manage', FileManagementView, base_name='file-manage')
route.register(r'certificate', CertificateView, base_name='certificate')

urlpatterns = [
    path('project-manage/<groupId>/milestone/', MilestoneListView.as_view()),
    path('project-manage/<groupId>/milestone/<mlstId>/', MilestoneRetrieveView.as_view()),
    path('project-manage/<Id>/results/', ResultsListView.as_view()),
    path('project-manage/<Id>/results/<rsltId>/', ResultsUpdateView.as_view()),
]

urlpatterns += route.urls
