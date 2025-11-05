# PyTheoSat

## Descripción
PyTheoSat es un script que aplíca el método de saturación teorica a un conjunto de documentos,
(PDF o PNG), utilizando un agente de OpenAI. El objetivo es recuperar las frases principales
de los documentos que sean referentes a un tema específico (En este caso, la falta de información
y comunicación en Puebla Capital después de eventos sísmicos).

## Características
- **Análisis Cualitativo Automatizado**: Implementa saturación teórica con IA
- **Procesamiento Multi-formato**: Soporta PDF y PNG (con OCR)
- **Selección Aleatoria**: Procesa un porcentaje configurable de documentos
- **Chunking Inteligente**: Divide textos largos automáticamente
- **Persistencia**: Guarda sesiones en SQLite para seguimiento
- **Barra de Progreso**: Visualización en tiempo real del procesamiento

## Uso
1. Instalar las dependencias.
```commandline
pip install -r requirements.txt
```

2. Configurar la variable de entorno con tu API KEY de OpenAI (ver .env.example).

3. Configura el script.
```python
SELECTION_RATE: float = 0.5 # Probabilidad de analizar un documento (0.0 - 1.0)
```

4. Introducir los documentos a analizar en la carpeta "/data".
5. Ejecutar el script.
```commandline
python3 main.py
```