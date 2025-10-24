use crate::others::common::MessageRequest;

use serde_json::{json, Value};

use std::sync::Arc;

use crate::network::server_https::AppState;

pub struct PersonalDataManager {}
impl PersonalDataManager {
    pub async fn check_all_cards(
        request: &MessageRequest,
        app_state: Arc<AppState>,
    ) -> (bool, Value) {
        let card_fields = vec!["identity_card", "driving_license", "passport"];

        let mut cards = Vec::new();

        for field in card_fields {
            let query = format!(
                "SELECT COUNT(*)::text as count FROM identity_wallet iw 
                 JOIN users u ON iw.user_id = u.id 
                 WHERE (u.username = '{}' OR u.email = '{}' OR u.phone_number = '{}') 
                 AND iw.{} IS NOT NULL",
                request.user_id, request.user_id, request.user_id, field
            );

            let exists = match app_state.db.select(query, "count").await {
                Ok(result) => {
                    let count: i32 = result.parse().unwrap_or(0);
                    count > 0
                }
                Err(_) => false,
            };
            if exists {
                cards.push(json!({ "title": field }));
            }
        }

        (true, json!({ "cards": cards }))
    }
    pub async fn check_all_auto_data(
        request: &MessageRequest,
        app_state: Arc<AppState>,
    ) -> (bool, Value) {
        let card_fields = vec!["vehicle_registration", "insurance_auto"];

        let mut cards = Vec::new();

        for field in card_fields {
            let query = format!(
                "SELECT COUNT(*)::text as count FROM identity_wallet iw 
                 JOIN users u ON iw.user_id = u.id 
                 WHERE (u.username = '{}' OR u.email = '{}' OR u.phone_number = '{}') 
                 AND iw.{} IS NOT NULL",
                request.user_id, request.user_id, request.user_id, field
            );

            let exists = match app_state.db.select(query, "count").await {
                Ok(result) => {
                    let count: i32 = result.parse().unwrap_or(0);
                    count > 0
                }
                Err(_) => false,
            };
            if exists {
                cards.push(json!({ "title": field }));
            }
        }

        (true, json!({ "cards": cards }))
    }
    pub async fn get_user_info(
        request: &MessageRequest,
        app_state: Arc<AppState>,
    ) -> (bool, Value) {
        match app_state
            .db
            .select_row(format!(
                "select email,username,phone_number from users where username='{}' or email='{}'",
                request.user_id, request.user_id
            ))
            .await
        {
            Ok(e) => (true, json!({ "user": e })),
            Err(e) => (false, json!({ "Errro": e.to_string() })),
        }
    }
}
