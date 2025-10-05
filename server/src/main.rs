mod network;

use crate::network::server_configure::ServerConfig;

fn main() {
    let mut server: ServerConfig = ServerConfig::new();
    server
        .set_ip(String::from("0.0.0.0"))
        .set_port(1234)
        .bind_and_listen()
        .accept_connection();
}
