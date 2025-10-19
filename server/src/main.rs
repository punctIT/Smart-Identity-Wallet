mod ai_microservice;
mod data_manager;
mod handle_requests;
mod network;
mod others;

use crate::network::server_https::HTTPServer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // let db = DBManager::new();
    // db.start().await.unwrap();
    let server = HTTPServer::new();
    server.start().await?;
    Ok(())
}
