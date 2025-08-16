from django.contrib import admin
from .models import Task, Category, ContextEntry


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'usage_frequency', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name',)
    readonly_fields = ('usage_frequency', 'created_at', 'updated_at')
    ordering = ('-usage_frequency', 'name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'status', 'priority', 'priority_score', 
        'deadline', 'created_at'
    )
    list_filter = (
        'status', 'priority', 'category', 'created_at', 'deadline'
    )
    search_fields = ('title', 'description', 'enhanced_description')
    readonly_fields = (
        'priority_score', 'enhanced_description', 'suggested_deadline',
        'ai_insights', 'completed_at', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Task Management', {
            'fields': ('status', 'priority', 'deadline')
        }),
        ('AI Enhancements', {
            'fields': (
                'priority_score', 'enhanced_description', 'suggested_deadline',
                'ai_insights'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ('-priority_score', '-created_at')


@admin.register(ContextEntry)
class ContextEntryAdmin(admin.ModelAdmin):
    list_display = (
        'get_summary', 'source_type', 'relevance_score', 'timestamp', 'created_at'
    )
    list_filter = ('source_type', 'timestamp', 'created_at')
    search_fields = ('content',)
    readonly_fields = (
        'processed_insights', 'relevance_score', 'created_at', 'updated_at'
    )
    fieldsets = (
        ('Content', {
            'fields': ('content', 'source_type', 'timestamp')
        }),
        ('AI Processing', {
            'fields': ('processed_insights', 'relevance_score'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    ordering = ('-timestamp', '-relevance_score')
    
    def get_summary(self, obj):
        return obj.get_summary()
    get_summary.short_description = 'Content Summary'
