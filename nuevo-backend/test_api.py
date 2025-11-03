# test_tools.py
import asyncio
from dotenv import load_dotenv
from fastmcp import FastMCP, Client
from typing import Any, Dict

# carga .env (FIEESOFT_API_BASE_URL, FIEESOFT_USER, FIEESOFT_PASS, etc.)
load_dotenv()

# importamos la función que registra las tools
from fieesoft_tools import register_tools

# 1) Crear servidor FastMCP e instalar las tools
app = FastMCP("Fieesoft Test Server")
register_tools(app)  # registra buscar_bienes, obtener_bien_por_id, ...

# 2) Cliente en memoria apuntando al servidor (muy útil para tests)
client = Client(app)

# Helper para imprimir resultado de forma robusta
def dump_result(name: str, res: Dict[str, Any]):
    print(f"\n>>> Resultado de {name}:")
    if res is None:
        print("  (None)")
        return
    # Si la tool devuelve key 'error' (tu implementación lo hace en fallos)
    if isinstance(res, dict) and "error" in res:
        print("  ❌ Error:", res.get("error"))
        # opcional: raw
        if "raw" in res:
            print("  raw:", res["raw"])
        return
    # Si la tool devuelve estructura Page-like
    if isinstance(res, dict) and "content" in res:
        content = res.get("content", [])
        total = res.get("totalElements", len(content))
        print(f"  ✔ success. totalElements={total}, returned={len(content)}")
        # mostrar hasta 5 items
        for i, item in enumerate(content[:5]):
            print(f"   - [{i}] id={item.get('id', 'n/a')} summary={str(item)[:80]}")
        return
    # si la tool devuelve lista simple o dict detalle
    print("  Raw response:", res)


async def main():
    async with client:
        # descubrir tools (útil para ver los nombres registrados)
        tools = await client.list_tools()
        print("Herramientas disponibles (primeros 20):")
        for t in tools[:20]:
            # tools vienen como objetos; mostramos nombre y descripción si existen
            print(" -", getattr(t, "name", str(t)), "-", getattr(t, "description", ""))

        # Llamada 1: buscar_bienes
        args = {"texto": "osci", "nombreMarca": None, "ubicacion": None, "estado": None, "page": 0, "size": 50}
        print("\nLlamando buscar_bienes with:", args)
        result = await client.call_tool("buscar_bienes", args)
        # FastMCP devuelve un objeto 'result' con .data / .content / .data[0] dependiendo de versión.
        # Para máxima compatibilidad intentamos extraer .data o .content o el propio result.
        # La mayoría de ejemplos muestran result.data o result.content; pero aqui manejamos ambos.
        data = None
        # Preferencia: result.data (si existe), luego result.content, luego result
        if hasattr(result, "data"):
            data = result.data
        elif hasattr(result, "content"):
            data = result.content
        else:
            # algunos clientes empaquetan el JSON directo en result
            try:
                data = result.json()
            except Exception:
                data = result

        # Si data es lista con items/objetos, convertir a dict similar al que tu tool devuelve
        # Muchas implementaciones retornan el JSON tal cual. Si tu buscar_bienes ya devolvió
        # {"content": [...], "number":..., ...} entonces data ya está listo.
        # Normalizamos para dump_result:
        if isinstance(data, list):
            payload = {"content": data, "number": 0, "size": len(data), "totalElements": len(data)}
        elif isinstance(data, dict):
            payload = data
        else:
            payload = {"content": [data]}

        dump_result("buscar_bienes", payload)

        # Llamada 2: obtener_bien_por_id (ejemplo con id 1)
        print("\nLlamando obtener_bien_por_id with id=1")
        result2 = await client.call_tool("obtener_bien_por_id", {"id": 4884})
        # extraer data similar al anterior
        if hasattr(result2, "data"):
            r2 = result2.data
        else:
            r2 = result2
        # si viene envuelto en una lista u objeto, mostrarlo
        # normalizamos:
        try:
            # si r2 tiene .json (poco probable), convertir
            data2 = r2
        except Exception:
            data2 = r2
        dump_result("obtener_bien_por_id", data2)


if __name__ == "__main__":
    asyncio.run(main())
