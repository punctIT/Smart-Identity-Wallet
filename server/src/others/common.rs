use serde::{Deserialize, Serialize};
use serde_json::Value;

#[derive(Deserialize, Serialize, Debug, Clone)]
pub struct MessageRequest {
    pub message_type: String,
    pub user_id: String,
    pub content: Option<Value>,
}

#[derive(Serialize)]
pub struct MessageResponse {
    pub success: bool,
    pub message_type: String,
    pub data: Value,
    pub timestamp: String,
}
