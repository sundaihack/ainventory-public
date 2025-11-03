"Crea un proyecto en TypeScript para un MCP que interactúe con Google Drive. El proyecto debe incluir:

1.  **Configuración inicial:**
    *   Un archivo `package.json` con dependencias mínimas para TypeScript, Node.js y la API de Google Drive.
    *   Configuración `tsconfig.json` estándar para un proyecto Node.js.
    *   Un archivo `.env` o similar para gestionar credenciales y variables de entorno de forma segura (ej. ID de cliente, secreto de cliente, URL de redirección).

2.  **Autenticación:**
    *   Implementación del flujo de autenticación OAuth2 de Google. Esto implica:
        *   Obtener las credenciales de Google Cloud (ID de cliente, secreto de cliente).
        *   Crear una URL de autorización para que el usuario dé permiso.
        *   Manejar el callback de autorización para intercambiar el código por tokens de acceso y refresco.
        *   Almacenar los tokens de forma persistente (ej. en un archivo local o una base de datos simple) para futuras sesiones.

3.  **Funcionalidad básica de Google Drive:**
    *   **Subir un archivo:** Una función que permita subir un archivo desde una ruta local a Google Drive.
    *   **Listar archivos:** Una función para listar los archivos (o al menos un subconjunto) en la carpeta raíz del usuario.
    *   **Descargar un archivo:** Una función que permita descargar un archivo específico de Google Drive a una ruta local.

4.  **Estructura del código:**
    *   Separación lógica en módulos (ej. `auth.ts`, `drive.ts`, `index.ts`).
    *   Uso de `async/await` para operaciones asíncronas.
    *   Manejo básico de errores para las llamadas a la API de Google Drive.

5.  **Instrucciones de uso:**
    *   Un archivo `README.md` que explique cómo configurar las credenciales de Google Cloud, instalar dependencias y ejecutar el MCP."