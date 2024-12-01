from PIL import Image
import base64
import io


def convert_and_resize_icon(image_path, size=(80, 80)):
    # Abrir e redimensionar a imagem
    with Image.open(image_path) as img:
        # Converter para RGBA se não estiver
        img = img.convert('RGBA')
        # Redimensionar
        img = img.resize(size, Image.Resampling.LANCZOS)

        # Salvar em bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()

        # Converter para base64
        base64_str = base64.b64encode(img_byte_arr).decode('utf-8')
        return base64_str


# Converter seus ícones
play_base64 = convert_and_resize_icon('resources/play_icon.png')
stop_base64 = convert_and_resize_icon('resources/stop_icon.png')

print("PLAY_ICON = '''")
print(play_base64)
print("'''")
print("\nSTOP_ICON = '''")
print(stop_base64)
print("'''")