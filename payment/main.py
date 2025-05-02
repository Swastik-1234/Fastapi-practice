from fastapi import FastAPI

import time
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from starlette.requests import Request  # corrected import
import requests
from redis_om import get_redis_connection, HashModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-15301.c305.ap-south-1-1.ec2.redns.redis-cloud.com",
    port=15301,
    password="8qXahaWZHdNFCXtYqQkkbcy9HLE5hMWT",
    decode_responses=True
)

class Order(HashModel):  # added colon
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:  # added colon and correct indentation
        database = redis

@app.get("/orders/{pk}")
def get(pk:str):
    return Order.get(pk)

@app.post("/orders")
async def Create(request: Request,background_tasks:BackgroundTasks):
    body = await request.json()
    req = requests.get(f"http://localhost:8000/products/{body['id']}")  # fixed formatting
    product= req.json()

    order=Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.2*product['price'],
        total=1.2*product['price'],
        quantity=body['quantity'],
        status='pending'
    )

    order.save()
    background_tasks.add_task(order_completed,order)

    

    return order

def order_completed(order:Order):
    time.sleep(12)
    order.status='completed'
    order.save()
    redis.xadd('order_completed',order.dict(),'*')


