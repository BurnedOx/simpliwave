from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from simpliwave.utils import get_roll, update_email, password_update
from .serializers import *
from employee.models import ProjectManagement, FileManagement


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups=get_roll('student'))
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if User.objects.filter(email__iexact=serializer.initial_data['email']):
            raise exceptions.ValidationError('Email address already exists')
        if serializer.is_valid():
            user = User.objects.create_user(username=serializer.initial_data['email'],
                                            email=serializer.initial_data['email'],
                                            password=serializer.initial_data['password'])
            user.first_name = serializer.initial_data['first_name']
            user.last_name = serializer.initial_data['last_name']
            user.save()
            user.groups.add(get_roll('student'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUser(generics.GenericAPIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializers_dict = {
        'email': EmailUpdateSerializer,
        'password': PasswordUpdateSerializer,
        'name': NameUpdateSerializer,
    }

    def get_serializer_class(self):
        update = self.request.query_params.get('update', None)
        if update is not None:
            try:
                serializer_class = self.serializers_dict[update]
            except:
                raise exceptions.ValidationError('Update should be email or password or name')
        else:
            raise exceptions.ValidationError('Must provide "update" in query_params')
        return serializer_class

    def post(self, request):
        user_id = request.query_params.get('userId', None)
        update = request.query_params.get('update', None)
        if user_id is not None:
            user = User.objects.get(id=user_id)
            profile = StudentProfile.objects.get(user=user)
            serializer = self.serializers_dict[update](data=request.data)
            if serializer.is_valid():
                if update == 'email':
                    update_email(user, profile, serializer.initial_data['email'])
                elif update == 'password':
                    password_update(user,
                                    serializer.initial_data['oldPassword'],
                                    serializer.initial_data['newPassword'])
                elif update == 'name':
                    record = NameApprove.objects.get_or_create(student=profile)[0]
                    record.first_name = serializer.initial_data['first_name']
                    record.last_name = serializer.initial_data['last_name']
                    record.save()
                return Response(f'{update} updated', status=status.HTTP_202_ACCEPTED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.ValidationError('Provide "userId" in query_params')


class NameApproveView(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication, BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAdminUser]
    queryset = NameApprove.objects.all()
    serializer_class = NameApproveSerializer

    def update(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.serializer_class(queryset, request.data)
        if serializer.is_valid():
            if serializer.initial_data['status'] == 'Accepted':
                user = queryset.student.user
                user.first_name = queryset.first_name
                user.last_name = queryset.last_name
                user.save()
                queryset.delete()
            elif serializer.initial_data['status'] == 'Rejected':
                queryset.delete()
            return Response(serializer.initial_data['status'], status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = StudentProfile.objects.all()
        user_id = self.request.query_params.get('userId', None)
        if user_id is not None:
            queryset = queryset.filter(user=User.objects.get(pk=user_id))
        return queryset


class VerifyView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = VerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            profile = StudentProfile.objects.get(user=request.user)
            if profile.verificationCode == serializer.initial_data['code']:
                profile.status = 'Verified'
                profile.verificationCode = None
                profile.save()
                return Response('Verified', status=status.HTTP_200_OK)
            return Response('Unverified', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResumeView(viewsets.ModelViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer


class ExperienceView(viewsets.ModelViewSet):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer


class ProjectApplyView(viewsets.ModelViewSet):
    serializer_class = ProjectApplySerializer
    
    def get_queryset(self):
        queryset = ProjectApply.objects.all()
        prjctid = self.request.query_params.get('prjctid', None)
        if prjctid is not None:
            queryset = queryset.filter(project=prjctid)
        return queryset


class ProjectApplyStatusView(generics.RetrieveUpdateAPIView):
    queryset = ProjectApply.objects.all()
    serializer_class = ProjectApplyStatusSerializer

    def update(self, request, *args, **kwargs):
        apply = self.get_object()
        if request.data['status'] == 'Approved':
            ProjectCompose.objects.get_or_create(
                student=apply.student,
                project=apply.project
            )
            project_comp = ProjectCompose.objects.get(project=apply.project, student=apply.student)
            project_mng = ProjectManagement.objects.get(project=apply.project)
            file_mng = FileManagement.objects.get(project=apply.project)
            project_mng.student.add(apply.student)
            file_mng.work.add(project_comp)
        apply.status = request.data['status']
        apply.save()
        return Response(request.data, status=status.HTTP_202_ACCEPTED)


class InternshipApplyView(viewsets.ModelViewSet):
    queryset = InternshipApply.objects.all()
    serializer_class = InternshipApplySerializer


class ProjectComposeView(viewsets.ModelViewSet):
    serializer_class = ProjectComposeSerializer

    def get_queryset(self):
        queryset = ProjectCompose.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(student__user__username=username)
        return queryset


class RankingView(viewsets.ModelViewSet):
    queryset = Ranking.objects.all()
    serializer_class = RankingSerializer


class CodeSharingView(viewsets.ModelViewSet):
    queryset = CodeSharing.objects.all()
    serializer_class = CodeSharingSerializer
