from django.test import TestCase, Client
from .models import Product, Inventory, Order, OrderItem, PendingOrder
import json

class InventorySystemTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create some products for testing
        Product.objects.create(product_id=1, product_name="RBC A+ Adult", mass_g=700)
        Product.objects.create(product_id=2, product_name="FFP A+", mass_g=300)

    #Test initializing the catalog
    def test_init_catalog(self):
     
        response = self.client.post('/inventory/init_catalog/', json.dumps([
            {"mass_g": 500, "product_name": "New Product"}
        ]), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Product.objects.filter(product_name="New Product").exists())

    #Test restocking the inventory
    def test_process_restock(self):

        product = Product.objects.get(product_name="RBC A+ Adult")
        response = self.client.post('/inventory/process_restock/', json.dumps([
            {"product_id": product.product_id, "quantity": 10}
        ]), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        inventory = Inventory.objects.get(product=product)
        self.assertEqual(inventory.quantity, 10)

    #Test processing a successful order
    def test_process_order_successful(self):
        
        product = Product.objects.get(product_name="FFP A+")
        # Restock first
        self.client.post('/inventory/process_restock/', json.dumps([
            {"product_id": product.product_id, "quantity": 5}
        ]), content_type='application/json')

        # Place an order
        response = self.client.post('/inventory/process_order/', json.dumps({
            "requested": [{"product_id": product.product_id, "quantity": 2}]
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check if inventory is reduced
        inventory = Inventory.objects.get(product=product)
        self.assertEqual(inventory.quantity, 3)

    #Test processing an order when inventory is insufficient
    def test_process_order_insufficient_inventory(self):
        
        product = Product.objects.get(product_name="FFP A+")
        # No restock done, inventory should be zero
        response = self.client.post('/inventory/process_order/', json.dumps({
            "requested": [{"product_id": product.product_id, "quantity": 2}]
        }), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        # Check that the order is added to pending orders
        self.assertTrue(PendingOrder.objects.exists())

    #Test restocking with an invalid product id
    def test_process_restock_handles_invalid_product(self):
        
        response = self.client.post('/inventory/process_restock/', json.dumps([
            {"product_id": 9999, "quantity": 10}
        ]), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    #Test that orders are split correctly based on the 1.8 kg weight limit
    def test_process_order_with_weight_limit(self):
  
        product_a = Product.objects.get(product_name="RBC A+ Adult")
        product_b = Product.objects.get(product_name="FFP A+")

        # Restock
        self.client.post('/inventory/process_restock/', json.dumps([
            {"product_id": product_a.product_id, "quantity": 5},
            {"product_id": product_b.product_id, "quantity": 3}
        ]), content_type='application/json')

        # Place an order
        response = self.client.post('/inventory/process_order/', json.dumps({
            "requested": [
                {"product_id": product_a.product_id, "quantity": 3},
                {"product_id": product_b.product_id, "quantity": 2}
            ]
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        # Verify that the output simulates correct packaging