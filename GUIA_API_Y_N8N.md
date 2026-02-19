# 🚀 GUÍA COMPLETA: API PQRS + N8N

## 📦 ARCHIVOS DESCARGADOS

1. `api_pqrs.py` - API REST completa
2. `requirements_api.txt` - Dependencias necesarias
3. Esta guía

---

## 🔧 INSTALACIÓN (15 MINUTOS)

### Paso 1: Instalar dependencias

```bash
# Navega a tu carpeta del proyecto
cd tu-carpeta-pqrs

# Instala Flask
pip install -r requirements_api.txt

# O manualmente:
pip install Flask==3.0.0 flask-cors==4.0.0
```

### Paso 2: Copiar archivo API

Copia `api_pqrs.py` a la misma carpeta donde están:
- `sistema_pqrs_v4_ia.py`
- `validador_automatico.py`
- `pqrs_sistema.db`

```
tu-carpeta-pqrs/
├── sistema_pqrs_v4_ia.py
├── validador_automatico.py
├── pqrs_sistema.db
├── api_pqrs.py          ← NUEVO
└── ...
```

### Paso 3: Iniciar la API

```bash
python api_pqrs.py
```

Deberías ver:

```
═══════════════════════════════════════════════════════════
  🚀 API PQRS IA - INICIANDO
═══════════════════════════════════════════════════════════

✅ Sistema PQRS cargado correctamente

📡 Endpoints disponibles:
   GET    /                       → Documentación
   GET    /api/health             → Health check
   POST   /api/resolver-pqrs      → Resolver PQRS
   ...

🌐 Servidor corriendo en: http://localhost:5000
```

### Paso 4: Probar que funciona

Abre tu navegador en: **http://localhost:5000**

Deberías ver la página de documentación de la API.

---

## 🧪 PRUEBAS DE LA API

### Prueba 1: Health Check

```bash
curl http://localhost:5000/api/health
```

**Respuesta esperada:**
```json
{
  "status": "ok",
  "sistema_disponible": true,
  "validador_disponible": true,
  "version": "1.0.0",
  "timestamp": "2025-02-17T12:00:00"
}
```

---

### Prueba 2: Resolver PQRS

```bash
curl -X POST http://localhost:5000/api/resolver-pqrs \
  -H "Content-Type: application/json" \
  -d '{
    "problema": "Para el crédito 5800325002956151 cambiar estado a 77",
    "incluir_validacion": true
  }'
```

**Respuesta esperada:**
```json
{
  "success": true,
  "problema": "Para el crédito 5800325002956151 cambiar estado a 77",
  "encontrado": true,
  "mejor_caso": {
    "categoria": "Estados",
    "sql_generado": "UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE CreditNumber = '5800325002956151'",
    "respuesta": "Estado actualizado a 77...",
    "similitud": 92.5,
    "confianza": "alta"
  },
  "validacion": {
    "puede_ejecutar": true,
    "requiere_aprobacion": true,
    "nivel_aprobacion": "supervisor",
    "razon": "Estado 77 es crítico"
  }
}
```

---

### Prueba 3: Listar casos

```bash
curl http://localhost:5000/api/casos?limit=5
```

---

### Prueba 4: Estadísticas

```bash
curl http://localhost:5000/api/estadisticas
```

---

## 🔗 INTEGRACIÓN CON N8N

### Opción A: N8N Cloud (más fácil)

1. Ve a https://n8n.io y crea una cuenta gratis
2. Crea un nuevo workflow
3. Agrega un nodo "HTTP Request"
4. Configura:
   - **Method:** POST
   - **URL:** http://TU-IP:5000/api/resolver-pqrs
   - **Authentication:** None
   - **Body Type:** JSON
   - **JSON:**
     ```json
     {
       "problema": "{{ $json.body }}",
       "incluir_validacion": true
     }
     ```

### Opción B: N8N Self-Hosted (gratis)

```bash
# Instalar con Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Accede en: http://localhost:5678
```

---

## 📧 EJEMPLO COMPLETO: EMAIL → API → RESPUESTA

