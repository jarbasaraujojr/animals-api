from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

# Configurações do banco
DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI()

# Middleware para CORS (permitindo acesso do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pode restringir para seu domínio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# FUNÇÃO AUXILIAR
# =========================
def query_db(query, params=None):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(query, params or ())
        colnames = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
        results = [dict(zip(colnames, row)) for row in rows]
        return results
    except Exception as e:
        return {"error": str(e)}

# =========================
# ENDPOINTS
# =========================

@app.get("/")
def root():
    return {"status": "ok", "message": "API Kaniu rodando 🚀"}

# ---- Listagem de animais ----
@app.get("/animals")
def get_animals():
    query = """
        SELECT id, nome AS name, descricao AS description, foto AS profile_picture_url,
               nascimento AS birth_date, castrado, vacinado, adotado,
               especie, raça AS breed, porte AS size, sexo, cor, pelagem,
               peso AS latest_weight, faixa_etaria AS age_range
        FROM animals_view
        LIMIT 100;
    """
    return query_db(query)

# ---- Detalhes do animal ----
@app.get("/animals/{animal_id}")
def get_animal(animal_id: str):
    query = """
        SELECT id, nome AS name, descricao AS description, foto AS profile_picture_url,
               nascimento AS birth_date, castrado, vacinado, adotado,
               especie, raça AS breed, porte AS size, sexo, cor, pelagem,
               peso AS latest_weight, faixa_etaria AS age_range
        FROM animals_view
        WHERE id = %s;
    """
    results = query_db(query, (animal_id,))
    if isinstance(results, dict) and "error" in results:
        return results
    if not results:
        return {"error": "Animal não encontrado"}
    return results[0]

# ---- Resumo ----
@app.get("/animals/{animal_id}/resumo")
def get_animal_resumo(animal_id: str):
    query = """
        SELECT 
            MAX(av.data) AS ultima_avaliacao,
            MAX(av.score) AS score_corporal,
            MAX(av.nota) AS indice_saude,
            MAX(av.observacao) AS observacoes
        FROM animal_avaliacoes av
        WHERE av.animal_id = %s
    """
    rows = query_db(query, (animal_id,))
    return {"items": rows}

# ---- Eventos ----
@app.get("/animals/{animal_id}/eventos")
def get_animal_eventos(animal_id: str):
    query = """
        SELECT data, tipo, descricao, veterinario_nome
        FROM animal_eventos
        WHERE animal_id = %s
        ORDER BY data DESC
    """
    return {"items": query_db(query, (animal_id,))}

# ---- Avaliações ----
@app.get("/animals/{animal_id}/avaliacoes")
def get_animal_avaliacoes(animal_id: str):
    query = """
        SELECT data, observacao, veterinario_nome, temperatura, score, peso, nota
        FROM animal_avaliacoes
        WHERE animal_id = %s
        ORDER BY data DESC
    """
    return {"items": query_db(query, (animal_id,))}

# ---- Pesagens ----
@app.get("/animals/{animal_id}/pesagens")
def get_animal_pesagens(animal_id: str):
    query = """
        SELECT id, data, peso
        FROM animal_pesagens
        WHERE animal_id = %s
        ORDER BY data DESC
    """
    return {"items": query_db(query, (animal_id,))}

# ---- Imunizações ----
@app.get("/animals/{animal_id}/imunizacoes")
def get_animal_imunizacoes(animal_id: str):
    query = """
        SELECT data_exibicao, tipo, nome_imunizante, veterinario_nome, aplicada
        FROM animal_imunizacoes
        WHERE animal_id = %s
        ORDER BY data_exibicao DESC
    """
    return {"items": query_db(query, (animal_id,))}

# ---- Tratamentos ----
@app.get("/animals/{animal_id}/tratamentos")
def get_animal_tratamentos(animal_id: str):
    query = """
        SELECT data, veterinario_nome, medicamentos, finalizada
        FROM animal_tratamentos
        WHERE animal_id = %s
        ORDER BY data DESC
    """
    return {"items": query_db(query, (animal_id,))}

# ---- Arquivos ----
@app.get("/animals/{animal_id}/arquivos")
def get_animal_arquivos(animal_id: str):
    query = """
        SELECT data, nome, observacao, url
        FROM animal_arquivos
        WHERE animal_id = %s
        ORDER BY data DESC
    """
    return {"items": query_db(query, (animal_id,))}
