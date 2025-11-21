from django.test import TestCase
from django.db import IntegrityError

from .models import Node, Edge


class GraphModelsTests(TestCase):
	def test_node_and_edge_creation(self):
		n1 = Node.objects.create(node_code="B1-F1-N01", name="Main Lobby", building="Main Building", floor_level=1, type="DESTINATION")
		n2 = Node.objects.create(node_code="B1-F1-N02", name="Hall Intersection", building="Main Building", floor_level=1, type="JUNCTION")

		edge = Edge.objects.create(start_node=n1, end_node=n2, weight=12.345, is_staircase=False, is_active=True)

		self.assertEqual(str(n1), "B1-F1-N01 — Main Lobby")
		self.assertIn("B1-F1-N01 -> B1-F1-N02", str(edge))
		self.assertTrue(edge.is_active)
		self.assertFalse(edge.is_staircase)

	def test_edge_unique_constraint(self):
		n1 = Node.objects.create(node_code="B1-F2-N01", name="Room 201", building="Main Building", floor_level=2)
		n2 = Node.objects.create(node_code="B1-F2-N02", name="Stairs Top", building="Main Building", floor_level=2)

		Edge.objects.create(start_node=n1, end_node=n2, weight=5.0)

		with self.assertRaises(IntegrityError):
			# Creating a duplicate edge should violate the unique constraint
			Edge.objects.create(start_node=n1, end_node=n2, weight=5.0)

	def test_inactive_edge(self):
		# An edge can be marked inactive to represent closed paths
		n1 = Node.objects.create(node_code="B1-F3-N01", name="Room 301", building="Main Building", floor_level=3)
		n2 = Node.objects.create(node_code="B1-F3-N02", name="Corridor End", building="Main Building", floor_level=3)

		edge = Edge.objects.create(start_node=n1, end_node=n2, weight=2.0, is_active=False)
		self.assertFalse(edge.is_active)

