import json
import requests
import time
import secrets


service_url = secrets.URL


def fetch_test(url) -> list:
    departures: list = []
    r = None
    while r is None:
        try:
            r = requests.get(url)
        except:
            print("Fetching failed, trying again...")
            time.sleep(2)

    dump = json.dumps(r.json())

    data = json.loads(dump)

    # Save response to file
    # json_str = json.dumps(data, indent=4)
    # with open("response.json", "w") as f:
    #     f.write(json_str)

    count = 0
    for result in data["result"]:
        if count < 7:
            single_departure: list = []
            time_now = str(result[0]["value"])[:-3]
            hours = int(time_now[:-3])
            minutes = int(time_now[-2:])
            if hours >= 24:
                true_hours = hours - 24
                true_hours = "{:02d}".format(true_hours)
                true_minutes = "{:02d}".format(minutes)
                time_now = str(true_hours) + ":" + str(true_minutes)
            mam = int(time_now[:2]) * 60 + int(time_now[-2:])
            single_departure.append(time_now)
            single_departure.append(result[1]["value"])
            destination = result[2]["value"]
            destination = " ".join(destination.split()[:2])
            single_departure.append(destination)
            single_departure.append(result[3]["value"])
            single_departure.append(mam)
            departures.append(single_departure)
            count += 1
    return departures


departures = fetch_test(service_url)
print("Response length is: ", len(fetch_test(service_url)))
for departure in departures:
    print(departure)
