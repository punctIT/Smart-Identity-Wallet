use crate::others::common::{MessageRequest, MessageResponse};
use axum::{
    extract::{Json as ExtractJson, State},
    response::Json,
};
use chrono::Utc;
use serde_json::{json, Value};
use std::sync::Arc;

use crate::handle_requests::info_data_requests::news_data_requests::NewsData;
use crate::handle_requests::personal_data_requests::personal_data_manager::PersonalDataManager;
use crate::handle_requests::personal_data_requests::wallet_data::WalletCards;
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
            "InsertIdenityCard" => WalletCards::insert("identity_card", &request, app_state).await,
            "GetIdenityCard" => WalletCards::get("identity_card", &request, app_state).await,
            "InsertDrivingLicense" => {
                WalletCards::insert("driving_license", &request, app_state).await
            }
            "GetDrivingLicense" => WalletCards::get("driving_license", &request, app_state).await,
            "InsertPassport" => WalletCards::insert("passport", &request, app_state).await,
            "GetPassport" => WalletCards::get("passport", &request, app_state).await,
            "InsertVehicleRegistration" => {
                WalletCards::insert("vehicle_registration", &request, app_state).await
            }
            "GetVehicleRegistration" => {
                WalletCards::get("vehicle_registration", &request, app_state).await
            }
            "InsertInsuranceAuto" => {
                WalletCards::insert("insurance_auto", &request, app_state).await
            }
            "logout" => DataRequestHandler::logout(&request, app_state).await,
            "GetInsuranceAuto" => WalletCards::get("insurance_auto", &request, app_state).await,
            "GetWalletCards" => PersonalDataManager::check_all_cards(&request, app_state).await,
            "GetWalletAuto" => PersonalDataManager::check_all_auto_data(&request, app_state).await,
            "UserInfo" => PersonalDataManager::get_user_info(&request, app_state).await,
            "News" => NewsData::get_latest_news(app_state).await,
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
    async fn logout(request: &MessageRequest, app_state: Arc<AppState>) -> (bool, Value) {
        (
            app_state.session_manager.logout(&request.user_id),
            json!(""),
        )
    }
}
