from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'apcweb.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$','apc.views.index', name='control'),
    url(r'^login/$', 'apc.views.login', name='login'),
    url(r'logout/', 'apc.views.logout', name='logout' ),
    )
