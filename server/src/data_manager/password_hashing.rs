use argon2::password_hash::{PasswordHash, SaltString};
use argon2::{Argon2, PasswordHasher, PasswordVerifier};
use rand_core::OsRng;

pub struct PasswordHashManager {
    password: String,
    password_hash: String,
}

impl PasswordHashManager {
    pub fn new(password: String, password_hash: String) -> Self {
        PasswordHashManager {
            password,
            password_hash,
        }
    }

    pub fn check(&self) -> Result<bool, String> {
        let parsed_hash = PasswordHash::new(&self.password_hash).map_err(|e| e.to_string())?;
        let argon2 = Argon2::default();
        let is_valid = argon2
            .verify_password(self.password.as_bytes(), &parsed_hash)
            .is_ok();

        Ok(is_valid)
    }

    pub fn get_hashed(password: String) -> Result<String, String> {
        let salt = SaltString::generate(&mut OsRng);
        let argon2 = Argon2::default();
        let password_hash = argon2
            .hash_password(password.as_bytes(), &salt)
            .map_err(|e| e.to_string())?
            .to_string();
        Ok(password_hash)
    }
}
