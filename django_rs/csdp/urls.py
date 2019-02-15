# from django.conf.urls import url
# from django.views.generic import TemplateView
#
# urlpatterns = [
#     url(r'^$', TemplateView.as_view(template_name="csdp/index.html")),
# ]

from django.conf.urls import url

from . import views

# app_name = 'csdp'
urlpatterns = [
    url(r'^$', views.index, name='index'),
]
