# Smart Todo List - AI-Powered Task Management

A production-ready Smart Todo List web application with AI-enhanced features for intelligent task prioritization, deadline suggestions, and context-aware task management.

## 🚀 Features

### Core Features
- **Task Management**: Full CRUD operations for tasks with status tracking (Todo, In Progress, Done)
- **Category System**: Organize tasks with color-coded categories and usage analytics
- **Priority Scoring**: AI-calculated priority scores (0-100) based on content analysis
- **Context Integration**: Multi-source context entries (WhatsApp, Email, Notes, Calendar, Meetings)
- **AI Suggestions**: Intelligent deadline suggestions, description enhancement, and category recommendations
- **Dashboard**: Real-time analytics and priority task overview

### AI-Enhanced Features
- **Priority Scoring**: Keyword-based analysis with context awareness
- **Deadline Prediction**: Smart deadline suggestions based on urgency and workload
- **Description Enhancement**: Context-aware task description improvements
- **Category Suggestions**: Automatic categorization based on content analysis
- **Fallback Logic**: Rule-based heuristics when AI services are unavailable

### Multi-AI Provider Support
- **OpenAI** (GPT-3.5-turbo, GPT-4)
- **Anthropic Claude** (Claude-3-haiku)
- **LM Studio** (Local LLM support)
- **Fallback Mode** (Rule-based analysis)

## 🏗️ Architecture

### Backend (Django + DRF)
```
backend/
├── smart_todo/           # Main Django project
│   ├── settings.py      # Configuration with AI service settings
│   └── urls.py          # URL routing
├── tasks/               # Core tasks app
│   ├── models.py        # Task, Category, ContextEntry models
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # API viewsets
│   ├── admin.py         # Django admin interface
│   └── tests.py         # Comprehensive test suite
├── ai_service/          # AI analysis module
│   └── analyzer.py      # TaskAIAnalyzer with multi-provider support
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── create_sample_data.py # Sample data generation script
```

### Frontend (Next.js + React + Tailwind)
```
frontend/
├── src/
│   ├── app/            # Next.js app router
│   ├── components/     # Reusable React components
│   ├── types/          # TypeScript type definitions
│   ├── services/       # API service layer
│   └── utils/          # Utility functions
├── package.json        # Node.js dependencies
└── tailwind.config.js  # Tailwind CSS configuration
```

## 📋 API Endpoints

### Tasks
- `GET /api/tasks/` - List tasks with filtering and pagination
- `POST /api/tasks/` - Create new task (with optional AI analysis)
- `GET /api/tasks/{id}/` - Get specific task
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `GET /api/tasks/summary/` - Get task statistics
- `GET /api/tasks/dashboard/` - Get dashboard data

### Categories
- `GET /api/categories/` - List categories
- `POST /api/categories/` - Create category
- `GET /api/categories/{id}/` - Get specific category
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category
- `GET /api/categories/stats/` - Get category statistics

### Context Entries
- `GET /api/context/` - List context entries
- `POST /api/context/` - Create context entry
- `GET /api/context/{id}/` - Get specific context entry
- `PUT /api/context/{id}/` - Update context entry
- `DELETE /api/context/{id}/` - Delete context entry
- `GET /api/context/insights/` - Get context insights

### AI Analysis
- `POST /api/ai/suggestions/` - Get AI suggestions for task

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (optional, SQLite works for development)
- Git

### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Environment Configuration**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create Sample Data**
```bash
python create_sample_data.py
```

7. **Create Superuser (Optional)**
```bash
python manage.py createsuperuser
```

8. **Run Development Server**
```bash
python manage.py runserver
```

Backend will be available at: http://localhost:8000

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Environment Configuration**
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

4. **Run Development Server**
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🤖 AI Configuration

### OpenAI Setup
```bash
# In backend/.env
AI_SERVICE_MODE=openai
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

### Anthropic Claude Setup
```bash
# In backend/.env
AI_SERVICE_MODE=anthropic
ANTHROPIC_API_KEY=your-api-key-here
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

### LM Studio Setup (Local LLM)
```bash
# In backend/.env
AI_SERVICE_MODE=lmstudio
LM_STUDIO_BASE_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model
```

1. **Install LM Studio**: Download from https://lmstudio.ai/
2. **Download Model**: Choose a compatible model (e.g., Llama 2, Mistral)
3. **Start Server**: Enable local server in LM Studio on port 1234
4. **Configure**: Update .env with your local endpoint

### Fallback Mode (No AI Required)
```bash
# In backend/.env
AI_SERVICE_MODE=fallback
```

## 🧪 Testing

