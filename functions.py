import requests
from datetime import *
from configuration import *
import csv
import traceback
from os import chdir, remove
import time
from threading import Timer


class MyError(Exception):
    def __init__(self, error_name, error_infos=""):
        self.error_name = error_name
        self.error_infos = error_infos


def sign(x):
    return (x > 0) - (x < 0)


def initialize_data_files_with_headers():
    with open("success.csv", "w", newline='') as f:
        f_names = ["symbol", "golden", "deaths", "last_update", "number-of-added-dates"]
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()

    with open("errors.csv", "w", newline='') as f:
        f_names = ["symbol", "date", "error_type", "error_code"]
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()

    with open("update_errors.csv", "w", newline='') as f:
        f_names = ["symbol", "date", "error_type", "error_code"]
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()

    with open("update_summary_file.csv", "w", newline='') as f:
        f_names = ['date', 'number_of_processed_symbs', 'number_of_modified_symbs', 'nbr_dates_added', 'nbr_errors']
        writer = csv.DictWriter(f, delimiter='\t', fieldnames=f_names)
        writer.writeheader()


def get_data(symbol, start_date, end_date, url=URL_data, auth_token=auth_token):
    PARAMS = {'auth-token': auth_token, 'symbol': symbol, 'type': 'daily', 'start-date': start_date,
              'end-date': end_date}

    response = requests.get(url=url, params=PARAMS)
    # handle get data error#
    if response.status_code != 200:
        raise MyError("response error", str(response.status_code))

    return response


def post_data(url, params):
    response = requests.post(url=url, params=params)
    return response


