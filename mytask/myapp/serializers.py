from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Event, RSVP, Review, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = '__all__'


class RSVPSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = RSVP
        fields = ['id', 'event', 'user', 'status']
        read_only_fields = ['id', 'event', 'user']
        
class EventSerializer(serializers.ModelSerializer):
    organizer = serializers.StringRelatedField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    rsvps = RSVPSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'
