import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from supabase import create_client

# Carrega variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis SUPABASE_URL e SUPABASE_KEY não estão definidas")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "API conectada ao Supabase com sucesso!"}

@app.get("/animals")
def get_animals():
    try:
        response = supabase.table("animals_view").select("*").limit(100).execute()
        return {"animals": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/animals/{animal_id}")
def get_animal(animal_id: str):
    try:
        response = supabase.table("animals_view").select("*").eq("id", animal_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Animal não encontrado")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints adicionais para tabs (exemplo: resumo, saúde, etc.)
@app.get("/animals/{animal_id}/resumo")
def get_animal_resumo(animal_id: str):
    try:
        response = supabase.table("animals_view").select("id,name,species,breed,size,sex,age_range,shelter_name").eq("id", animal_id).single().execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Animal não encontrado")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
