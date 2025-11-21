from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.db.models import Q
import json

from .models import Nodes, Edges, Annotation, CampusMap
from .pathfinding import get_pathfinder, reset_pathfinder


# ============= Main Dashboard =============
def index(request):
    """Main dashboard showing overview."""
    context = {
        'total_nodes': Nodes.objects.count(),
        'total_edges': Edges.objects.count(),
        'total_annotations': Annotation.objects.count(),
        'buildings': Nodes.objects.values_list('building', flat=True).distinct(),
    }
    return render(request, 'rec/index.html', context)


# ============= Nodes CRUD =============
def nodes_list(request):
    """List all nodes with search and filter."""
    nodes = Nodes.objects.all().order_by('building', 'floor_level', 'node_code')
    
    # Search
    search = request.GET.get('search', '')
    if search:
        nodes = nodes.filter(
            Q(node_code__icontains=search) |
            Q(name__icontains=search) |
            Q(building__icontains=search)
        )
    
    # Filter by building
    building_filter = request.GET.get('building', '')
    if building_filter:
        nodes = nodes.filter(building=building_filter)
    
    # Filter by floor
    floor_filter = request.GET.get('floor', '')
    if floor_filter:
        nodes = nodes.filter(floor_level=floor_filter)
    
    context = {
        'nodes': nodes,
        'search': search,
        'building_filter': building_filter,
        'floor_filter': floor_filter,
        'buildings': Nodes.objects.values_list('building', flat=True).distinct(),
        'floors': Nodes.objects.values_list('floor_level', flat=True).distinct().order_by('floor_level'),
    }
    return render(request, 'rec/nodes_list.html', context)


def node_create(request):
    """Create new node."""
    if request.method == 'POST':
        try:
            node = Nodes(
                node_code=request.POST['node_code'],
                name=request.POST['name'],
                building=request.POST['building'],
                floor_level=int(request.POST['floor_level']),
                type_of_node=request.POST.get('type_of_node', 'room'),
                description=request.POST.get('description', '')
            )
            
            # Handle 360 image upload
            if 'image360' in request.FILES:
                node.image360 = request.FILES['image360']
            
            # Handle map coordinates
            map_x = request.POST.get('map_x', '').strip()
            map_y = request.POST.get('map_y', '').strip()
            if map_x and map_y:
                node.map_x = float(map_x)
                node.map_y = float(map_y)
            
            node.save()  # QR code auto-generated on save
            messages.success(request, f'Node "{node.name}" created successfully with QR code!')
            reset_pathfinder()  # Rebuild graph
            return redirect('nodes_list')
        except Exception as e:
            messages.error(request, f'Error creating node: {str(e)}')
    
    # Get active campus map
    campus_map = CampusMap.objects.filter(is_active=True).first()
    
    return render(request, 'rec/node_form.html', {
        'mode': 'create',
        'campus_map': campus_map
    })


