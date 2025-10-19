use crate::handle_requests::response_handler::ResponseHandler;
use crate::others::common::{MessageRequest, MessageResponse};
use axum::{
    extract::{Json as ExtractJson, State},
    response::Json,
};
use chrono::Utc;
use reqwest::Client;
use serde_json::json;
use serde_json::Value;
pub struct AiRequests {}
impl AiRequests {
    pub async fn handle_ai_reqsuest(
        ExtractJson(request): ExtractJson<MessageRequest>,
    ) -> Json<MessageResponse> {
        println!("📨 Request primit: {:?}", request);
        let (success, data) = match request.message_type.as_str() {
            "ChatBot" => AiRequests::call_python_chat(&request).await,
            _ => AiRequests::call_python_chat(&request).await,
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
}

pub async fn call_python_ocr(request: &MessageRequest) -> (bool, Value) {
    // let client = Client::new();

    // let part = reqwest::multipart::Part::bytes(image_bytes.to_vec())
    //     .file_name("upload.jpg")
    //     .mime_str("image/jpeg")?;

    // let form = reqwest::multipart::Form::new()
    //     .part("file", part);

    // let response = client
    //     .post("http://localhost:8001/ocr")
    //     .multipart(form)
    //     .send()
    //     .await?;

    // let ocr_response: OCRResponse = response.json().await?;

    // println!("✅ OCR response: {} (from {})", ocr_response.text, ocr_response.service);

    (false, json!(" "))
}
pub async fn call_python_health(request: &MessageRequest) -> (bool, Value) {
    let client = Client::new();

    let response = match client.get("http://localhost:8001/health").send().await {
        Ok(re) => re,
        Err(e) => return ResponseHandler::standard_error(e.to_string()),
    };
    let health_response: String = response.json().await.unwrap();

    (true, json!(health_response))
}
