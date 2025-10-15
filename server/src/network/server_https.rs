use axum::{
    response::Json,
    routing::{get, post},
    extract::{Json as ExtractJson, State},
    Router,
    middleware,
};
use std::sync::Arc;
use axum_server::tls_rustls::RustlsConfig;
use chrono::Utc;
use serde_json::{json, Value};

use crate::handle_requests::request_handler::handle_message;
use crate::network::auth::{SessionManager,LoginResponse,LoginRequest,UserInfo,RegisterRequest};
use crate::network::middleware::auth_middleware;

pub struct HTTPServer {
    session_manager: Arc<SessionManager>,
}

impl HTTPServer {
    pub fn new() -> Self {
        Self {
            session_manager: Arc::new(SessionManager::new()),
        }
    }
    pub async fn start(&self) -> Result<(), Box<dyn std::error::Error>> {
        let session_manager = self.session_manager.clone();
        let public_routes = Router::new()
            .route("/health", get(Self::health_check))
            .route("/login", post(Self::login))
            .route("/register", post(Self::register));

        let protected_routes = Router::new()
            .route("/api/data", get(Self::get_data))
            .route("/api/message", post(handle_message))
            .layer(middleware::from_fn_with_state(
                session_manager.clone(), 
                auth_middleware
            ));

        let app = Router::new()
            .merge(public_routes)
            .merge(protected_routes)
            .with_state(self.session_manager.clone());

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

    async fn login(
        State(session_manager): State<Arc<SessionManager>>,
        ExtractJson(login_req): ExtractJson<LoginRequest>
    ) -> Json<LoginResponse> {
        println!("🔐 Încercare login: {} la 2025-10-14 04:38:43", login_req.username);

        // Verifică credențialele punctITok
        //aici trebuie facut cu DB
        let authenticated = match login_req.username.as_str() {
            "punctIT" => login_req.password == "securePunctIT2025", 
            "admin" => login_req.password == "admin2025",
            _ => false,
        };

        if authenticated {
            let token = session_manager.create_session(&login_req.username);
            let user_info = UserInfo {
                username: login_req.username.clone(),
                role: if login_req.username == "punctITok" { "Lead Developer".to_string() } else { "Admin".to_string() },
                permissions: vec!["read".to_string(), "write".to_string(), "admin".to_string()],
                login_time: "2025-10-14 04:38:43".to_string(),
            };

            Json(LoginResponse {
                success: true,
                token: Some(token),
                expires_in: 24 * 3600, // 24 ore
                user_info: Some(user_info),
                message: String::from("🎉 Bun venit punctITok! Login reușit la 2025-10-14 04:38:43"),
            })
        } else {
            println!("❌ Login eșuat pentru {} la 2025-10-14 04:38:43", login_req.username);
            Json(LoginResponse {
                success: false,
                token: None,
                expires_in: 0,
                user_info: None,
                message: "❌ Credențiale invalide pentru Smart Identity Wallet".to_string(),
            })
        }
    }

    async fn register(ExtractJson(register_req): ExtractJson<RegisterRequest>) -> Json<Value> {
        //aici se face registeru 
        if register_req.username.starts_with("ok") {
            Json(json!({
                "success": true,
                "message": "Cont creat cu succes pentru punctITok la 2025-10-14 04:38:43"
            }))
        } else {
            Json(json!({
                "success": false,
                "message": "❌ Doar punctITok poate crea conturi noi"
            }))
        }
    }
}
