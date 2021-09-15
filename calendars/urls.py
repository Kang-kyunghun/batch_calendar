from django.urls import path

from .views import (
    GoogleLoginView,
    FetchView,
    CalendarView,
    GoogleCalendarsView,
    GoogleCalendarEventsView,
    ResultSuccessView,
)

app_name = 'calendars'
urlpatterns = [
    #path('/google', GoogleLoginView.as_view()),
    path('/fetch', FetchView.as_view()),
    path('/success', ResultSuccessView.as_view()),
    #path('/<str:calendar_id>', CalendarView.as_view(), name='detail'),
    path('/google', GoogleCalendarsView.as_view()),
    path('/google/<str:calendar_id>/events', GoogleCalendarEventsView.as_view()),
]

