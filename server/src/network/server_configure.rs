use std::net::{TcpListener, TcpStream};
use std::thread;
use std::io::{Read, Write};


pub struct ServerConfig {
    ip: Option<String>,
    port: Option<usize>,
    listener: Option<TcpListener>,
}

impl ServerConfig {
    pub fn new() -> ServerConfig {
        ServerConfig {
            ip: None,
            port: None,
            listener: None,
        }
    }
    pub fn set_ip(&mut self, ip: String) -> &mut Self {
        self.ip = Some(ip);
        self
    }
    pub fn set_port(&mut self, port: usize) -> &mut Self {
        self.port = Some(port);
        self
    }
    pub fn bind_and_listen(&mut self) -> &mut Self {
        if self.ip.is_none() || self.port.is_none() {
            panic!("Error , Ip or PORT is empty");
        }
        let tcp = match TcpListener::bind(format!(
            "{}:{}",
            self.ip.as_mut().unwrap(),
            self.port.unwrap()
        )) {
            Ok(data) => data,
            Err(e) => panic!("error {}", e),
        };
        self.listener = Some(tcp);
        println!(
            "Server listen at {}:{}",
            self.ip.as_mut().unwrap(),
            self.port.unwrap()
        );
        self
    }
    pub fn accept_connection(&mut self) -> &mut Self {
        let listener = self
            .listener
            .as_mut()
            .unwrap_or_else(|| panic!("Error , listener not configured"));
        loop {
            for stream in listener.incoming() {
                match stream {
                    Ok(stream_ok) => {
                        println!("New client: {}", stream_ok.peer_addr().unwrap());
                        thread::spawn(move || {
                            ServerConfig::handle_connection(stream_ok);
                        });
                    }
                    Err(e) => eprintln!("Connection failed {}", e),
                }
            }
        }
        //self
    }
    fn handle_connection(mut stream: TcpStream) {
        let mut buffer = [0; 512];
        loop {
            match stream.read(&mut buffer) {
                Ok(0) => {
                    println!("Client disconnected");
                    break;
                }
                Ok(n) => {
                    let msg = String::from_utf8_lossy(&buffer[..n]);
                    println!("Received: {}", msg);
                    
                    if let Err(e) = stream.write_all("salut".as_bytes()) {
                        eprintln!("Failed to send response: {}", e);
                        break;
                    }
                }
                Err(e) => {
                    eprintln!("Error reading from client: {}", e);
                    break;
                }
            }
        }
    }
}
