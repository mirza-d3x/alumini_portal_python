import datetime
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Profile
from .serializers import UserSerializer
from .permissions import IsAdminUserOrVolunteer, IsAdminOrFaculty

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        print(f"DEBUG ACTION: {self.action}")
        if self.action in ['create', 'register', 'check_availability', 'check-availability']:
            # Anyone can register
            return [permissions.AllowAny()]
        elif self.action in ['approve', 'block']:
            # Faculty can approve students/alumni, Admin/Volunteers can do anything
            return [IsAdminOrFaculty()]
        elif self.action in ['change_role', 'destroy']:
            # Only Admins (and delegated Volunteers) can change roles or delete users
            return [IsAdminUserOrVolunteer()]
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['get'], url_path='check-availability')
    def check_availability(self, request):
        username = request.query_params.get('username')
        email = request.query_params.get('email')
        response_data = {}

        if username:
            response_data['username_taken'] = User.objects.filter(username=username).exists()
        if email:
            response_data['email_taken'] = User.objects.filter(email=email).exists()

        return Response(response_data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny], parser_classes=[MultiPartParser, FormParser, JSONParser])
    def register(self, request):
        data = request.data.copy()
        
        # Handle nested profile data sent in multipart request
        profile_data = {}
        # The fields for ProfileSerializer now include 'id_card'
        profile_fields = ['bio', 'graduation_year', 'degree', 'current_company', 'id_card', 'department', 'reg_no']
        for key in profile_fields:
            if key in data:
                # For file fields like 'id_card', request.FILES will contain it.
                # For other fields, data.getlist(key) handles multiple values for the same key (e.g., from form data)
                # and data.get(key) handles single values (e.g., from JSON data).
                if key == 'id_card':
                    if request.FILES.get(key):
                        profile_data[key] = request.FILES.get(key)
                else:
                    profile_data[key] = data.pop(key)[0] if isinstance(data.getlist(key), list) and data.getlist(key) else data.get(key)
                    
        # Remove file items before sending to UserSerializer to prevent unpicklable deepcopy error
        if 'id_card' in data:
            data.pop('id_card', None)
        if 'profile_picture' in data:
            data.pop('profile_picture', None)
        
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Add profile id_card if provided
            id_card = request.FILES.get('id_card')
            if id_card or profile_data:
                profile = user.profile
                for k, v in profile_data.items():
                    setattr(profile, k, v)
                if id_card:
                    profile.id_card = id_card
                profile.save()
                
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        user_to_approve = self.get_object()
        approver = request.user
        
        if user_to_approve.is_approved:
            return Response({'error': 'User is already approved.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if approver.role == 'FACULTY':
            if user_to_approve.role not in ['STUDENT', 'ALUMNI']:
                return Response({'error': 'Faculty can only verify Students and Alumni.'}, status=status.HTTP_403_FORBIDDEN)
            user_to_approve.faculty_verified = True
            user_to_approve.faculty_verifier = approver

        # Direct approval
        user_to_approve.is_approved = True
        user_to_approve.approved_by = approver
        user_to_approve.approved_at = timezone.now()
        user_to_approve.save()
        
        # Simulated welcome email
        print(f"[EMAIL TO USER] Subject: Welcome to Alumni Portal! To: {user_to_approve.email}. Your account has been approved and activated.")
        
        return Response({'status': 'User approved successfully.', 'approved_by': approver.username})

    @action(detail=True, methods=['post'])
    def change_role(self, request, pk=None):
        user_to_update = self.get_object()
        new_role = request.data.get('role')
        valid_roles = dict(User.ROLE_CHOICES).keys()
        
        if new_role not in valid_roles:
            return Response({'error': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_to_update.role = new_role
        user_to_update.save()
        return Response({'status': f'Role changed to {new_role}.'})

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        user_to_block = self.get_object()
        user_to_block.is_active = False
        user_to_block.save()
        return Response({'status': 'User blocked successfully.'})

    @action(detail=True, methods=['post'])
    def unblock(self, request, pk=None):
        user_to_unblock = self.get_object()
        user_to_unblock.is_active = True
        user_to_unblock.save()
        return Response({'status': 'User unblocked successfully.'})

from .models import Post, Job, Profile
from .serializers import PostSerializer, JobSerializer, ProfileSerializer
from .permissions import IsAuthorOrAdminOrVolunteer

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    # Only expose active/approved users' profiles
    queryset = Profile.objects.filter(user__is_active=True, user__is_approved=True)
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Exclude admin profiles from directory
        return self.queryset.exclude(user__role='ADMIN').select_related('user')

from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdminOrVolunteer]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        poster = self.request.FILES.get('poster_image')
        serializer.save(author=self.request.user, **({
            'poster_image': poster} if poster else {}))

class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdminOrVolunteer]

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)

from .models import JobApplication, Event, RSVP
from .serializers import JobApplicationSerializer, EventSerializer, RSVPSerializer

class JobApplicationViewSet(viewsets.ModelViewSet):
    # Only Admin, Volunteer or the poster of the job can see all applications
    # Applicants can only see their own applications
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['ADMIN', 'VOLUNTEER']:
            return JobApplication.objects.all().order_by('-applied_at')
        # They can see apps for jobs they posted or apps they submitted
        return JobApplication.objects.filter(models.Q(job__posted_by=user) | models.Q(applicant=user)).order_by('-applied_at')

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrAdminOrVolunteer]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        poster = self.request.FILES.get('poster_image')
        serializer.save(organizer=self.request.user, **({
            'poster_image': poster} if poster else {}))

