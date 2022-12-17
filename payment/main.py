from fastapi import FastAPI
from redis_om import get_redis_connection,HashModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from starlette.requests import Request
import requests,time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods = ['*'],
    allow_headers = ['*'],
    
)

# TO ADD A NEW DATABASE HERE
redis = get_redis_connection(
    host=$HOST,
    port='16142',
    password=$PASSWORD,
    decode_responses = True
)

class Order(HashModel):
    status:str #pending,completed,refunded
    product_id:str
    price:float
    fee:float
    total_price:float
    quantity:int

    class Meta:
        database = redis
    

def format(pk:str):
    order = Order.get(pk)

    return{
        'id':order.pk,
        'price':order.price,
        'fee':order.fee,
        'quantity':order.quantity,
        'total_price':order.total_price,
        'status':order.status
    }

@app.get('/orders/{pk}')
def getOrder(pk:str):
    try :
        order = Order.get(pk)
        return order
    except :
        return {"Order not found"}

@app.delete('/orders/{pk}')
def deleteOrder(pk:str):
    try:
        Order.delete(pk)
    except:
        return {"Order not found"}

@app.get('/orders')
def getOrders():
    return [format(pk) for pk in Order.all_pks()]


@app.post('/orders')
async def createRequest(request:Request,background_tasks:BackgroundTasks):
    body = await request.json() #id,quantity
    req = requests.get('http://127.0.0.1:8000/products/%s' % body['id'])
    product = req.json()
    order = Order(
        product_id=body['id'],
        price=product['price'],
        fee=0.3*product['price'],
        total_price=1.3*product['price'],
        quantity=body['quantity'],
        status='pending'
    )
    order.save()
    background_tasks.add_task(order_completed,order)
    return order

def order_completed(order:Order):
    time.sleep(3)
    order.status = 'completed'
    order.save()
    redis.xadd('order_completed', order.dict(), '*')