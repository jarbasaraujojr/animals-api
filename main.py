import os
from fastapi import FastAPI, HTTPException
from supabase import create_client, Client

# =========================
# CONFIGURAÇÃO SUPABASE
# =========================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="Kaniu API", version="1.0")


# =========================
# LISTAGEM DE ANIMAIS
# =========================
@app.get("/api/animais")
def listar_animais():
    """
    Retorna a lista básica de animais para exibição em cards ou listagens.
    """
    response = supabase.table("animais") \
        .select(
            "animal_id, nome, foto, nascimento, especie, genero, porte, raça, "
            "falecido, castrado, adotado, internado, desaparecido"
        ) \
        .order("nome") \
        .execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Nenhum animal encontrado")

    return response.data


# =========================
# DETALHES DO ANIMAL
# =========================
@app.get("/api/animais/{animal_id}")
def detalhes_animal(animal_id: str):
    """
    Retorna os detalhes completos de um animal específico.
    """
    # Tabela principal
    dados_principais = supabase.table("animais") \
        .select(
            "animal_id, nome, nascimento, especie, genero, porte, raça, cor, pelagem, "
            "falecido, castrado, desaparecido, vacinado, vermifugado, desparasitado, "
            "peso, comprimento, altura, torax, pescoço, faixaetaria, foto, adotado, internado"
        ) \
        .eq("animal_id", animal_id) \
        .single() \
        .execute()

    if not dados_principais.data:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    # Descrição (tabela separada)
    descricao = supabase.table("animais_descricao") \
        .select("descricao") \
        .eq("animal", animal_id) \
        .single() \
        .execute()

    resultado = dados_principais.data
    resultado["descricao"] = descricao.data["descricao"] if descricao.data else None

    return resultado


# =========================
# RESUMO DO ANIMAL
# =========================
@app.get("/api/animais/{animal_id}/resumo")
def resumo_animal(animal_id: str):
    """
    Retorna dados resumidos do animal — última pesagem, última vacinação, etc.
    """

    # Última pesagem
    pesagem = supabase.table("pesagens") \
        .select("data, peso") \
        .eq("animal", animal_id) \
        .order("data", desc=True) \
        .limit(1) \
        .execute()

    # Última imunização
    imunizacao = supabase.table("imunizacao") \
        .select("id, tipo, criacao, observacao") \
        .eq("animal", animal_id) \
        .order("criacao", desc=True) \
        .limit(1) \
        .execute()

    return {
        "ultima_pesagem": pesagem.data[0] if pesagem.data else None,
        "ultima_imunizacao": imunizacao.data[0] if imunizacao.data else None
    }