def node_edit(request, node_id):
    """Edit existing node."""
    node = get_object_or_404(Nodes, node_id=node_id)
    
    if request.method == 'POST':
        try:
            node.node_code = request.POST['node_code']
            node.name = request.POST['name']
            node.building = request.POST['building']
            node.floor_level = int(request.POST['floor_level'])
            node.type_of_node = request.POST.get('type_of_node', 'room')
            node.description = request.POST.get('description', '')
            
            # Handle 360 image upload
            if 'image360' in request.FILES:
                node.image360 = request.FILES['image360']
            
            # Handle map coordinates
            map_x = request.POST.get('map_x', '').strip()
            map_y = request.POST.get('map_y', '').strip()
            if map_x and map_y:
                node.map_x = float(map_x)
                node.map_y = float(map_y)
            elif map_x == '' and map_y == '':
                # Clear position if both are empty
                node.map_x = None
                node.map_y = None
            
            # Regenerate QR code if node_code changed
            if 'regenerate_qr' in request.POST or node.node_code != request.POST.get('old_node_code', ''):
                node.qrcode.delete(save=False)  # Delete old QR
                node.qrcode = None
            
            node.save()  # Auto-generates QR if needed
            messages.success(request, f'Node "{node.name}" updated successfully!')
            reset_pathfinder()
            return redirect('nodes_list')
        except Exception as e:
            messages.error(request, f'Error updating node: {str(e)}')
    
    # Get active campus map
    campus_map = CampusMap.objects.filter(is_active=True).first()
    
    context = {
        'mode': 'edit',
        'node': node,
        'campus_map': campus_map
    }
    return render(request, 'rec/node_form.html', context)
    
    if request.method == 'POST':
        try:
            node.node_code = request.POST['node_code']
            node.name = request.POST['name']
            node.building = request.POST['building']
            node.floor_level = int(request.POST['floor_level'])
            node.type_of_node = request.POST.get('type_of_node', 'room')
            node.image360 = request.POST.get('image360', '')
            node.qrcode_url = request.POST.get('qrcode_url', '')
            node.description = request.POST.get('description', '')
            node.save()
            
            messages.success(request, f'Node "{node.name}" updated successfully!')
            reset_pathfinder()
            return redirect('nodes_list')
        except Exception as e:
            messages.error(request, f'Error updating node: {str(e)}')
    
    return render(request, 'rec/node_form.html', {'mode': 'edit', 'node': node})


def node_delete(request, node_id):
    """Delete node."""
    node = get_object_or_404(Nodes, node_id=node_id)
    
    if request.method == 'POST':
        node_name = node.name
        node.delete()
        messages.success(request, f'Node "{node_name}" deleted successfully!')
        reset_pathfinder()
        return redirect('nodes_list')
    
    return render(request, 'rec/node_confirm_delete.html', {'node': node})


# ============= Edges CRUD =============
def edges_list(request):
    """List all edges."""
    edges = Edges.objects.all().select_related('from_node', 'to_node').order_by('-created_at')
    
    # Filter by active/inactive
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        edges = edges.filter(is_active=True)
    elif status_filter == 'inactive':
        edges = edges.filter(is_active=False)
    
    # Filter by staircase
    stair_filter = request.GET.get('staircase', '')
    if stair_filter == 'yes':
        edges = edges.filter(is_staircase=True)
    elif stair_filter == 'no':
        edges = edges.filter(is_staircase=False)
    
    context = {
        'edges': edges,
        'status_filter': status_filter,
        'stair_filter': stair_filter,
    }
    return render(request, 'rec/edges_list.html', context)


def edge_create(request):
    """Create new edge."""
    if request.method == 'POST':
        try:
            from_node = Nodes.objects.get(node_id=request.POST['from_node'])
            to_node = Nodes.objects.get(node_id=request.POST['to_node'])
            
            edge = Edges.objects.create(
                from_node=from_node,
                to_node=to_node,
                distance=float(request.POST['distance']),
                compass_angle=float(request.POST['compass_angle']),
                is_staircase=request.POST.get('is_staircase') == 'on',
                is_active=request.POST.get('is_active', 'on') == 'on'
            )
            messages.success(request, f'Edge from {from_node.name} to {to_node.name} created!')
            reset_pathfinder()
            return redirect('edges_list')
        except Exception as e:
            messages.error(request, f'Error creating edge: {str(e)}')
    
    nodes = Nodes.objects.all().order_by('building', 'name')
    return render(request, 'rec/edge_form.html', {'mode': 'create', 'nodes': nodes})


def edge_edit(request, edge_id):
    """Edit existing edge."""
    edge = get_object_or_404(Edges, edge_id=edge_id)
    
    if request.method == 'POST':
        try:
            edge.from_node = Nodes.objects.get(node_id=request.POST['from_node'])
            edge.to_node = Nodes.objects.get(node_id=request.POST['to_node'])
            edge.distance = float(request.POST['distance'])
            edge.compass_angle = float(request.POST['compass_angle'])
            edge.is_staircase = request.POST.get('is_staircase') == 'on'
            edge.is_active = request.POST.get('is_active', 'on') == 'on'
            edge.save()
            
            messages.success(request, 'Edge updated successfully!')
            reset_pathfinder()
            return redirect('edges_list')
        except Exception as e:
            messages.error(request, f'Error updating edge: {str(e)}')
    
    nodes = Nodes.objects.all().order_by('building', 'name')
    return render(request, 'rec/edge_form.html', {'mode': 'edit', 'edge': edge, 'nodes': nodes})


