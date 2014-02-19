from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'apcweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','apc.views.index', name='status'),
    url(r'^login/$', 'apc.views.login', name='login'),
    url(r'logout/', 'apc.views.logout', name='logout' ),
    url(r'^control/$', 'apc.views.control', name='control'),
    url(r'control/(?P<outlet_id>\d+)/$', 'apc.views.control', name='outletcontrol'),
    url(r'config/$', 'apc.views.config', name='config')
    )
