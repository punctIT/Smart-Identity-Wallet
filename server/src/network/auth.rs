use chrono::{DateTime, Duration, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use uuid::Uuid;

#[derive(Clone)]
#[allow(dead_code)]
pub struct UserSession {
    pub user_id: String,
    pub token: String,
    pub expires_at: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

#[derive(Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
}
#[derive(Deserialize)]
#[allow(dead_code)]
pub struct RegisterRequest {
    pub username: String,
    pub password: String,
    pub email: String,
    pub phone_number: String,
}

#[derive(Serialize)]
pub struct LoginResponse {
    pub success: bool,
    pub token: Option<String>,
    pub expires_in: i64,
    pub user_info: Option<UserInfo>,
    pub message: String,
}

#[derive(Serialize)]
pub struct UserInfo {
    pub username: String,
    pub role: String,
    pub permissions: Vec<String>,
    pub login_time: String,
}

pub struct SessionManager {
    sessions: Arc<Mutex<HashMap<String, UserSession>>>,
}

impl SessionManager {
    pub fn new() -> Self {
        Self {
            sessions: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    pub fn create_session(&self, user_id: &str) -> String {
        let token = format!(
            "{}_{}_{}",
            user_id,
            &Uuid::new_v4().to_string().replace("-", "")[..16],
            Utc::now().timestamp()
        );

        let session = UserSession {
            user_id: user_id.to_string(),
            token: token.clone(),
            expires_at: Utc::now() + Duration::hours(24),
            created_at: Utc::now(),
        };

        let mut sessions = self.sessions.lock().unwrap();
        sessions.insert(token.clone(), session);

        println!(
            "✅ Sesiune creată pentru {} la 2025-10-14 04:38:43: {}",
            user_id, token
        );
        token
    }

    pub fn validate_token(&self, token: &str) -> Option<UserSession> {
        let mut sessions = self.sessions.lock().unwrap();

        if let Some(session) = sessions.get(token) {
            if session.expires_at > Utc::now() {
                println!("✅ Token valid pentru punctITok la 2025-10-14 04:38:43");
                let session = (*session).clone();
                return Some(session);
            } else {
                println!("❌ Token expirat pentru punctITok la 2025-10-14 04:38:43");
                sessions.remove(token);
            }
        }
        None
    }

    #[allow(dead_code)]
    pub fn logout(&self, token: &str) -> bool {
        let mut sessions = self.sessions.lock().unwrap();
        if sessions.remove(token).is_some() {
            println!("✅ punctITok logout la 2025-10-14 04:38:43");
            true
        } else {
            false
        }
    }
    #[allow(dead_code)]
    pub fn cleanup_expired(&self) {
        let mut sessions = self.sessions.lock().unwrap();
        let now = Utc::now();
        sessions.retain(|_, session| session.expires_at > now);
    }
}