def edge_delete(request, edge_id):
    """Delete edge."""
    edge = get_object_or_404(Edges, edge_id=edge_id)
    
    if request.method == 'POST':
        edge.delete()
        messages.success(request, 'Edge deleted successfully!')
        reset_pathfinder()
        return redirect('edges_list')
    
    return render(request, 'rec/edge_confirm_delete.html', {'edge': edge})


# ============= Annotations CRUD =============
def annotations_list(request):
    """List all annotations."""
    annotations = Annotation.objects.all().select_related('panorama', 'target_node').order_by('panorama', 'yaw')
    
    # Filter by panorama
    panorama_filter = request.GET.get('panorama', '')
    if panorama_filter:
        annotations = annotations.filter(panorama__node_id=panorama_filter)
    
    context = {
        'annotations': annotations,
        'panorama_filter': panorama_filter,
        'panoramas': Nodes.objects.exclude(image360='').order_by('name'),
    }
    return render(request, 'rec/annotations_list.html', context)


def annotation_create(request):
    """Create new annotation."""
    if request.method == 'POST':
        try:
            panorama = Nodes.objects.get(node_id=request.POST['panorama'])
            target_node_id = request.POST.get('target_node')
            target_node = Nodes.objects.get(node_id=target_node_id) if target_node_id else None
            
            annotation = Annotation.objects.create(
                panorama=panorama,
                target_node=target_node,
                label=request.POST['label'],
                yaw=float(request.POST['yaw']),
                pitch=float(request.POST['pitch']),
                visible_radius=float(request.POST.get('visible_radius', 10.0)),
                is_active=request.POST.get('is_active', 'on') == 'on'
            )
            messages.success(request, f'Annotation "{annotation.label}" created!')
            return redirect('annotations_list')
        except Exception as e:
            messages.error(request, f'Error creating annotation: {str(e)}')
    
    nodes = Nodes.objects.all().order_by('building', 'name')
    panoramas = Nodes.objects.exclude(image360='').order_by('name')
    return render(request, 'rec/annotation_form.html', {
        'mode': 'create',
        'nodes': nodes,
        'panoramas': panoramas
    })


def annotation_edit(request, annotation_id):
    """Edit existing annotation."""
    annotation = get_object_or_404(Annotation, id=annotation_id)
    
    if request.method == 'POST':
        try:
            annotation.panorama = Nodes.objects.get(node_id=request.POST['panorama'])
            target_node_id = request.POST.get('target_node')
            annotation.target_node = Nodes.objects.get(node_id=target_node_id) if target_node_id else None
            annotation.label = request.POST['label']
            annotation.yaw = float(request.POST['yaw'])
            annotation.pitch = float(request.POST['pitch'])
            annotation.visible_radius = float(request.POST.get('visible_radius', 10.0))
            annotation.is_active = request.POST.get('is_active', 'on') == 'on'
            annotation.save()
            
            messages.success(request, 'Annotation updated successfully!')
            return redirect('annotations_list')
        except Exception as e:
            messages.error(request, f'Error updating annotation: {str(e)}')
    
    nodes = Nodes.objects.all().order_by('building', 'name')
    panoramas = Nodes.objects.exclude(image360='').order_by('name')
    return render(request, 'rec/annotation_form.html', {
        'mode': 'edit',
        'annotation': annotation,
        'nodes': nodes,
        'panoramas': panoramas
    })


def annotation_delete(request, annotation_id):
    """Delete annotation."""
    annotation = get_object_or_404(Annotation, id=annotation_id)
    
    if request.method == 'POST':
        label = annotation.label
        annotation.delete()
        messages.success(request, f'Annotation "{label}" deleted successfully!')
        return redirect('annotations_list')
    
    return render(request, 'rec/annotation_confirm_delete.html', {'annotation': annotation})


