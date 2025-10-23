use std::env;
use std::sync::Arc;

use tokio_postgres::{Client, Error, NoTls};

use crate::data_manager::password_hashing::PasswordHashManager;
use crate::network::auth::LoginRequest;

#[derive(Clone)]
pub struct DBManager {
    #[allow(dead_code)]
    client: Arc<Client>,
}

impl DBManager {
    pub async fn new() -> Result<Arc<Self>, Error> {
        dotenv::dotenv().ok();
        let db_name = env::var("DB_NAME").expect("DB_NAME must be set");
        let db_password = env::var("DB_PASSWORD").expect("db_password must be set");
        let db_user = env::var("DB_USER").expect("DB_user must be set");

        let (client, connection) = tokio_postgres::connect(
            format!(
                "host=localhost user={} password={} dbname={}",
                db_user, db_password, db_name
            )
            .as_str(),
            NoTls,
        )
        .await?;

        tokio::spawn(async move {
            if let Err(e) = connection.await {
                eprintln!("connection error: {}", e);
            }
        });
        Ok(Arc::new(Self {
            client: Arc::new(client),
        }))
    }
    pub async fn check_email(&self, email: &String) -> Result<bool, Error> {
        let exists: bool = self
            .client
            .query_one(
                "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)",
                &[&email],
            )
            .await?
            .get(0);
        Ok(exists)
    }
    pub async fn select_count(&self, query: String, value: &'static str) -> Result<i64, Error> {
        let row = self.client.query_one(query.as_str(), &[]).await?;
        Ok(row.get::<&str, i64>(value))
    }
    pub async fn check_login_credentials(
        &self,
        login_request: &LoginRequest,
    ) -> Result<bool, Error> {
        let exists_username: bool = self
            .client
            .query_one(
                "SELECT EXISTS(SELECT 1 FROM users WHERE email = $1 OR  username = $1 OR phone_number = $1)",
                &[&login_request.username],
            )
            .await?
            .get(0);
        if !exists_username {
            return Ok(false);
        }
        let password_hash: String = self
            .client
            .query_one(
                "SELECT password_hash FROM users WHERE email = $1 OR  username = $1 OR phone_number = $1",
                &[&login_request.username],
            )
            .await?
            .get(0);
        let p_hash = PasswordHashManager::new(login_request.password.clone(), password_hash);
        Ok(exists_username && p_hash.check().unwrap_or(false))
    }
    pub async fn configure_database(&self) -> Result<(), Error> {
        self.execute(String::from(
            "
            CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(100) UNIQUE NOT NULL,
            username TEXT NOT NULL,            
            password_hash TEXT NOT NULL,  
            phone_number TEXT,          
            created_at TIMESTAMPTZ DEFAULT now(), 
            updated_at TIMESTAMPTZ DEFAULT now() 
        );",
        ))
        .await?;
        self.execute(
            "
         CREATE TABLE IF NOT EXISTS identity_wallet (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            identity_card TEXT,
            driving_license TEXT,
            passport TEXT,
            vehicle_registration TEXT,
            insurance_auto TEXT,
            CONSTRAINT unique_user_identity UNIQUE(user_id)
        );
        "
            .to_string(),
        )
        .await?;
        self.execute(
            "CREATE INDEX IF NOT EXISTS idx_identity_wallet_user_id ON identity_wallet(user_id);"
                .to_string(),
        )
        .await?;
        self.execute(
            "
            CREATE TABLE IF NOT EXISTS news (
                id SERIAL PRIMARY KEY,
                data_col DATE NOT NULL,
                json_col TEXT NOT NULL
            );
            "
            .to_string(),
        )
        .await?;
        Ok(())
    }
    pub async fn execute(&self, query: String) -> Result<(), Error> {
        self.client.execute(query.as_str(), &[]).await?;
        Ok(())
    }
    pub async fn select(&self, query: String, value: &'static str) -> Result<String, Error> {
        let row = self.client.query_one(query.as_str(), &[]).await?;
        Ok(row.get(value))
    }
    pub async fn select_all(
        &self,
        query: String,
        column: &'static str,
    ) -> Result<Vec<String>, Error> {
        let rows = self.client.query(query.as_str(), &[]).await?;
        let mut results = Vec::new();

        for row in rows {
            let value: String = row.get(column);
            results.push(value);
        }

        Ok(results)
    }
    pub async fn select_row(&self, query: String) -> Result<Vec<String>, Error> {
        use tokio_postgres::Row;
        let row: Row = self.client.query_one(query.as_str(), &[]).await?;
        let mut result = Vec::new();

        for i in 0..row.len() {
            let value: String = match row.try_get(i) {
                Ok(v) => v,
                Err(_) => String::from("NULL"),
            };
            result.push(value);
        }

        Ok(result)
    }
}