### Workflow n8n: "Auto-Resolver PQRS por Email"

```
┌────────────────────┐
│  1. Email Trigger  │
│  Gmail/Outlook     │
└────────┬───────────┘
         │
         ↓
┌────────────────────┐
│  2. Extract Data   │
│  problema = body   │
└────────┬───────────┘
         │
         ↓
┌────────────────────┐
│  3. HTTP Request   │
│  POST /api/        │
│  resolver-pqrs     │
└────────┬───────────┘
         │
         ↓
┌────────────────────┐
│  4. IF Node        │
│  ¿Puede ejecutar?  │
└────┬───────┬───────┘
     │       │
  TRUE│      │FALSE
     ↓       ↓
┌─────────┐ ┌─────────────┐
│ Ejecutar│ │ Enviar a    │
│ SQL     │ │ Slack para  │
│ (futuro)│ │ aprobación  │
└────┬────┘ └──────┬──────┘
     │             │
     ↓             ↓
┌────────────────────┐
│  5. Gmail Node     │
│  Responder email   │
└────────────────────┘
```

### Configuración paso a paso en n8n:

**Nodo 1: Email Trigger**
- Tipo: Gmail Trigger
- Filtro: emails a pqrs@tuempresa.com
- Frecuencia: Cada 1 minuto

**Nodo 2: Code (JavaScript)**
```javascript
const problema = $input.first().json.body;
const remitente = $input.first().json.from;

return {
  problema: problema,
  remitente: remitente
};
```

**Nodo 3: HTTP Request**
- Method: POST
- URL: http://localhost:5000/api/resolver-pqrs
- Body Type: JSON
- JSON:
```json
{
  "problema": "{{ $json.problema }}",
  "incluir_validacion": true
}
```

**Nodo 4: IF**
- Condition: {{ $json.validacion.puede_ejecutar }} = true
- AND: {{ $json.validacion.requiere_aprobacion }} = false

**Nodo 5a (TRUE): Gmail**
- Operation: Send Email
- To: {{ $node["Email Trigger"].json.from }}
- Subject: Re: PQRS - Solucionado
- Body:
```
Hola,

Tu PQRS ha sido resuelta automáticamente.

{{ $json.mejor_caso.respuesta }}

SQL ejecutado:
{{ $json.mejor_caso.sql_generado }}

Saludos
```

**Nodo 5b (FALSE): Slack**
- Channel: #pqrs-aprobaciones
- Message:
```
⚠️ PQRS requiere aprobación

Problema: {{ $json.problema }}
Nivel: {{ $json.validacion.nivel_aprobacion }}

SQL:
{{ $json.mejor_caso.sql_generado }}

[Aprobar] [Rechazar]
```

---

## 🛡️ SEGURIDAD

### Producción - Configuraciones importantes:

1. **Cambiar debug a False** en `api_pqrs.py`:
```python
app.run(
    host='0.0.0.0',
    port=5000,
    debug=False  # ← IMPORTANTE
)
```

2. **Agregar autenticación** (ejemplo con API Key):

```python
from functools import wraps
from flask import request, jsonify

API_KEY = "tu-api-key-secreta"  # Guardar en variable de entorno

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') != API_KEY:
            return jsonify({"error": "API key inválida"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Aplicar a endpoints:
@app.route('/api/resolver-pqrs', methods=['POST'])
@require_api_key
def resolver_pqrs():
    ...
```

3. **Rate limiting** (limitar requests por IP):

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/resolver-pqrs', methods=['POST'])
@limiter.limit("10 per minute")
def resolver_pqrs():
    ...
```

---

## 🚀 DESPLIEGUE EN SERVIDOR

### Opción 1: Servidor con systemd (Linux)

Crear archivo `/etc/systemd/system/api-pqrs.service`:

```ini
[Unit]
Description=API PQRS IA
After=network.target

