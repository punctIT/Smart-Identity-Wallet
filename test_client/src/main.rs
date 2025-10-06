use std::io::{Read, Write};
use std::net::TcpStream;
use std::thread;

fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:1234").unwrap();
    let mut stream2 = stream.try_clone().unwrap();
    let sent = thread::spawn(move || {
        loop {
            let mut text: String = String::new();
            std::io::stdin().read_line(&mut text).unwrap();
            stream.write_all(text.as_bytes()).unwrap();
        }
    });

    thread::spawn(move || {
        loop {
            let mut buffer = [0; 512];
            let n = stream2.read(&mut buffer).unwrap();
            let text: String = String::from_utf8_lossy(&buffer[0..n]).to_string();
            println!("server:{}", text);
        }
    });
    sent.join().unwrap();
}
