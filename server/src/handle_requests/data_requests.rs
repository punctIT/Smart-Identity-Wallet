use crate::others::common::{MessageRequest, MessageResponse};
use axum::{
    extract::{Json as ExtractJson, State},
    response::Json,
};
use chrono::Utc;
use serde_json::Value;
use std::sync::Arc;

use crate::handle_requests::personal_data_requests::identity_card::IdentityCard;
use crate::handle_requests::personal_data_requests::personal_data_manager::PersonalDataManager;
use crate::handle_requests::response_handler::ResponseHandler;
use crate::network::server_https::AppState;

pub struct DataRequestHandler {}
impl DataRequestHandler {
    pub async fn handle_message(
        State(app_state): State<Arc<AppState>>,
        ExtractJson(request): ExtractJson<MessageRequest>,
    ) -> Json<MessageResponse> {
        println!("📨 Request primit: {:?}", request);
        let (success, data) = match request.message_type.as_str() {
            "InsertIdenityCard" => IdentityCard::insert(&request, app_state).await,
            "GetIdenityCard" => IdentityCard::get(&request, app_state).await,
            "UpdateIdenityCard" => IdentityCard::update(&request, app_state).await,
            "GetWalletCards" => PersonalDataManager::get_wallet_data(&request, app_state).await,
            "nimic" => IdentityCard::get(&request, app_state).await,
            "identity_verify" => IdentityCard::get(&request, app_state).await,
            _ => DataRequestHandler::unknown().await,
        };

        Json(MessageResponse {
            success,
            message_type: request.message_type.clone(),
            data,
            timestamp: Utc::now().to_rfc3339(),
        })
    }
    async fn unknown() -> (bool, Value) {
        ResponseHandler::standard_error(String::from("unknown request"))
    }
}
