use crate::handle_requests::response_handler::ResponseHandler;
use crate::network::server_https::AppState;
use crate::others::common::MessageRequest;
use serde_json::{json, Value};
use std::sync::Arc;

pub struct WalletCards {}

impl WalletCards {
    pub async fn insert(
        value: &'static str,
        request: &MessageRequest,
        app_state: Arc<AppState>,
    ) -> (bool, Value) {
        let content = match &request.content {
            Some(content) => content,
            None => return ResponseHandler::standard_error("Must be a json".to_string()),
        };

        let json_string = serde_json::to_string(content).unwrap_or_else(|_| "{}".to_string());
        let encrypted_data = match app_state.cripto_manager.encrypt(&json_string) {
            Ok(encrypted) => encrypted,
            Err(e) => return ResponseHandler::standard_error(format!("Encryption error: {}", e)),
        };

        let check_query = format!(
            "SELECT COUNT(*) as cnt FROM identity_wallet WHERE user_id = (SELECT id FROM users WHERE username = '{}' OR email = '{}')",
            request.user_id, request.user_id
        );
        let exists = match app_state.db.select_count(check_query, "cnt").await {
            Ok(cnt) => cnt > 0,
            Err(_) => false,
        };

        if exists {
            // UPDATE
            let update_query = format!(
                "UPDATE identity_wallet 
                 SET {} = '{}' 
                 WHERE user_id = (
                     SELECT id FROM users 
                     WHERE username = '{}' OR email = '{}'
                 )",
                value, encrypted_data, request.user_id, request.user_id
            );
            if let Err(e) = app_state.db.execute(update_query).await {
                return ResponseHandler::standard_error(format!("UPDATE ERROR {}", e));
            }
        } else {
            // INSERT
            let insert_query = format!(
                "INSERT INTO identity_wallet (user_id, {}) VALUES (
                    (SELECT id FROM users WHERE username = '{}' OR email = '{}'), '{}'
                )",
                value, request.user_id, request.user_id, encrypted_data
            );
            if let Err(e) = app_state.db.execute(insert_query).await {
                return ResponseHandler::standard_error(format!("INSERT ERROR {}", e));
            }
        }

        (true, json!({"msg": "Identity card updated successfully"}))
    }

    pub async fn get(
        value: &'static str,
        request: &MessageRequest,
        app_state: Arc<AppState>,
    ) -> (bool, Value) {
        let encrypted_card = match app_state
            .db
            .select(
                format!(
                    "SELECT iw.{} FROM identity_wallet iw 
                    JOIN users u ON iw.user_id = u.id 
                    WHERE u.username = '{}' OR u.email = '{}'",
                    value, request.user_id, request.user_id
                ),
                value,
            )
            .await
        {
            Ok(card) => card,
            Err(e) => return ResponseHandler::standard_error(e.to_string()),
        };

        let decrypted_json = match app_state.cripto_manager.decrypt(&encrypted_card) {
            Ok(decrypted) => decrypted,
            Err(e) => return ResponseHandler::standard_error(format!("Decryption error: {}", e)),
        };

        let identity_card: Value = match serde_json::from_str(&decrypted_json) {
            Ok(json) => json,
            Err(e) => return ResponseHandler::standard_error(format!("JSON parse error: {}", e)),
        };

        (true, json!(identity_card))
    }
}
