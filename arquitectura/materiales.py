from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.arquitectura

# Modelos de datos
class Material(BaseModel):
    nombre: str
    descripcion: str
    cantidad: int
    unidad_medida: str
    precio_unitario: float

class MaterialOut(Material):
    idMaterial: str

# Operaciones expuestas
@app.post("/materiales/", response_model=MaterialOut)
async def agregar_material(material: Material):
    nuevo_material = await db.materiales.insert_one(material.dict())
    material_guardado = await db.materiales.find_one({"_id": nuevo_material.inserted_id})
    return {**material_guardado, "idMaterial": str(material_guardado["_id"])}

@app.put("/materiales/{idMaterial}", response_model=MaterialOut)
async def actualizar_material(idMaterial: str, material: Material):
    material_obj_id = ObjectId(idMaterial)
    result = await db.materiales.update_one({"_id": material_obj_id}, {"$set": material.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    material_actualizado = await db.materiales.find_one({"_id": material_obj_id})
    return {**material_actualizado, "idMaterial": str(material_actualizado["_id"])}

@app.delete("/materiales/{idMaterial}", response_model=dict)
async def eliminar_material(idMaterial: str):
    material_obj_id = ObjectId(idMaterial)
    result = await db.materiales.delete_one({"_id": material_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return {"estatus": "Éxito", "mensaje": "Material eliminado correctamente"}

@app.get("/materiales/{idMaterial}", response_model=MaterialOut)
async def consultar_material_por_id(idMaterial: str):
    material_obj_id = ObjectId(idMaterial)
    material = await db.materiales.find_one({"_id": material_obj_id})
    if not material:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return {**material, "idMaterial": str(material["_id"])}

@app.get("/materiales/categoria/{categoria}", response_model=List[MaterialOut])
async def consultar_materiales_por_categoria(categoria: str):
    materiales = await db.materiales.find({"categoria": categoria}).to_list(100)
    return [{**material, "idMaterial": str(material["_id"])} for material in materiales]