def delete_events(event_ids, URLevents=URL_events, auth_token=auth_token):
    for event_id in event_ids:
        URLevent = URLevents + "/" + str(event_id)
        PARAMSdeleteevent = {"auth-token": auth_token}
        response = requests.delete(url=URLevent, params=PARAMSdeleteevent)
        # handle event creation error #
        if response.status_code != 204:
            with open("../delete events/events_ids_not_deleted.csv", "a", newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow([event_id])
    return 1


def create_event(symbol, event_type, URLevents=URL_events, auth_token=auth_token):
    PARAMS3 = {"auth-token": auth_token, "event_name": "daily - " + event_type + "-cross - " + symbol,
               "event_edit": "private", "event_read": "public"}
    response = post_data(URLevents, PARAMS3)

    # handle event creation error #
    if response.status_code != 200:
        raise MyError("event error", str(response.status_code))

    return response.json()["event_id"]


def add_tags(event_id, tags, URLevents=URL_events, auth_token=auth_token):
    URLtag = URLevents + "/tag/" + str(event_id)

    for tag in tags:
        PARAMStag = {"auth-token": auth_token, "event_category_name": tag}
        response = post_data(URLtag, PARAMStag)

        #  handle TAG errors  #
        if response.status_code != 200:
            raise MyError("tag error", str(response.status_code))

    return 1


def add_date(event_id, event_type, cross_date, cross_value, URLevents=URL_events, auth_token=auth_token):
    URLdate = URLevents + "/date/" + str(event_id)
    PARAMSdate = {"auth-token": auth_token, "event_date": cross_date,
                  "event_date_description": event_type + " cross - " + str(cross_value),
                  'event_date_timezone': "Z"}
    response = post_data(URLdate, PARAMSdate)

    #  handle date errors  #
    if response.status_code != 200:
        raise MyError("date error", str(response.status_code))

    return 1


def note_error(symbol, error_name, data_to_note="", error_file=error_file):

    with open(error_file, "a", newline='') as f:
        print(symbol + " generated ERRRRRRRRROR: " + error_name + "       " + data_to_note)
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([symbol, date.today().strftime("%Y-%m-%d"), error_name, data_to_note])
    return 1


def note_success(symbol, golden_id, deaths_id, last_update, success_file=success_file):

    with open(success_file, "a", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([symbol, golden_id, deaths_id, last_update])
    return 1


def note_update_to_temp_file(row, success_file_temp=success_file_temp):

    with open(success_file_temp, "a", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(row)
    return 1


def sync_success_file(success_file_temp=success_file_temp, success_file=success_file):

    with open(success_file_temp, "r", newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        next(f)
        data_temp = list(reader)

    with open(success_file, "r", newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        next(f)
        data = list(reader)

    for item in data:
        item[4] = 0
    data_symbs = [item[0] for item in data]
    for index, row in enumerate(data_temp):
        if row[0] in data_symbs and data:
            data[data_symbs.index(row[0])] = row
        else:
            data.append(row)

    with open(success_file, "w", newline='') as f:
        header = ['symbol', 'golden', 'deaths', "last_update", "number-of-added-dates"]
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerows(data)

    return 1

def note_update_summary(summary, update_summary_file=update_summary_file):

    with open(update_summary_file, "a", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(summary)

    return 1




def process_data(dl):
    # handle data errors#
    if len(dl) < 201:
        if len(dl) == 0:
            raise MyError("no data")
        else:
            raise MyError("low data size")
    if "close" not in dl[0]:
        raise MyError("no close price in data")
    if dl[0]["close"] is None:
        raise MyError("none data")

    golden = []
    deaths = []
    prices = [item["close"] for item in dl]
    for i in range(199, len(prices)):

        sma200 = sum(prices[i - 199:i + 1]) / 200
        sma50 = sum(prices[i - 49:i + 1]) / 50
        dl[i]["sma200"] = sma200
        dl[i]["sma50"] = sma50

        if i == 199:
            comprs = sign(sma50 - sma200)
        if comprs != 0:
            if comprs < sign(sma50 - sma200):
                dl[i]["cross"] = "Golden"
                dl[i]["cross-value"] = round((sma200p * sma50 - sma200 * sma50p) / (sma50 - sma50p - sma200 + sma200p),
                                             5)
                dl[i]["sma200p"] = sma200p
                dl[i]["sma50p"] = sma50p

                golden.append(dl[i])
            if comprs > sign(sma50 - sma200):
                dl[i]["cross"] = "Death"
                dl[i]["cross-value"] = round((sma200p * sma50 - sma200 * sma50p) / (sma50 - sma50p - sma200 + sma200p),
                                             5)
                dl[i]["sma200p"] = sma200p
                dl[i]["sma50p"] = sma50p

                deaths.append(dl[i])

        comprs = sign(sma50 - sma200)
        sma50p = sma50
        sma200p = sma200

    return {"Golden": golden, 'Death': deaths}


def create_full_event(symbol, event_type, ids_file=ids_file):
    # create event #
    event_id = create_event(symbol, event_type)

    #  enter event ids in file#

    with open(ids_file, "a", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([event_id])

    #  add TAGS  #
    tags = ["technical analysis", "daily", "closing price", "trading indicator", symbol]
    add_tags(event_id, tags)

    return event_id


def update_symbol(symbol, golden_id='', deaths_id='', update_type="first", start_date='1800-01-01',
                  last_updated_date='1800-01-01', end_date= date.today().strftime("%Y-%m-%d")):
    #date.today().strftime("%Y-%m-%d")

    print(symbol)
    event_ids = {'Golden': golden_id, 'Death': deaths_id}
    nbr_added_dates = {'Golden': 0, 'Death': 0}
    last_updated_date = datetime.strptime(last_updated_date, "%Y-%m-%d")

    # get data from server #
    response = get_data(symbol, start_date=start_date, end_date=end_date)

    print("data received successfully")

    # extract data #
    dl = response.json()["data"]


    # process data #
    cross_lists = process_data(dl)

    # send data to server#
    for cross_name, cross_list in cross_lists.items():

        # create events #
        if update_type == "first":

            event_id = create_full_event(symbol, cross_name)
            event_ids[cross_name] = event_id

        #  add cross dates  #
        counter = 0
        for info in cross_list:
            cross_date = datetime.strptime(info["time"], "%Y-%m-%dT%H:%M:%SZ")
            if cross_date.date() > last_updated_date.date():
                add_date(event_ids[cross_name], cross_name, cross_date.strftime("%Y%m%d%H%M%S"), info["cross-value"])
                counter += 1
        nbr_added_dates[cross_name] = counter

    if update_type == "first":
        word = "added"
    elif update_type == "update":
        word = "updated"

    print(symbol + word + " succefully :")
    print(event_ids)
    print(str(nbr_added_dates['Golden']) + "golden" + "\n" + str(nbr_added_dates["Death"]) + "deaths")

    tot_nbr_added_dates = nbr_added_dates['Golden'] + nbr_added_dates["Death"]

    last_update_date = datetime.strptime(dl[-1]["time"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

    return event_ids, tot_nbr_added_dates, last_update_date


def create_symbols(symbols_file='symbols.csv', first=0, last=31705):

    with open(symbols_file, 'r') as f:
        reader = csv.reader(f)
        symbols = [i[0] for i in reader]

    update_symbols(symbols[first:last])


def update_success_file(success_file=success_file, type='periodically'):

    with open(success_file, "r", newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        next(f)
        symbols = [item[0] for item in list(reader)]

    if type == 'periodically':
        while 1:
            x = datetime.today()
            y = x.replace(day=x.day, hour=20, minute=0, second=0, microsecond=0) + timedelta(days=1)
            delta_t = y - x
            secs = delta_t.total_seconds()
            time.sleep(secs)
            update_symbols(symbols, success_file)

    if type == 'now':
        update_symbols(symbols, success_file)

    # replace function by update_symbol






def update_symbols(symbs,success_file=success_file, success_file_temp=success_file_temp):

    with open(success_file, "r", newline='') as f:
        reader = csv.reader(f, delimiter='\t')
        next(f)
        data = list(reader)

    # initialize temporary success file #
    header = ['symbol', 'golden', 'deaths', "last_update", "number-of-added-dates"]
    with open(success_file_temp, "w", newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)

    number_of_processed_symbs = 0
    number_of_modified_symbs=0
    total_nbr_added_dates = 0
    nbr_errors = 0
    event_ids = {}
    update_type = "update"

    # iterate over symbols#

    registred_symbs = [row[0] for row in data]
    for index, symbol in enumerate(symbs):
        print(index)
        try:
            number_of_processed_symbs += 1
            if symbol in registred_symbs:
                row = data[registred_symbs.index(symbol)]
                [golden_id, deaths_id] = row[1:3]
                update_type = "update"

                # compare update date and today#
                last_updated_date = datetime.strptime(row[3], "%Y-%m-%d")
                if last_updated_date.date() >= date.today():
                    continue
                start_date = (last_updated_date - timedelta(days=500)).strftime("%Y-%m-%d")
                last_updated_date = last_updated_date.strftime("%Y-%m-%d")

            else:
                golden_id = ''
                deaths_id = ''
                update_type = "first"
                start_date = '1800-01-01'
                last_updated_date = '1800-01-01'

            # update symbols#
            event_ids, nbr_added_dates, last_update_date = update_symbol(symbol, golden_id, deaths_id, update_type,
                                                        start_date, last_updated_date)

            #  add successful update symbols to file#
            note_update_to_temp_file([symbol, event_ids['Golden'], event_ids['Death'],
                                      last_update_date, nbr_added_dates])

            # increment counters
            total_nbr_added_dates += nbr_added_dates

            if total_nbr_added_dates > 0:
                number_of_modified_symbs += 1


        # handle program errors
        except MyError as e:
            note_error(symbol, e.error_name, e.error_infos, update_error_file)
            nbr_errors += 1
            if update_type == "first":
                delete_events(list(event_ids.values()))
                continue

        except Exception as e:
            traceback_str = "".join(traceback.format_tb(e.__traceback__))
            note_error(symbol, "program error", type(e).__name__, update_error_file)
            traceback.print_exc()
            nbr_errors += 1
            if update_type == "first":
                delete_events(list(event_ids.values()))
            continue


    summary = [date.today().strftime("%Y-%m-%d"), number_of_processed_symbs, number_of_modified_symbs, total_nbr_added_dates, nbr_errors]
    if total_nbr_added_dates > 0:
        sync_success_file()
    note_update_summary(summary)
    remove(success_file_temp)
