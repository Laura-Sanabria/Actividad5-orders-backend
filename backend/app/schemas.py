from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Esquemas para Customer
class CustomerBase(BaseModel):
    firstName: str
    lastName: str
    city: str
    country: str
    phone: str

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    
    class Config:
        from_attributes = True

# Esquemas para Product
class ProductBase(BaseModel):
    productName: str
    supplierId: int
    unitPrice: float
    package: str
    isDiscontinued: bool = False

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    
    class Config:
        from_attributes = True

# Esquemas para OrderItem
class OrderItemBase(BaseModel):
    productId: int
    quantity: int

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    orderId: int
    unitPrice: float
    
    class Config:
        from_attributes = True

# Esquemas para Order
class OrderCreate(BaseModel):
    customerId: int
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    customerId: Optional[int] = None
    orderDate: Optional[datetime] = None

class Order(BaseModel):
    id: int
    orderNumber: str
    orderDate: datetime
    customerId: int
    totalAmount: float
    
    class Config:
        from_attributes = True

# ===== NUEVOS ESQUEMAS PARA ITEMS =====

class OrderItemUpdate(BaseModel):
    """Para actualizar cantidad o precio de un item"""
    quantity: Optional[int] = None
    unitPrice: Optional[float] = None

class OrderUpdatePartial(BaseModel):
    """Para PATCH /orders/{orderId}"""
    customerId: Optional[int] = None
    orderDate: Optional[datetime] = None

class OrderReplace(BaseModel):
    """Para PUT /orders/{orderId} - reemplazo completo"""
    customerId: int
    orderDate: datetime
    items: List[OrderItemCreate]