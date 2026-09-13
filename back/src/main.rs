use std::fs;
use std::io::{BufReader, prelude::*};
use std::net::{TcpListener, TcpStream};

const IP: &str = env!("IP");

fn main() {
    let address = IP;
    let listener = TcpListener::bind(address).unwrap();
    for stream in listener.incoming() {
        let stream = stream.unwrap();
        handle_connection(stream);
    }
}

fn handle_connection(mut stream: TcpStream) {
    let buf_reader = BufReader::new(&mut stream);
    let _http_request: Vec<_> = buf_reader
        .lines()
        .map(|result| result.unwrap())
        .take_while(|line| !line.is_empty())
        .collect();
    let file_path = "test_data/111.json";
    let contents: String = fs::read_to_string(file_path).unwrap();
    let response = format!("HTTP/1.1 200 OK\r\n\r\n{contents}");
    stream.write_all(response.as_bytes()).unwrap();
}