# ============= Pathfinding Test Page =============
def pathfinding_test(request):
    """Interactive pathfinding test page."""
    nodes = Nodes.objects.all().order_by('building', 'name')
    campus_map = CampusMap.objects.filter(is_active=True).first()
    return render(request, 'rec/pathfinding_test.html', {
        'nodes': nodes,
        'campus_map': campus_map
    })


def map_viewer(request):
    """Interactive campus map viewer showing all positioned nodes."""
    campus_map = CampusMap.objects.filter(is_active=True).first()
    
    total_nodes = Nodes.objects.count()
    positioned_nodes = Nodes.objects.filter(map_x__isnull=False, map_y__isnull=False).count()
    buildings = Nodes.objects.values_list('building', flat=True).distinct().order_by('building')
    floors = Nodes.objects.values_list('floor_level', flat=True).distinct().order_by('floor_level')
    
    return render(request, 'rec/map_viewer.html', {
        'campus_map': campus_map,
        'total_nodes': total_nodes,
        'positioned_nodes': positioned_nodes,
        'buildings': buildings,
        'floors': floors
    })


# ============= API Endpoints =============
@require_http_methods(["POST"])
def api_find_path(request):
    """API endpoint to find path between two nodes."""
    try:
        data = json.loads(request.body)
        start_code = data.get('start')
        goal_code = data.get('goal')
        avoid_stairs = data.get('avoid_stairs', False)
        
        if not start_code or not goal_code:
            return JsonResponse({'error': 'Start and goal codes required'}, status=400)
        
        pathfinder = get_pathfinder()
        result = pathfinder.get_directions(start_code, goal_code, avoid_stairs)
        
        return JsonResponse(result)
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_annotations(request, node_id):
    """API endpoint to get annotations for a panorama node."""
    try:
        annotations = Annotation.objects.filter(
            panorama__node_id=node_id,
            is_active=True
        ).select_related('target_node')
        
        data = [{
            'id': a.id,
            'label': a.label,
            'yaw': a.yaw,
            'pitch': a.pitch,
            'visible_radius': a.visible_radius,
            'target_node': {
                'node_id': a.target_node.node_id,
                'name': a.target_node.name,
                'building': a.target_node.building
            } if a.target_node else None
        } for a in annotations]
        
        return JsonResponse({'annotations': data})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_node_details(request, node_id):
    """API endpoint to get detailed information about a specific node."""
    try:
        node = get_object_or_404(Nodes, node_id=node_id)
        
        data = {
            'node_id': node.node_id,
            'node_code': node.node_code,
            'name': node.name,
            'building': node.building,
            'floor_level': node.floor_level,
            'type_of_node': node.type_of_node,
            'map_x': float(node.map_x) if node.map_x is not None else None,
            'map_y': float(node.map_y) if node.map_y is not None else None,
            'qrcode': node.qrcode.url if node.qrcode else None,
            'image360': node.image360.url if node.image360 else None
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_graph_data(request):
    """API endpoint to get graph visualization data."""
    try:
        nodes_data = [{
            'id': n.node_id,
            'code': n.node_code,
            'name': n.name,
            'building': n.building,
            'floor': n.floor_level,
            'type': n.type_of_node,
            'map_x': float(n.map_x) if n.map_x is not None else None,
            'map_y': float(n.map_y) if n.map_y is not None else None
        } for n in Nodes.objects.all()]
        
        edges_data = [{
            'id': e.edge_id,
            'from': e.from_node.node_id,
            'to': e.to_node.node_id,
            'distance': e.distance,
            'compass': e.compass_angle,
            'staircase': e.is_staircase,
            'active': e.is_active
        } for e in Edges.objects.filter(is_active=True).select_related('from_node', 'to_node')]
        
        return JsonResponse({
            'nodes': nodes_data,
            'edges': edges_data
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
