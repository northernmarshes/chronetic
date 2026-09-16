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

// #[derive(Serialize)]
// pub struct Post {
//     title: String,
//     created: String,
//     link: String,
//     description: String,
//     content: String,
//     author: String,
// }
//
#[derive(Serialize)]
pub struct Output {
    result: Vec<Vec<KeyValue>>,
}

// #[derive(Serialize)]
// pub struct NextDeparture {
//     time: String,
//     number: String,
//     direction: String,
//     stop: String,
// }

pub fn get_buses() -> Vec<String> {
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

    let dap: Vec<Departure> = timetable
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

    Departures { departures: dap }
}

pub fn time_to_mam(timestamp: &str) -> u16 {
    let time: Vec<&str> = timestamp.split(":").collect();
    let hours: u16 = time[0].parse().unwrap_or(0);
    let minutes = time[1].parse().unwrap_or(0);
    hours * 60 + minutes
}

pub fn mam_to_time(mam: u16) -> String {
    let mut hours = 0;
    let mut minutes = 0;
    if mam > 60 {
        hours = mam / 60;
        minutes = mam % 60;
    }
    let time = format!("{:02}:{}:00", hours, minutes);
    time
}

pub fn current_time() -> u16 {
    let now = chrono::Local::now();
    let hours: u16 = now.hour() as u16;
    let minutes: u16 = now.minute() as u16;
    let mam: u16 = hours * 60 + minutes;
    mam
}

// pub fn construct_response(departures: Departures) -> String {
//     let mut displayed = 0;
//     for d in departures.departures {
//         if d.mam > time && displayed <= 6 {
//             let left = d.mam - time;
//             println!(
//                 "Line: {}, Direction: {}, Leaves in {} minutes, Departure: {}",
//                 d.line, d.direction, left, time
//             );
//             displayed += 1;
//         }
//     }
// }

pub fn run() -> String {
    let time = current_time();
    let now = chrono::Local::now();
    println!("time: {now}");
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
    // let mut displayed = 0;

    // for d in combined.departures {
    //     if d.mam > time && displayed <= 6 {
    //         let left = d.mam - time;
    //         println!(
    //             "Line: {}, Direction: {}, Leaves in {} minutes, Departure: {}",
    //             d.line, d.direction, left, time
    //         );
    //         displayed += 1;
    //     }
    // }

    let mut departures: Vec<Vec<KeyValue>> = Vec::new();
    let post_0 = vec![
        KeyValue {
            key: "time".to_string(),
            value: mam_to_time(combined.departures[0].mam).to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: combined.departures[0].line.to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: combined.departures[0].direction.to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Stacja".to_string(),
        },
    ];

    let post_1 = vec![
        KeyValue {
            key: "time".to_string(),
            value: "12:22:00".to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: "123".to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: "Avalon".to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Zwyciezcow".to_string(),
        },
    ];
    let post_2 = vec![
        KeyValue {
            key: "time".to_string(),
            value: "12:22:00".to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: "123".to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: "Avalon".to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Zwyciezcow".to_string(),
        },
    ];
    let post_3 = vec![
        KeyValue {
            key: "time".to_string(),
            value: "12:22:00".to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: "123".to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: "Avalon".to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Zwyciezcow".to_string(),
        },
    ];
    let post_4 = vec![
        KeyValue {
            key: "time".to_string(),
            value: "12:22:00".to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: "123".to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: "Avalon".to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Zwyciezcow".to_string(),
        },
    ];
    let post_5 = vec![
        KeyValue {
            key: "time".to_string(),
            value: "12:22:00".to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: "123".to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: "Avalon".to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Zwyciezcow".to_string(),
        },
    ];
    let post_6 = vec![
        KeyValue {
            key: "time".to_string(),
            value: "12:22:00".to_string(),
        },
        KeyValue {
            key: "number".to_string(),
            value: "123".to_string(),
        },
        KeyValue {
            key: "direction".to_string(),
            value: "Avalon".to_string(),
        },
        KeyValue {
            key: "stop".to_string(),
            value: "Zwyciezcow".to_string(),
        },
    ];
    departures.push(post_0);
    departures.push(post_1);
    departures.push(post_2);
    departures.push(post_3);
    departures.push(post_4);
    departures.push(post_5);
    departures.push(post_6);

    let result = Output { result: departures };

    serde_json::to_string(&result).unwrap()
}
