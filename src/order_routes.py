from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from database import Session, engine
from fastapi.encoders import jsonable_encoders

order_router = APIRouter(
    prefix = '/orders',
    tags = ['orders']
)

session = Session(bind=engine)

@order_router.get('/')
async def hello(Authorize: AuthJWT = Depends()):
    
    """
        ## A sample hello world route
        This returns Hello World
    """
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    return {"message": "Hello World"}

@order_router.post('/orders', status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    
    """
        ## Placing an Order
        This requires the following:
        - quantity: integer
        - pizza_size: string
    """    
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(User).filter(User.username==current_user).first()
    
    new_order = Order(
        pizza_size = order.pizza_size,
        quantity = order.quantity
    ) 

    new_order.user = user
    
    session.add(new_order)
    
    session.commit()
    
    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }
    
    return jsonable_encoders(response)
    
@order_router.get('/orders')
async def list_all_orders(Authorize: AuthJWT = Depends()):
    
    """
        ## List all Orders
        This lists all orders made. It can be accessed by superusers
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(User).filter(User.username==current_user).first()
    
    if user.is_staff:
        orders=session.query(Order).all()
        
        return jsonable_encoders(orders)
    
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        details = "You are not a superuser"
    )
    
@order_router.get('/orders/{id}')
async def get_order_by_id(int: int,Authorize: AuthJWT = Depends()):
    
    """
        ## Get an Order by its ID
        This requires the following:
        - id: integer
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(User).filter(User.username==current_user).first()
    
    if user.is_staff:
        orders=session.query(Order).filter(Order.id==id).all()
        
        return jsonable_encoders(orders)
    
    raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        details = "You are not a superuser"
    )
    
@order_router.get('/user/orders')
async def get_user_orders(Authorize: AuthJWT = Depends()):
    
    """
        ## Get User Orders
        This gets the orders from the user
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(User).filter(User.username==current_user).first()
    
    return jsonable_encoders(user.orders)

@order_router.get('/user/orders/{id}')
async def get_specific_order(Authorize: AuthJWT = Depends()):
    
    """
        ## Get User Order by ID
        This requires the following:
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    current_user = Authorize.get_jwt_subject()
    
    user = session.query(User).filter(User.username==current_user).first()
    
    orders = user.orders
    
    for o in orders:
        if o.id == id:
            return jsonable_encoders(o)
        
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, details = "No order with such id")

@order_router.put('/order/update/{order_id}/')
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    
    """
        ## Update an Order
        This requires the following:
        - id: integer
        - order: attributes from the order model to be updated
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    order_to_update = session.query(Order).filter(Order.id==id).first()
    
    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size
    
    session.commit()
    
    return jsonable_encoders(order_to_update)
    
@order_router.patch('/order/update/{id}/')
async def update_order_status(id: int, order: OrderStatusModel,Authorize: AuthJWT = Depends()):
    
    """
        ## Update an Order Status
        This requires the following:
        - id: integer
        - order: attributes from the order model to be updated
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    username = Authorize.get_jwt_subject()
    
    current_user = session.query(User).filter(User.username==username)
    
    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id==id)
        
        order_to_update.order_status = order.order_status
        
        session.commit()
        
        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status": order_to_update.order_status
        }
        
        return jsonable_encoders(response)
            
@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, Authorize: AuthJWT = Depends()):   
    
    """
        ## Delete an Order
        This requires the following:
        - id: integer
    """        
    
    try:
        Authorize.jwt_required()
    except:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            details = "Invalid Token!"
        )
        
    order_to_delete = session.query(Order).filter(Order.id==id).first()
    
    session.delete(order_to_delete)
    
    session.commit()    
    
    return order_to_delete