from fastapi import FastAPI
from redis_om import get_redis_connection,HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = ['http://localhost:3000'],
    allow_methods = ['*'],
    allow_headers = ['*'],
    
    )


redis = get_redis_connection(
    host='redis-16142.c264.ap-south-1-1.ec2.cloud.redislabs.com',
    port='16142',
    password='LErw218RE2KpMV0kX13Lc3PQBVJNbyJQ',
    decode_responses = True
)


class Product(HashModel):
    name:str
    price:float
    quantity:int

    class Meta:
        database = redis

def format(pk: str):
    product = Product.get(pk)

    return{
        'id':product.pk,
        'name':product.name,
        'price':product.price,
        'quantity':product.quantity,
    }

@app.get('/products')
def all():
    return [format(pk) for pk in Product.all_pks()]

@app.post('/products')
def create(product: Product):
    return product.save()

@app.get('/products/{pk}')
def getProduct(pk:str):
    try :
        product = Product.get(pk)
        return product
    except :
        print("Product not found")
        return {"product not found"}
    
    


@app.delete('/products/{pk}')
def deleteProduct(pk: str):
    return Product.delete(pk)

