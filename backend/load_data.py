import json
from datetime import datetime
from app.database import SessionLocal, engine, Base
from app import models

# Crear tablas
Base.metadata.create_all(bind=engine)

# Leer el archivo JSON
with open('Orders.json', 'r', encoding='utf-8') as f:
    orders_data = json.load(f)

db = SessionLocal()

try:
    # Primero, limpiar datos existentes (opcional)
    db.query(models.OrderItem).delete()
    db.query(models.Order).delete()
    db.query(models.Product).delete()
    db.query(models.Customer).delete()
    db.query(models.Supplier).delete()
    
    # Diccionarios para evitar duplicados
    customers = {}
    suppliers = {}
    products = {}
    
    for order_data in orders_data:
        # 1. Crear/obtener Customer
        cust_data = order_data['customer']
        if cust_data['id'] not in customers:
            customer = models.Customer(
                id=cust_data['id'],
                firstName=cust_data['firstName'],
                lastName=cust_data['lastName'],
                city=cust_data['city'],
                country=cust_data['country'],
                phone=cust_data['phone']
            )
            db.add(customer)
            customers[cust_data['id']] = customer
        
        # 2. Crear Order
        order_date = datetime.fromisoformat(order_data['orderDate'].replace('Z', '+00:00'))
        order = models.Order(
            id=order_data['id'],
            orderNumber=order_data['orderNumber'],
            orderDate=order_date,
            customerId=order_data['customer']['id'],
            totalAmount=order_data['totalAmount']
        )
        db.add(order)
        
        # 3. Procesar items y productos
        for item_data in order_data['items']:
            prod_data = item_data['product']
            supp_data = prod_data['supplier']
            
            # Crear/obtener Supplier
            if supp_data['id'] not in suppliers:
                supplier = models.Supplier(
                    id=supp_data['id'],
                    companyName=supp_data['companyName'],
                    contactName=supp_data['contactName'],
                    contactTitle=supp_data['contactTitle'],
                    city=supp_data['city'],
                    country=supp_data['country'],
                    phone=supp_data['phone'],
                    fax=supp_data.get('fax')
                )
                db.add(supplier)
                suppliers[supp_data['id']] = supplier
            
            # Crear/obtener Product
            if prod_data['id'] not in products:
                product = models.Product(
                    id=prod_data['id'],
                    productName=prod_data['productName'],
                    supplierId=prod_data['supplier']['id'],
                    unitPrice=prod_data['unitPrice'],
                    package=prod_data['package'],
                    isDiscontinued=prod_data['isDiscontinued']
                )
                db.add(product)
                products[prod_data['id']] = product
            
            # Crear OrderItem
            order_item = models.OrderItem(
                id=item_data['id'],
                orderId=order_data['id'],
                productId=prod_data['id'],
                unitPrice=item_data['unitPrice'],
                quantity=item_data['quantity']
            )
            db.add(order_item)
    
    db.commit()
    print("✅ Datos cargados exitosamente!")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    
finally:
    db.close()