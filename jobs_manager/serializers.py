from rest_framework import serializers
from .models import Job

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class JobPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id',
            'title_name',
            'title_path',
            'description',
            'images_number',
            'status',
            'step',
            'created_at',
            'completed_at',
            'used_model_name',
        ]

class JobsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            'id',
            'title_name',
            'created_at',
            'completed_at',
            'used_model_name'
        ]
