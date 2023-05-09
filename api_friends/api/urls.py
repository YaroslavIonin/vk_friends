from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import RegisterView, BidView, FriendsView

router = DefaultRouter()
# router.register('bid', BidViewSet, basename='bid')
# router.register('friends', FriendsViewSet, basename='friends')

urlpatterns = [
    path('register/', RegisterView.as_view()),

    path('bids/', BidView.as_view({
        'get': 'list',
        'post': 'create'
    })),
    path('bids/check_status/', BidView.as_view({
        'get': 'check_status',
    })),
    path('bids/<int:pk>', BidView.as_view({
        'patch': 'update'
    })),
    path('friends/', FriendsView.as_view({
        'get': 'list',
    })),
    path('friends/<int:pk>', FriendsView.as_view({
        'delete': 'destroy'
    }))
]

urlpatterns += router.urls
