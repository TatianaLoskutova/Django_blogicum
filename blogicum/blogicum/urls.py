from django.contrib import admin
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.urls import path, include, reverse_lazy
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from django.conf import settings
from django.conf.urls.static import static


handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        CreateView.as_view(
            template_name='registration/registration_form.html',
            form_class=UserCreationForm,
            success_url=reverse_lazy('blog:index'),
        ),
        name='registration',
    ),
    path(
        'auth/password_change/',
        PasswordChangeView.as_view(
            template_name='registration/password_change_form.html',
            success_url=reverse_lazy('blog:index'),
        ),
        name='password_change',
    ),
    path(
        'auth/password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='registration/password_change_done.html',
        ),
        name='password_change_done',
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)