from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model

User = get_user_model()


  

class ProfileSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField() 

    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "photo_url", "provider")

    def get_photo_url(self, obj):
        return getattr(obj, "photo_url", None) or None

    def get_provider(self, obj):
        try:
            from allauth.socialaccount.models import SocialAccount
            sa = SocialAccount.objects.filter(user=obj).first()
            if sa:
                return sa.provider  
        except Exception:
            pass
        return "local"

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('full_name', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            full_name=validated_data['full_name'],
            email=validated_data['email'],
            password=validated_data['password'],
        )


class SignInSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
