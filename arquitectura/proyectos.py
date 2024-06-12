from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

app = FastAPI()

# Conexión a MongoDB
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.arquitectura

# Modelos de datos
class Proyecto(BaseModel):
    nombre: str
    descripcion: str
    fecha_inicio: str
    fecha_fin: str
    estado: str
    responsable: str

class ProyectoOut(Proyecto):
    idProyecto: str

# Operaciones expuestas
@app.post("/proyectos/", response_model=ProyectoOut)
async def agregar_proyecto(proyecto: Proyecto):
    nuevo_proyecto = await db.proyectos.insert_one(proyecto.dict())
    proyecto_guardado = await db.proyectos.find_one({"_id": nuevo_proyecto.inserted_id})
    return {**proyecto_guardado, "idProyecto": str(proyecto_guardado["_id"])}

@app.put("/proyectos/{idProyecto}", response_model=ProyectoOut)
async def actualizar_proyecto(idProyecto: str, proyecto: Proyecto):
    proyecto_obj_id = ObjectId(idProyecto)
    result = await db.proyectos.update_one({"_id": proyecto_obj_id}, {"$set": proyecto.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    proyecto_actualizado = await db.proyectos.find_one({"_id": proyecto_obj_id})
    return {**proyecto_actualizado, "idProyecto": str(proyecto_actualizado["_id"])}

@app.delete("/proyectos/{idProyecto}", response_model=dict)
async def eliminar_proyecto(idProyecto: str):
    proyecto_obj_id = ObjectId(idProyecto)
    result = await db.proyectos.delete_one({"_id": proyecto_obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {"estatus": "Éxito", "mensaje": "Proyecto eliminado correctamente"}

@app.get("/proyectos/{idProyecto}", response_model=ProyectoOut)
async def consultar_proyecto_por_id(idProyecto: str):
    proyecto_obj_id = ObjectId(idProyecto)
    proyecto = await db.proyectos.find_one({"_id": proyecto_obj_id})
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return {**proyecto, "idProyecto": str(proyecto["_id"])}

@app.get("/proyectos/estado/{estado}", response_model=List[ProyectoOut])
async def consultar_proyectos_por_estado(estado: str):
    proyectos = await db.proyectos.find({"estado": estado}).to_list(100)
    return [{**proyecto, "idProyecto": str(proyecto["_id"])} for proyecto in proyectos]

@app.get("/proyectos/responsable/{responsable}", response_model=List[ProyectoOut])
async def consultar_proyectos_por_responsable(responsable: str):
    proyectos = await db.proyectos.find({"responsable": responsable}).to_list(100)
    return [{**proyecto, "idProyecto": str(proyecto["_id"])} for proyecto in proyectos]

