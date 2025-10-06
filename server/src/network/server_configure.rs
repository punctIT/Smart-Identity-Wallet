use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::thread;

use crate::network::protocol_handler::ProtocolHandler;

pub struct ServerConfig {
    ip: Option<String>,
    port: Option<usize>,
    listener: Option<TcpListener>,
    terminator: Option<String>,
}

impl ServerConfig {
    pub fn new() -> ServerConfig {
        ServerConfig {
            ip: None,
            port: None,
            listener: None,
            terminator: None,
        }
    }
    pub fn set_ip(&mut self, ip: String) -> &mut Self {
        self.ip = Some(ip);
        self
    }
    pub fn set_terminator(&mut self, terminator: String) -> &mut Self {
        self.terminator = Some(terminator);
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
                        let terminator = self.terminator.clone().unwrap_or(String::new());
                        thread::spawn(move || {
                            ServerConfig::handle_connection(stream_ok, terminator);
                        });
                    }
                    Err(e) => eprintln!("Connection failed {}", e),
                }
            }
        }
        //self
    }
    fn handle_connection(mut stream: TcpStream, terminator: String) {
        let mut buffer = [0; 512];
        let mut command: String = String::new();
        let mut authentificaton_status = false;
        let mut custom_protocol: ProtocolHandler = ProtocolHandler::new();
        'main: loop {
            match stream.read(&mut buffer) {
                Ok(0) => {
                    println!("Client disconnected");
                    break;
                }
                Ok(n) => {
                    let mut msg = String::from_utf8_lossy(&buffer[..n]).to_string();
                    //deci , ce am facut aici,
                    //am facut un terminator , pt comenziile primite , fiecare comanda trebuie sa se termine cu [TERMINATORUL(URMEAZA SA FIE DECIS)]
                    //asta e pentru a evita ca sa se combine comenziile, gen COMANDA1 ARG ARG COMANDA2
                    // si sa considere COMANDA2 ca argument

                    if msg.contains(terminator.as_str()) {
                        while let Some(index) = msg.find(terminator.as_str()) {
                            command.push_str(&msg[..index]);
                            println!("RECEIVED COMMAND: {}", command);
                            if authentificaton_status {
                            } else {
                                if let Err(e) = stream.write_all(
                                    custom_protocol
                                        .set_text(String::from("must loggin"))
                                        .get_text()
                                        .unwrap()
                                        .as_bytes(),
                                ) {
                                    eprintln!("Failed to send response: {}", e);
                                    break 'main;
                                }
                            }
                            command.clear();
                            msg = msg[index + 3..].to_string();
                            //command.push_str(&msg[index+3..]);
                        }
                    } else {
                        command += msg.to_string().as_str();
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
