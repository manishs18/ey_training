from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Day19 Agent Backend",
    version="1.0.0"
)

# ============================================
# Fake Database
# ============================================

ORDERS = {
    "A1001": {
        "id": "A1001",
        "customer_id": "C1001",
        "item": "Mechanical Keyboard",
        "qty": 1,
        "status": "Shipped",
        "total": 129.00,
    },
    "A1002": {
        "id": "A1002",
        "customer_id": "C1002",
        "item": "USB-C Hub",
        "qty": 2,
        "status": "Processing",
        "total": 58.00,
    },
    "A1003": {
        "id": "A1003",
        "customer_id": "C1001",
        "item": "4K Monitor",
        "qty": 1,
        "status": "Delivered",
        "total": 410.00,
    },
}

CUSTOMERS = {
    "C1001": {
        "id": "C1001",
        "name": "Asha",
        "membership": "Gold",
        "city": "Bangalore",
    },
    "C1002": {
        "id": "C1002",
        "name": "Rahul",
        "membership": "Silver",
        "city": "Hyderabad",
    },
}

# ============================================
# Models
# ============================================

class Order(BaseModel):
    id: str
    customer_id: str
    item: str
    qty: int
    status: str
    total: float


class Customer(BaseModel):
    id: str
    name: str
    membership: str
    city: str


# ============================================
# Routes
# ============================================

@app.get("/")
def root():
    return {
        "message": "Day19 Agent API Running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/orders")
def get_orders():
    return list(ORDERS.values())


@app.get("/customers")
def get_customers():
    return list(CUSTOMERS.values())


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):

    order = ORDERS.get(order_id.upper())

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):

    customer = CUSTOMERS.get(customer_id.upper())

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    return customer


@app.post("/orders")
def create_order(order: Order):

    ORDERS[order.id.upper()] = order.model_dump()

    return {
        "success": True,
        "order": order
    }


@app.post("/customers")
def create_customer(customer: Customer):

    CUSTOMERS[customer.id.upper()] = customer.model_dump()

    return {
        "success": True,
        "customer": customer
    }


@app.delete("/orders/{order_id}")
def delete_order(order_id: str):

    if order_id.upper() not in ORDERS:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    del ORDERS[order_id.upper()]

    return {
        "deleted": order_id
    }


@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: str):

    if customer_id.upper() not in CUSTOMERS:
        raise HTTPException(
            status_code=404,
            detail="Customer not found"
        )

    del CUSTOMERS[customer_id.upper()]

    return {
        "deleted": customer_id
    }


if __name__ == "__main__":

    uvicorn.run(

        "api:app",

        host="0.0.0.0",

        port=8000,

        reload=True,

    )