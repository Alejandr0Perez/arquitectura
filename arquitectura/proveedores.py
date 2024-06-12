from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.arquitectura

# Modelos de datos
class Producto(BaseModel):
    nombre: str
    descripcion: str
    precio_unitario: float
    cantidad_disponible: int

class Proveedor(BaseModel):
    nombre: str
    direccion: str
    telefono: str
    email: str
    productos: List[Producto]

class ProveedorOut(Proveedor):
    idProveedor: str

# Operaciones expuestas
@app.post("/proveedores/", response_model=ProveedorOut)
async def agregar_proveedor(proveedor: Proveedor):
    nuevo_proveedor = await db.proveedores.insert_one(proveedor.dict())
    proveedor_guardado = await db.proveedores.find_one({"_id": nuevo_proveedor.inserted_id})
    return {**proveedor_guardado, "idProveedor": str(proveedor_guardado["_id"])}

@app.put("/proveedores/{idProveedor}", response_model=ProveedorOut)
async def actualizar_proveedor(idProveedor: str, proveedor: Proveedor):
    proveedor_obj_id = ObjectId(idProveedor)
    result = await db.proveedores.update_one({"_id": proveedor_obj_id}, {"$set": proveedor.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    proveedor_actualizado = await db.proveedores.find_one({"_id": proveedor_obj_id})
    return {**proveedor_actualizado, "idProveedor": str(proveedor_actualizado["_id"])}

@app.delete("/proveedores/{idProveedor}", response_model=dict)
async def eliminar_proveedor(idProveedor: str):
    proveedor_obj_id = ObjectId(idProveedor)
    result = await db.proveedores.delete_one({"_id": proveedor_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {"estatus": "Éxito", "mensaje": "Proveedor eliminado correctamente"}

@app.get("/proveedores/{idProveedor}", response_model=ProveedorOut)
async def consultar_proveedor_por_id(idProveedor: str):
    proveedor_obj_id = ObjectId(idProveedor)
    proveedor = await db.proveedores.find_one({"_id": proveedor_obj_id})
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return {**proveedor, "idProveedor": str(proveedor["_id"])}

@app.get("/proveedores/producto/{nombreProducto}", response_model=List[ProveedorOut])
async def consultar_proveedores_por_producto(nombreProducto: str):
    proveedores = await db.proveedores.find({"productos.nombre": nombreProducto}).to_list(100)
    return [{**proveedor, "idProveedor": str(proveedor["_id"])} for proveedor in proveedores]

