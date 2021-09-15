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

CALENDAR_LIST_API  = 'https://www.googleapis.com/calendar/v3/users/me/calendarList?access_token='
CALENDAR_API       = 'https://www.googleapis.com/calendar/v3/calendars/'
EVENTS_CONDITION   = '/events?showDeleted=False&singleEvents=True&access_token='
REFERENCE_CALENDAR = 'c_classroom1c823bba@group.calendar.google.com'
REFERENCE_DATE     = '2021-06-07'

class GoogleLoginView(View):
    def get(self, request):
        return render(request, 'google/index.html')

class FetchView(View):
    def get(self, request):
        return render(request, 'calendars/fetch.html')

class ResultSuccessView(View):
    def get(self, request):
        return render(request, 'calendars/success.html')

class CalendarView(View):
    def get(self, request, calendar_id):

        calendar = get_object_or_404(Calendar, pk = calendar_id)
        return render(request, 'calendars/detail.html', {'calendar' : calendar})

class GoogleCalendarsView(View):
    def get(self, request):
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)

        response = requests.get(CALENDAR_LIST_API + token)
         
        if not response.ok:
            return JsonResponse({'message' : response.json()}, status=400)

        calendar_list = response.json()['items']
        return JsonResponse({'data' : calendar_list}, status=200)

class GoogleCalendarEventsView(View):
    def get(self, request, calendar_id):
        token = request.headers.get('Authorization')

        if not token:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
        
        response = requests.get(CALENDAR_API + calendar_id + EVENTS_CONDITION +token)
        
        if not response.ok:
            return JsonResponse({'message' : response.json()}, status=400)
        
        events = [
            {
                'id'          : event['id'],
                'name'        : event.get('summary', None),
                'description' : event.get('description', None),
                'start_time'  : event['start']['dateTime'] if 'start' in event else None,
                'end_time'    : event['end']['dateTime'] if 'end' in event else None
            } for event in response.json()['items']
        ]
        print(response.json()['items'][15]['end']['dateTime']) 
        print(type(response.json()['items'][0]['end']['dateTime']) )
        print(type(datetime.strptime(response.json()['items'][0]['end']['dateTime'], '%Y-%m-%dT%H:%M:%SZ')))
        return JsonResponse({'events' : events, 'number_of_events' : len(events)}, status=200)

    def post(self, request, calendar_id):
        try:
            token           = request.headers['Authorization']
            payload         = json.loads(request.body)
            start_holiday   = payload.get('start_holiday', '2100-01-01')
            start_batch     = datetime.strptime(payload['start_batch'], '%Y-%m-%d')
            start_reference = datetime.strptime(REFERENCE_DATE, '%Y-%m-%d')
            
            delta_days      = (start_batch - start_reference).days
            delta_weeks     = delta_days // 7
            
            response        = requests.get(CALENDAR_API + REFERENCE_CALENDAR + EVENTS_CONDITION +token)
            
            if not response.ok:
                return JsonResponse({'message' : response.json()}, status=400)
            
            print('REFERENC_CALENDAR : ', response.json()['summary'])
            referenced_events = response.json()['items']


            for event in referenced_events:
                print('CURRENT_EVENT: ', event['summary'])
                print('DATE_TIME: ', event['start']['dateTime'][:10])
                print(event['start']['dateTime'])

                start_time      = datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
                end_time        = datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%SZ')
                start_timedelta = start_time + timedelta(weeks=delta_weeks)
                end_timedelta   = end_time + timedelta(weeks=delta_weeks)
                
                if datetime.strptime(start_holiday, '%Y-%m-%d') <= start_timedelta:
                    start_timedelta += timedelta(weeks=1)
                    end_timedelta   += timedelta(weeks=1)
                
                calender_body = {
                    'summary'     : event['summary'],
                    'description' : event.get('description', ''),
                    'start'       : { 'dateTime' : start_timedelta.strftime('%Y-%m-%dT%H:%M:%SZ') },
                    'end'         : { 'dateTime' : end_timedelta.strftime('%Y-%m-%dT%H:%M:%SZ') },
                }
            
                copy = requests.post(CALENDAR_API + calendar_id + EVENTS_CONDITION + token, json=calender_body)
        
            return JsonResponse({'result' : response.json()}, status=200)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)
    
    def delete(self, request, calendar_id):
        token = request.headers['Authorization']
        event_list = requests.get(f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events?showDeleted=False&singleEvents=True&access_token=' + token).json()
        
        for event in event_list['items']:
            print(event['summary'])
            event_id = event['id']
            
            a = requests.delete(f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events/{event_id}?showDeleted=False&singleEvents=True&access_token=' + token)
                                
        return JsonResponse({'messae': 'ok'})