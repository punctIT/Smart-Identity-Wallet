use axum::{
    extract::Json as ExtractJson,
    response::Json,
    routing::{get, post},
    Router,
};

use axum_server::tls_rustls::RustlsConfig;
use chrono::Utc;
use serde_json::{json, Value};

use crate::network::handle_message::handle_message;

pub struct HTTPServer {}

impl HTTPServer {
    pub fn new() -> Self {
        HTTPServer {}
    }
    pub async fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        let app = Router::new()
            .route("/health", get(Self::health_check))
            .route("/api/data", get(Self::get_data))
            .route("/api/message", post(handle_message))
            .route("/api/auth", post(Self::authenticate_user));

        let tls_config =
            RustlsConfig::from_pem_file("certs/server.crt", "certs/server.key").await?;

        let addr = "0.0.0.0:8443".parse()?;
        println!("🚀 Starting HTTPS server on https://{}", addr);
        println!("👤 Server pentru punctIT - 2025-10-13 20:23:53 UTC");
        println!("📱 Entry points disponibile:");
        println!("   GET  /health - verifică starea");
        println!("   GET  /api/data - date generale");
        println!("   POST /api/message - mesaje specifice în funcție de tip");
        println!("   POST /api/auth - autentificare");

        axum_server::bind_rustls(addr, tls_config)
            .serve(app.into_make_service())
            .await?;

        Ok(())
    }

    async fn health_check() -> Json<Value> {
        Json(json!({
            "status": "ok",
            "message": "Server is running",
            "timestamp": Utc::now().to_rfc3339()
        }))
    }

    async fn get_data() -> Json<Value> {
        Json(json!({
            "data": {
                "id": 1,
                "message": "Hello from HTTPS server!",
                "timestamp": Utc::now().to_rfc3339(),
                "secure": true
            }
        }))
    }

    async fn authenticate_user(ExtractJson(auth_data): ExtractJson<Value>) -> Json<Value> {
        println!("🔐 Autentificare: {:?}", auth_data);
        Json(json!({
            "authenticated": true,
            "token": "jwt_token_example",
            "expires_in": 3600
        }))
    }
}
