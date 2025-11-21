"""URL Configuration for rec app."""
from django.urls import path
from . import views

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
    
    # API endpoints
    path('api/find-path/', views.api_find_path, name='api_find_path'),
    path('api/annotations/<int:node_id>/', views.api_annotations, name='api_annotations'),
    path('api/graph-data/', views.api_graph_data, name='api_graph_data'),
    path('api/node-details/<int:node_id>/', views.api_node_details, name='api_node_details'),
]
