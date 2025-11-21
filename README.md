# Campus Navigation System 🗺️

A full-stack Django web application for campus navigation using **A* pathfinding algorithm** with compass directions and 360° panorama support.

## 🌟 Features

### Core Functionality
- ✅ **A* Pathfinding Algorithm** - Efficient shortest path computation with compass angle awareness
- ✅ **Bidirectional Graph** - Automatic reverse edge creation with proper compass calculations
- ✅ **Staircase Detection** - Special handling for vertical movement between floors
- ✅ **Accessibility Mode** - Option to avoid stairs in pathfinding
- ✅ **360° Panorama Upload** - Upload and store real equirectangular panoramic images
- ✅ **Automatic QR Code Generation** - QR codes auto-generated for every node on save
- ✅ **Smart Annotations** - Add labels with spherical coordinates (yaw/pitch) on 360° images
- ✅ **Full CRUD Operations** - Complete create, read, update, delete for all entities
- ✅ **Searchable Node Selection** - Modal popups with search for easy node selection
- ✅ **File Upload System** - Secure image storage for 360° panoramas and QR codes

### User Interface
- 📊 **Interactive Dashboard** - Overview of nodes, edges, and annotations
- 🧪 **Pathfinding Test Page** - Visual path testing with graph visualization
- 🎨 **Modern UI** - Responsive design with gradient navigation and clean layout
- 📱 **Mobile Responsive** - Works on all device sizes
- 🔍 **Advanced Filtering** - Search and filter nodes, edges, and annotations
- 🖼️ **Image Previews** - Thumbnail previews of 360° images and QR codes in lists

## 🏗️ Architecture

### Database Models

#### 1. **Nodes** (Locations)
```python
- node_id (Primary Key)
- node_code (Unique identifier, e.g., "BLDG-101-R01")
- name (Display name)
- building (Building name)
- floor_level (Integer, supports basement with negative numbers)
- type_of_node (room, hallway, entrance, staircase, elevator, landmark)
- image360 (ImageField, uploaded 360° panorama)
- qrcode (ImageField, auto-generated QR code)
- description (Additional info)
```

**Special Features:**
- **Auto QR Generation**: QR codes are automatically created on save containing node data
- **File Upload**: Supports direct 360° image upload instead of URLs
- **Media Storage**: Files stored in `media/360_images/` and `media/qrcodes/`

#### 2. **Edges** (Connections)
```python
- edge_id (Primary Key)
- from_node (Foreign Key to Nodes)
- to_node (Foreign Key to Nodes)
- distance (Float, meters)
- compass_angle (Float, 0-360°, North=0°, East=90°)
- is_staircase (Boolean, affects pathfinding)
- is_active (Boolean, for temporarily disabling paths)
```

#### 3. **Annotation** (360° Labels)
```python
- id (Primary Key)
- panorama (Foreign Key to Nodes with 360° image)
- target_node (Optional Foreign Key to target room/building)
- label (Text to display)
- yaw (Float, -180 to 180°, horizontal angle)
- pitch (Float, -90 to 90°, vertical angle)
- visible_radius (Float, angular radius for visibility)
- is_active (Boolean)
```

### Pathfinding Algorithm

The A* implementation (`rec/pathfinding.py`) includes:

- **Heuristic**: Floor difference-based estimation (4 meters per floor)
- **Cost Function**: Actual edge distance
- **Bidirectional Edges**: Automatic creation with reverse compass angles
- **Staircase Avoidance**: Optional filtering for accessibility
- **Direction Output**: Human-readable compass directions (N, NE, E, etc.)

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Django 5.2+

### Installation & Setup

1. **Navigate to project directory**
```powershell
cd C:\Users\Admin\Desktop\recorder\record
```

2. **Install dependencies** (if needed)
```powershell
pip install django
```

3. **Run migrations** (already done)
```powershell
py manage.py makemigrations
py manage.py migrate
```

4. **Create superuser** (for admin access)
```powershell
py manage.py createsuperuser
```

5. **Start development server**
```powershell
py manage.py runserver
```

6. **Access the application**
- Main App: http://127.0.0.1:8000/
- Django Admin: http://127.0.0.1:8000/admin/

## 📖 Usage Guide

### Adding Data

#### Option 1: Django Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Add Nodes, Edges, and Annotations through the admin interface

#### Option 2: Web Interface
1. Go to http://127.0.0.1:8000/
2. Click "Add Node", "Add Edge", or "Add Annotation" buttons
3. Fill in the forms and submit

### Creating a Campus Map

**Step 1: Add Nodes**
```
Example:
- Code: MAIN-G-ENTRANCE
- Name: Main Entrance
- Building: Main Building
- Floor: 0
- Type: entrance
```

