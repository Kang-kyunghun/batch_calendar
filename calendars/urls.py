from django.urls import path

from .views import (
    BatchesView,
    CalendarView,
    CalendarsView,
    GoogleCalendarsView,
    GoogleCalendarEventsView
)

app_name = 'calendars'
urlpatterns = [
    path('', CalendarsView.as_view()),
    path('/<int:calendar_id>', CalendarView.as_view(), name='detail'),
    path('/batches', BatchesView.as_view()),
    path('/google', GoogleCalendarsView.as_view()),
    path('/google/<str:calendar_id>/events', GoogleCalendarEventsView.as_view()),
]

