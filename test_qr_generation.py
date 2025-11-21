"""
Test script to demonstrate QR code generation for nodes.

This script creates a sample node and shows how the QR code is automatically generated.
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'record.settings')
django.setup()

from rec.models import Nodes

def test_qr_generation():
    """Test automatic QR code generation."""
    print("=" * 60)
    print("QR Code Generation Test")
    print("=" * 60)
    
    # Create a test node
    test_node = Nodes(
        node_code="TEST-001",
        name="Test Room",
        building="Test Building",
        floor_level=1,
        type_of_node="room",
        description="Test node for QR code generation"
    )
    
    print(f"\n✓ Creating node: {test_node.node_code}")
    print(f"  Name: {test_node.name}")
    print(f"  Building: {test_node.building}")
    
    # Save the node (QR code will be auto-generated)
    test_node.save()
    
    print(f"\n✓ Node saved successfully!")
    print(f"  Node ID: {test_node.node_id}")
    
    # Check if QR code was generated
    if test_node.qrcode:
        print(f"\n✓ QR Code generated automatically!")
        print(f"  Path: {test_node.qrcode.path}")
        print(f"  URL: {test_node.qrcode.url}")
        print(f"  File exists: {os.path.exists(test_node.qrcode.path)}")
        
        # QR code data
        qr_data = f'{{"node_code": "{test_node.node_code}", "name": "{test_node.name}", "building": "{test_node.building}"}}'
        print(f"\n📱 QR Code contains:")
        print(f"  {qr_data}")
    else:
        print("\n✗ QR code was not generated")
    
    print("\n" + "=" * 60)
    print("Test completed! You can now:")
    print("1. View the node at: http://127.0.0.1:8000/nodes/")
    print(f"2. Download QR code at: http://127.0.0.1:8000{test_node.qrcode.url}")
    print("3. Edit the node to upload a 360° image")
    print("=" * 60)
    
    return test_node

if __name__ == "__main__":
    try:
        node = test_qr_generation()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
