import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_backend.settings')
django.setup()

from portal.models import User, Profile, Event, RSVP, Job, JobApplication, Donation, FundAllocation, Community, Message, Post

users_to_create = [
    {"username": "yaashuu", "first_name": "Yaashuu", "last_name": "Yaashii", "role": "ALUMNI", "email": "yaashuu@example.com", "password": "password123"},
    {"username": "anjana", "first_name": "Anjana", "last_name": "", "role": "STUDENT", "email": "anjana@example.com", "password": "password123"},
    {"username": "akshara", "first_name": "Akshara", "last_name": "", "role": "FACULTY", "email": "akshara@example.com", "password": "password123"},
    {"username": "akash", "first_name": "Akash", "last_name": "", "role": "VOLUNTEER", "email": "akash@example.com", "password": "password123"},
    {"username": "admin", "first_name": "Super", "last_name": "Admin", "role": "ADMIN", "email": "admin@example.com", "password": "adminpassword"},
]

roles = ['ALUMNI', 'STUDENT', 'FACULTY', 'VOLUNTEER', 'ALUMNI', 'STUDENT', 'FACULTY', 'ALUMNI', 'STUDENT', 'VOLUNTEER']
companies = ['Google', 'Microsoft', 'Amazon', 'Meta', 'Netflix', 'Tesla', 'Apple', 'Spotify', 'Twitter', 'Adobe']
departments = ['Computer Science', 'Electrical Engineering', 'Mechanical', 'Civil', 'Information Tech']

for i in range(1, 11):
    users_to_create.append({
        "username": f"user{i}",
        "first_name": f"TestName{i}",
        "last_name": "Demo",
        "role": roles[i-1],
        "email": f"user{i}@example.com",
        "password": "password123"
    })

credentials = []

for u_data in users_to_create:
    username = u_data['username']
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(
            username=username,
            password=u_data['password'],
            email=u_data['email'],
            first_name=u_data['first_name'],
            last_name=u_data['last_name'],
            role=u_data['role'],
            is_approved=True,
            faculty_verified=True
        )
        credentials.append({"username": username, "password": u_data['password'], "role": u_data['role']})
        
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.department = departments[len(credentials) % len(departments)]
        if u_data['role'] in ['ALUMNI', 'STUDENT']:
            profile.graduation_year = 2024 if u_data['role'] == 'ALUMNI' else 2026
        if u_data['role'] == 'ALUMNI':
            profile.current_company = companies[len(credentials) % len(companies)]
            profile.designation = "Engineer"
        profile.save()
    else:
        user = User.objects.get(username=username)
        user.set_password(u_data['password'])
        user.save()
        credentials.append({"username": username, "password": u_data['password'], "role": user.role})


alumni_users = list(User.objects.filter(role='ALUMNI'))
student_users = list(User.objects.filter(role='STUDENT'))
faculty_users = list(User.objects.filter(role='FACULTY'))
volunteer_users = list(User.objects.filter(role='VOLUNTEER'))
admin_user = User.objects.filter(role='ADMIN').first()

if not alumni_users:
    alumni_users = [admin_user]
if not student_users:
    student_users = [admin_user]
if not faculty_users:
    faculty_users = [admin_user]

print("--- Seeding 10 Events ---")
for i in range(10):
    event, created = Event.objects.get_or_create(
        title=f"Annual Tech Symposium {i+1}",
        defaults={
            'organizer': alumni_users[i % len(alumni_users)],
            'description': f"Join us for the {i+1}th annual tech symposium. Food and drinks provided.",
            'date': timezone.now() + timedelta(days=15+i),
            'location': f"Main Auditorium {i%3 + 1}"
        }
    )
    if created:
        for student in student_users[:3]:
            RSVP.objects.get_or_create(event=event, user=student, is_attending=True)

print("--- Seeding 10 Jobs ---")
for i in range(10):
    job, created = Job.objects.get_or_create(
        title=f"Software Engineer L{i+1}",
        defaults={
            'posted_by': alumni_users[i % len(alumni_users)],
            'company': companies[i % len(companies)],
            'location': "Remote" if i % 2 == 0 else "New York",
            'job_type': "FULL_TIME" if i % 3 != 0 else "PART_TIME",
            'description': f"We are looking for self-starters to join team {i+1}."
        }
    )
    if created:
        for student in student_users[:2]:
            JobApplication.objects.get_or_create(
                job=job,
                applicant=student,
                resume_link="https://docs.google.com/document/d/example",
                cover_letter=f"Dear Hiring Manager,\nI am writing to apply for Software Engineer L{i+1}."
            )

print("--- Seeding 10 Posts ---")
for i in range(10):
    Post.objects.get_or_create(
        content=f"Hello Network! I'm sharing some awesome industry news part {i+1}.",
        defaults={'author': alumni_users[i % len(alumni_users)]}
    )

print("--- Seeding 10 Communities ---")
for i in range(10):
    comm, created = Community.objects.get_or_create(
        name=f"Developer Group {i+1}",
        defaults={
            'description': f"A safe space for Developer Group {i+1} members.",
            'created_by': alumni_users[i % len(alumni_users)]
        }
    )
    if created:
        comm.members.add(*alumni_users[:2])
        comm.members.add(*student_users[:2])
        Message.objects.create(
            community=comm,
            sender=alumni_users[i % len(alumni_users)],
            content=f"Welcome to Developer Group {i+1}!"
        )
        Message.objects.create(
            community=comm,
            sender=student_users[0],
            content="Thanks! Glad to be here."
        )

print("--- Seeding 10 Donations ---")
for i in range(10):
    Donation.objects.get_or_create(
        donor=alumni_users[i % len(alumni_users)],
        amount=50.00 + i*10,
        purpose=f"Campus Development Fund {i+1}",
        defaults={"is_approved": True}
    )

print("--- Seeding 10 Fund Allocations ---")
if admin_user:
    for i in range(10):
        FundAllocation.objects.get_or_create(
            title=f"Scholarship #{i+1}",
            defaults={
                'description': "Supporting outstanding students.",
                'amount': 20.00 + i*10,
                'allocated_by': admin_user
            }
        )

print("\n\n#####################################################")
print("CREDENTIALS TABLE:")
print(f"{'USERNAME':<15} | {'PASSWORD':<15} | {'ROLE':<15}")
print("-" * 50)
for c in credentials:
    print(f"{c['username']:<15} | {c['password']:<15} | {c['role']:<15}")
print("#####################################################")
