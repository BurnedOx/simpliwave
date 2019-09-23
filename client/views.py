from rest_framework import viewsets, mixins, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .utils import unique_name
from simpliwave.utils import get_roll, update_email, password_update
from employee.models import ProjectManagement, FileManagement, EmployeeProfile, Milestone
import json


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups=get_roll('client'))
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
            user.groups.add(get_roll('client'))
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
            profile = ClientProfile.objects.get(user=user)
            serializer = self.serializers_dict[update](data=request.data)
            if serializer.is_valid():
                if update == 'email':
                    update_email(user, profile, serializer.initial_data['email'])
                elif update == 'password':
                    password_update(user,
                                    serializer.initial_data['oldPassword'],
                                    serializer.initial_data['newPassword'])
                elif update == 'name':
                    user.first_name = serializer.initial_data['first_name']
                    user.last_name = serializer.initial_data['last_name']
                    user.save()
                return Response(f'{update} updated', status=status.HTTP_202_ACCEPTED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise exceptions.ValidationError('Provide "userId" in query_params')


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = ClientProfile.objects.all()
        user_id = self.request.query_params.get('userid', None)
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
            profile = ClientProfile.objects.get(user=request.user)
            if profile.verificationCode == serializer.initial_data['code']:
                profile.status = 'Verified'
                profile.verificationCode = None
                profile.save()
                return Response('Verified', status=status.HTTP_200_OK)
            return Response('Unverified', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DomainView(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class PackageView(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class ProjectView(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Project.objects.all()
        username = self.request.query_params.get('username', None)
        status = self.request.query_params.get('status', None)
        name = self.request.query_params.get('name',None)
        if username is not None:
            queryset = queryset.filter(client__user__username=username)
        if status is not None:
            queryset = queryset.filter(status=status)
        if name is not None:
            queryset = queryset.filter(name=name)
        return queryset


class ProjectStatusView(generics.RetrieveUpdateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectStatusSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        project = self.get_object()
        if request.data['status'] == 'Approved':
            ProjectManagement.objects.get_or_create(
                name=unique_name(project.name, ProjectManagement),
                project=project,
                client=project.client,
                employee=EmployeeProfile.objects.get(user=request.user)
            )
            FileManagement.objects.get_or_create(
                employee=EmployeeProfile.objects.get(user=request.user),
                project=project
            )
        project.status = request.data['status']
        project.save()
        return Response(request.data, status=status.HTTP_202_ACCEPTED)


class ProjectProgressView(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = Project.objects.get(id=project_id)
        progress = {
            'backlogs': len(Milestone.objects.filter(project=project, progress='Backlog')),
            'inProgress': len(Milestone.objects.filter(project=project, progress='In-Progress')),
            'readyForReview': len(Milestone.objects.filter(project=project, progress='Ready for Review')),
            'completed': len(Milestone.objects.filter(project=project, progress='Completed'))
        }
        return Response(json.loads(json.dumps(progress)))


class InternshipView(viewsets.ModelViewSet):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]


class ProjectInvoiceView(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    queryset = ProjectInvoice.objects.all()
    serializer_class = ProjectInvoiceSerializer
