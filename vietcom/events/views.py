from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Event, EventParticipation

@login_required
def event_list(request):
    """List all events"""
    # Chỉ hiển thị events chưa kết thúc, sắp xếp theo thời gian
    events = Event.objects.filter(time__gt=timezone.now()).order_by('time')
    
    # Phân trang
    paginator = Paginator(events, 12)  # 12 events per page
    page_number = request.GET.get('page')
    events = paginator.get_page(page_number)
    
    # Lấy thông tin tham gia của user hiện tại
    user_participations = {}
    if request.user.is_authenticated:
        participations = EventParticipation.objects.filter(
            user=request.user,
            event__in=[event.id for event in events]
        ).values_list('event_id', flat=True)
        user_participations = {event_id: True for event_id in participations}
    
    context = {
        'events': events,
        'user_participations': user_participations,
    }
    
    return render(request, 'event_list.html', context)

@login_required
def join_event(request, event_id):
    """Join an event"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        
        # Kiểm tra xem user có thể tham gia không
        can_join, message = event.can_user_join(request.user)
        
        if can_join:
            # Tạo participation
            participation, created = EventParticipation.objects.get_or_create(
                event=event,
                user=request.user,
                defaults={'status': 'joined'}
            )
            
            if created:
                messages.success(request, f'🎉 Bạn đã đăng ký tham gia sự kiện "{event.name}" thành công!')
                
                # Track cho gamification
                try:
                    from gamification.views import track_event_joined
                    track_event_joined(request.user)
                except ImportError:
                    pass
            else:
                messages.info(request, 'Bạn đã đăng ký sự kiện này rồi.')
        else:
            messages.error(request, message)
    
    return redirect('events:event_list')

@login_required
def leave_event(request, event_id):
    """Leave an event"""
    if request.method == 'POST':
        event = get_object_or_404(Event, id=event_id)
        
        try:
            participation = EventParticipation.objects.get(
                event=event,
                user=request.user
            )
            participation.delete()
            messages.success(request, f'Bạn đã hủy đăng ký sự kiện "{event.name}".')
        except EventParticipation.DoesNotExist:
            messages.error(request, 'Bạn chưa đăng ký sự kiện này.')
    
    return redirect('events:event_list')

@login_required
def event_detail(request, event_id):
    """Event detail view"""
    event = get_object_or_404(Event, id=event_id)
    
    # Lấy danh sách người tham gia
    participants = EventParticipation.objects.filter(
        event=event, 
        status='joined'
    ).select_related('user')[:20]  # Chỉ hiển thị 20 người đầu
    
    # Kiểm tra user hiện tại có tham gia không
    user_participation = None
    if request.user.is_authenticated:
        try:
            user_participation = EventParticipation.objects.get(
                event=event,
                user=request.user
            )
        except EventParticipation.DoesNotExist:
            pass
    
    # Kiểm tra xem user có thể tham gia không
    can_join, join_message = event.can_user_join(request.user)
    
    context = {
        'event': event,
        'participants': participants,
        'user_participation': user_participation,
        'can_join': can_join,
        'join_message': join_message,
    }
    
    return render(request, 'event_detail.html', context)
