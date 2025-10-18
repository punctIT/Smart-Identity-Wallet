use crate::others::common::MessageRequest;

use serde_json::{json, Value};

use std::sync::Arc;

use crate::handle_requests::response_handler::ResponseHandler;
use crate::network::server_https::AppState;

pub struct PersonalDataManager {}

impl PersonalDataManager {
    pub async fn get_wallet_data(
        request: &MessageRequest,
        app_state: Arc<AppState>,
    ) -> (bool, Value) {
        let exists_identity_card = match app_state
            .db
            .select(
                format!(
                    "SELECT COUNT(*)::text as count FROM identity_wallet iw 
                     JOIN users u ON iw.user_id = u.id 
                     WHERE (u.username = '{}' OR u.email = '{}' OR u.phone_number = '{}') 
                     AND iw.identity_card IS NOT NULL",
                    request.user_id, request.user_id, request.user_id
                ),
                "count",
            )
            .await
        {
            Ok(result) => {
                let count: i32 = result.parse().unwrap_or(0);
                count > 0
            }
            Err(_) => {
                return ResponseHandler::standard_error("exist identity card error".to_string())
            }
        };
        (
            true,
            json!({
                "Identity": exists_identity_card
            }),
        )
    }
}
