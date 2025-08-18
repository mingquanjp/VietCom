from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Event, EventParticipation

# Register your models here.

class EventParticipationInline(admin.TabularInline):
    model = EventParticipation
    extra = 0
    fields = ['user', 'status', 'joined_at']
    readonly_fields = ['joined_at']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'creator', 
        'time_display', 
        'location_desc', 
        'max_participants',
        'participant_count_display',
        'available_spots_display',
        'status_display',
        'created_at'
    ]
    list_filter = ['time', 'created_at', 'creator', 'max_participants']
    search_fields = ['name', 'description', 'location_desc', 'creator__username']
    ordering = ['-time']
    list_per_page = 25
    date_hierarchy = 'time'
    inlines = [EventParticipationInline]
    
    # Remove fields since we're using fieldsets
    fieldsets = (
        ('Thông tin sự kiện', {
            'fields': ('name', 'description', 'creator', 'image')
        }),
        ('Thời gian & Giới hạn', {
            'fields': ('time', 'max_participants')
        }),
        ('Địa điểm', {
            'fields': ('location_desc', 'latitude', 'longitude')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ['created_at']
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Set default creator to current admin user
        if not obj:  # Creating new event
            form.base_fields['creator'].initial = request.user
        return form
    
    inlines = [EventParticipationInline]
    
    def time_display(self, obj):
        """Display event time with formatting"""
        if obj.is_past:
            return format_html(
                '<span style="color: gray; text-decoration: line-through;">{}</span>',
                obj.time.strftime('%Y-%m-%d %H:%M')
            )
        else:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}</span>',
                obj.time.strftime('%Y-%m-%d %H:%M')
            )
    time_display.short_description = 'Event Time'
    time_display.admin_order_field = 'time'
    
    def participant_count_display(self, obj):
        """Display participant count with colors"""
        joined = obj.participant_count
        interested = obj.interested_count
        total = joined + interested
        
        return format_html(
            '<span style="color: green; font-weight: bold;">👥 {}</span> '
            '(<span style="color: orange;">💡 {}</span>)',
            joined, interested
        )
    participant_count_display.short_description = 'Participants (Interested)'
    
    def available_spots_display(self, obj):
        """Display available spots with colors"""
        available = obj.available_spots
        if available == 0:
            return format_html('<span style="color: red; font-weight: bold;">🚫 Full</span>')
        elif available <= 5:
            return format_html('<span style="color: orange; font-weight: bold;">⚠️ {}</span>', available)
        else:
            return format_html('<span style="color: green; font-weight: bold;">✅ {}</span>', available)
    available_spots_display.short_description = 'Available'
    
    def status_display(self, obj):
        """Display event status"""
        if obj.is_past:
            return format_html('<span style="color: red;">⏰ Past</span>')
        else:
            return format_html('<span style="color: green;">🔥 Upcoming</span>')
    status_display.short_description = 'Status'
    
    actions = ['mark_as_featured', 'send_reminder']
    
    def mark_as_featured(self, request, queryset):
        """Custom action placeholder"""
        count = queryset.count()
        self.message_user(request, f'{count} event(s) marked as featured.')
    mark_as_featured.short_description = "Mark selected events as featured"
    
    def send_reminder(self, request, queryset):
        """Custom action placeholder"""
        upcoming_events = queryset.filter(time__gt=timezone.now())
        count = upcoming_events.count()
        self.message_user(request, f'Reminders sent for {count} upcoming event(s).')
    send_reminder.short_description = "Send reminder for upcoming events"


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = [
        'event_name',
        'user', 
        'status_display', 
        'event_time',
        'joined_at'
    ]
    list_filter = ['status', 'joined_at', 'event__time']
    search_fields = [
        'event__name', 
        'user__username', 
        'user__email',
        'user__full_name'
    ]
    ordering = ['-joined_at']
    list_per_page = 30
    date_hierarchy = 'joined_at'
    
    def event_name(self, obj):
        """Display event name as link"""
        if obj.event.is_past:
            return format_html(
                '<span style="color: gray;">{}</span>',
                obj.event.name
            )
        return obj.event.name
    event_name.short_description = 'Event'
    event_name.admin_order_field = 'event__name'
    
    def event_time(self, obj):
        """Display event time"""
        return obj.event.time.strftime('%Y-%m-%d %H:%M')
    event_time.short_description = 'Event Time'
    event_time.admin_order_field = 'event__time'
    
    def status_display(self, obj):
        """Display status with icons"""
        if obj.status == 'joined':
            return format_html('<span style="color: green; font-weight: bold;">✅ Joined</span>')
        else:
            return format_html('<span style="color: orange; font-weight: bold;">💡 Interested</span>')
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    actions = ['convert_to_joined', 'convert_to_interested']
    
    def convert_to_joined(self, request, queryset):
        """Convert interested to joined"""
        updated = queryset.filter(status='interested').update(status='joined')
        self.message_user(request, f'{updated} participation(s) converted to joined.')
    convert_to_joined.short_description = "Convert to Joined"
    
    def convert_to_interested(self, request, queryset):
        """Convert joined to interested"""
        updated = queryset.filter(status='joined').update(status='interested')
        self.message_user(request, f'{updated} participation(s) converted to interested.')
    convert_to_interested.short_description = "Convert to Interested"
