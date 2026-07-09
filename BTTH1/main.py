from fastapi import FastAPI,HTTPException,Response,Depends,status
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from database import engine,get_db
from datetime import datetime
from enum import Enum
import model


app=FastAPI()

model.Base.metadata.create_all(bind=engine)
class StatusItems(str,Enum):
    AVAILABLE="AVAILABLE"
    OUT_OF_STOCK="OUT_OF_STOCK"

class CreateItems(BaseModel):
    dish_code:str
    dish_name:str
    calorie_count:int=Field(...,gt=0)
    price:float=Field(...,gt=0)
    status:StatusItems |None="AVAILABLE"
    

@app.get("/menu-items")
def get_all_menu_items(db:Session=Depends(get_db)):
    menu_items=db.query(model.MenuItem).all()
    if not menu_items:
        return{
            "statusCode": 200,
            "message": "Danh sách rỗng!",
            "error": None,
            "data": [],
            "path": "/menu-items",
            "timestamp": datetime.now().isoformat()
        }
        
    return{
        "statusCode": 200,
        "message": "Lấy danh sách món ăn thành công",
        "error": None,
        "data": menu_items,
        "path": "/menu-items",
        "timestamp": datetime.now().isoformat()
    }
    
@app.get("/menu-items/{item_id}")
def get_item(item_id:int,response:Response,db:Session=Depends(get_db)):
    item=db.query(model.MenuItem).filter(model.MenuItem.id==item_id).first()
    if not item:
        response.status_code=status.HTTP_404_NOT_FOUND
        return{
            "statusCode": 404,
            "message": "Menu item not found",
            "error": "Not Found",
            "data": None,
            "path": f"/menu-items/{item_id}",
            "timestamp": datetime.now().isoformat()
        }
        
    return{
        "statusCode": 200,
        "message": "Lấy thông tin chi tiết món ăn thành công",
        "error": None,
        "data": item,
        "path": f"/menu-items/{item_id}",
        "timestamp": datetime.now().isoformat()
    }
    
    
@app.post("/menu-items")
def create_item(response:Response,payload:CreateItems,db:Session=Depends(get_db)):
    duplicate_item=db.query(model.MenuItem).filter(model.MenuItem.dish_code == payload.dish_code ).first()
    if duplicate_item:
        response.status_code=status.HTTP_400_BAD_REQUEST
        return{
            "statusCode":400,
            "message":"Mã món ăn không được trùng",
            "error":"DO NOT DUPLICATE",
            "data":None,
            "path":"/menu-items",
            "timestamp": datetime.now().isoformat()
        }
    
    new_item=model.MenuItem(**payload.model_dump())
    try:
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return{
            "statusCode":201,
            "message":"Thêm món ăn thành công",
            "error":None,
            "data":new_item,
            "path":"/menu-items",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        db.rollback()
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return {
            "statusCode": 500,
            "message": "Lỗi hệ thống khi thêm món ăn",
            "error": str(e),
            "data": None,
            "path": "/menu-items",
            "timestamp": datetime.now().isoformat()
        }
        
        
@app.put("/menu-items/{item_id}")
def update_item(item_id:int,response:Response,payload:CreateItems,db:Session=Depends(get_db)):
    item=db.query(model.MenuItem).filter(model.MenuItem.id==item_id).first()
    if not item:
        response.status_code=status.HTTP_404_NOT_FOUND
        return{
            "statusCode":404,
            "message": "Menu item not found",
            "error": "Not Found",
            "data": None,
            "path":f"/menu-items/{item_id}",
            "timestamp":datetime.now().isoformat()
        }
            
    try:
        update_data = payload.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(item, key, value)
        db.commit()
        db.refresh(item)
        return{
            "statusCode":200,
            "message":"Cập nhật món ăn thành công",
            "error":None,
            "data":item,
            "path":f"/menu-items/{item_id}",
            "timestamp":datetime.now().isoformat()
        }
    except Exception as e:
        db.rollback()
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return{
            "statusCode":500,
            "message":"Lỗi hệ thống khi cập nhật món ăn",
            "error": str(e),
            "data": None,
            "path": f"/menu-items/{item_id}",
            "timestamp": datetime.now().isoformat()
        }
    

@app.delete("/menu-items/{item_id}")
def delete_item(item_id:int,response:Response,db:Session=Depends(get_db)):
    item=db.query(model.MenuItem).filter(model.MenuItem.id==item_id).first()
    if not item:
        response.status_code=status.HTTP_404_NOT_FOUND
        return{
            "statusCode":404,
            "message": "Menu item not found",
            "error": "Not Found",
            "data": None,
            "path":f"/menu-items/{item_id}",
            "timestamp":datetime.now().isoformat()
        }
    
    
    try:
        db.delete(item)
        db.commit()
        return{
            "statusCode":200,
            "message":"Xóa món ăn thành công",
            "error":None,
            "data":None,
            "path":f"/menu-items/{item_id}",
            "timestamp":datetime.now().isoformat()
        }
    except Exception as e:
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        db.rollback()
        return{
            "statusCode":500,
            "message":"Lỗi hệ thống khi cập nhật món ăn",
            "error": str(e),
            "data": None,
            "path": f"/menu-items/{item_id}",
            "timestamp": datetime.now().isoformat()
        }