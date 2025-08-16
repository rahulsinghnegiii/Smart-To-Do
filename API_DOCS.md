# Smart Todo API Documentation

Base URL: `http://localhost:8000/api/`

## Authentication
Currently, no authentication is required. In a production environment, you would typically use JWT tokens or session authentication.

## Common Response Formats

### Success Response
```json
{
  "id": 1,
  "title": "Task Title",
  "created_at": "2025-08-12T12:00:00Z"
}
```

### Error Response
```json
{
  "error": "Error message",
  "detail": "Detailed error information"
}
```

### Paginated Response
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/tasks/?page=2",
  "previous": null,
  "results": [...]
}
```

## Tasks API

### List Tasks
```http
GET /api/tasks/
```

**Query Parameters:**
- `category` (int): Filter by category ID
- `status` (string): Filter by status (`todo`, `in_progress`, `done`)
- `priority` (string): Filter by priority (`low`, `medium`, `high`, `urgent`)
- `search` (string): Search in title and description
- `ordering` (string): Order by field (`-priority_score`, `created_at`, etc.)
- `page` (int): Page number for pagination
- `page_size` (int): Number of results per page

**Example Request:**
```bash
curl "http://localhost:8000/api/tasks/?status=todo&priority=high&page=1"
```

**Example Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Prepare client presentation slides",
      "description": "Create comprehensive slides for quarterly review",
      "category": 1,
      "category_name": "Work",
      "status": "in_progress",
      "priority": "high",
      "priority_level": "high",
      "deadline": "2025-08-15T14:00:00Z",
      "priority_score": 85.0,
      "enhanced_description": "",
      "suggested_deadline": null,
      "ai_insights": {
        "reasoning": "High priority due to client importance",
        "confidence_score": 0.9
      },
      "is_overdue": false,
      "created_at": "2025-08-12T10:00:00Z",
      "updated_at": "2025-08-12T10:00:00Z",
      "completed_at": null
    }
  ]
}
```

### Get Task
```http
GET /api/tasks/{id}/
```

**Example:**
```bash
curl "http://localhost:8000/api/tasks/1/"
```

### Create Task
```http
POST /api/tasks/
Content-Type: application/json
```

**Request Body:**
```json
{
  "title": "New Task",
  "description": "Task description",
  "category": 1,
  "priority": "medium",
  "deadline": "2025-08-20T10:00:00Z",
  "apply_ai_analysis": true
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review documentation",
    "description": "Review and update API documentation",
    "category": 1,
    "priority": "medium",
    "apply_ai_analysis": true
  }'
```

### Update Task
```http
PATCH /api/tasks/{id}/
Content-Type: application/json
```

**Request Body:** (partial update)
```json
{
  "status": "done",
  "priority": "high"
}
```

### Delete Task
```http
DELETE /api/tasks/{id}/
```

### Task Summary
```http
GET /api/tasks/summary/
```

**Response:**
```json
{
  "total_tasks": 10,
  "by_status": {
    "todo": 6,
    "in_progress": 3,
    "done": 1
  },
  "by_priority": {
    "low": 2,
    "medium": 4,
    "high": 3,
    "urgent": 1
  },
  "overdue_tasks": 1,
  "high_priority_tasks": 4
}
```

### Dashboard Data
```http
GET /api/tasks/dashboard/
```

**Response:**
```json
{
  "high_priority_tasks": [...],
  "overdue_tasks": [...],
  "recent_tasks": [...],
  "completed_today": 2,
  "summary": {...}
}
```

## Categories API

### List Categories
```http
GET /api/categories/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Work",
    "color": "#3B82F6",
    "usage_frequency": 5,
    "task_count": 3,
    "created_at": "2025-08-12T10:00:00Z",
    "updated_at": "2025-08-12T10:00:00Z"
  }
]
```

### Create Category
```http
POST /api/categories/
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "New Category",
  "color": "#FF5722"
}
```

