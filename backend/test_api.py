#!/usr/bin/env python
"""
Quick API test script to demonstrate the AI suggestions endpoint
"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_todo.settings')
django.setup()

def test_ai_suggestions():
    """Test the AI suggestions endpoint"""
    
    url = 'http://localhost:8000/api/ai/suggestions/'
    
    # Test data for AI analysis
    test_request = {
        "task_data": {
            "title": "URGENT: Fix critical server bug",
            "description": "Production server is experiencing critical issues affecting all users. Needs immediate attention.",
            "priority": "medium"
        },
        "context_entries": [
            {
                "content": "Emergency alert: Production down! All hands on deck. CEO asking for updates every 30 minutes.",
                "source_type": "whatsapp",
                "timestamp": "2025-08-12T08:00:00Z"
            }
        ]
    }
    
    print("Testing AI Suggestions API...")
    print(f"URL: {url}")
    print(f"Request Data: {json.dumps(test_request, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=test_request)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! AI Analysis Result:")
            print(f"Priority Score: {result.get('priority_score', 'N/A')}")
            print(f"Suggested Deadline: {result.get('suggested_deadline', 'N/A')}")
            print(f"Enhanced Description: {result.get('enhanced_description', 'N/A')[:100]}...")
            print(f"Suggested Categories: {result.get('suggested_categories', [])}")
            print(f"Confidence Score: {result.get('confidence_score', 'N/A')}")
            print(f"Reasoning: {result.get('reasoning', 'N/A')[:150]}...")
            
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to server. Make sure Django server is running:")
        print("python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_tasks_list():
    """Test the tasks list endpoint"""
    
    url = 'http://localhost:8000/api/tasks/'
    
    print("\nTesting Tasks List API...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Tasks List:")
            print(f"Total Tasks: {result.get('count', 'N/A')}")
            
            tasks = result.get('results', [])
            print(f"Tasks in current page: {len(tasks)}")
            
            for i, task in enumerate(tasks[:3], 1):
                print(f"  {i}. {task.get('title', 'N/A')} [{task.get('status', 'N/A')}] - Priority: {task.get('priority_score', 'N/A')}")
            
            if len(tasks) > 3:
                print(f"  ... and {len(tasks) - 3} more tasks")
                
            return True
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("Smart Todo API Test")
    print("=" * 50)
    
    # Test tasks list first (should work without server running as it will fail gracefully)
    tasks_success = test_tasks_list()
    
    # Test AI suggestions
    ai_success = test_ai_suggestions()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Tasks API: {'✅ PASS' if tasks_success else '❌ FAIL'}")
    print(f"AI Suggestions API: {'✅ PASS' if ai_success else '❌ FAIL'}")
    
    if tasks_success and ai_success:
        print("\n🎉 All tests passed! The API is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the Django server is running:")
        print("cd backend && python manage.py runserver")
