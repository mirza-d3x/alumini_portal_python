from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('ALUMNI', 'Alumni'),
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty'),
        ('VOLUNTEER', 'Volunteer Student'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    is_approved = models.BooleanField(default=False)
    faculty_verified = models.BooleanField(default=False)
    faculty_verifier = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_users')
    approved_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_users')
    approved_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Auto-approve Admin and assign special permissions if needed
        if self.role == 'ADMIN':
            self.is_approved = True
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    reg_no = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    graduation_year = models.IntegerField(blank=True, null=True)
    degree = models.CharField(max_length=100, blank=True, null=True)
    current_company = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.FileField(upload_to='profile_pictures/', blank=True, null=True)
    id_card = models.FileField(upload_to='id_cards/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    poster_image = models.FileField(upload_to='post_posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Job(models.Model):
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)
    job_type = models.CharField(max_length=50, default='FULL_TIME')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume_link = models.URLField(max_length=500, blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)

class Event(models.Model):
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    poster_image = models.FileField(upload_to='event_posters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RSVP(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_rsvps')
    is_attending = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'user')

class Donation(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=200, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class FundAllocation(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    allocated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fund_allocations')
    allocated_at = models.DateTimeField(auto_now_add=True)

class Community(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_communities')
    members = models.ManyToManyField(User, related_name='joined_communities', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sent_at']
