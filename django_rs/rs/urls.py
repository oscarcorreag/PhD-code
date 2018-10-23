from django.conf.urls import include, url
from rest_framework import routers
import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'knnnodes', views.KnnNodeViewSet, base_name='knnnodes')
router.register(r'sessions', views.SessionViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]