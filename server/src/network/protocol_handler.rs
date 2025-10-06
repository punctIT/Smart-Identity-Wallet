pub struct ProtocolHandler {
    text: Option<String>,
}
impl ProtocolHandler {
    pub fn new() -> Self {
        Self { text: None }
    }
    pub fn set_text(&mut self, text: String) -> &mut Self {
        self.text = Some(text);
        self
    }
    pub fn get_text(&self) -> Option<String> {
        self.text.clone()
    }
}
