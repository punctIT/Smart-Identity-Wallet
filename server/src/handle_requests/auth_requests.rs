use crate::data_manager::password_hashing::PasswordHashManager;
use crate::network::auth::{LoginRequest, LoginResponse, RegisterRequest, UserInfo};
use crate::network::server_https::AppState;
use axum::{
    extract::{Json as ExtractJson, State},
    response::Json,
};
use serde_json::{json, Value};
use std::sync::Arc;

pub struct AuthRequestHandler {}
impl AuthRequestHandler {
    pub async fn handle_login(
        State(app_state): State<Arc<AppState>>,
        ExtractJson(login_req): ExtractJson<LoginRequest>,
    ) -> Json<LoginResponse> {
        println!(
            "🔐 Încercare login: {} la 2025-10-14 04:38:43",
            login_req.username
        );
        let authenticated = app_state
            .db
            .check_login_credentials(&login_req)
            .await
            .unwrap_or(false);

        if authenticated {
            let token = app_state
                .session_manager
                .create_session(&login_req.username);
            let user_info = UserInfo {
                username: login_req.username.clone(), //trebuie modificat cu username din db
                role: "user".to_string(),
                permissions: vec!["read".to_string(), "write".to_string(), "admin".to_string()],
                login_time: "2025-10-14 04:38:43".to_string(),
            };

            Json(LoginResponse {
                success: true,
                token: Some(token),
                expires_in: 24 * 3600, // 24 ore
                user_info: Some(user_info),
                message: format!(
                    "Bun venit {} Login reușit la 2025-10-14 04:38:43",
                    login_req.username
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

    pub async fn handle_register(
        State(app_state): State<Arc<AppState>>,
        ExtractJson(register_req): ExtractJson<RegisterRequest>,
    ) -> Json<Value> {
        println!(
            "🔐 Încercare register: {} la 2025-10-14 04:38:43",
            register_req.email
        );
        let check_email = match app_state.db.check_email(&register_req.email).await {
            Ok(result) => result,
            Err(_) => {
                return Json(json!({
                    "success": false,
                    "message": "Error Database"
                }));
            }
        };
        if check_email {
            return Json(json!({
                    "success": false,
                    "message": "mail already used"
            }));
        }
        let Ok(hash_pass) = PasswordHashManager::get_hashed(register_req.password.clone()) else {
            return Json(json!({
                    "success": false,
                    "message": "hashing error"
            }));
        };

        if let Err(e) = app_state
            .db
            .execute(
                format!("
                    INSERT INTO users (email, username, password_hash, phone_number, created_at, updated_at)
                    VALUES (
                        '{}',
                        '{}',
                        '{}', 
                        '{}',
                        now(),
                        now()
                    );",
                register_req.email,
                register_req.username,
                hash_pass,
                register_req.phone_number
                )
                .to_string(),
            )
            .await
        {
            println!("error insert db");
            return Json(json!({
                "success": false,
                "message": format!("eroare la insert in db {}",e),
            }));
        }
        println!("🔐 register: {} la 2025-10-14 04:38:43", register_req.email);
        Json(json!({
            "success": true,
            "message": "register succesful"
        }))
    }
}