[Service]
User=tu-usuario
WorkingDirectory=/ruta/a/tu/proyecto
Environment="PATH=/ruta/a/tu/venv/bin"
ExecStart=/ruta/a/tu/venv/bin/python api_pqrs.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Comandos:
```bash
sudo systemctl daemon-reload
sudo systemctl start api-pqrs
sudo systemctl enable api-pqrs  # Iniciar al arranque
sudo systemctl status api-pqrs  # Ver estado
```

### Opción 2: Docker

Crear `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements_api.txt ./
RUN pip install -r requirements.txt -r requirements_api.txt

COPY . .

EXPOSE 5000

CMD ["python", "api_pqrs.py"]
```

Comandos:
```bash
docker build -t api-pqrs .
docker run -d -p 5000:5000 --name api-pqrs api-pqrs
```

---

## 📊 MONITOREO

### Ver logs en tiempo real:

```bash
# Si usas systemd:
sudo journalctl -u api-pqrs -f

# Si usas Docker:
docker logs -f api-pqrs

# Si ejecutas directamente:
# Los logs aparecen en la terminal
```

### Endpoints de monitoreo:

```bash
# Health check cada 30 segundos
watch -n 30 curl http://localhost:5000/api/health

# Estadísticas
curl http://localhost:5000/api/estadisticas
```

---

## 🐛 TROUBLESHOOTING

### Error: "Address already in use"

```bash
# Encontrar proceso usando puerto 5000
lsof -i :5000

# Matar proceso
kill -9 [PID]

# O cambiar puerto en api_pqrs.py:
app.run(port=5001)
```

### Error: "Module not found: sistema_pqrs_v4_ia"

```bash
# Asegúrate de estar en la carpeta correcta
cd /ruta/a/tu/proyecto

# Verifica que el archivo existe
ls sistema_pqrs_v4_ia.py
```

### Error: "Sistema no disponible"

- Verifica que `pqrs_sistema.db` existe
- Verifica que todos los archivos están en la misma carpeta
- Reinicia la API

---

## 📚 EJEMPLOS DE REQUESTS

### Python

```python
import requests

response = requests.post(
    'http://localhost:5000/api/resolver-pqrs',
    json={
        'problema': 'Para el crédito 123 cambiar estado a 77',
        'incluir_validacion': True
    }
)

print(response.json())
```

### JavaScript (Node.js)

```javascript
const axios = require('axios');

axios.post('http://localhost:5000/api/resolver-pqrs', {
  problema: 'Para el crédito 123 cambiar estado a 77',
  incluir_validacion: true
})
.then(response => console.log(response.data))
.catch(error => console.error(error));
```

### cURL

```bash
curl -X POST http://localhost:5000/api/resolver-pqrs \
  -H "Content-Type: application/json" \
  -d '{"problema":"Para el crédito 123 cambiar estado a 77","incluir_validacion":true}'
```

---

## ✅ CHECKLIST DE INSTALACIÓN

- [ ] Instalado Flask y flask-cors
- [ ] Archivo `api_pqrs.py` en carpeta del proyecto
- [ ] API inicia sin errores
- [ ] Health check funciona (http://localhost:5000/api/health)
- [ ] Endpoint resolver-pqrs responde correctamente
- [ ] (Opcional) N8N instalado y funcionando
- [ ] (Opcional) Primer workflow n8n creado y probado

---

## 🎯 PRÓXIMOS PASOS

1. **Semana 1:** Probar la API manualmente con cURL
2. **Semana 2:** Instalar n8n y crear primer workflow simple
3. **Semana 3:** Integrar email → API → respuesta
4. **Semana 4:** Agregar Slack para aprobaciones
5. **Semana 5:** Desplegar en servidor de producción

---

## 💡 TIPS PRO

- Usa **Postman** para probar la API de forma visual
- Guarda los endpoints en una **colección** de Postman
- Configura **logs** en un archivo separado para producción
- Usa **ngrok** para exponer tu API local a internet temporalmente:
  ```bash
  ngrok http 5000
  ```

---

**¿Dudas? ¿Errores? ¿Necesitas ayuda con n8n?**

Pregúntame lo que necesites 💪
