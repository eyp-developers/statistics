from django.urls import path

from statisticscore.e2e import views

# Test-only endpoints used by the Playwright suite in /e2e to set up data over HTTP.
# Every view returns 404 unless E2E_ENDPOINTS_ENABLED is set and the request carries the E2E_TOKEN.

app_name = 'e2e'

urlpatterns = [
    path('sessions/', views.create_session, name='create_session'),
    path('sessions/<int:session_id>/', views.delete_session, name='delete_session'),
    path('sessions/<int:session_id>/state/', views.session_state, name='session_state'),
    path('sessions/<int:session_id>/data/', views.session_data, name='session_data'),
    path('login/', views.login_as, name='login'),
]
