from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .serializers import EventSerializer, RSVPSerializer, ReviewSerializer
from .permissions import IsOrganizerOrReadOnly, IsInvitedOrPublic
from .pagination import CustomPagination
from .models import Event, RSVP, Review
# Create your views here.

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title', 'location', 'organizer__username']
    ordering_fields = ['start_time', 'created_at']


    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsInvitedOrPublic()]
        if self.action == 'create':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsOrganizerOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        qs = Event.objects.all()
        if self.action == 'list':
            if user.is_authenticated:
                qs = Event.objects.filter(Q(is_public=True) | Q(organizer=user) | Q(invited_users=user)).distinct()
            else:
                qs = Event.objects.filter(is_public=True)
        return qs
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rsvp(self, request, pk=None):
        event = self.get_object()
        serializer = RSVPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_rsvp(self, request, pk=None):
        event = self.get_object()
        try:
            rsvp = RSVP.objects.get(event=event, user=request.user)
        except RSVP.DoesNotExist:
            return Response({"detail": "RSVP not found for this event."}, status=status.HTTP_404_NOT_FOUND)

        serializer = RSVPSerializer(rsvp, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticatedOrReadOnly])
    def reviews(self, request, pk=None):
        event = self.get_object()
        reviews = event.reviews.all()
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class RSVPViewSet(viewsets.ModelViewSet):
    queryset = RSVP.objects.all()
    serializer_class = RSVPSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return RSVP.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Please use /api/events/<event_id>/rsvp/ to RSVP."},
            status=status.HTTP_400_BAD_REQUEST
        )
   
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        event_id = self.kwargs.get('event_id')
        serializer.save(user=self.request.user, event_id=event_id)
