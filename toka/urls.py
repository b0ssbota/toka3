"""
URL configuration for toka project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings

#commit
urlpatterns = [
    path('', home, name='home'),
    path("admin/", admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', signup, name='register'),
    path('logout/', signout_view, name='logout'),
    path('workout/', workout_list, name='workout_list'),
    path('<int:id>/', workout_detail, name='workout_detail'),
    path('membership/', membership_options, name='membership_options'),
    path("aboutus/", about_us, name="aboutus"),
    path('workout-plans/', workoutplan_list, name='workoutplan_list'),
    path('workout-plan/<int:id>/', workoutplan_detail, name='workoutplan_detail'),
    path('workout-plan/<int:id>/purchase/', purchase_workoutplan, name='purchase_workoutplan'),
    path('workout-splan-purchases/', plan_purchase_list, name='plan_purchase_list'),
    path('health-plans/', healthplan_list, name='healthplan_list'),
    path('health-plan/<int:id>/', healthplan_detail, name='healthplan_detail'),
    path('health-plan/<int:id>/purchase/', purchase_healthplan, name='purchase_healthplan'),
    path('health-plan-purchases/', healthplan_purchase_list, name='healthplan_purchase_list'),
    path("contact/", contact, name="contact"),
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)