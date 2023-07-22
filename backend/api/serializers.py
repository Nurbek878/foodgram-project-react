from rest_framework import serializers
from user.models import NewUser

class NewUserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        model = NewUser