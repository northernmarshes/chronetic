use ::reqwest;
use ::serde::Deserialize;
use ::serde_json;
use chrono::Timelike;
use serde::Serialize;

#[derive(Deserialize, Debug)]
pub struct Departures {
    pub departures: Vec<Departure>,
}

#[derive(Deserialize, Debug)]
pub struct Departure {
    pub line: String,
    pub direction: String,
    pub mam: u16,
}

#[derive(Deserialize, Debug)]
pub struct Response {
    pub result: Vec<Item>,
}

#[derive(Deserialize, Debug)]
pub struct Item {
    pub values: Vec<KeyValue>,
}

#[derive(Deserialize, Debug, Serialize)]
pub struct KeyValue {
    pub key: String,
    pub value: String,
}

#[derive(Deserialize, Debug)]
pub struct Timetable {
    pub result: Vec<Vec<TimetableKV>>,
}

#[derive(Deserialize, Debug)]
pub struct TimetableKV {
    pub key: String,
    pub value: Option<String>,
}

#[derive(Serialize)]
pub struct Output {
    result: Vec<Vec<KeyValue>>,
}
pub fn get_buses() -> Vec<String> {
    // Get list of all buses from a busstop
    let mut buses: Vec<String> = Vec::new();
    let url = format!(
        "{}?id={}&busstopId={}&busstopNr={}&apikey={}",
        std::env::var("URL").unwrap(),
        std::env::var("LIST_ID").unwrap(),
        std::env::var("STOP_ID").unwrap(),
        std::env::var("STOP_NR").unwrap(),
        std::env::var("API_KEY").unwrap(),
    );

    let body = reqwest::blocking::get(&url).unwrap().text().unwrap();
    let body = body.as_str();
    let response: Response = serde_json::from_str(body).unwrap();
    for item in &response.result {
        for kv in &item.values {
            buses.push(kv.value.clone());
        }
    }
    buses
}

pub fn get_departures(bus: String) -> Departures {
    // Get all departures of a bus
    let url = format!(
        "{}?id={}&busstopId={}&busstopNr={}&line={}&apikey={}",
        std::env::var("URL").unwrap(),
        std::env::var("TIMETABLE_ID").unwrap(),
        std::env::var("STOP_ID").unwrap(),
        std::env::var("STOP_NR").unwrap(),
        bus,
        std::env::var("API_KEY").unwrap(),
    );
    let body = reqwest::blocking::get(&url).unwrap().text().unwrap();
    let body = body.as_str();
    let timetable: Timetable = serde_json::from_str(body).unwrap();

    let dep: Vec<Departure> = timetable
        .result
        .iter()
        .map(|group| {
            let find = |key: &str| {
                group
                    .iter()
                    .find(|kv| kv.key == key)
                    .and_then(|kv| kv.value.clone())
            };
            let timestamp = find("czas").unwrap();
            let mam_now = time_to_mam(&timestamp);
            Departure {
                line: bus.clone(),
                direction: find("kierunek").unwrap(),
                mam: mam_now,
            }
        })
        .collect();

    Departures { departures: dep }
}

pub fn time_to_mam(timestamp: &str) -> u16 {
    // Convert time to minutes after midnight
    let time: Vec<&str> = timestamp.split(":").collect();
    let hours: u16 = time[0].parse().unwrap_or(0);
    let minutes = time[1].parse().unwrap_or(0);
    hours * 60 + minutes
}

pub fn mam_to_time(mam: u16) -> String {
    // Convert minutes after midnight to time
    let mut hours = 0;
    let mut minutes = 0;
    if mam > 60 {
        hours = mam / 60;
        minutes = mam % 60;
    }
    let time = format!("{:02}:{:02}:00", hours, minutes);
    time
}

pub fn current_time() -> u16 {
    // Get current time
    let now = chrono::Local::now();
    let hours: u16 = now.hour() as u16;
    let minutes: u16 = now.minute() as u16;
    let mam: u16 = hours * 60 + minutes;
    mam
}

pub fn run() -> String {
    // Get json with next seven departures
    let time = current_time();
    let _now = chrono::Local::now();
    let data = get_buses();
    let mut all: Vec<Departures> = Vec::new();
    for bus in data {
        let departures = get_departures(bus);
        all.push(departures);
    }
    let mut combined = Departures {
        departures: all.into_iter().flat_map(|d| d.departures).collect(),
    };

    // Sorting next departures
    combined.departures.sort_by_key(|d| d.mam);

    let mut displayed = 0;
    let mut departures: Vec<Vec<KeyValue>> = Vec::new();
    for d in combined.departures {
        if d.mam > time && displayed <= 6 {
            let left = d.mam - time;
            let post = vec![
                KeyValue {
                    key: "time".to_string(),
                    value: mam_to_time(d.mam).to_string(),
                },
                KeyValue {
                    key: "number".to_string(),
                    value: d.line.to_string(),
                },
                KeyValue {
                    key: "direction".to_string(),
                    value: d.direction.to_string(),
                },
                KeyValue {
                    key: "stop".to_string(),
                    value: left.to_string(),
                    // value: "Stacja".to_string(),
                },
            ];
            departures.push(post);
            displayed += 1;
        }
    }

    let result = Output { result: departures };

    serde_json::to_string(&result).unwrap()
}
