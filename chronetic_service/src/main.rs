use crate::timetable::App;
use std::io::{BufReader, prelude::*};
use std::net::{TcpListener, TcpStream};
mod timetable;

const IP: &str = env!("IP");

fn main() {
    let address = IP;
    let listener = TcpListener::bind(address).unwrap();
    let mut app = App::new();
    for stream in listener.incoming() {
        let res = app.run();
        let stream = stream.unwrap();
        handle_connection(stream, res);
    }
}

fn handle_connection(mut stream: TcpStream, contents: String) {
    let buf_reader = BufReader::new(&mut stream);
    let _http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();
    let response = format!("HTTP/1.1 200 OK\r\n\r\n{contents}");
    stream.write_all(response.as_bytes()).unwrap();
}
