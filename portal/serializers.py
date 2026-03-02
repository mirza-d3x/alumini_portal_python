from rest_framework import serializers
from .models import User, Profile, Post, Job, JobApplication, Event, RSVP, Donation, FundAllocation, Community, Message
class ProfileSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField()
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)

    class Meta:
        model = Profile
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'bio', 'reg_no', 'department', 'graduation_year', 'degree', 'current_company', 'id_card', 'profile_picture', 'profile_picture_url']

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_approved', 'faculty_verified', 'approved_by_username', 'approved_at', 'profile', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        # Default to STUDENT role and not approved
        if 'role' not in validated_data:
             user.role = 'STUDENT'
        user.is_approved = False
        user.save()
        if profile_data:
            Profile.objects.create(user=user, **profile_data)
        else:
            Profile.objects.create(user=user)
        return user

class PostSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    poster_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'author', 'author_username', 'content', 'poster_image_url', 'created_at']
        read_only_fields = ['author']
        
    def get_poster_image_url(self, obj):
        if obj.poster_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.poster_image.url)
        return None

class JobSerializer(serializers.ModelSerializer):
    posted_by_username = serializers.CharField(source='posted_by.username', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'posted_by', 'posted_by_username', 'title', 'description', 'created_at']
        read_only_fields = ['posted_by']

class JobApplicationSerializer(serializers.ModelSerializer):
    applicant_username = serializers.CharField(source='applicant.username', read_only=True)

    class Meta:
        model = JobApplication
        fields = ['id', 'job', 'applicant', 'applicant_username', 'resume_link', 'cover_letter', 'applied_at']
        read_only_fields = ['applicant']

class RSVPSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'event', 'user', 'user_name', 'is_attending', 'created_at']
        read_only_fields = ['user']

class EventSerializer(serializers.ModelSerializer):
    organizer_username = serializers.CharField(source='organizer.username', read_only=True)
    rsvps = RSVPSerializer(many=True, read_only=True)
    poster_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'organizer', 'organizer_username', 'title', 'description', 'date', 'location', 'poster_image_url', 'created_at', 'rsvps']
        read_only_fields = ['organizer']
        
    def get_poster_image_url(self, obj):
        if obj.poster_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.poster_image.url)
        return None

class DonationSerializer(serializers.ModelSerializer):
    donor_username = serializers.CharField(source='donor.username', read_only=True)

    class Meta:
        model = Donation
        fields = ['id', 'donor', 'donor_username', 'amount', 'purpose', 'is_approved', 'created_at']
        read_only_fields = ['donor']

class FundAllocationSerializer(serializers.ModelSerializer):
    allocated_by_username = serializers.CharField(source='allocated_by.username', read_only=True)

    class Meta:
        model = FundAllocation
        fields = ['id', 'title', 'description', 'amount', 'allocated_by', 'allocated_by_username', 'allocated_at']
        read_only_fields = ['allocated_by']

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'community', 'sender', 'sender_username', 'content', 'sent_at']
        read_only_fields = ['sender']

class CommunitySerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    message_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_is_member(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.members.filter(id=request.user.id).exists()
        return False

    def get_member_count(self, obj):
        return obj.members.count()

    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'created_by', 'created_by_username', 'message_count', 'is_member', 'member_count', 'created_at']
        read_only_fields = ['created_by']
