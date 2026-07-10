"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from backend.config import settings
api_patterns = [ 
    path("auth/",include("users.urls")), 
    path("products/",include("products.urls")),
    path("cart/",include("cart.urls")),
    path("orders/",include("orders.urls")),
    path("payments/", include("apps.payments.urls")),
    path("ai/", include("apps.ai_assistant.urls")),
    path("search/", include("apps.search.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),

]
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(api_patterns)),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
