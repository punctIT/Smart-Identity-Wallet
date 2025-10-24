use crate::handle_requests::response_handler::ResponseHandler;
use crate::others::common::{MessageRequest, MessageResponse};
use axum::{extract::Json as ExtractJson, response::Json};
use chrono::Utc;
use reqwest::Client;
use serde_json::json;
use serde_json::Value;
pub struct AiRequests {}
impl AiRequests {
    pub async fn handle_ai_reqsuest(
        ExtractJson(request): ExtractJson<MessageRequest>,
    ) -> Json<MessageResponse> {
        println!("📨 AI Request primit: {:?}", request);
        let (success, data) = match request.message_type.as_str() {
            "ChatBot" => AiRequests::call_python_chat(&request).await,
            "OCR" => AiRequests::call_python_ocr(&request).await,
            "health" => AiRequests::call_python_health().await,
            _ => AiRequests::unknown().await,
        };

        Json(MessageResponse {
            success,
            message_type: request.message_type.clone(),
            data,
            timestamp: Utc::now().to_rfc3339(),
        })
    }

    pub async fn call_python_chat(request: &MessageRequest) -> (bool, Value) {
        let client = Client::new();

        let response = match client
            .post("http://localhost:8001/chat")
            .json(&request)
            .send()
            .await
        {
            Ok(re) => re,
            Err(e) => return ResponseHandler::standard_error(e.to_string()),
        };

        let chat_response: Value = response.json().await.unwrap();

        println!("{:?}", chat_response);

        (true, chat_response)
    }

    pub async fn call_python_ocr(request: &MessageRequest) -> (bool, Value) {
        let client = Client::new();
        println!("aici ceva");
        let response = match client
            .post("http://localhost:8001/ocr")
            .json(&request)
            .send()
            .await
        {
            Ok(re) => re,
            Err(e) => return ResponseHandler::standard_error(e.to_string()),
        };

        let chat_response: Value = response.json().await.unwrap();

        //println!("{:?}", chat_response);

        (true, chat_response)
    }
    pub async fn call_python_health() -> (bool, Value) {
        let client = Client::new();

        let response = match client.get("http://localhost:8001/health").send().await {
            Ok(re) => re,
            Err(e) => return ResponseHandler::standard_error(e.to_string()),
        };

        let health_response: String = match response.json().await{
            Ok(e)=>e,
            Err(_)=>return ResponseHandler::standard_error(String::from("unknown request")),
        };
        (true, json!(health_response))
    }
    async fn unknown() -> (bool, Value) {
        ResponseHandler::standard_error(String::from("unknown request"))
    }
}
