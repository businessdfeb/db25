from rest_framework import serializers
from .models import Advisor, AdvisorRole

class AdvisorRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvisorRole
        fields = '__all__'

class AdvisorSerializer(serializers.ModelSerializer):
    roles = AdvisorRoleSerializer(many=True, read_only=True)

    class Meta:
        model = Advisor
        fields = '__all__'
