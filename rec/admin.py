from django.contrib import admin
from .models import Nodes, Edges, Annotation, CampusMap


@admin.register(CampusMap)
class CampusMapAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Map Information', {
            'fields': ('name', 'blueprint_image', 'is_active'),
            'description': 'Upload the main campus blueprint image. Only one map should be active at a time.'
        }),
        ('Calibration (Optional)', {
            'fields': ('scale_meters_per_pixel',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Nodes)
class NodesAdmin(admin.ModelAdmin):
	list_display = ("node_code", "name", "building", "floor_level", "type_of_node", "created_at")
	search_fields = ("node_code", "name", "building")
	list_filter = ("building", "floor_level", "type_of_node")
	readonly_fields = ('created_at',)
	fieldsets = (
		('Basic Information', {
			'fields': ('node_code', 'name', 'building', 'floor_level', 'type_of_node')
		}),
		('Media & Links', {
			'fields': ('image360', 'qrcode')
		}),
		('Map Position', {
			'fields': ('map_x', 'map_y'),
			'description': 'Use Map Editor for visual positioning'
		}),
		('Additional Info', {
			'fields': ('description', 'created_at')
		}),
	)


@admin.register(Edges)
class EdgesAdmin(admin.ModelAdmin):
	list_display = ("from_node", "to_node", "distance", "compass_angle", "is_staircase", "is_active", "created_at")
	search_fields = ("from_node__node_code", "to_node__node_code")
	list_filter = ("is_staircase", "is_active")
	readonly_fields = ('created_at',)
	raw_id_fields = ['from_node', 'to_node']


@admin.register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
	list_display = ('label', 'panorama', 'target_node', 'yaw', 'pitch', 'visible_radius', 'is_active', 'created_at')
	list_filter = ('is_active', 'panorama__building')
	search_fields = ('label', 'panorama__name', 'target_node__name')
	ordering = ('panorama', 'yaw')
	readonly_fields = ('created_at', 'updated_at')
	raw_id_fields = ['panorama', 'target_node']
	fieldsets = (
		('Annotation Info', {
			'fields': ('label', 'panorama', 'target_node', 'is_active')
		}),
		('Position (Spherical Coordinates)', {
			'fields': ('yaw', 'pitch', 'visible_radius')
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at')
		}),
	)

