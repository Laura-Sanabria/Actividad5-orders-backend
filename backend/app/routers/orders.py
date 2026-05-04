from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app import models, schemas

router = APIRouter()

# ========== ENDPOINTS DE ORDERS ==========

@router.get("/orders")
def list_orders(
    page: int = 1,
    limit: int = 10,
    customerId: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Listar pedidos con paginación (OBLIGATORIO)"""
    skip = (page - 1) * limit
    query = db.query(models.Order)
    
    if customerId:
        query = query.filter(models.Order.customerId == customerId)
    
    orders = query.offset(skip).limit(limit).all()
    total = query.count()
    
    return {
        "data": orders,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": (total + limit - 1) // limit
    }

@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Obtener detalle de un pedido (OBLIGATORIO)"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return order

@router.post("/orders", status_code=status.HTTP_201_CREATED)
def create_order(order_data: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Crear un nuevo pedido (OBLIGATORIO)"""
    # Validar cliente
    customer = db.query(models.Customer).filter(models.Customer.id == order_data.customerId).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Validar productos y calcular total
    total = 0
    items_data = []
    
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.productId).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Producto {item.productId} no existe")
        
        subtotal = product.unitPrice * item.quantity
        total += subtotal
        items_data.append({
            "productId": item.productId,
            "quantity": item.quantity,
            "unitPrice": product.unitPrice
        })
    
    # Crear número de orden
    order_count = db.query(models.Order).count()
    order_number = f"ORD-{order_count + 1001}"
    
    # Crear el pedido
    new_order = models.Order(
        orderNumber=order_number,
        customerId=order_data.customerId,
        totalAmount=total,
        orderDate=datetime.now()
    )
    db.add(new_order)
    db.flush()
    
    # Crear los items
    for item_data in items_data:
        order_item = models.OrderItem(
            orderId=new_order.id,
            productId=item_data["productId"],
            quantity=item_data["quantity"],
            unitPrice=item_data["unitPrice"]
        )
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.put("/orders/{order_id}")
def replace_order(order_id: int, order_data: schemas.OrderReplace, db: Session = Depends(get_db)):
    """Reemplazar completamente un pedido (PUT - OBLIGATORIO)"""
    # Verificar que el pedido existe
    existing_order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not existing_order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Verificar que el cliente existe
    customer = db.query(models.Customer).filter(models.Customer.id == order_data.customerId).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    # Eliminar items existentes
    db.query(models.OrderItem).filter(models.OrderItem.orderId == order_id).delete()
    
    # Calcular nuevo total
    total = 0
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.productId).first()
        if not product:
            raise HTTPException(status_code=400, detail=f"Producto {item.productId} no existe")
        total += product.unitPrice * item.quantity
    
    # Actualizar el pedido
    existing_order.customerId = order_data.customerId
    existing_order.orderDate = order_data.orderDate
    existing_order.totalAmount = total
    
    # Crear nuevos items
    for item in order_data.items:
        product = db.query(models.Product).filter(models.Product.id == item.productId).first()
        new_item = models.OrderItem(
            orderId=order_id,
            productId=item.productId,
            quantity=item.quantity,
            unitPrice=product.unitPrice
        )
        db.add(new_item)
    
    db.commit()
    db.refresh(existing_order)
    
    return existing_order

@router.patch("/orders/{order_id}")
def update_order_partial(order_id: int, order_data: schemas.OrderUpdatePartial, db: Session = Depends(get_db)):
    """Actualizar parcialmente un pedido (PATCH - OBLIGATORIO)"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    if order_data.customerId is not None:
        customer = db.query(models.Customer).filter(models.Customer.id == order_data.customerId).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        order.customerId = order_data.customerId
    
    if order_data.orderDate is not None:
        order.orderDate = order_data.orderDate
    
    db.commit()
    db.refresh(order)
    
    return order

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    """Eliminar un pedido (DELETE - OBLIGATORIO)"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Primero eliminar los items relacionados
    db.query(models.OrderItem).filter(models.OrderItem.orderId == order_id).delete()
    # Luego eliminar el pedido
    db.delete(order)
    db.commit()
    
    return None

# ========== ENDPOINTS DE ORDER ITEMS ==========

@router.get("/orders/{order_id}/items")
def list_order_items(order_id: int, db: Session = Depends(get_db)):
    """Listar los items de un pedido (OBLIGATORIO)"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    items = db.query(models.OrderItem).filter(models.OrderItem.orderId == order_id).all()
    return items

@router.post("/orders/{order_id}/items", status_code=status.HTTP_201_CREATED)
def add_order_item(order_id: int, item_data: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    """Agregar un producto a un pedido existente (OBLIGATORIO)"""
    # Verificar que el pedido existe
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Verificar que el producto existe
    product = db.query(models.Product).filter(models.Product.id == item_data.productId).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar si el item ya existe
    existing_item = db.query(models.OrderItem).filter(
        models.OrderItem.orderId == order_id,
        models.OrderItem.productId == item_data.productId
    ).first()
    
    if existing_item:
        # Si existe, actualizar cantidad
        existing_item.quantity += item_data.quantity
        db.commit()
        new_item = existing_item
    else:
        # Crear nuevo item
        new_item = models.OrderItem(
            orderId=order_id,
            productId=item_data.productId,
            quantity=item_data.quantity,
            unitPrice=product.unitPrice
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
    
    # Recalcular total del pedido
    recalculate_order_total(order_id, db)
    
    return new_item

@router.patch("/orders/{order_id}/items/{item_id}")
def update_order_item(order_id: int, item_id: int, item_data: schemas.OrderItemUpdate, db: Session = Depends(get_db)):
    """Actualizar cantidad o precio unitario de un item (PATCH - OBLIGATORIO)"""
    # Verificar que el pedido existe
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Verificar que el item existe
    item = db.query(models.OrderItem).filter(
        models.OrderItem.id == item_id,
        models.OrderItem.orderId == order_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    if item_data.quantity is not None:
        item.quantity = item_data.quantity
    
    if item_data.unitPrice is not None:
        item.unitPrice = item_data.unitPrice
    
    db.commit()
    db.refresh(item)
    
    # Recalcular total del pedido
    recalculate_order_total(order_id, db)
    
    return item

@router.delete("/orders/{order_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order_item(order_id: int, item_id: int, db: Session = Depends(get_db)):
    """Eliminar un item de un pedido (DELETE - OBLIGATORIO)"""
    # Verificar que el pedido existe
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Verificar que el item existe
    item = db.query(models.OrderItem).filter(
        models.OrderItem.id == item_id,
        models.OrderItem.orderId == order_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
    db.delete(item)
    db.commit()
    
    # Recalcular total del pedido
    recalculate_order_total(order_id, db)
    
    return None

# ========== FUNCIÓN AUXILIAR ==========

def recalculate_order_total(order_id: int, db: Session):
    """Recalcular el totalAmount de un pedido"""
    items = db.query(models.OrderItem).filter(models.OrderItem.orderId == order_id).all()
    total = sum(item.unitPrice * item.quantity for item in items)
    
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        order.totalAmount = total
        db.commit()