### Category Statistics
```http
GET /api/categories/stats/
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Work",
    "color": "#3B82F6",
    "usage_frequency": 5,
    "active_tasks": 3,
    "total_tasks": 7
  }
]
```

## Context Entries API

### List Context Entries
```http
GET /api/context/
```

**Query Parameters:**
- `source_type` (string): Filter by source (`whatsapp`, `email`, `note`, etc.)
- `search` (string): Search in content
- `ordering` (string): Order by field

**Response:**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "content": "URGENT: Server maintenance scheduled for tonight...",
      "content_summary": "URGENT: Server maintenance scheduled for tonight...",
      "source_type": "email",
      "timestamp": "2025-08-12T08:30:00Z",
      "processed_insights": {
        "keywords_found": ["urgent", "maintenance", "backup"],
        "urgency_indicators": ["URGENT", "tonight"],
        "business_impact": "critical"
      },
      "relevance_score": 1.0,
      "created_at": "2025-08-12T10:00:00Z",
      "updated_at": "2025-08-12T10:00:00Z"
    }
  ]
}
```

### Create Context Entry
```http
POST /api/context/
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "Meeting notes from today's standup...",
  "source_type": "meeting",
  "timestamp": "2025-08-12T09:00:00Z"
}
```

### Context Insights
```http
GET /api/context/insights/
```

**Response:**
```json
{
  "total_entries": 6,
  "by_source": {
    "whatsapp": 1,
    "email": 2,
    "note": 2,
    "calendar": 1,
    "meeting": 0
  },
  "high_relevance_entries": 3,
  "recent_entries": 4
}
```

## AI Analysis API

### Get AI Suggestions
```http
POST /api/ai/suggestions/
Content-Type: application/json
```

**Request Body:**
```json
{
  "task_data": {
    "title": "Review contract",
    "description": "Review the new client contract for terms",
    "priority": "medium"
  },
  "context_entries": [
    {
      "content": "URGENT: Contract needs review by EOD",
      "source_type": "email",
      "timestamp": "2025-08-12T08:00:00Z"
    }
  ],
  "user_preferences": {
    "working_hours": "9-17",
    "timezone": "UTC"
  }
}
```

**Response:**
```json
{
  "priority_score": 85.0,
  "suggested_deadline": "2025-08-12T17:00:00Z",
  "enhanced_description": "Review the new client contract for terms and conditions. Priority elevated due to urgent email requesting completion by end of day.",
  "suggested_categories": ["work", "legal"],
  "confidence_score": 0.9,
  "reasoning": "High priority due to urgent context from email and explicit deadline requirement. Legal/contract review typically requires careful attention."
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (for DELETE) |
| 400 | Bad Request (validation errors) |
| 404 | Not Found |
| 500 | Internal Server Error |

## Sample API Calls

### Complete Workflow Example

1. **Create a category:**
```bash
curl -X POST "http://localhost:8000/api/categories/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Urgent Work", "color": "#FF0000"}'
```

2. **Add context:**
```bash
curl -X POST "http://localhost:8000/api/context/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Boss said this needs to be done ASAP!",
    "source_type": "whatsapp",
    "timestamp": "2025-08-12T08:00:00Z"
  }'
```

3. **Get AI suggestions:**
```bash
curl -X POST "http://localhost:8000/api/ai/suggestions/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_data": {
      "title": "Complete project proposal",
      "description": "Finish the Q4 project proposal document",
      "priority": "medium"
    }
  }'
```

4. **Create task with AI analysis:**
```bash
curl -X POST "http://localhost:8000/api/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project proposal",
    "description": "Finish the Q4 project proposal document",
    "category": 1,
    "priority": "high",
    "apply_ai_analysis": true
  }'
```

5. **Update task status:**
```bash
curl -X PATCH "http://localhost:8000/api/tasks/1/" \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

This API documentation provides all the endpoints needed to build a complete frontend application for the Smart Todo system.
