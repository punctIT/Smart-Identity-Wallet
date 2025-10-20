use crate::others::common::MessageRequest;

use serde_json::{json, Value};

use std::sync::Arc;

use crate::handle_requests::response_handler::ResponseHandler;
use crate::network::server_https::AppState;
pub struct NewsData {}
impl NewsData {
    #[allow(dead_code)]
    pub async fn insert(request: &MessageRequest, app_state: Arc<AppState>) -> (bool, Value) {
        let content = match &request.content {
            Some(content) => content,
            None => return ResponseHandler::standard_error("Must be a json".to_string()),
        };

        match app_state
            .db
            .execute(
                format!(
                    "INSERT INTO news (data_col, json_col) VALUES (CURRENT_DATE, '{}');",
                    content
                )
                .to_string(),
            )
            .await
        {
            Ok(_) => (true, json!({"msg": "Document successful"})),
            Err(e) => (false, json!({"Error": e.to_string()})),
        }
    }
    pub async fn get_latest_news(app_state: Arc<AppState>) -> (bool, Value) {
        // Query pentru ultimele 3 știri
        let query = "SELECT json_col FROM news ORDER BY data_col DESC LIMIT 3;".to_string();

        match app_state.db.select_all(query, "json_col").await {
            Ok(rows) => {
                let mut news_array = Vec::new();

                for row in rows {
                    // Încearcă să parseze fiecare JSON din baza de date
                    match serde_json::from_str::<Value>(&row) {
                        Ok(parsed_json) => news_array.push(parsed_json),
                        Err(_) => {
                            // Dacă vreunul e invalid, îl putem ignora sau înlocui cu o eroare
                            news_array.push(json!({"Error": "Invalid JSON format"}));
                        }
                    }
                }

                // Împachetăm toate știrile într-un singur JSON
                (true, json!({ "news": news_array }))
            }
            Err(e) => (false, json!({ "Error": e.to_string() })),
        }
    }
}
