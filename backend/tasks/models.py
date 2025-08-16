from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User


class Category(models.Model):
    """
    Category model for organizing tasks
    Tracks usage frequency for analytics and AI suggestions
    """
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color code
    usage_frequency = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['-usage_frequency', 'name']
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """Increment usage frequency when category is used"""
        self.usage_frequency += 1
        self.save(update_fields=['usage_frequency'])


class Task(models.Model):
    """
    Main Task model with AI-enhanced fields
    Stores both user input and AI-generated suggestions
    """
    
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'), 
        ('done', 'Done'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Core task fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tasks'
    )
    
    # Task management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    deadline = models.DateTimeField(null=True, blank=True)
    
    # AI-enhanced fields
    priority_score = models.FloatField(
        default=50.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="AI-calculated priority score from 0-100"
    )
    enhanced_description = models.TextField(
        blank=True,
        help_text="AI-enhanced version of the description"
    )
    suggested_deadline = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="AI-suggested deadline based on context"
    )
    ai_insights = models.JSONField(
        default=dict,
        help_text="AI-generated insights and metadata"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-priority_score', '-created_at']
        indexes = [
            models.Index(fields=['status', '-priority_score']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Increment category usage when task is created
        if self.pk is None and self.category:
            self.category.increment_usage()
        
        # Set completed_at timestamp when status changes to done
        if self.status == 'done' and not self.completed_at:
            from django.utils import timezone
            self.completed_at = timezone.now()
        elif self.status != 'done':
            self.completed_at = None
            
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.deadline:
            return False
        from django.utils import timezone
        return timezone.now() > self.deadline and self.status != 'done'
    
    @property
    def priority_level(self):
        """Get priority level based on priority_score"""
        if self.priority_score >= 80:
            return 'urgent'
        elif self.priority_score >= 60:
            return 'high'
        elif self.priority_score >= 40:
            return 'medium'
        else:
            return 'low'


class ContextEntry(models.Model):
    """
    Context entries from various sources that inform AI decision making
    Used to provide context for priority scoring and deadline suggestions
    """
    
    SOURCE_TYPE_CHOICES = [
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
        ('note', 'Manual Note'),
        ('calendar', 'Calendar'),
        ('meeting', 'Meeting Notes'),
    ]
    
    content = models.TextField(help_text="Raw content from the source")
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    timestamp = models.DateTimeField(help_text="When this context was created/received")
    
    # AI processing results
    processed_insights = models.JSONField(
        default=dict,
        help_text="AI-extracted insights and metadata from the content"
    )
    relevance_score = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text="How relevant this context is for task prioritization"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'context entries'
        ordering = ['-timestamp', '-relevance_score']
        indexes = [
            models.Index(fields=['source_type', '-timestamp']),
            models.Index(fields=['-relevance_score']),
        ]
    
    def __str__(self):
        return f"{self.get_source_type_display()} - {self.content[:50]}..."
    
    def get_summary(self):
        """Get a brief summary of the context entry"""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."
