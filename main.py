import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client

# Carrega variáveis de ambiente
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Kaniu API", version="1.0")


# =========================
# LISTAGEM DE ANIMAIS
# =========================
@app.get("/api/animals")
def list_animals():
    response = supabase.table("animals") \
        .select("id, name, profile_picture_url, birth_date, species_id, gender_id, size_id, breed_id, deceased, castrated, adopted, hospitalized, missing") \
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Nenhum animal encontrado")

    return response.data


# =========================
# DETALHES DO ANIMAL
# =========================
@app.get("/api/animals/{animal_id}")
def get_animal(animal_id: str):
    response = supabase.table("animals") \
        .select("id, name, description, profile_picture_url, birth_date, species_id, gender_id, size_id, breed_id, castrated, adopted, hospitalized, deceased") \
        .eq("id", animal_id) \
        .single() \
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    return response.data


# =========================
# RESUMO DO ANIMAL
# =========================
@app.get("/api/animals/{animal_id}/resumo")
def resumo_animal(animal_id: str):
    # Exemplo: pega a última pesagem e vacinação
    pesagem = supabase.table("animal_weights") \
        .select("date_time, value") \
        .eq("animal_id", animal_id) \
        .order("date_time", desc=True) \
        .limit(1) \
        .execute()

    vacinacao = supabase.table("imunizacoes") \
        .select("*") \
        .eq("animal_id", animal_id) \
        .order("data_exibicao", desc=True) \
        .limit(1) \
        .execute()

    return {
        "ultimo_peso": pesagem.data[0] if pesagem.data else None,
        "ultima_vacinacao": vacinacao.data[0] if vacinacao.data else None
    }
