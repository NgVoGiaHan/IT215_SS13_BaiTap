from fastapi import FastAPI,HTTPException,status,Depends,Response
from pydantic import BaseModel,Field
from sqlalchemy.orm import Session
from database import engine, get_db
from datetime import datetime,timezone
from enum import Enum

import model

app=FastAPI()

model.Base.metadata.create_all(bind=engine)
class RoomsizeEnum(str,Enum):
    SMALL="SMALL"
    MEDIUM="MEDIUM"
    LARGE="LARGE"
    
class StatusEnum(str,Enum):
    VACANT="VACANT"
    OCCUPIED="OCCUPIED"

class CreateSlot(BaseModel):
    slot_number :str
    room_size :RoomsizeEnum
    price_per_day :float=Field(...,gt=0)
    status :StatusEnum

@app.get("/boarding-slots")
def get_all_boarding_slots(db:Session=Depends(get_db)):
    boarding_slots=db.query(model.BoardingSlot).all()
    if not boarding_slots:
        return{
            "statusCode":200,
            "message":"Danh sách khoang lưu trú rỗng",
            "error": None,
            "data":[],
            "path":"/boarding-slots",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    return{
        "statusCode":200,
        "message":"Lấy danh sách thành công",
        "error": None,
        "data":boarding_slots,
        "path":"/boarding-slots",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    
@app.get("/boarding-slots/{slot_id}")
def get_boarding_slot(slot_id:int,response:Response,db:Session=Depends(get_db)):
    boarding_slot=db.query(model.BoardingSlot).filter(model.BoardingSlot.id==slot_id).first()
    if not boarding_slot:
        response.status_code=status.HTTP_404_NOT_FOUND
        return{
            "statusCode":404,
            "message":"ID không tồn tại",
            "error":"NOT FOUND",
            "data":None,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    
    return{
        "statusCode":200,
        "message":"Lấy chi tiết thông tin một khoang lưu trú thành công",
        "error":None,
        "data":boarding_slot,
        "path":f"/boarding-slots/{slot_id}",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    
@app.post("/boarding-slots")
def create_slot(payload:CreateSlot,response:Response,db:Session=Depends(get_db)):
    duplication_check=db.query(model.BoardingSlot).filter(model.BoardingSlot.slot_number == payload.slot_number ).first()
    if duplication_check:
        response.status_code=status.HTTP_400_BAD_REQUEST
        return{
            "statusCode":400,
            "message":"Slot number already exists",
            "error":"Bad Request",
            "data":None,
            "path":"/boarding-slots",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    new_boarding=model.BoardingSlot(**payload.model_dump())
    
    try:
        db.add(new_boarding)
        db.commit()
        db.refresh(new_boarding)
        response.status_code=status.HTTP_201_CREATED
        return{
            "statusCode":201,
            "message":"Thêm khoang trú mới thành công",
            "error":None,
            "data":new_boarding,
            "path":"/boarding-slots",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    except Exception as e:
        db.rollback() 
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return{
            "statusCode":500,
            "message":"Thất bại",
            "error":"Lỗi hệ thống thêm không thành công",
            "data":None,
            "path":"/boarding-slots",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        

@app.put("/boarding-slots/{slot_id}")
def update_boarding(slot_id:int,payload:CreateSlot,response:Response,db:Session=Depends(get_db)):
    boarding=db.query(model.BoardingSlot).filter(model.BoardingSlot.id==slot_id).first()
    if not boarding:
        response.status_code=status.HTTP_404_NOT_FOUND
        return{
            "statusCode":404,
            "message":"ID không tồn tại",
            "error":"NOT FOUND",
            "data":None,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    duplication_check = db.query(model.BoardingSlot).filter(
        model.BoardingSlot.slot_number == payload.slot_number,
        model.BoardingSlot.id != slot_id  
    ).first()
    
    if duplication_check:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "statusCode": 400,
            "message": "Slot number already exists",
            "error": "Bad Request",
            "data": None,
            "path": f"/boarding-slots/{slot_id}", 
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    try:
        update_data=payload.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(boarding,key,value)
        db.commit()
        db.refresh(boarding)
        response.status_code=status.HTTP_200_OK
        return{
            "statusCode":200,
            "message":"Cập nhật thông tin thành công",
            "error":None,
            "data":boarding,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    except Exception:
        db.rollback()
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return{
            "statusCode":500,
            "message":"Lỗi hệ thống",
            "error":"INTERNAL_SERVER_ERROR",
            "data":None,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
@app.delete("/boarding-slots/{slot_id}")
def delete_slot(slot_id:int,response:Response,db:Session=Depends(get_db)):
    id_slot=db.query(model.BoardingSlot).filter(model.BoardingSlot.id==slot_id).first()
    if not id_slot:
        response.status_code=status.HTTP_404_NOT_FOUND
        return{
            "statusCode":404,
            "message":"ID không tồn tại",
            "error":"NOT FOUND",
            "data":None,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
    try:
        db.delete(id_slot)
        db.commit()
        response.status_code=status.HTTP_200_OK
        return{
            "statusCode":200,
            "message":"Xóa thông tin thành công",
            "error":None,
            "data":None,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    except Exception:
        db.rollback()
        response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        return{
            "statusCode":500,
            "message":"Lỗi hệ thống",
            "error":"INTERNAL_SERVER_ERROR",
            "data":None,
            "path":f"/boarding-slots/{slot_id}",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        
