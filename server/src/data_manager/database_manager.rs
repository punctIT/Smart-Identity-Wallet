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
        let db_password = env::var("DB_PASSWORD").expect("DB_NAME must be set");
        let db_user = env::var("DB_USER").expect("DB_NAME must be set");
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
    pub async fn text(&self)->Result<(), Error>{
        self.client.execute("CREATE TABLE IF NOT EXISTS person (id SERIAL PRIMARY KEY, name TEXT)", &[]).await?;
        Ok(())
    }
}
