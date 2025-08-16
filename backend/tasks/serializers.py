from rest_framework import serializers
from .models import Task, Category, ContextEntry


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with usage statistics
    """
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'color', 'usage_frequency', 
            'task_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['usage_frequency', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        """Get current number of active tasks in this category"""
        return obj.tasks.exclude(status='done').count()


class TaskSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for Task model including AI fields
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    priority_level = serializers.CharField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'status', 'priority', 'priority_level', 'deadline', 
            'priority_score', 'enhanced_description', 'suggested_deadline',
            'ai_insights', 'is_overdue', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'priority_score', 'enhanced_description', 'suggested_deadline',
            'ai_insights', 'priority_level', 'is_overdue', 
            'created_at', 'updated_at', 'completed_at'
        ]
    
    def validate_deadline(self, value):
        """Ensure deadline is in the future"""
        if value:
            from django.utils import timezone
            if value <= timezone.now():
                raise serializers.ValidationError(
                    "Deadline must be in the future."
                )
        return value


class TaskCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating tasks (user input only)
    """
    category_name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category', 'category_name',
            'status', 'priority', 'deadline'
        ]
    
    def create(self, validated_data):
        # Handle category creation by name if provided
        category_name = validated_data.pop('category_name', None)
        if category_name and not validated_data.get('category'):
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'color': '#3B82F6'}
            )
            validated_data['category'] = category
        
        return super().create(validated_data)


class ContextEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for ContextEntry model
    """
    content_summary = serializers.CharField(source='get_summary', read_only=True)
    
    class Meta:
        model = ContextEntry
        fields = [
            'id', 'content', 'content_summary', 'source_type', 'timestamp',
            'processed_insights', 'relevance_score', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'processed_insights', 'relevance_score', 'created_at', 'updated_at'
        ]
    
    def validate_timestamp(self, value):
        """Ensure timestamp is not in the future"""
        from django.utils import timezone
        if value > timezone.now():
            raise serializers.ValidationError(
                "Timestamp cannot be in the future."
            )
        return value


class AITaskAnalysisSerializer(serializers.Serializer):
    """
    Serializer for AI task analysis requests and responses
    """
    # Input fields
    task_data = serializers.DictField(
        help_text="Task data to analyze (title, description, etc.)"
    )
    context_entries = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Relevant context entries for analysis"
    )
    user_preferences = serializers.DictField(
        required=False,
        help_text="User preferences and settings"
    )
    current_load = serializers.DictField(
        required=False,
        help_text="Current workload and schedule information"
    )
    
    # Output fields (for response)
    priority_score = serializers.FloatField(
        read_only=True,
        help_text="AI-calculated priority score (0-100)"
    )
    suggested_deadline = serializers.DateTimeField(
        read_only=True, 
        allow_null=True,
        help_text="AI-suggested deadline"
    )
    enhanced_description = serializers.CharField(
        read_only=True,
        allow_blank=True,
        help_text="AI-enhanced description"
    )
    suggested_categories = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        help_text="AI-suggested categories"
    )
    confidence_score = serializers.FloatField(
        read_only=True,
        help_text="Confidence in AI suggestions (0-1)"
    )
    reasoning = serializers.CharField(
        read_only=True,
        allow_blank=True,
        help_text="AI reasoning for the suggestions"
    )
