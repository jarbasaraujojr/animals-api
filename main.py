import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # pode ser anon (publishable) ou service_role (apenas no backend)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Defina SUPABASE_URL e SUPABASE_KEY nas variáveis de ambiente.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Kaniu API (Supabase)")

# CORS: se o site acessar via /api (proxy do nginx), nem precisa; mas manter não atrapalha
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # opcional: restrinja ao domínio do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------- utilidades ---------
def _ok(data: Any):
    return data

def _items(rows: List[Dict]):
    return {"items": rows}

def _alias_animal(row: Dict) -> Dict:
    """
    Normaliza as chaves que o front espera.
    Supabase pode retornar, por ex., 'profile_picture_url'; o front usa 'picture_url'.
    """
    if not row:
        return row
    # Cria um clone e aplica aliases
    out = dict(row)
    # aliases
    if "profile_picture_url" in row and "picture_url" not in row:
        out["picture_url"] = row["profile_picture_url"]
    if "shelter_name" in row and "shelter" not in row:
        out["shelter"] = row["shelter_name"]
    if "nome" in row and "name" not in row:
        out["name"] = row["nome"]
    if "raça" in row and "breed" not in row:
        out["breed"] = row["raça"]
    if "faixa_etaria" in row and "age_range" not in row:
        out["age_range"] = row["faixa_etaria"]
    if "foto" in row and "picture_url" not in row:
        out["picture_url"] = row["foto"]
    if "sexo" in row and "sex" not in row:
        out["sex"] = row["sexo"]
    if "porte" in row and "size" not in row:
        out["size"] = row["porte"]
    if "especie" in row and "species" not in row:
        out["species"] = row["especie"]
    return out


# --------- raiz ---------
@app.get("/")
def root():
    return {"status": "ok", "message": "API Kaniu conectada ao Supabase"}


# --------- listagem ---------
@app.get("/animals")
def get_animals():
    """
    Retorna até 100 animais para os cards da listagem.
    Requer uma view/tabela legível pelo anon: 'animals_view'.
    """
    try:
        # selecione somente colunas que o front usa para os cards
        sel = (
            "id, name, nome, species, especie, breed, raça, size, porte, sex, sexo, "
            "age_range, faixa_etaria, profile_picture_url, foto, shelter_name"
        )
        resp = supabase.table("animals_view").select(sel).order("name", desc=False).limit(100).execute()
        rows = resp.data or []

        # normaliza chaves
        normalized = [_alias_animal(r) for r in rows]
        return {"animals": normalized}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/animals: {e}")


# --------- detalhe ---------
@app.get("/animals/{animal_id}")
def get_animal(animal_id: str):
    """
    Detalhes de um animal para a página lateral (foto, espécie, raça, etc.).
    """
    try:
        sel = "*"
        resp = supabase.table("animals_view").select(sel).eq("id", animal_id).single().execute()
        if not resp.data:
            raise HTTPException(status_code=404, detail="Animal não encontrado")

        return _alias_animal(resp.data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"/animals/{animal_id}: {e}")


# --------- abas: resumo ---------
@app.get("/animals/{animal_id}/resumo")
def get_resumo(animal_id: str):
    """
    Resumo: crie uma view/materialized view com os campos consolidados
    ex: 'animal_resumo_view': (animal_id, ultima_avaliacao, score, peso, proxima_vacinacao, ultima_vermifugacao, ...)
    """
    try:
        resp = supabase.table("animal_resumo_view").select("*").eq("animal_id", animal_id).limit(1).execute()
        rows = resp.data or []
        # front espera um objeto simples; se vier vazio, devolve {}
        return rows[0] if rows else {}
    except Exception as e:
        # Se a view ainda não existir, devolve objeto vazio (não quebra o front)
        return {}


# --------- abas: eventos ---------
@app.get("/animals/{animal_id}/eventos")
def get_eventos(animal_id: str):
    try:
        resp = (
            supabase.table("animal_eventos_view")
            .select("data, tipo, descricao, veterinario_nome")
            .eq("animal_id", animal_id)
            .order("data", desc=True)
            .execute()
        )
        return _items(resp.data or [])
    except Exception:
        return _items([])


# --------- abas: avaliacoes ---------
@app.get("/animals/{animal_id}/avaliacoes")
def get_avaliacoes(animal_id: str):
    try:
        resp = (
            supabase.table("animal_avaliacoes_view")
            .select("data, observacao, veterinario_nome, temperatura, score, peso, nota")
            .eq("animal_id", animal_id)
            .order("data", desc=True)
            .execute()
        )
        return _items(resp.data or [])
    except Exception:
        return _items([])


# --------- abas: pesagens ---------
@app.get("/animals/{animal_id}/pesagens")
def get_pesagens(animal_id: str):
    try:
        resp = (
            supabase.table("animal_pesagens_view")
            .select("id, data, peso, variacao")
            .eq("animal_id", animal_id)
            .order("data", desc=True)
            .execute()
        )
        return _items(resp.data or [])
    except Exception:
        return _items([])


# --------- abas: imunizacoes ---------
@app.get("/animals/{animal_id}/imunizacoes")
def get_imunizacoes(animal_id: str):
    try:
        resp = (
            supabase.table("animal_imunizacoes_view")
            .select("data_exibicao, tipo, nome_imunizante, veterinario_nome, aplicada")
            .eq("animal_id", animal_id)
            .order("data_exibicao", desc=True)
            .execute()
        )
        return _items(resp.data or [])
    except Exception:
        return _items([])


# --------- abas: tratamentos ---------
@app.get("/animals/{animal_id}/tratamentos")
def get_tratamentos(animal_id: str):
    try:
        resp = (
            supabase.table("animal_tratamentos_view")
            .select("data, veterinario_nome, medicamentos, finalizada")
            .eq("animal_id", animal_id)
            .order("data", desc=True)
            .execute()
        )
        return _items(resp.data or [])
    except Exception:
        return _items([])


# --------- abas: arquivos ---------
@app.get("/animals/{animal_id}/arquivos")
def get_arquivos(animal_id: str):
    try:
        resp = (
            supabase.table("animal_arquivos_view")
            .select("data, nome, observacao, url")
            .eq("animal_id", animal_id)
            .order("data", desc=True)
            .execute()
        )
        return _items(resp.data or [])
    except Exception:
        return _items([])
