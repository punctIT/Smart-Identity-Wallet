use axum::{
    http::{Request, StatusCode, HeaderMap},
    middleware::Next,
    response::Response,
    extract::{State},
};
use crate::network::auth::SessionManager;

use std::sync::Arc;

pub async fn auth_middleware<B>(
    State(session_manager): State<Arc<SessionManager>>,
    headers: HeaderMap,
    request: Request<B>,
    next: Next<B>,
) -> Result<Response, StatusCode> {
    let auth_header = headers.get("Authorization")
        .and_then(|header| header.to_str().ok())
        .and_then(|header| {
            if header.starts_with("Bearer ") {
                header.strip_prefix("Bearer ")
            } else {
                None
            }
        });

    match auth_header {
        Some(token) => {
            if let Some(session) = session_manager.validate_token(token) {
                println!("🔓 Acces autorizat pentru {} la 2025-10-14 04:58:15", session.user_id);
                Ok(next.run(request).await)
            } else {
                println!("❌ Token invalid la 2025-10-14 04:58:15");
                Err(StatusCode::UNAUTHORIZED)
            }
        }
        None => {
            println!("❌ Lipsă token autentificare la 2025-10-14 04:58:15");
            Err(StatusCode::UNAUTHORIZED)
        }
    }
}