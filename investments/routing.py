from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/investments/(?P<user_id>\w+)/$', consumers.InvestmentConsumer.as_asgi()),
    re_path(r'ws/price-feeds/$', consumers.PriceFeedConsumer.as_asgi()),
    re_path(r'ws/portfolio/(?P<user_id>\w+)/$', consumers.PortfolioConsumer.as_asgi()),
]
