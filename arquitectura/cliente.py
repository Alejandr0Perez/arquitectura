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
class Cliente(BaseModel):
    nombre: str
    apellido: str
    email: str
    telefono: str
    direccion: str

class ClienteOut(Cliente):
    idCliente: str

# Operaciones expuestas
@app.post("/clientes/", response_model=ClienteOut)
async def agregar_cliente(cliente: Cliente):
    nuevo_cliente = await db.clientes.insert_one(cliente.dict())
    cliente_guardado = await db.clientes.find_one({"_id": nuevo_cliente.inserted_id})
    return {**cliente_guardado, "idCliente": str(cliente_guardado["_id"])}

@app.put("/clientes/{idCliente}", response_model=ClienteOut)
async def actualizar_cliente(idCliente: str, cliente: Cliente):
    cliente_obj_id = ObjectId(idCliente)
    result = await db.clientes.update_one({"_id": cliente_obj_id}, {"$set": cliente.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    cliente_actualizado = await db.clientes.find_one({"_id": cliente_obj_id})
    return {**cliente_actualizado, "idCliente": str(cliente_actualizado["_id"])}

@app.delete("/clientes/{idCliente}", response_model=dict)
async def eliminar_cliente(idCliente: str):
    cliente_obj_id = ObjectId(idCliente)
    result = await db.clientes.delete_one({"_id": cliente_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"estatus": "Éxito", "mensaje": "Cliente eliminado correctamente"}

@app.get("/clientes/{idCliente}", response_model=ClienteOut)
async def consultar_cliente_por_id(idCliente: str):
    cliente_obj_id = ObjectId(idCliente)
    cliente = await db.clientes.find_one({"_id": cliente_obj_id})
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {**cliente, "idCliente": str(cliente["_id"])}

@app.get("/clientes/proyecto/{idProyecto}", response_model=List[ClienteOut])
async def consultar_clientes_por_proyecto(idProyecto: str):
    clientes = await db.clientes.find({"proyectos": idProyecto}).to_list(100)
    return [{**cliente, "idCliente": str(cliente["_id"])} for cliente in clientes]


