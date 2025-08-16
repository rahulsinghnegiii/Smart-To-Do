"""
AI Task Analyzer Module

This module provides AI-powered task analysis capabilities including:
- Priority scoring based on content and context
- Deadline suggestion based on urgency and workload
- Description enhancement with additional details
- Category suggestions based on content analysis

Design Philosophy:
- Graceful fallback to rule-based logic when AI is unavailable
- Modular design supporting multiple AI providers (OpenAI, Anthropic, LM Studio)
- Clear prompt templates for consistent AI behavior
- Confidence scoring for AI suggestions

The analyzer works in three modes:
1. Remote AI (OpenAI/Anthropic): Uses cloud-based LLM APIs
2. Local AI (LM Studio): Uses locally hosted LLM
3. Fallback: Uses rule-based heuristics when AI is unavailable
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from django.conf import settings
from django.utils import timezone

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class AIAnalysisResult:
    """Structure for AI analysis results"""
    priority_score: float
    suggested_deadline: Optional[datetime] 
    enhanced_description: str
    suggested_categories: List[str]
    confidence_score: float
    reasoning: str
    

class PromptTemplates:
    """
    Centralized prompt templates for consistent AI behavior
    
    These templates are designed to:
    - Extract structured information from task descriptions
    - Consider context from various sources (WhatsApp, email, notes)
    - Provide reasoning for AI decisions
    - Return JSON-formatted responses for easy parsing
    """
    
    TASK_ANALYSIS_PROMPT = """
You are a smart task management assistant. Analyze the following task and provide structured recommendations.

TASK TO ANALYZE:
Title: {title}
Description: {description}
Current Priority: {priority}
Deadline: {deadline}

CONTEXT INFORMATION:
{context_info}

USER PREFERENCES:
{user_prefs}

CURRENT WORKLOAD:
{current_load}

Please provide a JSON response with the following structure:
{{
    "priority_score": <float 0-100>,
    "suggested_deadline": "<ISO datetime or null>",
    "enhanced_description": "<improved description>",
    "suggested_categories": ["<category1>", "<category2>"],
    "confidence_score": <float 0-1>,
    "reasoning": "<explanation of your analysis>"
}}

ANALYSIS GUIDELINES:
1. Priority Score (0-100):
   - 90-100: Critical/Urgent (immediate action required)
   - 70-89: High (important, needs attention soon)
   - 40-69: Medium (normal priority)
   - 0-39: Low (can be deferred)

2. Consider these factors for priority:
   - Urgency keywords: "urgent", "asap", "immediately", "critical"
   - Deadlines and time constraints
   - Dependencies and blocking factors
   - Business impact and stakeholder importance
   - Context from WhatsApp/email indicating urgency

3. Deadline Suggestions:
   - Base on urgency, complexity, and current workload
   - Consider existing deadlines and dependencies
   - Account for realistic time estimates

4. Enhanced Description:
   - Add relevant details from context
   - Clarify ambiguous requirements
   - Add actionable steps if helpful
   - Keep original intent intact

5. Category Suggestions:
   - Analyze content for domain/topic
   - Consider: Work, Personal, Health, Finance, Learning, etc.
   - Maximum 3 relevant categories
   - Use existing categories when appropriate

Respond with valid JSON only.
"""

    CONTEXT_ANALYSIS_PROMPT = """
Analyze this context entry and extract insights relevant to task prioritization:

CONTENT: {content}
SOURCE: {source_type}
TIMESTAMP: {timestamp}

Extract:
1. Urgency indicators
2. Deadline mentions
3. Stakeholder importance
4. Dependencies
5. Business impact

