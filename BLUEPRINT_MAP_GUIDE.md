# Campus Blueprint Map Feature Guide

## Overview

The campus map feature allows you to:
1. Upload blueprint/floor plan images for each building and floor
2. Visually position nodes by clicking on the blueprint
3. Display navigation routes as lines on the map
4. Store coordinates as percentages (responsive to different screen sizes)

## Quick Start

### Step 1: Upload a Blueprint

1. Navigate to **Map Editor** from the navigation menu
2. Select a **Building** and **Floor** from the dropdowns
3. If no map exists, click **"Upload Blueprint"**
4. Fill in the form:
   - **Map Name**: e.g., "Engineering Building - Floor 1"
   - **Blueprint Image**: Upload your floor plan image (JPG, PNG)
   - **Scale** (optional): Meters per pixel for distance calculations
5. Click **Upload**

### Step 2: Position Nodes

1. After uploading, the blueprint will appear on the canvas
2. The left sidebar shows all nodes on that floor
3. **Click on a node** in the sidebar to select it
4. **Click on the blueprint** where that node should be positioned
5. The node appears as a blue dot with its code label
6. Repeat for all nodes on the floor
7. Click **"Save All Positions"** when done

### Step 3: View Results

- Positioned nodes show as blue dots on the blueprint
- Selected node highlights in yellow
- Node list shows coordinates (X%, Y%)
- Green border = positioned, Gray border = not positioned

## Data Structure

### What Data is Stored

#### For Each Map (CampusMap Model):
```python
- building: "Engineering Building"
- floor_level: 1
- blueprint_image: Image file stored in media/campus_maps/
- scale_meters_per_pixel: 0.05 (optional, for distance calculations)
- north_rotation: 0.0 (degrees, where north points on the image)
```

#### For Each Node (map_x, map_y fields):
```python
- map_x: 45.5  # Percentage from left (0-100%)
- map_y: 32.8  # Percentage from top (0-100%)
```

### Why Percentages?

Coordinates are stored as **percentages (0-100%)** instead of pixels because:
- **Responsive**: Works on any screen size
- **Resolution Independent**: Same coordinates work for different image sizes
- **Scalable**: Blueprint can be replaced without repositioning nodes

### Coordinate System

```
(0%, 0%)  ────────────────────────  (100%, 0%)
   │                                    │
   │                                    │
   │         • Node at (45%, 30%)      │
   │                                    │
   │                                    │
(0%, 100%) ────────────────────────  (100%, 100%)

X: Left (0%) to Right (100%)
Y: Top (0%) to Bottom (100%)
```

## How to Determine Dot Position (Frontend)

### Interactive Canvas Method

The Map Editor uses HTML5 Canvas with click handling:

```javascript
// 1. User selects a node from the sidebar
selectedNodeId = 5;

// 2. User clicks on the blueprint canvas
canvas.addEventListener('click', function(e) {
    // Get click position relative to canvas
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Convert pixels to percentage
    const xPercent = (x / canvas.width) * 100;
    const yPercent = (y / canvas.height) * 100;
    
    // Save to node data
    node.map_x = xPercent;  // e.g., 45.5
    node.map_y = yPercent;  // e.g., 32.8
});

// 3. Redraw canvas with dot at position
function drawNode(node) {
    // Convert percentage back to pixels
    const x = (node.map_x / 100) * canvas.width;
    const y = (node.map_y / 100) * canvas.height;
    
    // Draw blue dot
    ctx.arc(x, y, 8, 0, 2 * Math.PI);
    ctx.fillStyle = '#007bff';
    ctx.fill();
}
```

### Alternative: Click and Drag

For more precision, you could implement drag-and-drop:

```javascript
// Drag existing dot to new position
canvas.addEventListener('mousedown', function(e) {
    // Check if clicking on existing node dot
    // Start dragging
});

canvas.addEventListener('mousemove', function(e) {
    if (dragging) {
        // Update position in real-time
    }
});

canvas.addEventListener('mouseup', function(e) {
    // Save final position
});
```

## Drawing Route Lines

To display navigation paths as lines on the blueprint:

### Frontend Implementation

```javascript
function drawPath(pathNodes) {
    ctx.beginPath();
    
    // Start at first node
    const firstNode = pathNodes[0];
    let startX = (firstNode.map_x / 100) * canvas.width;
    let startY = (firstNode.map_y / 100) * canvas.height;
    ctx.moveTo(startX, startY);
    
    // Draw lines to each subsequent node
    for (let i = 1; i < pathNodes.length; i++) {
        const node = pathNodes[i];
        const x = (node.map_x / 100) * canvas.width;
        const y = (node.map_y / 100) * canvas.height;
        ctx.lineTo(x, y);
    }
    
    // Style the route line
    ctx.strokeStyle = '#28a745';  // Green
    ctx.lineWidth = 4;
    ctx.setLineDash([10, 5]);  // Dashed line
    ctx.stroke();
    
    // Draw start and end markers
    drawMarker(pathNodes[0], 'START', 'green');
    drawMarker(pathNodes[pathNodes.length - 1], 'END', 'red');
}
```

### Example: Pathfinding Integration

