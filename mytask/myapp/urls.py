from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EventViewSet, RSVPViewSet, ReviewViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'rsvps', RSVPViewSet, basename='rsvp')  
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('events/<int:event_pk>/rsvp/', RSVPViewSet.as_view({'post':'create'}), name='event-rsvp'),
    path('events/<int:event_pk>/rsvp/<int:pk>/', RSVPViewSet.as_view({'patch':'partial_update', 'get':'retrieve'}), name='event-rsvp-detail'),
    path('events/<int:event_pk>/reviews/', ReviewViewSet.as_view({'get':'list','post':'create'}), name='event-reviews'),
]
