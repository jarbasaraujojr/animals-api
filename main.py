import os
import psycopg2
from dotenv import load_dotenv
from fastapi import FastAPI

# Carregue as variáveis de ambiente do arquivo .env
load_dotenv()

# Inicialize o FastAPI
app = FastAPI()

# Obtenha a URL do banco de dados das variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")

# Verifique se a variável de ambiente está carregada
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

@app.get("/animals")
def get_animals():
    try:
        # Estabeleça a conexão com o banco de dados
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        # Execute a consulta SQL para buscar todos os animais
        cur.execute("SELECT name, species FROM animals")
        animals = cur.fetchall()

        # Feche o cursor e a conexão
        cur.close()
        conn.close()

        # Transforme o resultado em uma lista de dicionários
        animal_list = []
        for animal in animals:
            animal_list.append({"name": animal[0], "species": animal[1]})

        return {"animals": animal_list}
    except Exception as e:
        return {"error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Animal API!"}