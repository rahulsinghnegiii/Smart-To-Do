from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
import json

from .models import Task, Category, ContextEntry
from ai_service.analyzer import TaskAIAnalyzer, AIAnalysisResult


class TaskModelTests(TestCase):
    """Test Task model functionality"""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test Category', color='#FF0000')
    
    def test_task_creation(self):
        """Test task creation with required fields"""
        task = Task.objects.create(
            title='Test Task',
            description='Test Description',
            category=self.category
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'todo')  # Default status
        self.assertEqual(task.priority, 'medium')  # Default priority
        self.assertEqual(task.priority_score, 50.0)  # Default priority score
        self.assertIsNotNone(task.created_at)
    
    def test_task_priority_level_property(self):
        """Test priority_level property calculation"""
        # Test different priority scores
        test_cases = [
            (90, 'urgent'),
            (75, 'high'), 
            (50, 'medium'),
            (25, 'low')
        ]
        
        for score, expected_level in test_cases:
            task = Task.objects.create(
                title=f'Test Task {score}',
                priority_score=score
            )
            self.assertEqual(task.priority_level, expected_level)
    
    def test_task_is_overdue_property(self):
        """Test is_overdue property"""
        now = timezone.now()
        
        # Task with past deadline - should be overdue
        overdue_task = Task.objects.create(
            title='Overdue Task',
            deadline=now - timedelta(days=1)
        )
        self.assertTrue(overdue_task.is_overdue)
        
        # Task with future deadline - should not be overdue
        future_task = Task.objects.create(
            title='Future Task',
            deadline=now + timedelta(days=1)
        )
        self.assertFalse(future_task.is_overdue)
        
        # Completed task with past deadline - should not be overdue
        completed_task = Task.objects.create(
            title='Completed Task',
            deadline=now - timedelta(days=1),
            status='done'
        )
        self.assertFalse(completed_task.is_overdue)
    
    def test_task_completion_timestamp(self):
        """Test that completed_at is set when status changes to done"""
        task = Task.objects.create(title='Test Task')
        self.assertIsNone(task.completed_at)
        
        # Mark as done
        task.status = 'done'
        task.save()
        self.assertIsNotNone(task.completed_at)
        
        # Change back to todo
        task.status = 'todo'
        task.save()
        self.assertIsNone(task.completed_at)


class CategoryModelTests(TestCase):
    """Test Category model functionality"""
    
    def test_category_creation(self):
        """Test category creation"""
        category = Category.objects.create(name='Work', color='#3B82F6')
        self.assertEqual(category.name, 'Work')
        self.assertEqual(category.usage_frequency, 0)
    
    def test_category_usage_increment(self):
        """Test category usage frequency increment"""
        category = Category.objects.create(name='Work')
        initial_frequency = category.usage_frequency
        
        category.increment_usage()
        category.refresh_from_db()
        
        self.assertEqual(category.usage_frequency, initial_frequency + 1)


class ContextEntryModelTests(TestCase):
    """Test ContextEntry model functionality"""
    
    def test_context_entry_creation(self):
        """Test context entry creation"""
        now = timezone.now()
        entry = ContextEntry.objects.create(
            content='Test context content',
            source_type='email',
            timestamp=now
        )
        
        self.assertEqual(entry.content, 'Test context content')
        self.assertEqual(entry.source_type, 'email')
        self.assertEqual(entry.relevance_score, 0.0)  # Default
    
    def test_context_entry_summary(self):
        """Test get_summary method"""
        short_content = 'Short content'
        long_content = 'x' * 150  # Longer than 100 chars
        
        short_entry = ContextEntry.objects.create(
            content=short_content,
            source_type='note',
            timestamp=timezone.now()
        )
        
        long_entry = ContextEntry.objects.create(
            content=long_content,
            source_type='note',
            timestamp=timezone.now()
        )
        
        self.assertEqual(short_entry.get_summary(), short_content)
        self.assertTrue(long_entry.get_summary().endswith('...'))
        self.assertEqual(len(long_entry.get_summary()), 100)  # 97 chars + '...'


