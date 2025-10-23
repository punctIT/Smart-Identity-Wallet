
import io
import qrcode
from kivy.uix.image import Image
from kivy.core.image import Image as CoreImage


class QRCodeWidget(Image):
    def __init__(self, data_str, **kwargs):
        super().__init__(**kwargs)
        self.generate_qr(data_str)

    def generate_qr(self, data_str):
        # Generăm codul QR
        qr = qrcode.QRCode(version=1, box_size=8, border=2)
        qr.add_data(data_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Salvăm în buffer (nu pe disc)
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # Convertim în imagine Kivy
        core_img = CoreImage(buffer, ext='png')
        self.texture = core_img.texture