class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
         user = self.request.user
         if user.role in ['ADMIN', 'VOLUNTEER']:
             return RSVP.objects.all()
         return RSVP.objects.filter(user=user)

    def perform_create(self, serializer):
        # Prevent duplicate RSVPs which would throw IntegrityError
        event = serializer.validated_data.get('event')
        rsvp, created = RSVP.objects.get_or_create(
            event=event, user=self.request.user,
            defaults={'is_attending': serializer.validated_data.get('is_attending', True)}
        )
        if not created:
             rsvp.is_attending = serializer.validated_data.get('is_attending', True)
             rsvp.save()

from rest_framework.views import APIView

class DashboardStatsView(APIView):
    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        from .models import Community # Avoid potential NameError if not imported above
        total_alumni = User.objects.filter(role='ALUMNI', is_approved=True).count()
        total_students = User.objects.filter(role='STUDENT').count()
        active_jobs = Job.objects.count()
        total_communities = Community.objects.count()
        total_events = Event.objects.count()
        total_notices = Post.objects.count()
        return Response({
            'total_alumni': total_alumni,
            'total_students': total_students,
            'active_jobs': active_jobs,
            'total_communities': total_communities,
            'total_events': total_events,
            'total_notices': total_notices
        })

class PendingRequestsView(APIView):
    permission_classes = [IsAdminOrFaculty]

    def get(self, request):
        # Admins and Volunteers see all pending users
        if request.user.role in ['ADMIN', 'VOLUNTEER']:
            pending_users = User.objects.filter(is_approved=False).exclude(role='ADMIN')
            pending_donations = Donation.objects.filter(is_approved=False)
        else: # Faculty can only see pending Students and Alumni
            pending_users = User.objects.filter(is_approved=False, role__in=['STUDENT', 'ALUMNI'])
            pending_donations = Donation.objects.none()
        
        user_serializer = UserSerializer(pending_users, many=True)
        donation_serializer = DonationSerializer(pending_donations, many=True)
        return Response({
            'pending_users': user_serializer.data,
            'pending_donations': donation_serializer.data
        })

from .models import Donation, FundAllocation
from .serializers import DonationSerializer, FundAllocationSerializer

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all().order_by('-created_at')
    serializer_class = DonationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(donor=self.request.user)
        
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUserOrVolunteer])
    def approve(self, request, pk=None):
        donation = self.get_object()
        if donation.is_approved:
            return Response({'error': 'Donation already approved.'}, status=status.HTTP_400_BAD_REQUEST)
        donation.is_approved = True
        donation.save()
        return Response({'status': 'Donation approved.'})

class FundAllocationViewSet(viewsets.ModelViewSet):
    queryset = FundAllocation.objects.all().order_by('-allocated_at')
    serializer_class = FundAllocationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        # Only admin/volunteers can create/update/delete fund allocations. Anyone can view.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUserOrVolunteer()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(allocated_by=self.request.user)

from .models import Community, Message
from .serializers import CommunitySerializer, MessageSerializer

class CommunityViewSet(viewsets.ModelViewSet):
    queryset = Community.objects.all().order_by('-created_at')
    serializer_class = CommunitySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        community = serializer.save(created_by=self.request.user)
        community.members.add(self.request.user)

    @action(detail=True, methods=['post'], url_path='join')
    def join(self, request, pk=None):
        community = self.get_object()
        if community.members.filter(id=request.user.id).exists():
            community.members.remove(request.user)
            return Response({'status': 'left'})
        else:
            community.members.add(request.user)
            return Response({'status': 'joined'})

    @action(detail=True, methods=['get', 'post'], url_path='messages')
    def messages(self, request, pk=None):
        community = self.get_object()
        if request.method == 'GET':
            messages = community.messages.all()
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = MessageSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(sender=request.user, community=community)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
