# Quick Start Guide - Campus Navigator

## ✅ Current Status
Your application is **RUNNING** at: http://127.0.0.1:8000/

## 🎯 Next Steps

### 1. Create Admin Account
```powershell
py manage.py createsuperuser
```
Follow the prompts to create username, email, and password.

### 2. Access the Application

**Main Dashboard**
- URL: http://127.0.0.1:8000/
- Features: Overview, quick stats, navigation menu

**Django Admin Panel**
- URL: http://127.0.0.1:8000/admin/
- Login with superuser credentials
- Best for bulk data entry

**Pathfinding Test**
- URL: http://127.0.0.1:8000/pathfinding/
- Test A* algorithm with visual graph

### 3. Add Sample Data

#### Using Django Admin (Recommended for First Time)

1. Go to http://127.0.0.1:8000/admin/
2. Add some **Nodes** first:
   - Click "Nodes" → "Add Node"
   - Fill in required fields (code, name, building, floor)
   - Save

3. Add **Edges** to connect nodes:
   - Click "Edges" → "Add Edge"
   - Select from_node and to_node
   - Enter distance and compass angle
   - Save

4. Add **Annotations** (optional):
   - Click "Annotations" → "Add Annotation"
   - Select panorama node (must have image360 URL)
   - Enter label, yaw, pitch
   - Save

#### Using Web Interface

1. Go to http://127.0.0.1:8000/
2. Click "Add Node" button
3. Fill the form and submit
4. Repeat for edges and annotations

### 4. Test Pathfinding

1. Go to http://127.0.0.1:8000/pathfinding/
2. You need at least 2 connected nodes
3. Select start and goal from dropdowns
4. Click "Find Path"
5. View results with turn-by-turn directions

## 📊 Sample Data Example

### Example Node 1
```
Code: MAIN-1-ENTRANCE
Name: Main Entrance
Building: Main Building
Floor: 1
Type: entrance
```

### Example Node 2
```
Code: MAIN-1-LOBBY
Name: Main Lobby
Building: Main Building
Floor: 1
Type: hallway
```

### Example Edge
```
From: MAIN-1-ENTRANCE
To: MAIN-1-LOBBY
Distance: 10.0
Compass Angle: 90
Is Staircase: No
Is Active: Yes
```

## 🔍 Available Pages

| Page | URL | Description |
|------|-----|-------------|
| Dashboard | / | Main overview |
| Nodes List | /nodes/ | View all nodes with filters |
| Add Node | /nodes/create/ | Create new node |
| Edges List | /edges/ | View all edges |
| Add Edge | /edges/create/ | Create new edge |
| Annotations | /annotations/ | View all annotations |
| Pathfinding Test | /pathfinding/ | Test A* algorithm |
| Admin Panel | /admin/ | Django admin interface |

## 🎨 Features to Try

1. **Search & Filter**
   - Go to /nodes/ and use search box
   - Filter by building or floor

2. **CRUD Operations**
   - Edit any node/edge/annotation
   - Delete with confirmation

3. **Pathfinding**
   - Test with different start/goal combinations
   - Enable "Avoid stairs" mode
   - View graph visualization

4. **360° Annotations**
   - Add panorama URL to a node
   - Create annotations with yaw/pitch coordinates
   - Test with 360° viewer

## 🛠️ Troubleshooting

### Can't access the site?
Check if server is running:
```powershell
# If not running, start it:
py manage.py runserver
```

### No data showing up?
- Make sure you added nodes and edges
- Check filters aren't hiding data
- Verify database has records in admin panel

### Pathfinding not working?
- Need at least 2 nodes connected by edges
- Edges must be marked as "active"
- Check that path exists between selected nodes

## 📝 Common Commands

```powershell
# Start server
py manage.py runserver

# Stop server
# Press Ctrl+C in terminal

# Create superuser
py manage.py createsuperuser

# Apply migrations
py manage.py migrate

# Check for issues
py manage.py check

# Open Django shell (for testing)
py manage.py shell
```

## 🎓 Learning Path

1. **Day 1**: Add 3-5 nodes and connect them with edges
2. **Day 2**: Test pathfinding between nodes
3. **Day 3**: Add 360° image URLs and create annotations
4. **Day 4**: Customize CSS and add more node types
5. **Day 5**: Build a complete floor map of a building

## 💡 Pro Tips

- Use consistent naming for node codes (e.g., BUILDING-FLOOR-ROOM)
- Compass angles: 0°=North, 90°=East, 180°=South, 270°=West
- Set distance in meters for accuracy
- Mark stairs with is_staircase=True for accessibility features
- Use QR codes at physical locations pointing to node URLs

---

**Need Help?** Check README.md for full documentation.

**Ready to Start?** Open http://127.0.0.1:8000/ and explore!
