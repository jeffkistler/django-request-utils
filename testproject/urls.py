from django.conf.urls.defaults import patterns, include, handler500, url
from django.conf import settings
from django.contrib import admin
admin.autodiscover()

handler500 # Pyflakes

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^.*$', 'django.views.generic.simple.direct_to_template', {'template': 'index.html'}),
)
