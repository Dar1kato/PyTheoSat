import random
import fitz
import asyncio
from tqdm import tqdm
from PIL import Image
import pytesseract
import os
from agents import Agent, Runner, SQLiteSession
from dotenv import load_dotenv

# Cargar la API KEY de OPENAI
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise ValueError("No se encontró OPENAI_API_KEY en el archivo .env")

# Porcentaje de selección de documentos
SELECTION_RATE: float = 0.5

# Prompt inicial del agente
PROMPT: str = """
Rol:
Eres un experto en investigación cualitativa que estudia los daños y necesidades de la población posterior a sismos mediante el método de saturación teórica. 

Objetivo:
Tu tarea es analizar una serie de textos sobre sismos en Puebla Capital utilizando el método cualitativo de saturación teórica y tu conocimiento acerca de las necesidades informativas y de comunicación que una población pueda generar posteriormente a estos eventos.

Instrucciones de análisis:
1. Mediante de método de saturación teórica elige un texto  y utiliza como categorías semilla: “Necesidades de información” y “Necesidades de comunicación”
2. En cada texto que elijas, identifica las frases clave o un dato que impliquen una necesidad informativa, una necesidad de comunicación o de relevancia que ayuden a mantener informada y comunicada a la población mediante un sistema de información offline posterior a eventos sísmicos.
3. Aplica el método de saturación teórica: Cuando se alcance la saturación teórica y los textos ya no arrojen frases, datos o implicaciones nuevas detén el análisis e indica: “Saturación teórica alcanzada en el texto [número total de texto revisados hasta alcanzar la saturación teórica]”.
4. Por cada texto, devuelve el título del documento y genera un listado por texto de las frases o datos encontrados en cada uno y su implicación. Si dos frases implican la misma necesidad agrúpalas.
5. No incluyas citas, subtítulos ni explicaciones adicionales.
"""

# Inicialización del agente y la sesión
agent: Agent = Agent(
    name="Investigador",
    instructions=PROMPT,
    model="gpt-4o"
)
session: SQLiteSession = SQLiteSession("analisis_ASE.db")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extrae texto de un archivo PDF."""
    try:
        doc = fitz.open(pdf_path)
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error al leer PDF {pdf_path}: {e}")
        return ""

def extract_text_from_png(image_path: str) -> str:
    """Extrae texto de una imagen PNG usando OCR."""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang="spa")
        return text.strip()
    except Exception as e:
        print(f"Error al leer PNG {image_path}: {e}")
        return ""

def chunk_text(text: str, max_length: int = 6000) -> list[str]:
    """
    Divide el texto en fragmentos para evitar exceder el límite de contexto del modelo.
    """
    paragraphs = text.split("\n")
    chunks, current_chunk = [], ""

    for p in paragraphs:
        if len(current_chunk) + len(p) < max_length:
            current_chunk += p + "\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = p + "\n"
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

async def process_text(text: str) -> str:
    """Envía texto al agente y devuelve su análisis."""
    chunks = chunk_text(text)
    all_results = []

    for i, chunk in enumerate(chunks):
        try:
            result = await Runner.run(agent, chunk, session=session)
            all_results.append(result.final_output)
        except Exception as e:
            print(f"Error al procesar fragmento {i+1}: {e}")

    return "\n".join(all_results)

async def main() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")

    files = [
        os.path.join(data_dir, f)
        for f in os.listdir(data_dir)
        if f.lower().endswith((".pdf", ".png"))
    ]

    if not files:
        print("No se encontraron archivos en la carpeta 'data'.")
        return

    for file_path in tqdm(files, desc="Procesando archivos", unit="archivo"):
        if random.random() < SELECTION_RATE:
            ext = os.path.splitext(file_path)[1].lower()
            text = ""

            if ext == ".pdf":
                text = extract_text_from_pdf(file_path)
            elif ext == ".png":
                text = extract_text_from_png(file_path)

            if not text:
                continue

            result = await process_text(text)

            with open("results.txt", "a", encoding="utf-8") as f:
                f.write(f"Documento: {os.path.basename(file_path)}\n")
                f.write(f"{result}\n\n")

    print("\n Análisis completado. Resultados guardados en 'results.txt'.")

if __name__ == "__main__":
    asyncio.run(main())
