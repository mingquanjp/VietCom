from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Event

@login_required
def event_list(request):
    """List all events"""
    events = Event.objects.all()[:20]
    
    context = {
        'events': events
    }
    
    return render(request, 'event_list.html', context)

@login_required
def create_event(request):
    """Create a new event"""
    return render(request, 'create_event.html')

@login_required
def event_detail(request, event_id):
    """Event detail view"""
    event = get_object_or_404(Event, id=event_id)
    
    context = {
        'event': event
    }
    
    return render(request, 'event_detail.html', context)
