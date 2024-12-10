from django.http import JsonResponse
from .models import Product, Inventory, Order, OrderItem, PendingOrder
from django.views.decorators.csrf import csrf_exempt
import json

# """Initialize the catalog with given products."""
@csrf_exempt
def init_catalog(request):

    if request.method == 'POST':
        try:
            product_info = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
    try:
        for product in product_info:
            Product.objects.create(
                product_name=product['product_name'],
                mass_g=product['mass_g']
            )
        return JsonResponse({"status": "Catalog initialized successfully!"}, status=201)
    # except json.JSONDecodeError:
    #     return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

#Restock inventory and attempt to fulfill pending orders.
@csrf_exempt
def process_restock(request):

    if request.method == 'POST':
        restock_info = json.loads(request.body)
    try:
        for item in restock_info:
            product = Product.objects.get(id=item['product_id'])
            inventory, created = Inventory.objects.get_or_create(product=product)
            inventory.quantity += item['quantity']
            inventory.save()
        # Call a method to fulfill pending orders
        fulfill_pending_orders()
        return JsonResponse({"status": "Restocked successfully!"}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=404)


#Handle incoming orders, and ship packages if inventory allows.
@csrf_exempt
def process_order(request):

    if request.method == 'POST':
        order_data = json.loads(request.body)
    try:
        order = Order.objects.create()
        for item in order_data['requested']:
            product = Product.objects.get(id=item['product_id'])
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])
        # Attempt to fulfill the order
        can_fulfill = try_fulfill_order(order)
        if not can_fulfill:
            # Save as a pending order
            PendingOrder.objects.create(order=order)
        return JsonResponse({"status": "Order processed!"}, status=200)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


 #Try to fulfill pending orders after restock.
def fulfill_pending_orders():

    for pending in PendingOrder.objects.all():
        if try_fulfill_order(pending.order):
            pending.delete()


#Try to fulfill an order based on inventory. Returns True if successful.
def try_fulfill_order(order):

    packages = []
    current_package = []
    current_weight = 0
    all_items_available = True

    # Check if we can fulfill the order
    for item in order.orderitem_set.all():
        inventory = Inventory.objects.get(product=item.product)
        if inventory.quantity < item.quantity:
            all_items_available = False
            break

    if not all_items_available:
        return False  # Can't fulfill order

    # Create packages that do not exceed 1.8 kg

    for item in order.orderitem_set.all():
        product = item.product
        mass_per_unit = product.mass_g
        quantity_needed = item.quantity

        while quantity_needed > 0:
            if (current_weight + mass_per_unit) <= 1800:
                # Add product to current package
                current_package.append({'product_id': product.product_id, 'quantity': 1})
                current_weight += mass_per_unit
                quantity_needed -= 1

                # Reduce from inventory
                inventory = Inventory.objects.get(product=product)
                inventory.quantity -= 1
                inventory.save()
            else:
                # Ship current package
                packages.append(current_package)
                current_package = []
                current_weight = 0

    if current_package:
        packages.append(current_package)

    # Ship all packages
    for package in packages:
        ship_package({'order_id': order.order_id, 'shipped': package})

    return True

#Simulate shipping by printing the shipment details.
def ship_package(shipment):

    print(f"Shipping Order #{shipment['order_id']}")
    for item in shipment['shipped']:
        product = Product.objects.get(product_id=item['product_id'])
        print(f"Product: {product.product_name}, Quantity: {item['quantity']}")


#Ship the order and print the details.
def ship_order(order):

    print(f"Shipping Order #{order.order_id}")
    for item in order.orderitem_set.all():
        print(f"Product: {item.product.product_name}, Quantity: {item.quantity}")



def health_check(request):
    return JsonResponse({"status": "ok"})