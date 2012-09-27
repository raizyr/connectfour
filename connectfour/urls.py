from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'game.views.home', name='home'),
    # url(r'^connectfour/', include('connectfour.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^game/$', 'game.views.index'),
    url(r'^game/(?P<algo>\w+)/$', 'game.views.index'),
    url(r'^game/(?P<algo>\w+)/(?P<diff>\d{1})/$', 'game.views.index'),
)