**Step 2: Add Edges**
```
Example:
- From: MAIN-G-ENTRANCE
- To: MAIN-G-LOBBY
- Distance: 5.0 meters
- Compass Angle: 90° (East)
- Is Staircase: No
```

**Step 3: Add 360° Annotations** (Optional)
```
Example:
- Panorama: MAIN-G-LOBBY (node with image360 URL)
- Label: "Exit to Parking"
- Yaw: 180°
- Pitch: 0°
- Visible Radius: 15°
```

### Testing Pathfinding

1. Go to http://127.0.0.1:8000/pathfinding/
2. Select **Start Node** from dropdown
3. Select **Goal Node** from dropdown
4. Optional: Check "Avoid stairs" for accessibility mode
5. Click **Find Path**
6. View results:
   - Path summary (distance, number of nodes)
   - Turn-by-turn directions with compass bearings
   - Detailed node-by-node path
   - Visual graph representation

## 🛠️ API Endpoints

### Pathfinding API
```http
POST /api/find-path/
Content-Type: application/json

{
  "start": "NODE-CODE-1",
  "goal": "NODE-CODE-2",
  "avoid_stairs": false
}
```

**Response:**
```json
{
  "success": true,
  "total_distance": 45.5,
  "num_nodes": 5,
  "path": [...],
  "directions": [...]
}
```

### Annotations API
```http
GET /api/annotations/{node_id}/
```

**Response:**
```json
{
  "annotations": [
    {
      "id": 1,
      "label": "Computer Lab 1",
      "yaw": 45.0,
      "pitch": 0.0,
      "visible_radius": 10.0,
      "target_node": {...}
    }
  ]
}
```

### Graph Data API
```http
GET /api/graph-data/
```

**Response:**
```json
{
  "nodes": [...],
  "edges": [...]
}
```

## 📂 Project Structure

```
record/
├── rec/                          # Main app
│   ├── models.py                 # Database models (Nodes, Edges, Annotation)
│   ├── views.py                  # Views for CRUD and pathfinding
│   ├── urls.py                   # URL routing
│   ├── admin.py                  # Admin panel configuration
│   ├── pathfinding.py            # A* algorithm implementation
│   ├── templates/rec/            # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── nodes_list.html
│   │   ├── node_form.html
│   │   ├── edges_list.html
│   │   ├── annotations_list.html
│   │   └── pathfinding_test.html
│   └── static/rec/               # Static files
│       ├── css/style.css
│       └── js/main.js
├── record/                       # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── db.sqlite3                    # SQLite database
└── manage.py                     # Django management script
```

## 🎯 Use Cases

1. **Campus Navigation** - Help students and visitors find their way
2. **Indoor Wayfinding** - Navigate complex buildings
3. **Accessibility Planning** - Find wheelchair-accessible routes
4. **Virtual Tours** - Combine with 360° images for immersive experience
5. **Emergency Routing** - Quick path calculation for emergency services

## 🔧 Customization

### Adding New Node Types
Edit `rec/templates/rec/node_form.html` and add options to the `type_of_node` select field.

### Changing Heuristic
Modify the `heuristic()` method in `rec/pathfinding.py` to use different distance estimation.

### Styling
Edit `rec/static/rec/css/style.css` to customize colors and layout.

## 🐛 Troubleshooting

### Server won't start
```powershell
# Check if migrations are applied
py manage.py migrate

# Check for errors
py manage.py check
```

### Static files not loading
```powershell
# Collect static files
py manage.py collectstatic
```

### Pathfinding returns "No path found"
- Ensure edges exist between nodes
- Check that edges are marked as `is_active=True`
- Verify nodes are on connected graph

## 📝 Development Notes

### Database Reset
```powershell
# Delete database
Remove-Item db.sqlite3

# Recreate migrations
py manage.py makemigrations
py manage.py migrate

# Create new superuser
py manage.py createsuperuser
```

### Performance Optimization
- The pathfinder uses a singleton pattern with cached graph
- Call `reset_pathfinder()` after database changes
- For large graphs (>1000 nodes), consider adding indexes

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Technical Details

- **Framework**: Django 5.2
- **Database**: SQLite3 (development)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Algorithm**: A* with Manhattan distance heuristic
- **UI Framework**: Custom CSS with CSS Grid and Flexbox

## 🎓 Educational Value

This project demonstrates:
- Graph algorithms (A* pathfinding)
- Django ORM and model relationships
- RESTful API design
- Responsive web design
- Database normalization
- Spatial data handling (spherical coordinates)

---

**Status**: ✅ Fully functional and tested

**Server**: Running at http://127.0.0.1:8000/

**Last Updated**: November 21, 2025
