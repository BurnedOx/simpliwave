from rest_framework import routers
from django.urls import path
from .views import *

route = routers.DefaultRouter()

route.register(r'user', UserView, base_name='student_user')
route.register(r'name-approve', NameApproveView, base_name='name-approve')
route.register(r'profile', ProfileView, base_name='student_profile')
route.register(r'resume', ResumeView, base_name='resume')
route.register(r'experience', ExperienceView, base_name='experience')
route.register(r'project-apply', ProjectApplyView, base_name='project-apply')
route.register(r'internship-apply', InternshipApplyView, base_name='internship-apply')
route.register(r'project-compose', ProjectComposeView, base_name='project-compose')
route.register(r'ranking', RankingView, base_name='ranking')
route.register(r'code-sharing', CodeSharingView, base_name='code=sharing')

urlpatterns = [
    path('verify/', VerifyView.as_view()),
    path('project-apply/<pk>/status/', ProjectApplyStatusView.as_view()),
    path('user-update/', UpdateUser.as_view()),
]

urlpatterns += route.urls
