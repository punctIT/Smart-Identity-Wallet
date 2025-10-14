mod network;
mod handle_message;

use crate::network::server_https::HTTPServer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let server = HTTPServer::new();
    server.start().await?; // ✅ Acum merge cu instanța

    Ok(())
}
