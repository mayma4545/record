"""
Sample Data Loader for Campus Navigation System

Run this script to populate the database with sample nodes, edges, and annotations.

Usage:
    python load_sample_data.py
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'record.settings')
django.setup()

from rec.models import Nodes, Edges, Annotation
from rec.pathfinding import reset_pathfinder


def clear_existing_data():
    """Clear existing data (optional)."""
    print("Clearing existing data...")
    Annotation.objects.all().delete()
    Edges.objects.all().delete()
    Nodes.objects.all().delete()
    print("✓ Data cleared")


def create_sample_nodes():
    """Create sample nodes for a multi-floor building."""
    print("\nCreating sample nodes...")
    
    nodes_data = [
        # Ground Floor
        {
            'node_code': 'MAIN-G-ENTRANCE',
            'name': 'Main Entrance',
            'building': 'Main Building',
            'floor_level': 0,
            'type_of_node': 'entrance',
            'description': 'Main entrance with automatic doors',
        },
        {
            'node_code': 'MAIN-G-LOBBY',
            'name': 'Main Lobby',
            'building': 'Main Building',
            'floor_level': 0,
            'type_of_node': 'hallway',
            'description': 'Central lobby with information desk',
        },
        {
            'node_code': 'MAIN-G-CAFETERIA',
            'name': 'Cafeteria',
            'building': 'Main Building',
            'floor_level': 0,
            'type_of_node': 'room',
            'description': 'Student cafeteria and dining area',
        },
        {
            'node_code': 'MAIN-G-STAIRS1',
            'name': 'Stairwell A',
            'building': 'Main Building',
            'floor_level': 0,
            'type_of_node': 'staircase',
            'description': 'Main stairwell to upper floors',
        },
        
        # First Floor
        {
            'node_code': 'MAIN-1-STAIRS1',
            'name': 'Stairwell A - Floor 1',
            'building': 'Main Building',
            'floor_level': 1,
            'type_of_node': 'staircase',
            'description': 'Stairwell landing on floor 1',
        },
        {
            'node_code': 'MAIN-1-CORRIDOR',
            'name': 'First Floor Corridor',
            'building': 'Main Building',
            'floor_level': 1,
            'type_of_node': 'hallway',
            'description': 'Main corridor with classrooms',
        },
        {
            'node_code': 'MAIN-1-LAB101',
            'name': 'Computer Lab 101',
            'building': 'Main Building',
            'floor_level': 1,
            'type_of_node': 'room',
            'image360': 'https://example.com/panorama-lab101.jpg',
            'description': 'Computer lab with 30 workstations',
        },
        {
            'node_code': 'MAIN-1-ROOM102',
            'name': 'Classroom 102',
            'building': 'Main Building',
            'floor_level': 1,
            'type_of_node': 'room',
            'description': 'Lecture room with 50 seats',
        },
        {
            'node_code': 'MAIN-1-LIBRARY',
            'name': 'Library Entrance',
            'building': 'Main Building',
            'floor_level': 1,
            'type_of_node': 'room',
            'description': 'Main library entrance',
        },
        
        # Second Floor
        {
            'node_code': 'MAIN-2-STAIRS1',
            'name': 'Stairwell A - Floor 2',
            'building': 'Main Building',
            'floor_level': 2,
            'type_of_node': 'staircase',
            'description': 'Stairwell landing on floor 2',
        },
        {
            'node_code': 'MAIN-2-CORRIDOR',
            'name': 'Second Floor Corridor',
            'building': 'Main Building',
            'floor_level': 2,
            'type_of_node': 'hallway',
            'description': 'Faculty offices corridor',
        },
        {
            'node_code': 'MAIN-2-OFFICE201',
            'name': 'Faculty Office 201',
            'building': 'Main Building',
            'floor_level': 2,
            'type_of_node': 'room',
            'description': 'Computer Science Department',
        },
    ]
    
    created_nodes = {}
    for node_data in nodes_data:
        node = Nodes.objects.create(**node_data)
        created_nodes[node.node_code] = node
        print(f"  ✓ Created: {node.node_code} - {node.name}")
    
    return created_nodes


def create_sample_edges(nodes):
    """Create sample edges connecting the nodes."""
    print("\nCreating sample edges...")
    
    edges_data = [
        # Ground Floor connections
        ('MAIN-G-ENTRANCE', 'MAIN-G-LOBBY', 8.0, 0),     # North
        ('MAIN-G-LOBBY', 'MAIN-G-CAFETERIA', 15.0, 90),  # East
        ('MAIN-G-LOBBY', 'MAIN-G-STAIRS1', 12.0, 270),   # West
        
        # Stairs (vertical connections)
        ('MAIN-G-STAIRS1', 'MAIN-1-STAIRS1', 4.5, 0, True),  # Up stairs
        ('MAIN-1-STAIRS1', 'MAIN-2-STAIRS1', 4.5, 0, True),  # Up stairs
        
        # First Floor connections
        ('MAIN-1-STAIRS1', 'MAIN-1-CORRIDOR', 5.0, 90),      # East
        ('MAIN-1-CORRIDOR', 'MAIN-1-LAB101', 10.0, 180),     # South
        ('MAIN-1-CORRIDOR', 'MAIN-1-ROOM102', 8.0, 0),       # North
        ('MAIN-1-CORRIDOR', 'MAIN-1-LIBRARY', 20.0, 90),     # East
        
        # Second Floor connections
        ('MAIN-2-STAIRS1', 'MAIN-2-CORRIDOR', 5.0, 90),      # East
        ('MAIN-2-CORRIDOR', 'MAIN-2-OFFICE201', 12.0, 180),  # South
    ]
    
    for edge_data in edges_data:
        from_code, to_code, distance, compass_angle = edge_data[:4]
        is_staircase = edge_data[4] if len(edge_data) > 4 else False
        
        edge = Edges.objects.create(
            from_node=nodes[from_code],
            to_node=nodes[to_code],
            distance=distance,
            compass_angle=compass_angle,
            is_staircase=is_staircase,
            is_active=True
        )
        
        stair_marker = "🚶 STAIRS" if is_staircase else ""
        print(f"  ✓ {from_code} → {to_code} ({distance}m, {compass_angle}°) {stair_marker}")


def create_sample_annotations(nodes):
    """Create sample annotations for 360° panoramas."""
    print("\nCreating sample annotations...")
    
    # Only create annotation if node has image360
    lab_node = nodes.get('MAIN-1-LAB101')
    if lab_node and lab_node.image360:
        annotations_data = [
            {
                'panorama': lab_node,
                'target_node': nodes.get('MAIN-1-CORRIDOR'),
                'label': 'Exit to Corridor',
                'yaw': 180.0,
                'pitch': 0.0,
                'visible_radius': 15.0,
            },
            {
                'panorama': lab_node,
                'target_node': None,
                'label': 'Workstation Area',
                'yaw': 45.0,
                'pitch': -10.0,
                'visible_radius': 20.0,
            },
            {
                'panorama': lab_node,
                'target_node': None,
                'label': 'Instructor Desk',
                'yaw': -90.0,
                'pitch': 0.0,
                'visible_radius': 12.0,
            },
        ]
        
        for ann_data in annotations_data:
            annotation = Annotation.objects.create(**ann_data)
            print(f"  ✓ Annotation: {annotation.label} @ {annotation.yaw}°, {annotation.pitch}°")
    else:
        print("  ℹ No panorama images defined, skipping annotations")


def print_summary():
    """Print summary of loaded data."""
    print("\n" + "="*60)
    print("📊 DATA LOADING COMPLETE!")
    print("="*60)
    print(f"Total Nodes: {Nodes.objects.count()}")
    print(f"Total Edges: {Edges.objects.count()}")
    print(f"Total Annotations: {Annotation.objects.count()}")
    print(f"Buildings: {', '.join(Nodes.objects.values_list('building', flat=True).distinct())}")
    print(f"Floors: {', '.join(map(str, sorted(Nodes.objects.values_list('floor_level', flat=True).distinct())))}")
    print("\n✅ Sample data loaded successfully!")
    print("\n🧪 Try pathfinding test:")
    print("   From: MAIN-G-ENTRANCE")
    print("   To: MAIN-2-OFFICE201")
    print("\n🌐 Access the app at: http://127.0.0.1:8000/")
    print("="*60)


def main():
    """Main function to load all sample data."""
    print("="*60)
    print("🗺️  CAMPUS NAVIGATION - SAMPLE DATA LOADER")
    print("="*60)
    
    # Ask user if they want to clear existing data
    clear = input("\nClear existing data? (y/N): ").strip().lower()
    if clear == 'y':
        clear_existing_data()
    
    # Create sample data
    nodes = create_sample_nodes()
    create_sample_edges(nodes)
    create_sample_annotations(nodes)
    
    # Reset pathfinder to rebuild graph
    print("\nRebuilding pathfinding graph...")
    reset_pathfinder()
    print("✓ Pathfinding graph rebuilt")
    
    # Print summary
    print_summary()


if __name__ == '__main__':
    main()
