from llama_cpp import Llama

# Ruta del modelo (ajustada a tu estructura real)
MODEL = "/home/pi/Documents/kg-llm/modelos/qwen2.5-0.5b.gguf"

llm = Llama(
    model_path=MODEL,
    n_ctx=2048,
    n_threads=4,
)

response = llm(
    "Hola, estoy corriendo en una Raspberry Pi 5. ¿Qué puedes hacer?",
    max_tokens=100,
    temperature=0.7,
)

print(response["choices"][0]["text"].strip())

