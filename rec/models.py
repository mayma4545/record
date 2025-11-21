from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO


class CampusMap(models.Model):
    """
    Stores the main campus blueprint image.
    Only one active map is used for the entire campus.
    """
    map_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default='Campus Map', help_text='Map name')
    blueprint_image = models.ImageField(upload_to='campus_maps/', help_text='Campus blueprint/floor plan image')
    
    # Optional calibration data
    scale_meters_per_pixel = models.FloatField(null=True, blank=True,
                                               help_text='Scale: meters per pixel (for distance calculation)')
    
    is_active = models.BooleanField(default=True, help_text='Only one map should be active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Campus Map'
        verbose_name_plural = 'Campus Maps'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        """Ensure only one active map."""
        if self.is_active:
            # Deactivate all other maps
            CampusMap.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

#This provides the database models for the application. for A* ALGORITHM PATH FINDING IN MY CAMPUS
class Nodes(models.Model):
    # in 360 image, we're using compass for direction, when we are capturing images we have to make sure north is upwards in the image and will do the 360 capturing image.
    node_id = models.AutoField(primary_key=True)
    node_code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    building = models.CharField(max_length=255)
    floor_level = models.IntegerField()
    type_of_node = models.CharField(max_length=255, default='room')
    image360 = models.ImageField(upload_to='360_images/', blank=True, null=True, help_text='Upload 360° panorama image')
    
    qrcode = models.ImageField(upload_to='qrcodes/', blank=True, null=True, help_text='Auto-generated QR code')
    description = models.TextField(blank=True, null=True)
    
    # Campus map coordinates (percentage-based for responsive positioning)
    map_x = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                              help_text='X coordinate on campus map (0-100%, left to right)')
    map_y = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
                              help_text='Y coordinate on campus map (0-100%, top to bottom)')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Auto-generate QR code on save."""
        # Generate QR code if node_code exists
        if self.node_code and not self.qrcode:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            # QR code contains node information in JSON format
            qr_data = f'{{"node_code": "{self.node_code}", "name": "{self.name}", "building": "{self.building}"}}'
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f'qr_{self.node_code}.png'
            self.qrcode.save(filename, ContentFile(buffer.getvalue()), save=False)
        
        super().save(*args, **kwargs)

class Edges(models.Model):
    # here from_node and to_node are foreign keys referencing the Nodes model
    # each edge represents a connection between two nodes
    edge_id = models.AutoField(primary_key=True)
    from_node = models.ForeignKey(Nodes, related_name='from_edges', on_delete=models.CASCADE)
    to_node = models.ForeignKey(Nodes, related_name='to_edges', on_delete=models.CASCADE)
    distance = models.FloatField(validators=[MinValueValidator(0.0)]) #distance in meters
    compass_angle = models.FloatField(validators=[MinValueValidator(0.0)], help_text="Compass angle in degrees (0-360) from from_node to to_node")
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_staircase = models.BooleanField(default=False) #Crucial. Set to True if this path is a stair.
    is_active = models.BooleanField(default=True) #If false, this edge is not considered in pathfinding.


class Annotation(models.Model):
    """
    Labels / hotspots to show on a 360° panorama image for a given node.

    An Annotation links a panorama (a Nodes entry -- the node that holds the 360 image)
    to an optional target node (the room/building being labelled). It stores spherical
    coordinates (yaw and pitch in degrees) and a visibility radius so front-end viewers
    can decide when to display the label.
    """

    id = models.AutoField(primary_key=True)
    # The node that owns the panorama image this annotation belongs to
    panorama = models.ForeignKey(Nodes, related_name='annotations', on_delete=models.CASCADE)
    # Optional target node this annotation points to (e.g. a different room)
    target_node = models.ForeignKey(Nodes, related_name='targeted_by_annotations',
                                    on_delete=models.SET_NULL, null=True, blank=True)

    label = models.CharField(max_length=255, help_text='Text label to display for this hotspot')

    # yaw: horizontal angle (-180 .. 180), pitch: vertical angle (-90 .. 90)
    yaw = models.FloatField(validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
                            help_text='Horizontal rotation in degrees (-180..180)')
    pitch = models.FloatField(validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
                              help_text='Vertical rotation in degrees (-90..90)')

    # How wide (in degrees) the annotation should remain visible around the center
    visible_radius = models.FloatField(default=10.0,
                                       validators=[MinValueValidator(0.0), MaxValueValidator(180.0)],
                                       help_text='Angular radius in degrees used by viewer when deciding visibility')

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Panorama Annotation'
        verbose_name_plural = 'Panorama Annotations'
        # avoid duplicate identical annotations for a panorama at the exact same spot
        unique_together = (('panorama', 'yaw', 'pitch', 'label'),)

    def __str__(self):
        target = f' -> {self.target_node.name}' if self.target_node else ''
        return f'{self.label} @ {self.yaw:.1f}°, {self.pitch:.1f}° on {self.panorama.name}{target}'