Return JSON:
{{
    "urgency_score": <float 0-1>,
    "deadline_mentions": ["<extracted dates/times>"],
    "stakeholders": ["<people mentioned>"],
    "keywords": ["<important terms>"],
    "sentiment": "<positive/negative/neutral>",
    "relevance_score": <float 0-1>
}}
"""


class TaskAIAnalyzer:
    """
    Main AI analyzer class supporting multiple AI providers and fallback logic
    
    This class implements the core AI functionality with:
    - Multiple AI provider support (OpenAI, Anthropic, LM Studio)
    - Intelligent fallback to rule-based analysis
    - Context-aware priority scoring
    - Deadline prediction based on workload and urgency
    """
    
    def __init__(self):
        self.mode = getattr(settings, 'AI_SERVICE_MODE', 'fallback')
        self.setup_ai_client()
    
    def setup_ai_client(self):
        """Initialize the appropriate AI client based on configuration"""
        try:
            if self.mode == 'openai':
                self._setup_openai()
            elif self.mode == 'anthropic':
                self._setup_anthropic()
            elif self.mode == 'lmstudio':
                self._setup_lmstudio()
            else:
                self.mode = 'fallback'
                logger.info("Using fallback mode for AI analysis")
        except Exception as e:
            logger.warning(f"Failed to setup AI client: {e}. Falling back to rule-based analysis.")
            self.mode = 'fallback'
    
    def _setup_openai(self):
        """Setup OpenAI client"""
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=getattr(settings, 'OPENAI_API_KEY')
            )
            self.model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
            logger.info("OpenAI client initialized successfully")
        except ImportError:
            raise Exception("OpenAI package not installed")
        except Exception as e:
            raise Exception(f"OpenAI setup failed: {e}")
    
    def _setup_anthropic(self):
        """Setup Anthropic client"""
        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=getattr(settings, 'ANTHROPIC_API_KEY')
            )
            self.model = getattr(settings, 'ANTHROPIC_MODEL', 'claude-3-haiku-20240307')
            logger.info("Anthropic client initialized successfully")
        except ImportError:
            raise Exception("Anthropic package not installed")
        except Exception as e:
            raise Exception(f"Anthropic setup failed: {e}")
    
    def _setup_lmstudio(self):
        """Setup LM Studio client (local LLM)"""
        try:
            import openai  # LM Studio uses OpenAI-compatible API
            self.client = openai.OpenAI(
                base_url=getattr(settings, 'LM_STUDIO_BASE_URL', 'http://localhost:1234/v1'),
                api_key="not-needed"  # LM Studio doesn't require API key
            )
            self.model = getattr(settings, 'LM_STUDIO_MODEL', 'local-model')
            logger.info("LM Studio client initialized successfully")
        except ImportError:
            raise Exception("OpenAI package required for LM Studio")
        except Exception as e:
            raise Exception(f"LM Studio setup failed: {e}")
    
    def analyze_task(
        self, 
        task_json: Dict[str, Any], 
        context_entries: Optional[List[Dict]] = None,
        user_prefs: Optional[Dict] = None,
        current_load: Optional[Dict] = None
    ) -> AIAnalysisResult:
        """
        Main analysis method - attempts AI analysis with fallback to rule-based
        
        Args:
            task_json: Task data (title, description, etc.)
            context_entries: Relevant context from various sources
            user_prefs: User preferences and settings
            current_load: Current workload information
            
        Returns:
            AIAnalysisResult with priority score, deadline, enhanced description, etc.
        """
        try:
            if self.mode == 'fallback':
                return self._fallback_analysis(task_json, context_entries, user_prefs, current_load)
            else:
                return self._ai_analysis(task_json, context_entries, user_prefs, current_load)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}. Using fallback.")
            return self._fallback_analysis(task_json, context_entries, user_prefs, current_load)
    
    def _ai_analysis(
        self, 
        task_json: Dict, 
        context_entries: Optional[List[Dict]], 
        user_prefs: Optional[Dict], 
        current_load: Optional[Dict]
    ) -> AIAnalysisResult:
        """Perform AI-powered analysis using configured LLM"""
        
        # Prepare context information
        context_info = self._format_context_entries(context_entries or [])
        user_prefs_str = json.dumps(user_prefs or {}, indent=2)
        current_load_str = json.dumps(current_load or {}, indent=2)
        
        # Create prompt
        prompt = PromptTemplates.TASK_ANALYSIS_PROMPT.format(
            title=task_json.get('title', ''),
            description=task_json.get('description', ''),
            priority=task_json.get('priority', 'medium'),
            deadline=task_json.get('deadline', 'None'),
            context_info=context_info,
            user_prefs=user_prefs_str,
            current_load=current_load_str
        )
        
        # Get AI response
        response = self._get_ai_response(prompt)
        
        # Parse response
        try:
            result_data = json.loads(response)
            return self._create_analysis_result(result_data)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response: {e}")
            return self._fallback_analysis(task_json, context_entries, user_prefs, current_load)
    
    def _get_ai_response(self, prompt: str) -> str:
        """Get response from configured AI provider"""
        try:
            if self.mode == 'openai' or self.mode == 'lmstudio':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful task management assistant. Respond with valid JSON only."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            
            elif self.mode == 'anthropic':
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            logger.error(f"AI provider error: {e}")
            raise
    
    def _format_context_entries(self, context_entries: List[Dict]) -> str:
        """Format context entries for prompt inclusion"""
        if not context_entries:
            return "No additional context available."
        
        formatted = []
        for entry in context_entries[:5]:  # Limit to 5 most relevant entries
            source = entry.get('source_type', 'unknown')
            content = entry.get('content', '')[:200]  # Limit content length
            timestamp = entry.get('timestamp', '')
            formatted.append(f"[{source.upper()}] {timestamp}: {content}")
        
        return "\n".join(formatted)
    
    def _create_analysis_result(self, result_data: Dict) -> AIAnalysisResult:
        """Create AIAnalysisResult from parsed AI response"""
        # Parse suggested deadline
        deadline_str = result_data.get('suggested_deadline')
        suggested_deadline = None
        if deadline_str and deadline_str.lower() != 'null':
            try:
                suggested_deadline = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                # Convert to timezone-aware datetime
                if timezone.is_naive(suggested_deadline):
                    suggested_deadline = timezone.make_aware(suggested_deadline)
            except (ValueError, TypeError):
                logger.warning(f"Could not parse suggested deadline: {deadline_str}")
        
        return AIAnalysisResult(
            priority_score=min(100.0, max(0.0, float(result_data.get('priority_score', 50.0)))),
            suggested_deadline=suggested_deadline,
            enhanced_description=result_data.get('enhanced_description', ''),
            suggested_categories=result_data.get('suggested_categories', []),
            confidence_score=min(1.0, max(0.0, float(result_data.get('confidence_score', 0.5)))),
            reasoning=result_data.get('reasoning', '')
        )
    
    def _fallback_analysis(
        self, 
        task_json: Dict, 
        context_entries: Optional[List[Dict]], 
        user_prefs: Optional[Dict], 
        current_load: Optional[Dict]
    ) -> AIAnalysisResult:
        """
        Rule-based fallback analysis when AI is unavailable
        
        This implements heuristic-based priority scoring and deadline suggestion
        based on keyword analysis, current priority, and context patterns.
        """
        title = task_json.get('title', '').lower()
        description = task_json.get('description', '').lower()
        current_priority = task_json.get('priority', 'medium')
        
        # Keyword-based priority scoring
        priority_score = self._calculate_priority_score(title, description, current_priority, context_entries)
        
        # Rule-based deadline suggestion
        suggested_deadline = self._suggest_deadline(title, description, priority_score, current_load)
        
        # Basic description enhancement
        enhanced_description = self._enhance_description(task_json, context_entries)
        
        # Category suggestions based on keywords
        suggested_categories = self._suggest_categories(title, description)
        
        return AIAnalysisResult(
            priority_score=priority_score,
            suggested_deadline=suggested_deadline,
            enhanced_description=enhanced_description,
            suggested_categories=suggested_categories,
            confidence_score=0.6,  # Medium confidence for rule-based analysis
            reasoning="Analysis performed using rule-based heuristics (AI unavailable)"
        )
    
    def _calculate_priority_score(
        self, 
        title: str, 
        description: str, 
        current_priority: str, 
        context_entries: Optional[List[Dict]]
    ) -> float:
        """Calculate priority score based on keywords and context"""
        
        # Base score from current priority
        priority_base = {
            'low': 25.0,
            'medium': 50.0,
            'high': 75.0,
            'urgent': 90.0
        }.get(current_priority, 50.0)
        
        text = f"{title} {description}"
        
        # Urgency keywords (boost priority)
        urgency_keywords = {
            'urgent': 20, 'asap': 15, 'immediately': 15, 'critical': 20,
            'emergency': 25, 'deadline': 10, 'due': 8, 'important': 5,
            'priority': 5, 'meeting': 8, 'call': 6, 'email': 3
        }
        
        # Calming keywords (reduce priority)
        calming_keywords = {
            'someday': -15, 'maybe': -10, 'later': -8, 'whenever': -12,
            'eventually': -10, 'optional': -15, 'nice to have': -10
        }
        
        score_adjustment = 0
        
        # Check urgency keywords
        for keyword, boost in urgency_keywords.items():
            if keyword in text:
                score_adjustment += boost
        
        # Check calming keywords
        for keyword, reduction in calming_keywords.items():
            if keyword in text:
                score_adjustment += reduction
        
        # Context-based adjustments
        if context_entries:
            for entry in context_entries:
                content = entry.get('content', '').lower()
                source = entry.get('source_type', '')
                
                # WhatsApp and email context often indicate urgency
                if source in ['whatsapp', 'email']:
                    if any(word in content for word in ['urgent', 'asap', 'need', 'help']):
                        score_adjustment += 10
        
        final_score = priority_base + score_adjustment
        return min(100.0, max(0.0, final_score))
    
    def _suggest_deadline(
        self, 
        title: str, 
        description: str, 
        priority_score: float, 
        current_load: Optional[Dict]
    ) -> Optional[datetime]:
        """Suggest deadline based on priority and workload"""
        
        text = f"{title} {description}"
        now = timezone.now()
        
        # Look for explicit time indicators
        time_patterns = {
            r'today|asap|immediately': 0.25,  # 6 hours
            r'tomorrow|by tomorrow': 1,       # 1 day
            r'this week|end of week': 7,      # 1 week
            r'next week': 14,                 # 2 weeks
            r'month|monthly': 30,             # 1 month
        }
        
        for pattern, days in time_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return now + timedelta(days=days)
        
        # Priority-based deadline suggestion
        if priority_score >= 80:      # Urgent
            days_ahead = 1
        elif priority_score >= 60:    # High
            days_ahead = 3
        elif priority_score >= 40:    # Medium
            days_ahead = 7
        else:                         # Low
            days_ahead = 14
        
        # Adjust based on current workload
        if current_load:
            task_count = current_load.get('active_tasks', 0)
            if task_count > 10:
                days_ahead *= 1.5  # Add more time if overloaded
        
        return now + timedelta(days=days_ahead)
    
    def _enhance_description(self, task_json: Dict, context_entries: Optional[List[Dict]]) -> str:
        """Basic description enhancement using context"""
        original_desc = task_json.get('description', '')
        
        if not original_desc:
            return ''
        
        enhanced = original_desc
        
        # Add context insights if available
        if context_entries:
            relevant_context = []
            for entry in context_entries[:2]:  # Limit to 2 most relevant
                if entry.get('source_type') in ['email', 'whatsapp']:
                    content = entry.get('content', '')[:100]
                    relevant_context.append(f"Context from {entry['source_type']}: {content}...")
            
            if relevant_context:
                enhanced += "\n\nAdditional context:\n" + "\n".join(relevant_context)
        
        return enhanced
    
    def _suggest_categories(self, title: str, description: str) -> List[str]:
        """Suggest categories based on keyword analysis"""
        text = f"{title} {description}".lower()
        
        category_keywords = {
            'work': ['meeting', 'project', 'deadline', 'client', 'business', 'office', 'presentation'],
            'health': ['doctor', 'appointment', 'exercise', 'gym', 'medicine', 'health', 'workout'],
            'finance': ['payment', 'bill', 'money', 'bank', 'budget', 'expense', 'invoice'],
            'personal': ['family', 'friend', 'home', 'personal', 'hobby', 'vacation', 'birthday'],
            'learning': ['study', 'course', 'learn', 'read', 'book', 'training', 'education'],
            'shopping': ['buy', 'purchase', 'shop', 'order', 'grocery', 'store'],
            'maintenance': ['repair', 'fix', 'clean', 'maintenance', 'service', 'update'],
        }
        
        suggestions = []
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                suggestions.append(category)
        
        # Limit to top 3 categories
        return suggestions[:3]


# Singleton instance for use throughout the application
task_analyzer = TaskAIAnalyzer()
