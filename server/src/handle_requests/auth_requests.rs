use crate::network::auth::{LoginRequest,LoginResponse,UserInfo,RegisterRequest};
use axum::{
    extract::{Json as ExtractJson, State},
    response::Json,
};
use serde_json::{json, Value};

use std::sync::Arc;

use crate::network::server_https::AppState;

pub struct AuthRequestHandler{}
impl AuthRequestHandler{
    pub async fn handle_login(
        State(app_state): State<Arc<AppState>>,
        ExtractJson(login_req): ExtractJson<LoginRequest>,
    ) -> Json<LoginResponse> {
        println!(
            "🔐 Încercare login: {} la 2025-10-14 04:38:43",
            login_req.username
        );

        // Verifică credențialele punctITok
        //aici trebuie facut cu DB
        let authenticated = match login_req.username.as_str() {
            "punctIT" => login_req.password == "securePunctIT2025",
            "admin" => login_req.password == "admin2025",
            _ => false,
        };

        if authenticated {
            let token = app_state
                .session_manager
                .create_session(&login_req.username);
            let user_info = UserInfo {
                username: login_req.username.clone(),
                role: if login_req.username == "punctITok" {
                    "Lead Developer".to_string()
                } else {
                    "Admin".to_string()
                },
                permissions: vec!["read".to_string(), "write".to_string(), "admin".to_string()],
                login_time: "2025-10-14 04:38:43".to_string(),
            };

            Json(LoginResponse {
                success: true,
                token: Some(token),
                expires_in: 24 * 3600, // 24 ore
                user_info: Some(user_info),
                message: String::from(
                    "🎉 Bun venit punctITok! Login reușit la 2025-10-14 04:38:43",
                ),
            })
        } else {
            println!(
                "❌ Login eșuat pentru {} la 2025-10-14 04:38:43",
                login_req.username
            );
            Json(LoginResponse {
                success: false,
                token: None,
                expires_in: 0,
                user_info: None,
                message: "❌ Credențiale invalide pentru Smart Identity Wallet".to_string(),
            })
        }
    }

    pub async fn handle_register(ExtractJson(register_req): ExtractJson<RegisterRequest>) -> Json<Value> {
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