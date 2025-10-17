use std::env;
use std::sync::Arc;
use tokio_postgres::{Client, Error, NoTls};

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
    pub async fn configure_database(&self) -> Result<(), Error> {
        self.execute(String::from(
            "
            CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,            
            username TEXT NOT NULL,            
            password_hash TEXT NOT NULL,  
            phone_number TEXT,          
            created_at TIMESTAMPTZ DEFAULT now(), 
            updated_at TIMESTAMPTZ DEFAULT now() 
        );
        ",
        ))
        .await?;
        Ok(())
    }
    pub async fn execute(&self, query: String) -> Result<(), Error> {
        self.client.execute(query.as_str(), &[]).await?;
        Ok(())
    }
    pub async fn select(&self, query: String, value: String) -> Result<String, Error> {
        let row = self.client.query_one(query.as_str(), &[]).await?;
        Ok(row.get(value.as_str()))
    }
}
