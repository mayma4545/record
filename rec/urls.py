"""URL Configuration for rec app."""
from django.urls import path
from . import views, api_views

urlpatterns = [
    # Main dashboard
    path('', views.index, name='index'),
    
    # Nodes CRUD
    path('nodes/', views.nodes_list, name='nodes_list'),
    path('nodes/create/', views.node_create, name='node_create'),
    path('nodes/<int:node_id>/edit/', views.node_edit, name='node_edit'),
    path('nodes/<int:node_id>/delete/', views.node_delete, name='node_delete'),
    
    # Edges CRUD
    path('edges/', views.edges_list, name='edges_list'),
    path('edges/create/', views.edge_create, name='edge_create'),
    path('edges/<int:edge_id>/edit/', views.edge_edit, name='edge_edit'),
    path('edges/<int:edge_id>/delete/', views.edge_delete, name='edge_delete'),
    
    # Annotations CRUD
    path('annotations/', views.annotations_list, name='annotations_list'),
    path('annotations/create/', views.annotation_create, name='annotation_create'),
    path('annotations/<int:annotation_id>/edit/', views.annotation_edit, name='annotation_edit'),
    path('annotations/<int:annotation_id>/delete/', views.annotation_delete, name='annotation_delete'),
    
    # Pathfinding test page
    path('pathfinding/', views.pathfinding_test, name='pathfinding_test'),
    
    # Map viewer
    path('map-viewer/', views.map_viewer, name='map_viewer'),
    
    # Original API endpoints
    path('api/find-path/', views.api_find_path, name='api_find_path'),
    path('api/annotations/<int:node_id>/', views.api_annotations, name='api_annotations'),
    path('api/graph-data/', views.api_graph_data, name='api_graph_data'),
    path('api/node-details/<int:node_id>/', views.api_node_details, name='api_node_details'),
    
    # Mobile App API Endpoints
    # Public endpoints
    path('api/mobile/nodes/', api_views.api_nodes_list, name='api_mobile_nodes_list'),
    path('api/mobile/nodes/<int:node_id>/', api_views.api_node_detail, name='api_mobile_node_detail'),
    path('api/mobile/buildings/', api_views.api_buildings_list, name='api_mobile_buildings_list'),
    path('api/mobile/campus-map/', api_views.api_campus_map, name='api_mobile_campus_map'),
    path('api/mobile/find-path/', api_views.api_find_path, name='api_mobile_find_path'),
    path('api/mobile/edges/', api_views.api_edges_list, name='api_mobile_edges_list'),
    path('api/mobile/annotations/', api_views.api_annotations_list, name='api_mobile_annotations_list'),
    
    # Admin authentication
    path('api/mobile/admin/login/', api_views.api_admin_login, name='api_mobile_admin_login'),
    
    # Admin CRUD endpoints
    path('api/mobile/admin/nodes/create/', api_views.api_node_create, name='api_mobile_node_create'),
    path('api/mobile/admin/nodes/<int:node_id>/update/', api_views.api_node_update, name='api_mobile_node_update'),
    path('api/mobile/admin/nodes/<int:node_id>/delete/', api_views.api_node_delete, name='api_mobile_node_delete'),
    
    path('api/mobile/admin/edges/create/', api_views.api_edge_create, name='api_mobile_edge_create'),
    path('api/mobile/admin/edges/<int:edge_id>/update/', api_views.api_edge_update, name='api_mobile_edge_update'),
    path('api/mobile/admin/edges/<int:edge_id>/delete/', api_views.api_edge_delete, name='api_mobile_edge_delete'),
    
    path('api/mobile/admin/annotations/create/', api_views.api_annotation_create, name='api_mobile_annotation_create'),
    path('api/mobile/admin/annotations/<int:annotation_id>/update/', api_views.api_annotation_update, name='api_mobile_annotation_update'),
    path('api/mobile/admin/annotations/<int:annotation_id>/delete/', api_views.api_annotation_delete, name='api_mobile_annotation_delete'),
]
