from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, ProfileViewSet, PostViewSet, JobViewSet, JobApplicationViewSet, 
    EventViewSet, RSVPViewSet, DonationViewSet, FundAllocationViewSet, 
    CommunityViewSet, DashboardStatsView, PendingRequestsView
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'posts', PostViewSet)
router.register(r'jobs', JobViewSet)
router.register(r'job-applications', JobApplicationViewSet, basename='jobapplication')
router.register(r'events', EventViewSet)
router.register(r'rsvps', RSVPViewSet, basename='rsvp')
router.register(r'donations', DonationViewSet, basename='donation')
router.register(r'fund-allocations', FundAllocationViewSet, basename='fundallocation')
router.register(r'communities', CommunityViewSet, basename='community')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('pending-requests/', PendingRequestsView.as_view(), name='pending-requests'),
]
