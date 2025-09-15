import json
import uuid
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import ChatConversation, ChatMessage, ChatTypingIndicator, ChatOnlineStatus, ChatSettings
from .serializers import ChatConversationSerializer, ChatMessageSerializer


def chat_widget(request):
    """Render the chat widget for customers"""
    settings = ChatSettings.get_settings()
    
    # Check if chat is enabled
    if not settings.is_enabled:
        return JsonResponse({'enabled': False})
    
    # Get or create conversation for authenticated user
    conversation = None
    if request.user.is_authenticated:
        conversation = ChatConversation.objects.filter(
            customer=request.user,
            status__in=['active', 'waiting']
        ).first()
    
    # Get online staff count
    online_staff_count = ChatOnlineStatus.objects.filter(is_online=True).count()
    
    context = {
        'conversation': conversation,
        'settings': settings,
        'online_staff_count': online_staff_count,
        'is_online': online_staff_count > 0,
    }
    
    return render(request, 'chat/chat_widget.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def start_conversation(request):
    """Start a new conversation"""
    try:
        data = json.loads(request.body)
        
        # Create conversation ID
        conversation_id = str(uuid.uuid4())
        
        # Get customer info
        customer = request.user if request.user.is_authenticated else None
        customer_name = data.get('customer_name', '')
        customer_email = data.get('customer_email', '')
        customer_phone = data.get('customer_phone', '')
        subject = data.get('subject', 'General Inquiry')
        
        # Create conversation
        conversation = ChatConversation.objects.create(
            id=conversation_id,
            customer=customer,
            customer_name=customer_name or (customer.get_full_name() if customer else 'Anonymous'),
            customer_email=customer_email or (customer.email if customer else ''),
            customer_phone=customer_phone,
            subject=subject,
            status='waiting'
        )
        
        # Send welcome message
        settings = ChatSettings.get_settings()
        if settings.welcome_message:
            # Create a system message
            system_user = User.objects.filter(is_staff=True).first()
            if system_user:
                ChatMessage.objects.create(
                    conversation=conversation,
                    sender=system_user,
                    content=settings.welcome_message,
                    message_type='system'
                )
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation_id,
            'message': 'Conversation started successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def send_message(request):
    """Send a message in a conversation"""
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        
        if not conversation_id or not content:
            return JsonResponse({
                'success': False,
                'error': 'Conversation ID and content are required'
            }, status=400)
        
        # Get conversation
        conversation = get_object_or_404(ChatConversation, id=conversation_id)
        
        # Check if user can send messages to this conversation
        if request.user.is_authenticated:
            if not conversation.customer == request.user and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'Unauthorized'
                }, status=403)
        else:
            # For anonymous users, check if they provided the right info
            if not conversation.customer_name or conversation.customer:
                return JsonResponse({
                    'success': False,
                    'error': 'Unauthorized'
                }, status=403)
        
        # Determine sender
        if request.user.is_authenticated:
            sender = request.user
        else:
            # For anonymous users, create a temporary user or use system user
            sender = User.objects.filter(is_staff=True).first()
            if not sender:
                return JsonResponse({
                    'success': False,
                    'error': 'No staff available'
                }, status=500)
        
        # Create message
        message = ChatMessage.objects.create(
            conversation=conversation,
            sender=sender,
            content=content,
            message_type=message_type
        )
        
        # Update conversation status
        if conversation.status == 'waiting':
            conversation.status = 'active'
            conversation.save()
        
        return JsonResponse({
            'success': True,
            'message_id': message.id,
            'message': 'Message sent successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def get_messages(request, conversation_id):
    """Get messages for a conversation"""
    try:
        conversation = get_object_or_404(ChatConversation, id=conversation_id)
        
        # Check permissions
        if request.user.is_authenticated:
            if not conversation.customer == request.user and not request.user.is_staff:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
        else:
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        # Get messages
        messages = conversation.messages.all().order_by('created_at')
        
        # Mark messages as read for staff
        if request.user.is_staff:
            messages.filter(is_read=False).update(is_read=True)
        
        # Serialize messages
        message_data = []
        for message in messages:
            message_data.append({
                'id': message.id,
                'content': message.content,
                'sender': message.sender_display_name,
                'is_from_customer': message.is_from_customer,
                'is_from_staff': message.is_from_staff,
                'message_type': message.message_type,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read,
                'is_edited': message.is_edited,
            })
        
        return JsonResponse({
            'success': True,
            'messages': message_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@require_http_methods(["GET"])
def get_conversations(request):
    """Get conversations for staff dashboard"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    try:
        # Get filter parameters
        status = request.GET.get('status', 'all')
        search = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 20))
        
        # Build query
        conversations = ChatConversation.objects.all()
        
        if status != 'all':
            conversations = conversations.filter(status=status)
        
        if search:
            conversations = conversations.filter(
                Q(customer_name__icontains=search) |
                Q(customer__username__icontains=search) |
                Q(subject__icontains=search) |
                Q(customer_email__icontains=search)
            )
        
        # Paginate
        paginator = Paginator(conversations, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize conversations
        conversation_data = []
        for conversation in page_obj:
            conversation_data.append({
                'id': conversation.id,
                'customer_name': conversation.customer_display_name,
                'subject': conversation.subject,
                'status': conversation.status,
                'priority': conversation.priority,
                'created_at': conversation.created_at.isoformat(),
                'last_message_at': conversation.last_message_at.isoformat() if conversation.last_message_at else None,
                'staff_member': conversation.staff_member.username if conversation.staff_member else None,
                'unread_count': conversation.messages.filter(is_read=False, sender__is_staff=False).count(),
            })
        
        return JsonResponse({
            'success': True,
            'conversations': conversation_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total_pages': paginator.num_pages,
                'total_count': paginator.count,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def assign_conversation(request, conversation_id):
    """Assign conversation to staff member"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    try:
        conversation = get_object_or_404(ChatConversation, id=conversation_id)
        conversation.assign_to_staff(request.user)
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation assigned successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def close_conversation(request, conversation_id):
    """Close a conversation"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    try:
        conversation = get_object_or_404(ChatConversation, id=conversation_id)
        conversation.close_conversation()
        
        return JsonResponse({
            'success': True,
            'message': 'Conversation closed successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def update_online_status(request):
    """Update staff online status"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    try:
        data = json.loads(request.body)
        is_online = data.get('is_online', False)
        status_message = data.get('status_message', 'Available')
        
        online_status, created = ChatOnlineStatus.objects.get_or_create(
            user=request.user,
            defaults={'is_online': is_online, 'status_message': status_message}
        )
        
        if not created:
            online_status.is_online = is_online
            online_status.status_message = status_message
            online_status.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Online status updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def staff_dashboard(request):
    """Staff chat dashboard"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Staff access required'}, status=403)
    
    # Get conversation statistics
    total_conversations = ChatConversation.objects.count()
    active_conversations = ChatConversation.objects.filter(status='active').count()
    waiting_conversations = ChatConversation.objects.filter(status='waiting').count()
    closed_conversations = ChatConversation.objects.filter(status='closed').count()
    
    # Get recent conversations
    recent_conversations = ChatConversation.objects.filter(
        status__in=['active', 'waiting']
    ).order_by('-last_message_at')[:10]
    
    # Get online staff
    online_staff = ChatOnlineStatus.objects.filter(is_online=True)
    
    context = {
        'total_conversations': total_conversations,
        'active_conversations': active_conversations,
        'waiting_conversations': waiting_conversations,
        'closed_conversations': closed_conversations,
        'recent_conversations': recent_conversations,
        'online_staff': online_staff,
    }
    
    return render(request, 'chat/staff_dashboard.html', context)
