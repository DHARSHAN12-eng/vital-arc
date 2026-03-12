import base64, re, os
from PIL import Image
import io

img_path = r'z:\vital-arc\LOGOVA.png'
print(f'Original image size: {os.path.getsize(img_path)} bytes')

img = Image.open(img_path).convert('RGBA')
bg = Image.new('RGBA', img.size, (255, 255, 255))
out = Image.alpha_composite(bg, img).convert('RGB')
out.thumbnail((120, 120))  # Resize smaller since it's just a top-bar/profile logo

buffer = io.BytesIO()
out.save(buffer, format='JPEG', quality=85)
logo_data = buffer.getvalue()

new_logo = 'data:image/jpeg;base64,' + base64.b64encode(logo_data).decode()
print(f'New logo base64 size: {len(new_logo)} bytes')

index_path = r'z:\vital-arc\api\index.py'
with open(index_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace LOGO_B64 = "data:image/..." 
content = re.sub(r'LOGO_B64 = "data:image[^"]*"', 'LOGO_B64 = "' + new_logo + '"', content)

with open(index_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Updated index.py size: {os.path.getsize(index_path)} bytes')
