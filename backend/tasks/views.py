from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone

from .models import Task, Category, ContextEntry
from .serializers import (
    TaskSerializer, TaskCreateSerializer, CategorySerializer, 
    ContextEntrySerializer, AITaskAnalysisSerializer
)
from ai_service.analyzer import task_analyzer


class TaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks with AI-enhanced features
    
    Provides:
    - CRUD operations for tasks
    - Filtering by category, status, priority
    - Search functionality
    - AI-powered task analysis
    """
    
    queryset = Task.objects.all()
    pagination_class = TaskPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'priority']
    search_fields = ['title', 'description', 'enhanced_description']
    ordering_fields = ['priority_score', 'created_at', 'deadline']
    ordering = ['-priority_score', '-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Create task and optionally apply AI enhancements"""
        task = serializer.save()
        
        # Apply AI analysis if requested
        if self.request.data.get('apply_ai_analysis', False):
            self.apply_ai_analysis(task)
    
    def perform_update(self, serializer):
        """Update task and optionally reapply AI analysis"""
        task = serializer.save()
        
        # Reapply AI analysis if requested
        if self.request.data.get('apply_ai_analysis', False):
            self.apply_ai_analysis(task)
    
    def apply_ai_analysis(self, task):
        """Apply AI analysis to a task"""
        try:
            # Prepare task data
            task_data = {
                'title': task.title,
                'description': task.description,
                'priority': task.priority,
                'deadline': task.deadline.isoformat() if task.deadline else None
            }
            
            # Get relevant context (last 10 entries)
            context_entries = list(ContextEntry.objects.order_by('-relevance_score', '-timestamp')[:10].values())
            
            # Get current workload info
            active_tasks = Task.objects.exclude(status='done').count()
            current_load = {
                'active_tasks': active_tasks,
                'high_priority_tasks': Task.objects.filter(
                    status__in=['todo', 'in_progress'],
                    priority_score__gte=70
                ).count()
            }
            
            # Analyze with AI
            result = task_analyzer.analyze_task(
                task_data, 
                context_entries, 
                current_load=current_load
            )
            
            # Update task with AI results
            task.priority_score = result.priority_score
            task.enhanced_description = result.enhanced_description
            task.suggested_deadline = result.suggested_deadline
            task.ai_insights = {
                'confidence_score': result.confidence_score,
                'reasoning': result.reasoning,
                'suggested_categories': result.suggested_categories,
                'analysis_timestamp': timezone.now().isoformat()
            }
            task.save()
            
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"AI analysis failed for task {task.id}: {e}")
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get task summary statistics"""
        queryset = self.get_queryset()
        
        summary_data = {
            'total_tasks': queryset.count(),
            'by_status': {
                status[0]: queryset.filter(status=status[0]).count() 
                for status in Task.STATUS_CHOICES
            },
            'by_priority': {
                priority[0]: queryset.filter(priority=priority[0]).count()
                for priority in Task.PRIORITY_CHOICES
            },
            'overdue_tasks': queryset.filter(
                deadline__lt=timezone.now(),
                status__in=['todo', 'in_progress']
            ).count(),
            'high_priority_tasks': queryset.filter(
                priority_score__gte=70,
                status__in=['todo', 'in_progress']
            ).count()
        }
        
        return Response(summary_data)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard data with priority tasks and recent activity"""
        # High priority tasks
        high_priority = self.get_queryset().filter(
            priority_score__gte=70,
            status__in=['todo', 'in_progress']
        ).order_by('-priority_score')[:5]
        
        # Overdue tasks
        overdue = self.get_queryset().filter(
            deadline__lt=timezone.now(),
            status__in=['todo', 'in_progress']
        ).order_by('deadline')[:5]
        
        # Recent tasks
        recent = self.get_queryset().order_by('-created_at')[:5]
        
        # Completed today
        today = timezone.now().date()
        completed_today = self.get_queryset().filter(
            status='done',
            completed_at__date=today
        ).count()
        
        dashboard_data = {
            'high_priority_tasks': TaskSerializer(high_priority, many=True).data,
            'overdue_tasks': TaskSerializer(overdue, many=True).data,
            'recent_tasks': TaskSerializer(recent, many=True).data,
            'completed_today': completed_today,
            'summary': self.summary(request).data
        }
        
        return Response(dashboard_data)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing task categories
    
    Provides:
    - CRUD operations for categories
    - Usage statistics
    - Task count per category
    """
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'usage_frequency', 'created_at']
    ordering = ['-usage_frequency', 'name']
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get category usage statistics"""
        categories = self.get_queryset().annotate(
            active_task_count=Count('tasks', filter=Q(tasks__status__in=['todo', 'in_progress']))
        )
        
        stats_data = []
        for category in categories:
            stats_data.append({
                'id': category.id,
                'name': category.name,
                'color': category.color,
                'usage_frequency': category.usage_frequency,
                'active_tasks': category.active_task_count,
                'total_tasks': category.tasks.count()
            })
        
        return Response(stats_data)


class ContextEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing context entries
    
    Provides:
    - CRUD operations for context entries
    - Filtering by source type
    - AI processing of context for insights
    """
    
    queryset = ContextEntry.objects.all()
    serializer_class = ContextEntrySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['source_type']
    search_fields = ['content']
    ordering_fields = ['timestamp', 'relevance_score', 'created_at']
    ordering = ['-timestamp', '-relevance_score']
    
    def perform_create(self, serializer):
        """Create context entry and process for insights"""
        context_entry = serializer.save()
        self.process_context_insights(context_entry)
    
    def process_context_insights(self, context_entry):
        """Process context entry for AI insights (placeholder for now)"""
        # This would use the AI service to extract insights from context
        # For now, we'll do basic keyword analysis
        content = context_entry.content.lower()
        
        # Simple relevance scoring based on keywords
        relevance_keywords = [
            'urgent', 'deadline', 'important', 'asap', 'meeting', 
            'call', 'email', 'task', 'project', 'due'
        ]
        
        relevance_score = 0.0
        for keyword in relevance_keywords:
            if keyword in content:
                relevance_score += 0.1
        
        context_entry.relevance_score = min(1.0, relevance_score)
        context_entry.processed_insights = {
            'keywords_found': [kw for kw in relevance_keywords if kw in content],
            'character_count': len(context_entry.content),
            'processed_at': timezone.now().isoformat()
        }
        context_entry.save()
    
    @action(detail=False, methods=['get'])
    def insights(self, request):
        """Get aggregated insights from context entries"""
        entries = self.get_queryset()
        
        insights_data = {
            'total_entries': entries.count(),
            'by_source': {
                source[0]: entries.filter(source_type=source[0]).count()
                for source in ContextEntry.SOURCE_TYPE_CHOICES
            },
            'high_relevance_entries': entries.filter(relevance_score__gte=0.7).count(),
            'recent_entries': entries.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=7)
            ).count()
        }
        
        return Response(insights_data)


class AIAnalysisView(viewsets.GenericViewSet):
    """
    ViewSet for AI-powered task analysis
    
    Provides:
    - Task analysis with priority scoring
    - Deadline suggestions
    - Description enhancement
    - Category suggestions
    """
    
    serializer_class = AITaskAnalysisSerializer
    
    @action(detail=False, methods=['post'])
    def suggestions(self, request):
        """
        Analyze task data and provide AI suggestions
        
        POST /api/ai/suggestions/
        {
            "task_data": {
                "title": "Task title",
                "description": "Task description",
                "priority": "medium",
                "deadline": "2024-08-15T10:00:00Z"
            },
            "context_entries": [...],  // optional
            "user_preferences": {...}, // optional
            "current_load": {...}     // optional
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Extract data
            task_data = serializer.validated_data['task_data']
            context_entries = serializer.validated_data.get('context_entries', [])
            user_prefs = serializer.validated_data.get('user_preferences', {})
            current_load = serializer.validated_data.get('current_load')
            
            # If no current_load provided, calculate from existing tasks
            if not current_load:
                active_tasks = Task.objects.exclude(status='done').count()
                current_load = {
                    'active_tasks': active_tasks,
                    'high_priority_tasks': Task.objects.filter(
                        status__in=['todo', 'in_progress'],
                        priority_score__gte=70
                    ).count()
                }
            
            # Perform AI analysis
            result = task_analyzer.analyze_task(
                task_data, 
                context_entries, 
                user_prefs, 
                current_load
            )
            
            # Format response
            response_data = {
                'priority_score': result.priority_score,
                'suggested_deadline': result.suggested_deadline.isoformat() if result.suggested_deadline else None,
                'enhanced_description': result.enhanced_description,
                'suggested_categories': result.suggested_categories,
                'confidence_score': result.confidence_score,
                'reasoning': result.reasoning
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': f'AI analysis failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