### Backend Tests
```bash
cd backend

# Run all tests
python manage.py test

# Run specific test modules
python manage.py test tasks.tests.TaskModelTests
python manage.py test tasks.tests.AIAnalyzerTests

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Coverage
- **Model Tests**: Task, Category, ContextEntry functionality
- **API Tests**: All CRUD endpoints with filtering
- **AI Tests**: Analyzer functionality and fallback logic
- **Integration Tests**: End-to-end workflows

## 📊 Sample Data

The application includes comprehensive sample data:

### Tasks (10 samples)
- Various priorities (Low to Urgent)
- Different categories (Work, Personal, Health, etc.)
- Mixed statuses (Todo, In Progress, Done)
- Realistic deadlines and AI insights

### Context Entries (8 samples)
- Multi-source entries (WhatsApp, Email, Notes, etc.)
- Varying relevance scores
- Processed insights with keywords and urgency indicators

### Categories (7 defaults)
- Work, Personal, Health, Learning, Finance, Shopping, Maintenance
- Color-coded with usage tracking

## 🔗 Database Schema

### Task Model
```python
- title: CharField(200)
- description: TextField
- category: ForeignKey(Category)
- status: CharField(choices=['todo', 'in_progress', 'done'])
- priority: CharField(choices=['low', 'medium', 'high', 'urgent'])
- priority_score: FloatField(0-100)
- deadline: DateTimeField(nullable)
- enhanced_description: TextField
- suggested_deadline: DateTimeField(nullable)
- ai_insights: JSONField
- created_at, updated_at, completed_at: DateTimeField
```

### Category Model
```python
- name: CharField(50, unique=True)
- color: CharField(7)  # Hex color
- usage_frequency: PositiveIntegerField
- created_at, updated_at: DateTimeField
```

### ContextEntry Model
```python
- content: TextField
- source_type: CharField(choices=['whatsapp', 'email', 'note', 'calendar', 'meeting'])
- timestamp: DateTimeField
- processed_insights: JSONField
- relevance_score: FloatField(0-1)
- created_at, updated_at: DateTimeField
```

## 🚦 AI Pipeline Design

### Design Philosophy
The AI pipeline is designed with graceful degradation and multiple fallback layers:

1. **Primary AI Analysis**: Uses configured AI provider (OpenAI/Anthropic/LM Studio)
2. **Fallback Logic**: Rule-based heuristics when AI is unavailable
3. **Confidence Scoring**: All suggestions include confidence metrics
4. **Context Awareness**: Incorporates multi-source context for better analysis

### Analysis Process
1. **Input Processing**: Task data + context entries + user preferences
2. **Prompt Generation**: Structured prompts with analysis guidelines
3. **AI Inference**: Provider-specific API calls with error handling
4. **Response Parsing**: JSON parsing with validation and fallback
5. **Result Enhancement**: Confidence scoring and reasoning extraction

### Fallback Heuristics
- **Priority Scoring**: Keyword-based urgency detection
- **Deadline Suggestion**: Time pattern recognition and priority-based scheduling
- **Category Classification**: Content keyword mapping
- **Description Enhancement**: Context integration and formatting

## 📱 Frontend Components (In Progress)

The frontend architecture includes:

### Core Components
- **TaskCard**: Individual task display with priority indicators
- **TaskForm**: Create/edit tasks with AI suggestions
- **Dashboard**: Overview with statistics and priority tasks
- **CategoryManager**: Category CRUD with color picker
- **ContextPanel**: Context entry management
- **AIInsightsPanel**: AI analysis results display

### Pages
- **Dashboard** (`/`): Main overview with priority tasks and statistics
- **Task Detail** (`/task/[id]`): Individual task view/edit
- **Context** (`/context`): Context entry management

### Features
- Real-time AI suggestions during task creation
- Priority visual indicators with color coding
- Responsive design with Tailwind CSS
- Toast notifications for user feedback
- Loading states and error handling

## 🔧 Development Notes

### Code Quality
- **Type Safety**: Full TypeScript implementation
- **Error Handling**: Comprehensive error boundaries and API error handling
- **Testing**: Unit tests for models, API endpoints, and AI functionality
- **Documentation**: Inline comments and API documentation

### Performance Considerations
- **Database Indexing**: Optimized queries with strategic indexes
- **Caching**: Django caching for frequent queries
- **Pagination**: API pagination for large datasets
- **Lazy Loading**: Component-based lazy loading

### Security
- **CORS Configuration**: Properly configured for frontend-backend communication
- **Input Validation**: Comprehensive serializer validation
- **SQL Injection Prevention**: Django ORM usage
- **API Key Security**: Environment-based configuration

## 🚀 Deployment

### Backend Deployment
- **Docker**: Dockerfile ready for containerization
- **Environment Variables**: Production-ready configuration
- **Database**: PostgreSQL recommended for production
- **Static Files**: Configured for production serving

### Frontend Deployment
- **Build**: `npm run build` for production build
- **Static Export**: Compatible with static hosting
- **Environment**: Configurable API endpoints

## 🔮 Future Enhancements

### Planned Features
- **User Authentication**: Multi-user support with role-based access
- **Real-time Updates**: WebSocket integration for live updates
- **Mobile App**: React Native companion app
- **Advanced AI**: Custom model fine-tuning for specific use cases
- **Integrations**: Calendar sync, email parsing, Slack integration
- **Analytics**: Detailed productivity analytics and reporting

### AI Improvements
- **Learning**: User feedback integration for model improvement
- **Custom Models**: Domain-specific model training
- **Advanced Context**: Email/calendar API integrations
- **Predictive Analytics**: Task completion prediction and workload optimization

## 📄 License

This project is created as an internship assignment and is available for review and educational purposes.

## 👥 Contributing

This is an internship project, but suggestions and feedback are welcome through the review process.

## 📧 Support

For questions or issues, please refer to the code documentation and test cases, or contact the development team.

---

**Note**: This application demonstrates production-ready development practices including comprehensive testing, proper error handling, type safety, and scalable architecture. The AI integration showcases modern LLM integration patterns with fallback mechanisms for reliability.
