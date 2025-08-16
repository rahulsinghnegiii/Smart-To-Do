#!/usr/bin/env python
"""
Sample data creation script for Smart Todo App

This script creates sample categories, context entries, and tasks
to demonstrate the application functionality.
"""

import os
import sys
import django
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_todo.settings')
django.setup()

from tasks.models import Category, ContextEntry, Task

def create_sample_categories():
    """Create sample categories"""
    categories_data = [
        {'name': 'Work', 'color': '#3B82F6'},
        {'name': 'Personal', 'color': '#10B981'},  
        {'name': 'Health', 'color': '#F59E0B'},
        {'name': 'Learning', 'color': '#8B5CF6'},
        {'name': 'Finance', 'color': '#EF4444'},
        {'name': 'Shopping', 'color': '#06B6D4'},
        {'name': 'Maintenance', 'color': '#6B7280'},
    ]
    
    categories = []
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'color': cat_data['color']}
        )
        categories.append(category)
        print(f"{'Created' if created else 'Found'} category: {category.name}")
    
    return categories

def create_sample_context_entries():
    """Create sample context entries from various sources"""
    now = timezone.now()
    
    context_entries_data = [
        {
            'content': 'Hi, can we schedule the client presentation for next week? The budget proposal needs to be ready by then.',
            'source_type': 'whatsapp',
            'timestamp': now - timedelta(hours=2)
        },
        {
            'content': 'URGENT: Server maintenance scheduled for tonight. Please backup all important data before 6 PM.',
            'source_type': 'email',
            'timestamp': now - timedelta(hours=4)
        },
        {
            'content': 'Doctor appointment reminder: Annual checkup scheduled for Thursday at 2 PM. Please arrive 15 minutes early.',
            'source_type': 'email',
            'timestamp': now - timedelta(days=1)
        },
        {
            'content': 'Team meeting notes: Discussed Q4 goals, need to finalize marketing strategy by end of month.',
            'source_type': 'meeting',
            'timestamp': now - timedelta(hours=6)
        },
        {
            'content': 'Grocery list: milk, bread, eggs, fruits. Also need to pick up prescription from pharmacy.',
            'source_type': 'note',
            'timestamp': now - timedelta(hours=12)
        },
        {
            'content': 'Conference call with investors at 3 PM tomorrow. Need to prepare financial projections.',
            'source_type': 'calendar',
            'timestamp': now - timedelta(hours=8)
        }
    ]
    
    context_entries = []
    for entry_data in context_entries_data:
        entry, created = ContextEntry.objects.get_or_create(
            content=entry_data['content'],
            defaults={
                'source_type': entry_data['source_type'],
                'timestamp': entry_data['timestamp']
            }
        )
        context_entries.append(entry)
        print(f"{'Created' if created else 'Found'} context entry: {entry.get_summary()}")
    
    return context_entries

