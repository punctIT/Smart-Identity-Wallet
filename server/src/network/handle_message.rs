use crate::network::common::{MessageRequest, MessageResponse};
use axum::{extract::Json as ExtractJson, response::Json};
use chrono::Utc;
use serde_json::{json, Value};

pub async fn handle_message(
    ExtractJson(request): ExtractJson<MessageRequest>,
) -> Json<MessageResponse> {
    println!("📨 Request primit: {:?}", request);

    let (success, data) = match request.message_type.as_str() {
        "greeting" => handle_greeting(&request),
        "user_data" => handle_user_data(&request),
        "status_check" => handle_status_check(&request),
        "notification" => handle_notification(&request),
        "identity_verify" => handle_identity_verification(&request),
        _ => handle_unknown_request(&request),
    };

    Json(MessageResponse {
        success,
        message_type: request.message_type.clone(),
        data,
        timestamp: Utc::now().to_rfc3339(),
    })
}

// Funcții specifice pentru fiecare tip de mesaj
fn handle_greeting(request: &MessageRequest) -> (bool, Value) {
    let user = &request.user_id;
    let greeting = match user.as_str() {
        "punctITok" => "Salut punctITok! Bine ai revenit! 👨‍💻",
        "admin" => "Bună ziua, Administrator! 👑",
        _ => "Bună ziua! Bine ați venit! 👋",
    };

    (
        true,
        json!({
            "greeting": greeting,
            "user": user,
            "special_message": format!("Mesaj special pentru {}", user)
        }),
    )
}

fn handle_user_data(request: &MessageRequest) -> (bool, Value) {
    let user = &request.user_id;
    if &request.content.clone().unwrap() == "nimic" {
        return (
            true,
            json!(
                "
                cacat
            "
            ),
        );
    }
    // Date specifice pentru utilizatori
    let user_data = match user.as_str() {
        "punctITok" => json!({
            "name": "punctITok",
            "role": "Developer",
            "permissions": ["read", "write", "admin"],
            "last_login": "2025-01-13 19:50:47",
            "projects": ["Smart Identity Wallet", "HTTPS Server"],
            "status": "active"
        }),
        _ => json!({
            "name": user,
            "role": "User",
            "permissions": ["read"],
            "status": "active"
        }),
    };
    (
        true,
        json!({
            "user_data": user_data,
            "message": format!("Date pentru utilizatorul {}", user)
        }),
    )
}

fn handle_status_check(request: &MessageRequest) -> (bool, Value) {
    (
        true,
        json!({
            "server_status": "online",
            "uptime": "2h 15m 30s",
            "connections": 5,
            "memory_usage": "45%",
            "cpu_usage": "12%",
            "message": format!("Status cerut de {}", request.user_id)
        }),
    )
}

fn handle_notification(request: &MessageRequest) -> (bool, Value) {
    let content = request.content.as_deref().unwrap_or("Notificare generală");

    (
        true,
        json!({
            "notification": {
                "title": "Notificare nouă",
                "content": content,
                "priority": "high",
                "delivered_to": request.user_id
            },
            "message": "Notificare trimisă cu succes"
        }),
    )
}

fn handle_identity_verification(request: &MessageRequest) -> (bool, Value) {
    let user = &request.user_id;

    // Simulare verificare identitate
    let verified = user == "punctITok" || user.starts_with("admin");

    (
        true,
        json!({
            "identity_check": {
                "user": user,
                "verified": verified,
                "trust_level": if verified { "high" } else { "medium" },
                "certificate_valid": true
            },
            "message": format!("Verificare identitate pentru {}", user)
        }),
    )
}

fn handle_unknown_request(request: &MessageRequest) -> (bool, Value) {
    (
        false,
        json!({
            "error": "Tip de mesaj necunoscut",
            "received_type": request.message_type,
            "available_types": [
                "greeting", "user_data", "status_check",
                "weather", "crypto", "notification", "identity_verify"
            ],
            "message": "Te rog să folosești un tip de mesaj valid"
        }),
    )
}
