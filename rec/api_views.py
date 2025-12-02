"""
REST API Views for Mobile App
Provides endpoints for the React Native mobile application
"""
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.files.base import ContentFile
import json
import base64

from .models import Nodes, Edges, Annotation, CampusMap
from .pathfinding import get_pathfinder, reset_pathfinder


# ============= Public API Endpoints =============

@require_http_methods(["GET"])
def api_nodes_list(request):
    """Get list of all nodes with optional search/filter."""
    try:
        nodes = Nodes.objects.all()
        
        # Search parameter
        search = request.GET.get('search', '').strip()
        if search:
            nodes = nodes.filter(
                Q(node_code__icontains=search) |
                Q(name__icontains=search) |
                Q(building__icontains=search)
            )
        
        # Filter by building
        building = request.GET.get('building', '').strip()
        if building:
            nodes = nodes.filter(building=building)
        
        # Filter by floor
        floor = request.GET.get('floor', '').strip()
        if floor:
            nodes = nodes.filter(floor_level=int(floor))
        
        data = [{
            'node_id': n.node_id,
            'node_code': n.node_code,
            'name': n.name,
            'building': n.building,
            'floor_level': n.floor_level,
            'type_of_node': n.type_of_node,
            'map_x': float(n.map_x) if n.map_x is not None else None,
            'map_y': float(n.map_y) if n.map_y is not None else None,
            'has_360_image': bool(n.image360),
            'image360_url': request.build_absolute_uri(n.image360.url) if n.image360 else None,
            'qrcode_url': request.build_absolute_uri(n.qrcode.url) if n.qrcode else None,
            'description': n.description
        } for n in nodes.order_by('building', 'floor_level', 'name')]
        
        return JsonResponse({
            'success': True,
            'nodes': data,
            'count': len(data)
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_buildings_list(request):
    """Get list of all buildings."""
    try:
        buildings = Nodes.objects.values_list('building', flat=True).distinct().order_by('building')
        return JsonResponse({
            'success': True,
            'buildings': list(buildings)
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_campus_map(request):
    """Get active campus map information."""
    try:
        campus_map = CampusMap.objects.filter(is_active=True).first()
        
        if not campus_map:
            return JsonResponse({
                'success': False,
                'error': 'No active campus map found'
            }, status=404)
        
        return JsonResponse({
            'success': True,
            'map': {
                'map_id': campus_map.map_id,
                'name': campus_map.name,
                'image_url': request.build_absolute_uri(campus_map.blueprint_image.url),
                'scale_meters_per_pixel': campus_map.scale_meters_per_pixel
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def api_find_path(request):
    """Find path between two nodes using A* algorithm."""
    try:
        data = json.loads(request.body)
        start_code = data.get('start_code')
        goal_code = data.get('goal_code')
        avoid_stairs = data.get('avoid_stairs', False)
        
        if not start_code or not goal_code:
            return JsonResponse({
                'success': False,
                'error': 'start_code and goal_code are required'
            }, status=400)
        
        pathfinder = get_pathfinder()
        result = pathfinder.get_directions(start_code, goal_code, avoid_stairs)
        
        if 'error' in result:
            return JsonResponse({'success': False, 'error': result['error']}, status=404)
        
        # Add absolute URLs for images
        for node in result['path']:
            if node['image360']:
                node['image360'] = request.build_absolute_uri(node['image360'])
        
        return JsonResponse({
            'success': True,
            **result
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_node_detail(request, node_id):
    """Get detailed information about a specific node."""
    try:
        node = get_object_or_404(Nodes, node_id=node_id)
        
        # Get annotations for this node
        annotations = Annotation.objects.filter(
            panorama=node,
            is_active=True
        ).select_related('target_node')
        
        annotations_data = [{
            'id': a.id,
            'label': a.label,
            'yaw': a.yaw,
            'pitch': a.pitch,
            'visible_radius': a.visible_radius,
            'target_node': {
                'node_id': a.target_node.node_id,
                'node_code': a.target_node.node_code,
                'name': a.target_node.name
            } if a.target_node else None
        } for a in annotations]
        
        return JsonResponse({
            'success': True,
            'node': {
                'node_id': node.node_id,
                'node_code': node.node_code,
                'name': node.name,
                'building': node.building,
                'floor_level': node.floor_level,
                'type_of_node': node.type_of_node,
                'map_x': float(node.map_x) if node.map_x is not None else None,
                'map_y': float(node.map_y) if node.map_y is not None else None,
                'image360_url': request.build_absolute_uri(node.image360.url) if node.image360 else None,
                'qrcode_url': request.build_absolute_uri(node.qrcode.url) if node.qrcode else None,
                'description': node.description,
                'annotations': annotations_data
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============= Admin Authentication =============

@require_http_methods(["POST"])
@csrf_exempt
def api_admin_login(request):
    """Admin login endpoint."""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password required'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful',
                'user': {
                    'username': user.username,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid credentials or not an admin user'
            }, status=401)
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ============= Admin CRUD Operations =============

@require_http_methods(["POST"])
@csrf_exempt
@login_required
def api_node_create(request):
    """Create a new node (Admin only)."""
    try:
        data = json.loads(request.body)
        
        node = Nodes(
            node_code=data['node_code'],
            name=data['name'],
            building=data['building'],
            floor_level=int(data['floor_level']),
            type_of_node=data.get('type_of_node', 'room'),
            description=data.get('description', '')
        )
        
        # Handle map coordinates
        if 'map_x' in data and 'map_y' in data:
            node.map_x = float(data['map_x'])
            node.map_y = float(data['map_y'])
        
        # Handle base64 image for 360 image
        if 'image360_base64' in data:
            image_data = base64.b64decode(data['image360_base64'])
            node.image360.save(f"{node.node_code}_360.jpg", ContentFile(image_data), save=False)
        
        node.save()  # Auto-generates QR code
        reset_pathfinder()
        
        return JsonResponse({
            'success': True,
            'message': 'Node created successfully',
            'node_id': node.node_id
        })
    
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["PUT"])
@csrf_exempt
@login_required
def api_node_update(request, node_id):
    """Update an existing node (Admin only)."""
    try:
        node = get_object_or_404(Nodes, node_id=node_id)
        data = json.loads(request.body)
        
        # Update fields
        node.node_code = data.get('node_code', node.node_code)
        node.name = data.get('name', node.name)
        node.building = data.get('building', node.building)
        node.floor_level = int(data.get('floor_level', node.floor_level))
        node.type_of_node = data.get('type_of_node', node.type_of_node)
        node.description = data.get('description', node.description)
        
        # Update coordinates
        if 'map_x' in data and 'map_y' in data:
            node.map_x = float(data['map_x'])
            node.map_y = float(data['map_y'])
        
        # Handle base64 image for 360 image
        if 'image360_base64' in data:
            image_data = base64.b64decode(data['image360_base64'])
            node.image360.save(f"{node.node_code}_360.jpg", ContentFile(image_data), save=False)
        
        node.save()
        reset_pathfinder()
        
        return JsonResponse({
            'success': True,
            'message': 'Node updated successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
@login_required
def api_node_delete(request, node_id):
    """Delete a node (Admin only)."""
    try:
        node = get_object_or_404(Nodes, node_id=node_id)
        node.delete()
        reset_pathfinder()
        
        return JsonResponse({
            'success': True,
            'message': 'Node deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_edges_list(request):
    """Get list of all edges."""
    try:
        edges = Edges.objects.all().select_related('from_node', 'to_node')
        
        data = [{
            'edge_id': e.edge_id,
            'from_node': {
                'node_id': e.from_node.node_id,
                'node_code': e.from_node.node_code,
                'name': e.from_node.name
            },
            'to_node': {
                'node_id': e.to_node.node_id,
                'node_code': e.to_node.node_code,
                'name': e.to_node.name
            },
            'distance': e.distance,
            'compass_angle': e.compass_angle,
            'is_staircase': e.is_staircase,
            'is_active': e.is_active
        } for e in edges]
        
        return JsonResponse({
            'success': True,
            'edges': data,
            'count': len(data)
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def api_edge_create(request):
    """Create a new edge (Admin only)."""
    try:
        data = json.loads(request.body)
        
        from_node = get_object_or_404(Nodes, node_id=data['from_node_id'])
        to_node = get_object_or_404(Nodes, node_id=data['to_node_id'])
        
        edge = Edges(
            from_node=from_node,
            to_node=to_node,
            distance=float(data['distance']),
            compass_angle=float(data['compass_angle']),
            is_staircase=data.get('is_staircase', False),
            is_active=data.get('is_active', True)
        )
        edge.save()
        reset_pathfinder()
        
        return JsonResponse({
            'success': True,
            'message': 'Edge created successfully',
            'edge_id': edge.edge_id
        })
    
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["PUT"])
@csrf_exempt
@login_required
def api_edge_update(request, edge_id):
    """Update an existing edge (Admin only)."""
    try:
        edge = get_object_or_404(Edges, edge_id=edge_id)
        data = json.loads(request.body)
        
        if 'from_node_id' in data:
            edge.from_node = get_object_or_404(Nodes, node_id=data['from_node_id'])
        if 'to_node_id' in data:
            edge.to_node = get_object_or_404(Nodes, node_id=data['to_node_id'])
        
        edge.distance = float(data.get('distance', edge.distance))
        edge.compass_angle = float(data.get('compass_angle', edge.compass_angle))
        edge.is_staircase = data.get('is_staircase', edge.is_staircase)
        edge.is_active = data.get('is_active', edge.is_active)
        
        edge.save()
        reset_pathfinder()
        
        return JsonResponse({
            'success': True,
            'message': 'Edge updated successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
@login_required
def api_edge_delete(request, edge_id):
    """Delete an edge (Admin only)."""
    try:
        edge = get_object_or_404(Edges, edge_id=edge_id)
        edge.delete()
        reset_pathfinder()
        
        return JsonResponse({
            'success': True,
            'message': 'Edge deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_annotations_list(request):
    """Get list of all annotations."""
    try:
        annotations = Annotation.objects.all().select_related('panorama', 'target_node')
        
        # Filter by panorama node
        panorama_id = request.GET.get('panorama_id')
        if panorama_id:
            annotations = annotations.filter(panorama__node_id=panorama_id)
        
        data = [{
            'id': a.id,
            'panorama': {
                'node_id': a.panorama.node_id,
                'node_code': a.panorama.node_code,
                'name': a.panorama.name
            },
            'target_node': {
                'node_id': a.target_node.node_id,
                'node_code': a.target_node.node_code,
                'name': a.target_node.name
            } if a.target_node else None,
            'label': a.label,
            'yaw': a.yaw,
            'pitch': a.pitch,
            'visible_radius': a.visible_radius,
            'is_active': a.is_active
        } for a in annotations]
        
        return JsonResponse({
            'success': True,
            'annotations': data,
            'count': len(data)
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["POST"])
@csrf_exempt
@login_required
def api_annotation_create(request):
    """Create a new annotation (Admin only)."""
    try:
        data = json.loads(request.body)
        
        panorama = get_object_or_404(Nodes, node_id=data['panorama_id'])
        target_node = None
        if 'target_node_id' in data and data['target_node_id']:
            target_node = get_object_or_404(Nodes, node_id=data['target_node_id'])
        
        annotation = Annotation(
            panorama=panorama,
            target_node=target_node,
            label=data['label'],
            yaw=float(data['yaw']),
            pitch=float(data['pitch']),
            visible_radius=float(data.get('visible_radius', 10.0)),
            is_active=data.get('is_active', True)
        )
        annotation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Annotation created successfully',
            'annotation_id': annotation.id
        })
    
    except KeyError as e:
        return JsonResponse({'success': False, 'error': f'Missing field: {str(e)}'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["PUT"])
@csrf_exempt
@login_required
def api_annotation_update(request, annotation_id):
    """Update an existing annotation (Admin only)."""
    try:
        annotation = get_object_or_404(Annotation, id=annotation_id)
        data = json.loads(request.body)
        
        if 'panorama_id' in data:
            annotation.panorama = get_object_or_404(Nodes, node_id=data['panorama_id'])
        if 'target_node_id' in data:
            if data['target_node_id']:
                annotation.target_node = get_object_or_404(Nodes, node_id=data['target_node_id'])
            else:
                annotation.target_node = None
        
        annotation.label = data.get('label', annotation.label)
        annotation.yaw = float(data.get('yaw', annotation.yaw))
        annotation.pitch = float(data.get('pitch', annotation.pitch))
        annotation.visible_radius = float(data.get('visible_radius', annotation.visible_radius))
        annotation.is_active = data.get('is_active', annotation.is_active)
        
        annotation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Annotation updated successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["DELETE"])
@csrf_exempt
@login_required
def api_annotation_delete(request, annotation_id):
    """Delete an annotation (Admin only)."""
    try:
        annotation = get_object_or_404(Annotation, id=annotation_id)
        annotation.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Annotation deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