class TaskAPITests(APITestCase):
    """Test Task API endpoints"""
    
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.task_data = {
            'title': 'Test API Task',
            'description': 'Test Description',
            'category': self.category.id,
            'priority': 'high'
        }
    
    def test_create_task_api(self):
        """Test task creation via API"""
        url = reverse('task-list')
        response = self.client.post(url, self.task_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        
        task = Task.objects.first()
        self.assertEqual(task.title, self.task_data['title'])
        self.assertEqual(task.priority, self.task_data['priority'])
    
    def test_list_tasks_api(self):
        """Test task listing via API"""
        # Create some test tasks
        Task.objects.create(title='Task 1', category=self.category)
        Task.objects.create(title='Task 2', category=self.category)
        
        url = reverse('task-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_update_task_api(self):
        """Test task update via API"""
        task = Task.objects.create(title='Original Title', category=self.category)
        
        url = reverse('task-detail', kwargs={'pk': task.pk})
        updated_data = {'title': 'Updated Title'}
        response = self.client.patch(url, updated_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        task.refresh_from_db()
        self.assertEqual(task.title, 'Updated Title')
    
    def test_delete_task_api(self):
        """Test task deletion via API"""
        task = Task.objects.create(title='Task to Delete', category=self.category)
        
        url = reverse('task-detail', kwargs={'pk': task.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)
    
    def test_task_filtering(self):
        """Test task filtering by category and status"""
        # Create tasks with different categories and statuses
        other_category = Category.objects.create(name='Other')
        
        Task.objects.create(title='Task 1', category=self.category, status='todo')
        Task.objects.create(title='Task 2', category=self.category, status='done')
        Task.objects.create(title='Task 3', category=other_category, status='todo')
        
        # Test category filtering
        url = reverse('task-list')
        response = self.client.get(url, {'category': self.category.id})
        self.assertEqual(len(response.data['results']), 2)
        
        # Test status filtering
        response = self.client.get(url, {'status': 'todo'})
        self.assertEqual(len(response.data['results']), 2)
        
        # Test combined filtering
        response = self.client.get(url, {
            'category': self.category.id,
            'status': 'todo'
        })
        self.assertEqual(len(response.data['results']), 1)
    
    def test_task_summary_endpoint(self):
        """Test task summary statistics endpoint"""
        # Create tasks with different statuses
        Task.objects.create(title='Todo Task', status='todo', priority_score=85)
        Task.objects.create(title='Done Task', status='done')
        Task.objects.create(title='In Progress Task', status='in_progress')
        
        url = reverse('task-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertEqual(data['total_tasks'], 3)
        self.assertEqual(data['by_status']['todo'], 1)
        self.assertEqual(data['by_status']['done'], 1)
        self.assertEqual(data['by_status']['in_progress'], 1)
        self.assertEqual(data['high_priority_tasks'], 1)  # priority_score >= 70


class AIAnalysisAPITests(APITestCase):
    """Test AI analysis API endpoints"""
    
    def test_ai_suggestions_api(self):
        """Test AI suggestions endpoint"""
        url = reverse('ai-suggestions')
        
        request_data = {
            'task_data': {
                'title': 'Urgent client meeting',
                'description': 'Prepare for important client presentation tomorrow',
                'priority': 'high'
            }
        }
        
        response = self.client.post(url, request_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.data
        self.assertIn('priority_score', data)
        self.assertIn('suggested_deadline', data)
        self.assertIn('enhanced_description', data)
        self.assertIn('suggested_categories', data)
        self.assertIn('confidence_score', data)
        self.assertIn('reasoning', data)
        
        # Verify priority score is reasonable for urgent task
        self.assertGreater(data['priority_score'], 70)  # Should be high priority
    
    def test_ai_suggestions_with_context(self):
        """Test AI suggestions with context entries"""
        url = reverse('ai-suggestions')
        
        request_data = {
            'task_data': {
                'title': 'Review contract',
                'description': 'Review the new client contract',
                'priority': 'medium'
            },
            'context_entries': [
                {
                    'content': 'URGENT: Contract needs to be reviewed by EOD',
                    'source_type': 'email',
                    'timestamp': timezone.now().isoformat()
                }
            ]
        }
        
        response = self.client.post(url, request_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Priority should be boosted due to urgent context
        data = response.data
        self.assertGreater(data['priority_score'], 60)


class AIAnalyzerTests(TestCase):
    """Test AI Analyzer functionality"""
    
    def setUp(self):
        self.analyzer = TaskAIAnalyzer()
    
    def test_fallback_analysis(self):
        """Test fallback analysis when AI is unavailable"""
        task_data = {
            'title': 'URGENT: Fix server issue',
            'description': 'Critical server down, needs immediate attention',
            'priority': 'high'
        }
        
        result = self.analyzer.analyze_task(task_data)
        
        self.assertIsInstance(result, AIAnalysisResult)
        self.assertGreater(result.priority_score, 80)  # Should be high due to 'URGENT'
        self.assertIsInstance(result.suggested_categories, list)
        self.assertEqual(result.confidence_score, 0.6)  # Fallback confidence
    
    def test_priority_score_calculation(self):
        """Test priority score calculation with keywords"""
        # Test urgent keywords
        urgent_task = {
            'title': 'ASAP: Critical bug fix',
            'description': 'Emergency fix needed immediately',
            'priority': 'medium'
        }
        
        result = self.analyzer.analyze_task(urgent_task)
        self.assertGreater(result.priority_score, 70)
        
        # Test calming keywords
        low_task = {
            'title': 'Maybe update documentation',
            'description': 'Someday when we have time',
            'priority': 'medium'
        }
        
        result = self.analyzer.analyze_task(low_task)
        self.assertLess(result.priority_score, 40)
    
    def test_category_suggestions(self):
        """Test category suggestion based on keywords"""
        work_task = {
            'title': 'Client meeting preparation',
            'description': 'Prepare slides for quarterly business review',
            'priority': 'medium'
        }
        
        result = self.analyzer.analyze_task(work_task)
        self.assertIn('work', [cat.lower() for cat in result.suggested_categories])
        
        health_task = {
            'title': 'Doctor appointment',
            'description': 'Annual health checkup and blood tests',
            'priority': 'medium'
        }
        
        result = self.analyzer.analyze_task(health_task)
        self.assertIn('health', [cat.lower() for cat in result.suggested_categories])
    
    def test_deadline_suggestion(self):
        """Test deadline suggestion based on priority and keywords"""
        urgent_task = {
            'title': 'Fix critical bug ASAP',
            'description': 'Production system is down',
            'priority': 'urgent'
        }
        
        result = self.analyzer.analyze_task(urgent_task)
        
        # Should suggest a deadline soon
        if result.suggested_deadline:
            time_diff = result.suggested_deadline - timezone.now()
            self.assertLess(time_diff.days, 2)  # Should be within 2 days


class IntegrationTests(APITestCase):
    """Integration tests combining multiple components"""
    
    def test_task_creation_with_ai_analysis(self):
        """Test task creation with automatic AI analysis"""
        category = Category.objects.create(name='Work')
        
        # Create context entry that should influence analysis
        ContextEntry.objects.create(
            content='URGENT: Client presentation tomorrow at 9 AM',
            source_type='email',
            timestamp=timezone.now()
        )
        
        url = reverse('task-list')
        task_data = {
            'title': 'Prepare client presentation',
            'description': 'Create slides for quarterly review',
            'category': category.id,
            'apply_ai_analysis': True  # Trigger AI analysis
        }
        
        response = self.client.post(url, task_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check that AI analysis was applied
        task = Task.objects.first()
        self.assertGreater(task.priority_score, 50)  # Should have AI-calculated score
        
        # AI insights should be populated
        self.assertIsInstance(task.ai_insights, dict)
        self.assertIn('reasoning', task.ai_insights)
