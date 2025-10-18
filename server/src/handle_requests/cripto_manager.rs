use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce,
};
use base64::{engine::general_purpose, Engine as _};
use std::env;

#[derive(Clone)]
#[allow(dead_code)]
pub struct CryptoManager {
    cipher: Aes256Gcm,
}

impl CryptoManager {
    pub fn new() -> Result<Self, Box<dyn std::error::Error>> {
        dotenv::dotenv().ok();
        let key_string =
            env::var("ENCRYPTION_KEY").map_err(|_| "ENCRYPTION_KEY nu a fost găsit în .env")?;

        let key_bytes = general_purpose::STANDARD
            .decode(&key_string)
            .map_err(|_| "Cheia nu este un base64 valid")?;

        if key_bytes.len() != 32 {
            return Err("Cheia trebuie să aibă 32 de bytes (256 biți)".into());
        }

        let key: &Key<Aes256Gcm> = key_bytes.as_slice().into();
        let cipher = Aes256Gcm::new(key);

        Ok(CryptoManager { cipher })
    }

    pub fn encrypt(&self, plaintext: &str) -> Result<String, Box<dyn std::error::Error>> {
        let nonce = Aes256Gcm::generate_nonce(&mut OsRng);
        let ciphertext = self
            .cipher
            .encrypt(&nonce, plaintext.as_bytes())
            .map_err(|_| "Eroare la criptare")?;

        let mut result = nonce.to_vec();
        result.extend_from_slice(&ciphertext);
        Ok(general_purpose::STANDARD.encode(&result))
    }

    pub fn decrypt(&self, encrypted_data: &str) -> Result<String, Box<dyn std::error::Error>> {
        let data = general_purpose::STANDARD
            .decode(encrypted_data)
            .map_err(|_| "Date criptate invalide (base64)")?;

        if data.len() < 12 {
            return Err("Date criptate prea scurte".into());
        }

        let (nonce_bytes, ciphertext) = data.split_at(12);

        let nonce_array: [u8; 12] = nonce_bytes.try_into().map_err(|_| "Invalid nonce length")?;
        let nonce = Nonce::from(nonce_array);

        let plaintext = self
            .cipher
            .decrypt(&nonce, ciphertext)
            .map_err(|_| "Eroare la decriptare")?;

        String::from_utf8(plaintext).map_err(|_| "Textul decriptat nu este UTF-8 valid".into())
    }

    #[allow(dead_code)]
    pub fn generate_key() -> String {
        let key = Aes256Gcm::generate_key(OsRng);
        general_purpose::STANDARD.encode(key)
    }
}
