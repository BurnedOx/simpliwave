from rest_framework import viewsets, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from simpliwave.utils import get_roll
from client.utils import create_invoice
from .utils import create_certificate, share_credit
from .serializers import *
from student.models import Experience, Ranking
from student.utils import ranking


class UserView(viewsets.ModelViewSet):
    queryset = User.objects.filter(groups=get_roll('employee'))
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(username=serializer.initial_data['username'],
                                            password=serializer.initial_data['password'])
            user.groups.add(get_roll('employee'))
            EmployeeProfile.objects.create(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.serializer_class(queryset, data=request.data)
        if serializer.is_valid():
            serializer.save()
            queryset.set_password(serializer.initial_data['password'])
            queryset.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeIdView(viewsets.ModelViewSet):
    queryset = EmployeeId.objects.all()
    serializer_class = EmployeeIdSerializer

    def create(self, request, *args, **kwargs):
        serializer = EmployeeIdSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = User.objects.create_user(username=serializer.initial_data['empId'],
                                            password=serializer.initial_data['empId'])
            user.groups.add(get_roll('employee'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        queryset = EmployeeProfile.objects.all()
        user_id = self.request.query_params.get('userid', None)
        if user_id is not None:
            queryset = queryset.filter(user=User.objects.get(pk=user_id))
        return queryset


class ProjectManagementView(viewsets.ModelViewSet):
    serializer_class = ProjectManagementSerializer

    def get_queryset(self):
        queryset = ProjectManagement.objects.all()
        studentId=self.request.query_params.get('studentid',None)
        projectId= self.request.query_params.get('projId',None)
        if projectId is not None:
            queryset = queryset.filter(project = projectId)
        if studentId is not None:
            queryset = queryset.filter(student = studentId)
        return queryset

    def update(self, request, *args, **kwargs):
        queryset = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.update(queryset, serializer.validated_data)
            if serializer.initial_data['status'] == 'Completed':
                create_invoice(queryset.project.id)
                for student in queryset.student.all():
                    result = Result.objects.create(student=student, project=queryset.project)
                    queryset.results.add(result)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MilestoneListView(generics.ListCreateAPIView):
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        queryset = ProjectManagement.objects.get(pk=self.kwargs['groupId']).milestones.all()
        prog = self.request.query_params.get('prog', None)
        if prog is not None:
            queryset = queryset.filter(progress=prog)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            project_mng = ProjectManagement.objects.get(pk=kwargs['groupId'])
            project = project_mng.project
            serializer.save(project=project)
            milestone = Milestone.objects.filter(project=project).latest('id')
            project_mng.milestones.add(milestone)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MilestoneRetrieveView(generics.RetrieveUpdateAPIView):
    serializer_class = MilestoneSerializer
    queryset = Milestone.objects.all()

    def get_object(self):
        instance = self.queryset.get(id=self.kwargs['mlstId'])
        return instance


class ResultsListView(generics.ListAPIView):
    serializer_class = ResultSerializer

    def get_queryset(self):
        queryset = ProjectManagement.objects.get(pk=self.kwargs['Id']).results.all()
        return queryset


class ResultsUpdateView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResultSerializer
    queryset = Result.objects.all()

    def get_object(self):
        instance = self.queryset.get(id=self.kwargs['rsltId'])
        return instance

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            exp = Experience.objects.get_or_create(student=instance.student, domain=instance.domain)[0]
            exp.projectComposed.add(instance.project)
            exp.points = exp.points + int(serializer.initial_data['points'])
            exp.save()
            rank = Ranking.objects.get_or_create(student=instance.student, domain=instance.domain)[0]
            ranking(rank)
            create_certificate(instance, serializer.initial_data['role'])
            share_credit(
                percentage=int(serializer.initial_data['creditPercentage']),
                project=instance.project,
                student=instance.student
            )
            instance.delete()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileManagementView(viewsets.ModelViewSet):
    queryset = FileManagement.objects.all()
    serializer_class = FileManagementSerializer


class CertificateView(viewsets.ModelViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer
