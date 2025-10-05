use std::net::TcpStream;
use std::io::{Write,Read};
fn main() {
    let mut stream = TcpStream::connect("127.0.0.1:1234").unwrap();
    loop{
        let mut text:String = String::new();
        std::io::stdin().read_line(&mut text).unwrap();
        stream.write_all(text.as_bytes()).unwrap();
        let mut buffer = [0; 512];
        let n=stream.read(&mut buffer).unwrap();
        text = String::from_utf8_lossy(&buffer[0..n]).to_string();
        println!("{}",text);
    }
}
