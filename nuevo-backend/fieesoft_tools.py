# fieesoft_tools.py
import os
import requests
from typing import Optional, Dict, Any, List
from fastmcp import FastMCP

# No creamos un FastMCP aquí — las tools se registran sobre el app que pase main.py
# Pero dejamos constantes / helpers reutilizables.

DEFAULT_BASE = os.environ.get("FIEESOFT_API_BASE_URL")
DEFAULT_USER = os.environ.get("FIEESOFT_USER")
DEFAULT_PASS = os.environ.get("FIEESOFT_PASS")
DEFAULT_TIMEOUT = float(os.environ.get("FIEESOFT_TIMEOUT", "10.0"))  # segundos

def _create_logged_session(base_url: str = DEFAULT_BASE,
                           username: str = DEFAULT_USER,
                           password: str = DEFAULT_PASS,
                           timeout: float = DEFAULT_TIMEOUT) -> requests.Session:
    """
    Crea una requests.Session, hace POST a /api/auth/login con JSON {username,password}
    y garantiza que haya cookies válidas en la sesión. Lanza requests.HTTPError en fallo.
    """
    sess = requests.Session()
    login_url = base_url.rstrip("/") + "/api/auth/login"
    payload = {"username": username, "password": password}

    resp = sess.post(login_url, json=payload, timeout=timeout)
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # incluir el contenido para facilitar debug
        raise requests.HTTPError(f"Login failed ({resp.status_code}): {resp.text}") from e

    # requests.Session fills sess.cookies automatically from Set-Cookie.
    if not sess.cookies:
        # fallback: intentar extraer Set-Cookie en headers (poco probable)
        set_cookie = resp.headers.get("Set-Cookie")
        if not set_cookie:
            raise requests.HTTPError("Login did not yield cookies; cannot authenticate to API.")
    return sess

def register_tools(app: FastMCP):
    """
    Registra las tools sobre 'app' pasado desde main.py.
    Definimos las tools con @app.tool() para que FastMCP las exponga.
    """

    @app.tool()
    def buscar_bienes(
        texto: Optional[str] = None,
        nombreMarca: Optional[str] = None,
        ubicacion: Optional[str] = None,
        estado: Optional[str] = None,
        page: Optional[int] = 0,
        size: Optional[int] = 50
    ) -> Dict[str, Any]:
        """
        Busca bienes en la API remota:
        Devuelve una estructura similar a Spring Page:
        { "content": [...], "number": 0, "size": 50, "totalElements": 123 }
        """
        base = os.environ.get("FIEESOFT_API_BASE_URL", DEFAULT_BASE)
        try:
            sess = _create_logged_session(
                base,
                os.environ.get("FIEESOFT_USER", DEFAULT_USER),
                os.environ.get("FIEESOFT_PASS", DEFAULT_PASS),
            )
        except Exception as e:
            return {"error": f"Login error: {str(e)}"}

        url = base.rstrip("/") + "/api/bienes"
        params: Dict[str, Any] = {}
        if texto:
            params["texto"] = texto
        if nombreMarca:
            params["nombreMarca"] = nombreMarca
        if ubicacion:
            params["ubicacion"] = ubicacion
        if estado:
            params["estado"] = estado
        if page is not None:
            params["page"] = page
        if size is not None:
            params["size"] = size

        try:
            resp = sess.get(url, params=params, timeout=float(os.environ.get("FIEESOFT_TIMEOUT", DEFAULT_TIMEOUT)))
            resp.raise_for_status()
        except Exception as e:
            return {"error": f"Error calling {url}: {str(e)}"}

        # Intentar parsear la respuesta — admitir tanto Page Spring como lista simple
        try:
            data = resp.json()
        except ValueError:
            return {"error": "Respuesta no es JSON válido", "raw": resp.text}

        # Si la API ya devuelve Page (tiene 'content'), devolver tal cual (pero asegurar tipos)
        if isinstance(data, dict) and "content" in data:
            content = data.get("content", [])
            number = int(data.get("number", 0))
            size_resp = int(data.get("size", len(content) if content else 0))
            total = int(data.get("totalElements", len(content)))
            return {
                "content": content,
                "number": number,
                "size": size_resp,
                "totalElements": total
            }

        # si devuelve lista directa
        if isinstance(data, list):
            return {
                "content": data,
                "number": 0,
                "size": len(data),
                "totalElements": len(data)
            }

        # fallback: encapsular lo que venga
        return {"content": data}

    @app.tool()
    def obtener_bien_por_id(id: int) -> Dict[str, Any]:
        """
        Obtiene el detalle de un bien por id (GET /api/bienes/{id}).
        """
        if id is None:
            return {"error": "id es requerido"}

        base = os.environ.get("FIEESOFT_API_BASE_URL", DEFAULT_BASE)
        try:
            sess = _create_logged_session(
                base,
                os.environ.get("FIEESOFT_USER", DEFAULT_USER),
                os.environ.get("FIEESOFT_PASS", DEFAULT_PASS),
            )
        except Exception as e:
            return {"error": f"Login error: {str(e)}"}

        url = f"{base.rstrip('/')}/api/bienes/{id}"
        try:
            resp = sess.get(url, timeout=float(os.environ.get("FIEESOFT_TIMEOUT", DEFAULT_TIMEOUT)))
            resp.raise_for_status()
        except Exception as e:
            # No devolver objetos Response. Extraer info segura y legible si existe:
            resp_obj = getattr(e, "response", None)
            status_info = None
            body_snippet = None
            if resp_obj is not None:
                try:
                    status_info = f"{resp_obj.status_code} {getattr(resp_obj, 'reason', '')}".strip()
                    # evitar incluir body entero: solo primeros 500 chars (o None si está vacío)
                    body_text = getattr(resp_obj, "text", "")
                    body_snippet = body_text[:500] if body_text else None
                except Exception:
                    status_info = str(resp_obj)  # fallback seguro
            return {
                "error": f"Error calling {url}: {str(e)}",
                "status": status_info,
                "body_snippet": body_snippet,
            }

        try:
            data = resp.json()
        except ValueError:
            return {"error": "Respuesta no es JSON válido", "raw": resp.text[:1000]}

        return data


    @app.tool()
    def buscar_cambios_ubicacion_de_bien(id: int):
        """
        Placeholder: no implementado en el backend (igual que en tu Java).
        """
        raise NotImplementedError("No implementado en el API remoto (placeholder)")

    # Fin register_tools
