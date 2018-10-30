from django.conf.urls import include, url
from rest_framework import routers
from push_notifications.api.rest_framework import GCMDeviceAuthorizedViewSet, GCMDevice

import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)
# router.register(r'knnnodes', views.KnnNodeViewSet, base_name='knnnodes')
router.register(r'sessions', views.SessionViewSet)
router.register(r'sessions/(?P<session>[0-9]+)/activities', views.SessionActivityViewSet, base_name='session-activities')
router.register(r'sessions/(?P<session>[0-9]+)/users', views.SessionUserViewSet, base_name='session-users')
router.register(r'sessions/(?P<session>[0-9]+)/nodes', views.SessionGraphNodeViewSet, base_name='session-nodes')
router.register(r'device/gcm', GCMDeviceAuthorizedViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]