from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

app = FastAPI()

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.arquitectura

# Modelos de datos
class Pedido(BaseModel):
    proyecto_id: str
    proveedor_id: str
    material_id: str
    cantidad: int
    fecha_pedido: str
    estatus: str

class PedidoOut(Pedido):
    idPedido: str

# Operaciones expuestas
@app.post("/pedidos/", response_model=PedidoOut)
async def agregar_pedido(pedido: Pedido):
    nuevo_pedido = await db.pedidos.insert_one(pedido.dict())
    pedido_guardado = await db.pedidos.find_one({"_id": nuevo_pedido.inserted_id})
    return {**pedido_guardado, "idPedido": str(pedido_guardado["_id"])}

@app.put("/pedidos/{idPedido}", response_model=PedidoOut)
async def actualizar_pedido(idPedido: str, pedido: Pedido):
    pedido_obj_id = ObjectId(idPedido)
    result = await db.pedidos.update_one({"_id": pedido_obj_id}, {"$set": pedido.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    pedido_actualizado = await db.pedidos.find_one({"_id": pedido_obj_id})
    return {**pedido_actualizado, "idPedido": str(pedido_actualizado["_id"])}

@app.delete("/pedidos/{idPedido}", response_model=dict)
async def eliminar_pedido(idPedido: str):
    pedido_obj_id = ObjectId(idPedido)
    result = await db.pedidos.delete_one({"_id": pedido_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {"estatus": "Éxito", "mensaje": "Pedido eliminado correctamente"}

@app.get("/pedidos/{idPedido}", response_model=PedidoOut)
async def consultar_pedido_por_id(idPedido: str):
    pedido_obj_id = ObjectId(idPedido)
    pedido = await db.pedidos.find_one({"_id": pedido_obj_id})
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {**pedido, "idPedido": str(pedido["_id"])}

@app.get("/pedidos/proyecto/{idProyecto}", response_model=List[PedidoOut])
async def consultar_pedidos_por_proyecto(idProyecto: str):
    pedidos = await db.pedidos.find({"proyecto_id": idProyecto}).to_list(100)
    return [{**pedido, "idPedido": str(pedido["_id"])} for pedido in pedidos]

@app.get("/pedidos/proveedor/{idProveedor}", response_model=List[PedidoOut])
async def consultar_pedidos_por_proveedor(idProveedor: str):
    pedidos = await db.pedidos.find({"proveedor_id": idProveedor}).to_list(100)
    return [{**pedido, "idPedido": str(pedido["_id"])} for pedido in pedidos]

