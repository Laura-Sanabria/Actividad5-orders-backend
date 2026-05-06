# backend/app/load_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
import json
from datetime import datetime

router = APIRouter()

@router.post("/load-data")
def load_initial_data(db: Session = Depends(get_db)):
    """Endpoint para cargar datos desde Orders.json"""
    
    # Leer el archivo JSON
    with open('Orders.json', 'r', encoding='utf-8') as f:
        orders_data = json.load(f)
    
    # Limpiar datos existentes
    db.query(models.OrderItem).delete()
    db.query(models.Order).delete()
    db.query(models.Product).delete()
    db.query(models.Customer).delete()
    db.query(models.Supplier).delete()
    
    customers = {}
    suppliers = {}
    products = {}
    
    for order_data in orders_data:
        # Customer
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
        
        # Order
        order_date = datetime.fromisoformat(order_data['orderDate'].replace('Z', '+00:00'))
        order = models.Order(
            id=order_data['id'],
            orderNumber=order_data['orderNumber'],
            orderDate=order_date,
            customerId=order_data['customer']['id'],
            totalAmount=order_data['totalAmount']
        )
        db.add(order)
        
        # Items, Products, Suppliers
        for item_data in order_data['items']:
            prod_data = item_data['product']
            supp_data = prod_data['supplier']
            
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
            
            order_item = models.OrderItem(
                id=item_data['id'],
                orderId=order_data['id'],
                productId=prod_data['id'],
                unitPrice=item_data['unitPrice'],
                quantity=item_data['quantity']
            )
            db.add(order_item)
    
    db.commit()
    
    return {
        "message": "Datos cargados exitosamente",
        "customers": len(customers),
        "suppliers": len(suppliers),
        "products": len(products),
        "orders": len(orders_data)
    }