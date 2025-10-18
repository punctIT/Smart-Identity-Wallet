use crate::others::common::MessageRequest;

use serde_json::{json, Value};

use std::sync::Arc;

use crate::handle_requests::response_handler::ResponseHandler;
use crate::network::server_https::AppState;
pub struct IdentityCard {}
impl IdentityCard {
    pub async fn insert(request: &MessageRequest, app_state: Arc<AppState>) -> (bool, Value) {
        let content = match &request.content {
            Some(content) => content,
            None => return ResponseHandler::standard_error("Must be a json".to_string()),
        };

        let user_id = match app_state
            .db
            .select(
                format!(
                    "SELECT id::text as id FROM users WHERE username = '{}' OR email = '{}'",
                    request.user_id, request.user_id
                ),
                "id",
            )
            .await
        {
            Ok(user_id) => user_id,
            Err(e) => return ResponseHandler::standard_error(e.to_string()),
        };

        let json_string = serde_json::to_string(content).unwrap_or_else(|_| "{}".to_string());
        let encrypted_data = match app_state.cripto_manager.encrypt(&json_string) {
            Ok(encrypted) => encrypted,
            Err(e) => return ResponseHandler::standard_error(format!("Encryption error: {}", e)),
        };

        if let Err(e) = app_state
            .db
            .execute(format!(
                "INSERT INTO identity_wallet (user_id, identity_card) VALUES ('{}', '{}')",
                user_id, encrypted_data
            ))
            .await
        {
            return ResponseHandler::standard_error(e.to_string());
        }

        (true, json!({"msg": "Document successful"}))
    }

    pub async fn update(request: &MessageRequest, app_state: Arc<AppState>) -> (bool, Value) {
        let content = match &request.content {
            Some(content) => content,
            None => return ResponseHandler::standard_error("Must be a json".to_string()),
        };

        let json_string = serde_json::to_string(content).unwrap_or_else(|_| "{}".to_string());
        let encrypted_data = match app_state.cripto_manager.encrypt(&json_string) {
            Ok(encrypted) => encrypted,
            Err(e) => return ResponseHandler::standard_error(format!("Encryption error: {}", e)),
        };

        if let Err(e) = app_state
            .db
            .execute(format!(
                "UPDATE identity_wallet 
                 SET identity_card = '{}' 
                 WHERE user_id = (
                     SELECT id FROM users 
                     WHERE username = '{}' OR email = '{}'
                 )",
                encrypted_data, request.user_id, request.user_id
            ))
            .await
        {
            return ResponseHandler::standard_error(format!("UPDATE ERROR {}", e));
        }

        (true, json!({"msg": "Identity card updated successfully"}))
    }

    pub async fn get(request: &MessageRequest, app_state: Arc<AppState>) -> (bool, Value) {
        let encrypted_card = match app_state
            .db
            .select(
                format!(
                    "SELECT iw.identity_card FROM identity_wallet iw 
                    JOIN users u ON iw.user_id = u.id 
                    WHERE u.username = '{}' OR u.email = '{}'",
                    request.user_id, request.user_id
                ),
                "identity_card",
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
