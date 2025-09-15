from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Customer-facing URLs
    path('widget/', views.chat_widget, name='chat_widget'),
    path('start-conversation/', views.start_conversation, name='start_conversation'),
    path('send-message/', views.send_message, name='send_message'),
    path('messages/<str:conversation_id>/', views.get_messages, name='get_messages'),
    
    # Staff URLs
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/conversations/', views.get_conversations, name='get_conversations'),
    path('staff/assign/<str:conversation_id>/', views.assign_conversation, name='assign_conversation'),
    path('staff/close/<str:conversation_id>/', views.close_conversation, name='close_conversation'),
    path('staff/online-status/', views.update_online_status, name='update_online_status'),
]
