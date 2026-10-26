use reqwest::header;

fn main() {
    let api_key: &str = env!("API_KEY");
    fetch_departures(&api_key);
    fetch_lines(&api_key);
}

fn fetch_lines(key: &str) -> Result<(), Box<dyn std::error::Error>> {
    let mut headers = header::HeaderMap::new();
    headers.insert("Authorization", key.parse().unwrap());
    headers.insert("Content-Type", "application/json".parse().unwrap());

    let client = reqwest::blocking::Client::new();
    let res = client
        .post("https://dane.um.warszawa.pl/api/action/get_ztm_lista_linii_na_przystanku")
        .headers(headers)
        .body("{\"busstopId\": \"5070\", \"busstopNr\": \"03\" }")
        .send()?
        .text()?;
    println!("{}", res);

    Ok(())
}

fn fetch_departures(key: &str) -> Result<(), Box<dyn std::error::Error>> {
    let mut headers = header::HeaderMap::new();
    headers.insert("Authorization", key.parse().unwrap());
    headers.insert("Content-Type", "application/json".parse().unwrap());

    let client = reqwest::blocking::Client::new();
    let res = client
        .post("https://dane.um.warszawa.pl/api/action/get_ztm_odjazdy_linii_z_przystanku")
        .headers(headers)
        .body("{\"busstopId\": \"5070\", \"busstopNr\": \"03\", \"line\": \"20\"}")
        .send()?
        .text()?;
    println!("{:?}", res);
    Ok(())
}
