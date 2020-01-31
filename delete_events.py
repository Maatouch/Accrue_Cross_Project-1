import requests
import json
import csv
import os
from functions import *
URLevents = 'http://db.accrue.com/api/events'


def delete_events(event_ids,URLevents=URLevents,auth_token=auth_token):

    for event_id in event_ids[0:50]:
        print(event_ids.index(event_id))
        URLevent = URLevents + "/" + str(event_id)
        print(str(event_id))
        PARAMSdeleteevent = {"auth-token": auth_token}
        response= requests.delete(url=URLevent, params=PARAMSdeleteevent)
        print(response)

        if response.status_code !=204:
            with open("events_ids_not_deleted.csv", "a", newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(event_id)])
    return 1


def delete_events_in_file(file='events_ids.txt'):
    with open(file, 'r') as f:
        reader = csv.reader(f)
        event_ids = list(reader)


    event_ids = [i[0] for i in event_ids]
    print(event_ids)
    delete_events(event_ids)


delete_events_in_file('events_ids.csv')

