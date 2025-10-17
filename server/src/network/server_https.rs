use axum::{
    middleware,
    response::Json,
    routing::{get, post},
    Router,
};
use axum_server::tls_rustls::RustlsConfig;
use chrono::Utc;
use serde_json::{json, Value};
use std::sync::Arc;

use crate::data_manager::database_manager::DBManager;
use crate::network::middleware::auth_middleware;
use crate::{
    handle_requests::auth_requests::AuthRequestHandler,
    handle_requests::data_requests::DataRequestHandler, network::auth::SessionManager,
};

pub struct HTTPServer {
    session_manager: Arc<SessionManager>,
}

#[derive(Clone)]
pub struct AppState {
    pub db: Arc<DBManager>,
    pub session_manager: Arc<SessionManager>,
}
impl AppState {
    fn new(db: Arc<DBManager>, session_manager: Arc<SessionManager>) -> Self {
        AppState {
            db,
            session_manager,
        }
    }
}

impl HTTPServer {
    pub fn new() -> Self {
        Self {
            session_manager: Arc::new(SessionManager::new()),
        }
    }
    pub async fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        let database_manager = DBManager::new().await?;
        database_manager.configure_database().await?;
        let app_state = Arc::new(AppState::new(
            database_manager.clone(),
            self.session_manager.clone(),
        ));

        let public_routes = Router::new()
            .route("/health", get(Self::health_check))
            .route("/login", post(AuthRequestHandler::handle_login))
            .route("/register", post(AuthRequestHandler::handle_register))
            .with_state(app_state.clone());

        let protected_routes = Router::new()
            .route("/api/data", get(Self::get_data))
            .route("/api/message", post(DataRequestHandler::handle_message))
            .layer(middleware::from_fn_with_state(
                app_state.clone(),
                auth_middleware,
            ))
            .with_state(app_state.clone());

        let app = Router::new().merge(public_routes).merge(protected_routes);

        let tls_config =
            match RustlsConfig::from_pem_file("certs/server.crt", "certs/server.key").await {
                Ok(config) => config,
                Err(e) => panic!("error, certs {}", e),
            };

        let addr = "0.0.0.0:8443".parse()?;
        println!("🚀 Starting HTTPS server on https://{}", addr);
        println!("👤 Server pentru punctIT - 2025-10-13 20:23:53 UTC");
        println!("📱 Entry points disponibile:");
        println!("   GET  /health - verifică starea");
        println!("   GET  /api/data - date generale");
        println!("   POST /api/message - mesaje specifice în funcție de tip");
        println!("   POST /api/auth - autentificare");

        axum_server::bind_rustls(addr, tls_config)
            .serve(app.into_make_service_with_connect_info::<std::net::SocketAddr>())
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
}
