# File Upload & QR Code Generation Guide

## Overview

The system now supports:
1. **360° Image Upload**: Upload real panorama images instead of providing URLs
2. **Automatic QR Code Generation**: QR codes are automatically created when you save a node

## Features

### 1. 360° Panorama Image Upload

**How to Upload:**
- When creating or editing a node, use the "360° Panorama Image" file input
- Accepts: JPG, PNG, and other common image formats
- Recommended: Equirectangular 360° panorama images (2:1 aspect ratio)
- Images are stored in `media/360_images/` directory

**Viewing Uploaded Images:**
- Nodes list shows thumbnail previews of uploaded 360° images
- Click on thumbnail to view full-size image in new tab
- Edit form displays current image with option to replace

### 2. Automatic QR Code Generation

**How It Works:**
- QR code is **automatically generated** when you save a node
- No manual input required
- QR code contains JSON data with node information:
  ```json
  {
    "node_code": "BLDG-101-R01",
    "name": "Computer Lab 1",
    "building": "Engineering Building"
  }
  ```

**QR Code Features:**
- Stored as PNG images in `media/qrcodes/` directory
- Filename format: `qr_{node_code}.png`
- Can be downloaded directly from nodes list
- Regenerate option available when editing nodes

**Using QR Codes:**
1. Print the QR code and place it at the physical location
2. Users scan the QR code with their mobile device
3. The app can parse the JSON data to identify the node
4. Perfect for navigation and location identification

### 3. File Storage

**Directory Structure:**
```
media/
├── 360_images/        # Uploaded 360° panorama images
│   └── panorama_*.jpg
└── qrcodes/          # Auto-generated QR codes
    └── qr_*.png
```

**Accessing Files:**
- Development server: `http://127.0.0.1:8000/media/360_images/filename.jpg`
- QR codes: `http://127.0.0.1:8000/media/qrcodes/qr_CODE.png`

### 4. Node Form Updates

**Creating a Node:**
1. Fill in required fields (code, name, building, floor)
2. Optionally upload a 360° image
3. Click Save
4. QR code is automatically generated and saved

**Editing a Node:**
1. Current 360° image is displayed (if exists)
2. Upload new image to replace (optional)
3. Current QR code is shown
4. Check "Regenerate QR code on save" to create new QR
5. QR is auto-regenerated if node_code changes

## Technical Details

### Models

```python
class Nodes(models.Model):
    # ... other fields ...
    image360 = models.ImageField(upload_to='360_images/', blank=True, null=True)
    qrcode = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
```

### QR Code Generation

The `Nodes` model automatically generates QR codes in the `save()` method:

```python
def save(self, *args, **kwargs):
    # Generate QR code if node_code exists and qrcode doesn't
    if self.node_code and not self.qrcode:
        qr = qrcode.QRCode(...)
        qr_data = f'{{"node_code": "{self.node_code}", ...}}'
        # ... QR generation logic ...
    super().save(*args, **kwargs)
```

### View Updates

File uploads are handled with `request.FILES`:

```python
if 'image360' in request.FILES:
    node.image360 = request.FILES['image360']
```

Forms must include `enctype="multipart/form-data"` attribute.

## Best Practices

### 360° Images
- Use equirectangular projection (2:1 aspect ratio)
- Recommended resolution: 4096x2048 or higher
- Ensure north direction is at top of image for compass accuracy
- Compress images to reduce file size (recommended < 5MB)

### QR Codes
- Print at minimum 2x2 inches for reliable scanning
- Use white background for best results
- Laminate printed QR codes for durability
- Place at eye level for easy scanning

### File Management
- Regularly backup `media/` directory
- Consider implementing file size limits
- Use descriptive filenames for uploaded images
- Monitor disk space usage

## Database Migrations

The system automatically created migration `0003` with these changes:
- Removed: `qrcode_url` (URLField)
- Added: `qrcode` (ImageField)
- Changed: `image360` from URLField to ImageField

## Dependencies

Required packages (already installed):
- `Pillow`: Image processing library
- `qrcode[pil]`: QR code generation with PIL support

## Production Deployment

For production environments:
1. Configure proper media storage (e.g., AWS S3, Azure Blob)
2. Set up proper file upload size limits
3. Implement image optimization/compression
4. Configure CDN for media file delivery
5. Set up backup strategy for media files

## Troubleshooting

**Images not displaying:**
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings.py
- Verify media URL pattern in urls.py
- Ensure `media/` directory has proper permissions

**QR codes not generating:**
- Verify `qrcode` and `Pillow` packages are installed
- Check for errors in save() method
- Ensure `media/qrcodes/` directory exists and is writable

**File upload fails:**
- Check form has `enctype="multipart/form-data"`
- Verify file size is within limits
- Check disk space availability
- Review file format restrictions
