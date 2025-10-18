use serde_json::{json, Value};

pub struct ResponseHandler {}

impl ResponseHandler {
    pub fn standard_error(err: String) -> (bool, Value) {
        (
            false,
            json!({
                "Error": err
            }),
        )
    }
}