def create_sample_tasks(categories):
    """Create sample tasks with different priorities and statuses"""
    now = timezone.now()
    
    # Get categories by name for easier reference
    cat_dict = {cat.name: cat for cat in categories}
    
    tasks_data = [
        {
            'title': 'Prepare client presentation slides',
            'description': 'Create comprehensive slides for the quarterly review meeting with our biggest client. Include performance metrics and future roadmap.',
            'category': cat_dict.get('Work'),
            'status': 'in_progress',
            'priority': 'high',
            'deadline': now + timedelta(days=3),
            'priority_score': 85.0
        },
        {
            'title': 'Schedule annual health checkup',
            'description': 'Book appointment with family doctor for yearly physical exam and blood tests.',
            'category': cat_dict.get('Health'),
            'status': 'todo',
            'priority': 'medium',
            'deadline': now + timedelta(days=14),
            'priority_score': 60.0
        },
        {
            'title': 'Backup server data URGENT',
            'description': 'Critical server maintenance tonight requires full data backup. Must be completed before 6 PM today.',
            'category': cat_dict.get('Work'),
            'status': 'todo',
            'priority': 'urgent',
            'deadline': now + timedelta(hours=6),
            'priority_score': 95.0
        },
        {
            'title': 'Complete online Python course',
            'description': 'Finish the remaining 3 modules of the Advanced Python Programming course on Coursera.',
            'category': cat_dict.get('Learning'),
            'status': 'in_progress',
            'priority': 'medium',
            'deadline': now + timedelta(days=30),
            'priority_score': 55.0
        },
        {
            'title': 'Pay credit card bill',
            'description': 'Monthly credit card payment due. Set up automatic payment to avoid late fees.',
            'category': cat_dict.get('Finance'),
            'status': 'todo',
            'priority': 'high',
            'deadline': now + timedelta(days=5),
            'priority_score': 75.0
        },
        {
            'title': 'Grocery shopping for the week',
            'description': 'Buy essentials: milk, bread, eggs, fruits, vegetables. Also pick up prescription from pharmacy.',
            'category': cat_dict.get('Shopping'),
            'status': 'todo',
            'priority': 'low',
            'deadline': now + timedelta(days=2),
            'priority_score': 35.0
        },
        {
            'title': 'Fix leaky faucet in bathroom',
            'description': 'Kitchen faucet has been dripping for weeks. Need to replace the washer or call a plumber.',
            'category': cat_dict.get('Maintenance'),
            'status': 'todo',
            'priority': 'low',
            'deadline': now + timedelta(days=7),
            'priority_score': 30.0
        },
        {
            'title': 'Review and update resume',
            'description': 'Update resume with recent projects and skills for potential job opportunities.',
            'category': cat_dict.get('Personal'),
            'status': 'todo',
            'priority': 'medium',
            'deadline': None,  # No specific deadline
            'priority_score': 45.0
        },
        {
            'title': 'Submit quarterly tax documents',
            'description': 'Compile and submit Q3 tax documents to accountant. Include all receipts and invoices.',
            'category': cat_dict.get('Finance'),
            'status': 'done',
            'priority': 'high',
            'deadline': now - timedelta(days=2),  # Past deadline but completed
            'priority_score': 80.0
        },
        {
            'title': 'Plan birthday party for mom',
            'description': 'Organize surprise birthday party for mom\'s 60th. Book venue, arrange catering, invite family.',
            'category': cat_dict.get('Personal'),
            'status': 'in_progress',
            'priority': 'high',
            'deadline': now + timedelta(days=21),
            'priority_score': 70.0
        }
    ]
    
    tasks = []
    for task_data in tasks_data:
        task, created = Task.objects.get_or_create(
            title=task_data['title'],
            defaults=task_data
        )
        if created and task_data['status'] == 'done':
            task.completed_at = timezone.now() - timedelta(days=1)
            task.save()
        
        tasks.append(task)
        print(f"{'Created' if created else 'Found'} task: {task.title} [{task.get_status_display()}]")
    
    return tasks

def main():
    """Main function to create all sample data"""
    print("Creating sample data for Smart Todo App...")
    print("=" * 50)
    
    # Create categories
    print("\n1. Creating Categories:")
    categories = create_sample_categories()
    
    # Create context entries
    print("\n2. Creating Context Entries:")
    context_entries = create_sample_context_entries()
    
    # Create tasks
    print("\n3. Creating Tasks:")
    tasks = create_sample_tasks(categories)
    
    print("\n" + "=" * 50)
    print("Sample data creation completed!")
    print(f"Created {len(categories)} categories, {len(context_entries)} context entries, and {len(tasks)} tasks.")
    print("\nYou can now:")
    print("- Start the Django server: python manage.py runserver")
    print("- Access the API at: http://localhost:8000/api/")
    print("- View the admin interface: http://localhost:8000/admin/")
    print("  (Create superuser first: python manage.py createsuperuser)")

if __name__ == '__main__':
    main()
