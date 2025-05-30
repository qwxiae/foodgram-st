from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from recipes.views import redirect_to_full_recipe

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
    path('s/<str:short_url>/', redirect_to_full_recipe),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)