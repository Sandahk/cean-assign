from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import (create_engine, Column, Integer, String, Float, Boolean, ForeignKey, JSON)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@db:5432/quotesdb")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

app = FastAPI()
# Allow local frontend dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

### DB MODELS

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Float)
    has_colors = Column(Boolean, default=False)
    colors = Column(JSON, nullable=True)  # e.g. ["red", "blue"]
    is_kit = Column(Boolean, default=False)
    kit_components = Column(JSON, nullable=True)  # list of product ids (in default order)

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(Integer, primary_key=True)
    customer = Column(String)
    total = Column(Float)
    items = relationship("QuoteItem", back_populates="quote")

class QuoteItem(Base):
    __tablename__ = "quote_items"
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    color = Column(String, nullable=True)
    order = Column(Integer)   # For kits: custom order in quote
    is_kit_component = Column(Boolean, default=False)
    quote = relationship("Quote", back_populates="items")
    product = relationship("Product")

Base.metadata.create_all(bind=engine)

# --- Sample data seeding ---
@app.get("/seed")
def seed_db():
    session = SessionLocal()
    if session.query(Product).first():
        session.close()
        return  # already seeded

    # Add your products here!
    p1 = Product(name="ACME Basic AC", price=100.0, has_colors=False)
    p2 = Product(name="ACME Pro AC", price=180.0, has_colors=True, colors=["white", "black", "gray"])
    p3 = Product(name="ACME Wall Bracket", price=25.0, has_colors=False)
    p4 = Product(name="ACME Air Filter", price=15.0, has_colors=True, colors=["blue", "green"])
    # Define a kit
    kit = Product(
        name="ACME Installation Kit",
        price=0.0,
        has_colors=False,
        is_kit=True,
        kit_components=[2, 3]  # You can use dummy IDs first, will update below
    )

    # Add normal products first, flush to assign IDs
    session.add_all([p1, p2, p3, p4])
    session.flush()

    # Now assign real kit component IDs (e.g., p2, p3)
    kit.kit_components = [p2.id, p3.id]
    session.add(kit)
    session.commit()
    session.close()


# --- API Endpoints ---

@app.get("/products")
def get_products():
    session = SessionLocal()
    products = session.query(Product).all()
    result = []
    for p in products:
        result.append({
            "id": p.id, "name": p.name, "price": p.price,
            "has_colors": p.has_colors, "colors": p.colors or [],
            "is_kit": p.is_kit, "kit_components": p.kit_components or [],
        })
    session.close()
    return result

@app.post("/quotes")
def create_quote(data: dict):
    """
    Data format:
    {
        "customer": "John Doe",
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1, "color": "black"},
            {"product_id": 4, "quantity": 1, "kit_order": [3,1]}
        ]
    }
    """
    session = SessionLocal()
    total = 0
    items_to_save = []
    for order_idx, item in enumerate(data["items"]):
        product = session.query(Product).get(item["product_id"])
        if not product:
            session.close()
            raise HTTPException(404, "Product not found")
        if product.is_kit:
            # Expand kit into components, allow reordering
            kit_order = item.get("kit_order", product.kit_components)
            for comp_idx, pid in enumerate(kit_order):
                comp = session.query(Product).get(pid)
                if not comp:
                    session.close()
                    raise HTTPException(404, "Kit component not found")
                qty = item.get("quantity", 1)
                subtotal = comp.price * qty
                total += subtotal
                items_to_save.append(
                    QuoteItem(
                        product_id=comp.id,
                        quantity=qty,
                        color=None,
                        order=comp_idx,
                        is_kit_component=True
                    )
                )
        else:
            subtotal = product.price * item.get("quantity", 1)
            total += subtotal
            items_to_save.append(
                QuoteItem(
                    product_id=product.id,
                    quantity=item.get("quantity", 1),
                    color=item.get("color"),
                    order=order_idx,
                    is_kit_component=False
                )
            )
    quote = Quote(customer=data["customer"], total=total)
    session.add(quote)
    session.flush()  # to get quote.id
    for i in items_to_save:
        i.quote_id = quote.id
        session.add(i)
    session.commit()
    session.refresh(quote)
    session.close()
    return {"id": quote.id, "total": total}

@app.get("/quotes/{qid}")
def get_quote(qid: int):
    session = SessionLocal()
    quote = session.query(Quote).get(qid)
    if not quote:
        session.close()
        raise HTTPException(404, "Quote not found")
    result = {
        "id": quote.id,
        "customer": quote.customer,
        "total": quote.total,
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "color": item.color,
                "order": item.order,
                "is_kit_component": item.is_kit_component
            }
            for item in sorted(quote.items, key=lambda x: x.order)
        ]
    }
    session.close()
    return result

# Health check
@app.get("/")
def root():
    return {"msg": "Quote Manager API"}
