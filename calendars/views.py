import json
import requests
import progressbar

from time                   import sleep
from pprint                 import pprint
from datetime               import datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.http      import HttpResponse, JsonResponse
from django.views     import View
from django.shortcuts import render, get_object_or_404

from .models import Batch, Calendar


token = "ya29.a0AfH6SMBtPkM8F-eKJD4liR4GwxJwL_IiBya-Z7vpkmdtXQ8dY3x3gOBSDSh3xAHM-Dr2u5gjkAF8vpHuVz61U3s0ky-vOH5CBSVpGkGbguy96P9LEL_Q8d_d1JX5qIeGDhjpyTitY7_puCahTJXq3QLr_uxaYStYZsFU9XVpGtw"

class BatchesView(View):
    def get(self, request):

        batch_list = Batch.objects.all()
        output = ', '.join([batch.name for batch in batch_list])
        context = {'batch_list' : batch_list}

        return render(request, 'batches/index.html', context)

class CalendarsView(View):
    def get(self, request):

        calendar_list = Calendar.objects.all()
        output = ', '.join([calendar.name for calendar in calendar_list])
        context = {'calendar_list' : calendar_list}

        return render(request, 'calendars/index.html', context)

class CalendarView(View):
    def get(self, request, calendar_id):

        calendar = get_object_or_404(Calendar, pk = calendar_id)
        return render(request, 'calendars/detail.html', {'calendar' : calendar})

class GoogleCalendarsView(View):
    def get(self, request):
        google_calendar_list = requests.get('https://www.googleapis.com/calendar/v3/users/me/calendarList?access_token=' + token)

        calendars = google_calendar_list.json()['items']
        batch_calendars = [calendar for calendar in calendars]
        output = ', '.join([calendar['summary'] for calendar in batch_calendars])
        return JsonResponse({'result':batch_calendars}, status=200)

class GoogleCalendarEventsView(View):
    def get(self, request, calendar_id):
        event_list = requests.get(f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?showDeleted=False&singleEvents=True&access_token=' + token)

        print("CURRENT_CALENDAR : ", event_list.json()['summary'])

        events = [
            {
                'id' : event['id'],
                'name' : event.get('summary', None),
                'start_time' : event['start']['dateTime'] if 'start' in event else None,
                'end_time' : event['end']['dateTime'] if 'end' in event else None
            } for event in event_list.json()['items']
        ]

        return JsonResponse({'events' : events, 'number_of_events' : len(events)}, status=200)

    def post(self, request, calendar_id):
        payload = json.loads(request.body)

        referenced_calendar_id  = payload['referenced_calendar_id']
        week_added = payload['week_added']
        referenced_event_list   = requests.get(f'https://www.googleapis.com/calendar/v3/calendars/{referenced_calendar_id}/events?showDeleted=False&singleEvents=True&access_token=' + token)

        print('CURRENT_CALENDAR : ', referenced_event_list.json()['summary'])
        events = referenced_event_list.json()['items']

        for event in events:

            print('CURRENT_EVENT: ', event['summary'])
            print('DATE_TIME: ', event['start']['dateTime'][:10])


            if datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%SZ') < datetime(2021, 2, 8):
                body = {
                    'summary' : event['summary'].replace('[16기]',''),
                    'start' : { 'dateTime' : (datetime.strptime(event['start']['dateTime'],'%Y-%m-%dT%H:%M:%SZ') +
relativedelta(weeks=week_added)).strftime('%Y-%m-%dT%H:%M:%SZ') },
                    'end' : { 'dateTime' : (datetime.strptime(event['end']['dateTime'],'%Y-%m-%dT%H:%M:%SZ') + relativedelta(weeks=week_added)).strftime('%Y-%m-%dT%H:%M:%SZ') },
                }

            else:
                body = {
                    'summary' : event['summary'].replace('[16기]',''),
                    'start' : { 'dateTime' : (datetime.strptime(event['start']['dateTime'],'%Y-%m-%dT%H:%M:%SZ') + relativedelta(weeks=week_added-1)).strftime('%Y-%m-%dT%H:%M:%SZ') },
                    'end' : { 'dateTime' : (datetime.strptime(event['end']['dateTime'],'%Y-%m-%dT%H:%M:%SZ') + relativedelta(weeks=week_added-1)).strftime('%Y-%m-%dT%H:%M:%SZ') },
                }

#            if '[16기]' in event['summary']:
#                body['summary'] = event['summary'].replace('[16기]', '')
#
#            if '[Back]' in event['summary']:
#                body['summary'] = event['summary'].replace('[Back]', 'Session - Back |')
#
#            if '[Front]' in event['summary']:
#                body['summary'] = event['summary'].replace('[Front]', 'Session - Front |')
#
#            if 'Code Kata' in event['summary']:
#                body['summary'] = event['summary'].replace(event['summary'][-3]+'주차', 'week'+event['summary'][-3])
#
#            if '1:1 면담' in event['summary']:
#                continue

            a = requests.post(f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?access_token=' + token, json=body)

        return JsonResponse({'result' : 'ok'}, status=200)

    def delete(self, request, calendar_id):
        event_list = requests.get(f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?showDeleted=False&singleEvents=True&access_token=' + token).json()['items']

        for event in event_list:
            print(event['summary'])
            event_id = event['id']
            a = requests.delete(f"https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}?access_token=" + token)

        return JsonResponse({'messae': 'ok'})