```javascript
// After getting path from API
fetch('/api/find-path/', {
    method: 'POST',
    body: JSON.stringify({
        start: 'BLDG-101-R01',
        goal: 'BLDG-101-R15'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // data.path contains nodes with map_x and map_y
        drawBlueprintWithPath(data.path);
    }
});

function drawBlueprintWithPath(pathNodes) {
    // 1. Draw the blueprint image
    ctx.drawImage(blueprintImage, 0, 0);
    
    // 2. Draw all nodes as dots
    allNodes.forEach(node => drawNodeDot(node));
    
    // 3. Draw the path as a line
    drawPath(pathNodes);
    
    // 4. Highlight path nodes
    pathNodes.forEach(node => highlightNode(node));
}
```

## API Endpoints

### Get Map and Nodes for Floor

**Endpoint**: `GET /rec/api/campus-map/{building}/{floor}/`

**Example**: `GET /rec/api/campus-map/Engineering%20Building/1/`

**Response**:
```json
{
    "map": {
        "map_id": 1,
        "name": "Engineering Building - Floor 1",
        "blueprint_url": "/media/campus_maps/engineering_floor1.png",
        "scale": 0.05,
        "north_rotation": 0.0
    },
    "nodes": [
        {
            "node_id": 1,
            "node_code": "ENG-101-R01",
            "name": "Computer Lab",
            "building": "Engineering Building",
            "floor_level": 1,
            "map_x": 45.5,
            "map_y": 32.8
        }
    ]
}
```

### Upload Blueprint

**Endpoint**: `POST /rec/api/upload-campus-map/`

**Form Data**:
- `building`: Building name
- `floor_level`: Floor number
- `name`: Map name
- `blueprint_image`: Image file
- `scale_meters_per_pixel`: (optional) Scale value

### Save Node Positions

**Endpoint**: `POST /rec/api/save-node-positions/`

**Request**:
```json
{
    "nodes": [
        {
            "node_id": 1,
            "map_x": 45.5,
            "map_y": 32.8
        },
        {
            "node_id": 2,
            "map_x": 60.2,
            "map_y": 25.1
        }
    ]
}
```

**Response**:
```json
{
    "success": true,
    "updated": 2
}
```

## Best Practices

### Blueprint Image Preparation

1. **Resolution**: Use high-resolution images (at least 1920x1080)
2. **Format**: PNG for floor plans (better for lines/text), JPG for photos
3. **Orientation**: Align north to the top of the image for consistency
4. **Labels**: Include room numbers/labels in the blueprint itself
5. **Clean**: Remove unnecessary details that don't help navigation

### Node Positioning Tips

1. **Accuracy**: Click precisely on the center of each room/location
2. **Consistency**: Position hallway nodes in the center of corridors
3. **Check**: Verify positions visually before saving
4. **Update**: Recalibrate if blueprint image changes
5. **Test**: Draw sample paths to verify positioning accuracy

### Multiple Buildings/Floors

- Upload separate blueprints for each floor
- Use consistent naming: "{Building} - Floor {Number}"
- Ensure building names match exactly with node data
- Consider creating basement levels (negative floor numbers)

## Advanced Features

### Distance Calculation

If you set `scale_meters_per_pixel`, you can calculate real-world distances:

```javascript
function calculateDistance(node1, node2, canvasWidth, canvasHeight, scale) {
    // Convert percentages to pixels
    const x1 = (node1.map_x / 100) * canvasWidth;
    const y1 = (node1.map_y / 100) * canvasHeight;
    const x2 = (node2.map_x / 100) * canvasWidth;
    const y2 = (node2.map_y / 100) * canvasHeight;
    
    // Calculate pixel distance
    const pixelDistance = Math.sqrt(
        Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2)
    );
    
    // Convert to meters
    const meters = pixelDistance * scale;
    return meters;
}
```

### Compass Direction Overlay

Rotate the blueprint to align with compass:

```javascript
function rotateCanvas(degrees) {
    ctx.save();
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate(degrees * Math.PI / 180);
    ctx.drawImage(blueprint, -canvas.width / 2, -canvas.height / 2);
    ctx.restore();
}
```

### Animated Path

Animate route visualization:

```javascript
function animatePath(pathNodes, duration) {
    let progress = 0;
    const interval = setInterval(() => {
        progress += 0.01;
        drawPartialPath(pathNodes, progress);
        
        if (progress >= 1) clearInterval(interval);
    }, duration / 100);
}
```

## Troubleshooting

**Nodes not appearing:**
- Check that map_x and map_y are not null
- Verify building and floor_level match exactly
- Ensure blueprint image loaded successfully

**Coordinates seem wrong:**
- Clear browser cache and reload
- Verify percentage values are 0-100
- Check canvas dimensions match image dimensions

**Blueprint not uploading:**
- Check file size (recommend < 5MB)
- Verify image format (JPG, PNG, GIF)
- Ensure media directory has write permissions

## Future Enhancements

- **Multi-floor 3D view**: Stack blueprints with staircase connections
- **Real-time updates**: WebSocket for live position updates
- **Mobile app**: Scan QR code → show current position on blueprint
- **AR overlay**: Augmented reality with blueprint overlay
- **Batch import**: Upload coordinates from CSV/JSON file
