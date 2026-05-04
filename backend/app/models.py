from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    firstName = Column(String)
    lastName = Column(String)
    city = Column(String)
    country = Column(String)
    phone = Column(String)
    
    orders = relationship("Order", back_populates="customer")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    companyName = Column(String)
    contactName = Column(String)
    contactTitle = Column(String)
    city = Column(String)
    country = Column(String)
    phone = Column(String)
    fax = Column(String, nullable=True)
    
    products = relationship("Product", back_populates="supplier")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    productName = Column(String)
    supplierId = Column(Integer, ForeignKey("suppliers.id"))
    unitPrice = Column(Float)
    package = Column(String)
    isDiscontinued = Column(Boolean, default=False)
    
    supplier = relationship("Supplier", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    orderNumber = Column(String, unique=True)
    orderDate = Column(DateTime, default=datetime.now)
    customerId = Column(Integer, ForeignKey("customers.id"))
    totalAmount = Column(Float, default=0.0)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    orderId = Column(Integer, ForeignKey("orders.id"))
    productId = Column(Integer, ForeignKey("products.id"))
    unitPrice = Column(Float)
    quantity = Column(Integer)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")