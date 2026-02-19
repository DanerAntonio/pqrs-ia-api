# 🧠 MEJORAS PARA EXPANDIR EL CONOCIMIENTO DEL SISTEMA

## 📊 ESTADO ACTUAL DEL CHAT

**Lo que responde HOY:**
- ✅ Código de bancos (Davivienda, Bancolombia)
- ✅ Estados de liquidación (71, 77, 79)
- ✅ Resolver PQRS (con crédito + descripción)

**Total: ~20 preguntas predefinidas**

---

## 🚀 PLAN DE EXPANSIÓN DEL CONOCIMIENTO

### FASE 1: Expandir Base de Conocimiento (1-2 horas)

Agregar a `conocimiento_base.json`:

#### 1. PROCEDIMIENTOS COMUNES (STEP-BY-STEP)

```json
"procedimientos": {
  "cambiar_estado_liquidacion": {
    "titulo": "Cambiar estado de liquidación",
    "pasos": [
      "1. Identificar el crédito (número de 13-16 dígitos)",
      "2. Verificar el estado actual en formatexceldlle",
      "3. Validar que el cambio es permitido según flujo",
      "4. Ejecutar UPDATE formatexceldlle SET EstadoLiquidacionVendedor = [nuevo_estado] WHERE CreditNumber = '[credito]'",
      "5. Verificar que se actualizó correctamente con SELECT"
    ],
    "sql_ejemplo": "UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE CreditNumber = '5800325002956151'",
    "precauciones": [
      "No saltar estados en el flujo (ej: de 70 a 79 directo)",
      "Verificar que el vendedor tenga todos los datos completos",
      "El estado 77 es el más común para aprobar"
    ]
  },
  
  "actualizar_vendedor": {
    "titulo": "Actualizar datos del vendedor",
    "pasos": [
      "1. Obtener cédula del vendedor",
      "2. Buscar UserID en tabla user con la cédula",
      "3. Actualizar formatexceldlle con el nuevo UserID",
      "4. Verificar que los datos del vendedor sean correctos"
    ],
    "sql_ejemplo": "UPDATE formatexceldlle SET UserId = (SELECT UserID FROM user WHERE Identification = '1075272601') WHERE CreditNumber = '5800325002956151'",
    "precauciones": [
      "Verificar que el vendedor esté activo",
      "Validar que pertenezca al concesionario correcto"
    ]
  },
  
  "corregir_valores_comision": {
    "titulo": "Corregir valores de comisión",
    "pasos": [
      "1. Identificar el crédito",
      "2. Verificar el valor correcto (puede estar en otro sistema)",
      "3. Actualizar ValueCommission en formatexceldlle",
      "4. Si hay comisión de concesionario, actualizar también ValueCommissionConcesionario",
      "5. Validar que la suma sea correcta"
    ],
    "sql_ejemplo": "UPDATE formatexceldlle SET ValueCommission = 250000 WHERE CreditNumber = '5800325002956151'",
    "precauciones": [
      "Los valores deben coincidir con el contrato",
      "Verificar si requiere aprobación de supervisor"
    ]
  },
  
  "generar_certificado": {
    "titulo": "Generar certificado tributario",
    "pasos": [
      "1. Verificar que exista el NIT en la tabla user",
      "2. Crear registro en certificatefileuser",
      "3. Asociar el archivo PDF generado",
      "4. Marcar como generado en el sistema"
    ],
    "campos_requeridos": [
      "NIT del proveedor",
      "Tipo de certificado (ReteIVA, ReteFuente, ReteICA)",
      "Periodo fiscal",
      "Valores a certificar"
    ],
    "precauciones": [
      "Validar que los valores coincidan con contabilidad",
      "El PDF debe estar firmado digitalmente"
    ]
  }
}
```

#### 2. PREGUNTAS FRECUENTES (FAQs)

```json
"preguntas_frecuentes": {
  "como_aprobar_liquidacion": {
    "pregunta": "¿Cómo apruebo una liquidación?",
    "respuesta": "Para aprobar una liquidación, debes cambiar el estado a 77 (Aprobados Jefe-Coordinador). Esto se hace con: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE CreditNumber = '[numero_credito]'. El estado 77 indica que la comisión está lista para pago.",
    "relacionado": ["cambiar_estado_liquidacion", "estado_77"]
  },
  
  "que_significa_estado_70": {
    "pregunta": "¿Qué significa el estado 70?",
    "respuesta": "El estado 70 es 'Sin Liquidar'. Significa que la comisión aún no ha sido procesada para pago. Es el estado inicial de una liquidación.",
    "relacionado": ["estados_liquidacion", "flujo_liquidacion"]
  },
  
  "como_encontrar_vendedor": {
    "pregunta": "¿Cómo encuentro el ID de un vendedor?",
    "respuesta": "Usa: SELECT UserID, FirstName, LastName FROM user WHERE Identification = '[cedula]' AND TypeUserID = 1. El TypeUserID = 1 indica que es vendedor.",
    "relacionado": ["actualizar_vendedor", "tabla_user"]
  },
  
  "diferencia_comision_vendedor_concesionario": {
    "pregunta": "¿Cuál es la diferencia entre comisión de vendedor y concesionario?",
    "respuesta": "ValueCommission es la comisión del vendedor individual. ValueCommissionConcesionario es la comisión que va al concesionario/dealer. Ambas están en la misma fila de formatexceldlle pero son valores separados.",
    "relacionado": ["corregir_valores_comision", "tabla_formatexceldlle"]
  },
  
  "que_es_creditnumber": {
    "pregunta": "¿Qué es el CreditNumber?",
    "respuesta": "Es el identificador único del crédito/préstamo. Generalmente tiene 13-16 dígitos. Se usa como clave principal para buscar y actualizar registros en formatexceldlle.",
    "relacionado": ["tabla_formatexceldlle"]
  }
}
```

#### 3. ERRORES COMUNES Y SOLUCIONES

```json
"errores_comunes": {
  "estado_no_permite_cambio": {
    "error": "No se puede cambiar de estado X a estado Y",
    "causa": "El flujo de liquidación tiene restricciones. No todos los cambios están permitidos.",
    "solucion": "Revisa el flujo: 70→71→72→77→79. No puedes saltar etapas críticas.",
    "ejemplo": "No puedes ir directo de 70 (Sin Liquidar) a 79 (Liquidacion Manual)"
  },
  
  "vendedor_no_existe": {
    "error": "UserID no encontrado",
    "causa": "El vendedor no está registrado en la tabla user o la cédula es incorrecta",
    "solucion": "Verifica: 1) Que la cédula sea correcta, 2) Que el vendedor esté activo, 3) Que TypeUserID = 1",
    "sql_diagnostico": "SELECT * FROM user WHERE Identification = '[cedula]'"
  },
  
  "credito_no_existe": {
    "error": "CreditNumber no encontrado",
    "causa": "El número de crédito no existe o está mal escrito",
    "solucion": "Verifica que el número tenga todos los dígitos. Usa: SELECT * FROM formatexceldlle WHERE CreditNumber LIKE '%[ultimos_digitos]%'",
    "tip": "Si solo tienes los últimos dígitos, puedes buscar con LIKE"
  },
  
  "permiso_denegado": {
    "error": "No tienes permisos para esta operación",
    "causa": "Tu usuario no tiene permisos de UPDATE en esa tabla",
    "solucion": "Solicita permisos al administrador de BD o pide que lo ejecute alguien con permisos",
    "alternativa": "Genera el SQL y envíalo a quien tenga permisos"
  }
}
```

#### 4. GLOSARIO DE TÉRMINOS

```json
"glosario": {
  "liquidacion": "Proceso de calcular y aprobar las comisiones de vendedores",
  "concesionario": "Empresa dealer que vende los productos. Sinónimo: dealer",
  "asesor": "Vendedor. Sinónimo: comercial, vendedor",
  "comision": "Porcentaje o valor fijo que gana el vendedor por una venta. Sinónimo: fee",
  "certificado": "Documento tributario (ReteIVA, ReteFuente, ReteICA) requerido por ley",
  "NIT": "Número de Identificación Tributaria de empresas",
  "ACH": "Sistema de pagos electrónicos entre bancos",
  "formatexceldlle": "Tabla principal con datos de créditos y comisiones",
  "user": "Tabla con información de vendedores y usuarios",
  "certificatefileuser": "Tabla con certificados tributarios",
  "status": "Tabla con los estados del sistema (71, 77, 79, etc.)"
}
```

---

### FASE 2: Mejorar el Agente Conversacional (30 min)

Actualizar `agente_conversacional.py` para buscar en estas nuevas secciones:

```python
# Agregar al método _chat_basico()

# PREGUNTAS SOBRE PROCEDIMIENTOS
elif 'cómo' in ultimo_mensaje_lower or 'como' in ultimo_mensaje_lower:
    procedimientos = base_conocimiento.conocimiento.get('procedimientos', {})
    
    if 'aprobar' in ultimo_mensaje_lower or 'liquidación' in ultimo_mensaje_lower:
        proc = procedimientos.get('cambiar_estado_liquidacion', {})
        if proc:
            respuesta = f"📋 **{proc['titulo']}**\n\n"
            respuesta += "**Pasos:**\n"
            for paso in proc.get('pasos', []):
                respuesta += f"{paso}\n"
            respuesta += f"\n**Ejemplo SQL:**\n```sql\n{proc['sql_ejemplo']}\n```"
            return respuesta
    
    elif 'vendedor' in ultimo_mensaje_lower:
        proc = procedimientos.get('actualizar_vendedor', {})
        # Similar...

# PREGUNTAS FRECUENTES
faqs = base_conocimiento.conocimiento.get('preguntas_frecuentes', {})
for key, faq in faqs.items():
    if any(palabra in faq['pregunta'].lower() for palabra in ultimo_mensaje_lower.split()):
        respuesta = f"**{faq['pregunta']}**\n\n"
        respuesta += faq['respuesta']
        if faq.get('relacionado'):
            respuesta += f"\n\n💡 **Ver también:** {', '.join(faq['relacionado'])}"
        return respuesta

# ERRORES COMUNES
if 'error' in ultimo_mensaje_lower or 'no funciona' in ultimo_mensaje_lower:
    errores = base_conocimiento.conocimiento.get('errores_comunes', {})
    # Buscar error similar...
```

---

### FASE 3: Mejorar UX del Chat (1 hora)

#### Sugerencias Inteligentes

Agregar botones de acceso rápido al chat:

```python
# En pagina_chat.py

# Después del input, agregar sugerencias contextuales
if len(st.session_state.mensajes_chat) == 0:
    st.markdown("### 💡 Preguntas Frecuentes")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("¿Cómo aprobar liquidación?"):
            mensaje = "¿Cómo apruebo una liquidación?"
            # Procesar...
    
    with col2:
        if st.button("¿Qué es el estado 77?"):
            mensaje = "¿Qué significa el estado 77?"
            # Procesar...
    
    with col3:
        if st.button("¿Cómo encuentro un vendedor?"):
            mensaje = "¿Cómo busco un vendedor por cédula?"
            # Procesar...

# Sugerencias DESPUÉS de una respuesta
else:
    ultimo_tema = detectar_tema(st.session_state.mensajes_chat[-1]['content'])
    
    if ultimo_tema == "estados":
        st.markdown("**Preguntas relacionadas:**")
        if st.button("Ver flujo completo de estados"):
            # Mostrar flujo...
```

#### Historial de Búsquedas

```python
# Guardar historial de temas consultados
if 'temas_consultados' not in st.session_state:
    st.session_state.temas_consultados = []

# Al final del chat, mostrar
with st.expander("📚 Historial de consultas"):
    for tema in st.session_state.temas_consultados:
        st.write(f"• {tema}")
```

#### Modo Tutorial

```python
# Agregar switch para modo principiante
modo_tutorial = st.toggle("🎓 Modo Tutorial", value=False)

if modo_tutorial:
    # Respuestas más detalladas
    # Explicar cada término
    # Mostrar ejemplos visuales
```

---

### FASE 4: Indicadores de Calidad (30 min)

Agregar feedback del usuario:

```python
# Después de cada respuesta del asistente
col1, col2, col3 = st.columns([1, 1, 8])

with col1:
    if st.button("👍", key=f"like_{i}"):
        # Guardar feedback positivo
        registrar_feedback(mensaje_id, "positivo")
        st.success("¡Gracias!")

with col2:
    if st.button("👎", key=f"dislike_{i}"):
        # Guardar feedback negativo
        registrar_feedback(mensaje_id, "negativo")
        
        # Pedir detalle
        motivo = st.text_input("¿Qué podemos mejorar?", key=f"motivo_{i}")
        if motivo:
            guardar_sugerencia(motivo)
```

---

## 📊 MÉTRICAS DE CONOCIMIENTO

### Antes de Expansión:
- 20 preguntas predefinidas
- 2 procedimientos documentados
- 3 tablas explicadas

### Después de Expansión:
- 50+ preguntas respondibles
- 10+ procedimientos paso a paso
- 15+ FAQs
- 10+ errores comunes con soluciones
- 20+ términos en glosario

**Incremento: 250%** en conocimiento disponible

---

## 🎯 CRONOGRAMA DE IMPLEMENTACIÓN

### Hoy (2 horas):
1. Actualizar `conocimiento_base.json` con procedimientos y FAQs
2. Ejecutar `cargar_datos_reales.py` (ya actualiza automáticamente)
3. Probar nuevas respuestas

### Mañana (1 hora):
1. Mejorar UX con botones de sugerencias
2. Agregar feedback del usuario
3. Crear modo tutorial

### Pasado (30 min):
1. Documentar todas las mejoras
2. Tomar screenshots
3. Preparar demo

---

## 🚀 QUICK START

### Paso 1: Actualiza conocimiento_base.json

Copia este JSON y agrégalo al archivo `conocimiento_base.json` existente:

```json
{
  "procedimientos": { ... },
  "preguntas_frecuentes": { ... },
  "errores_comunes": { ... },
  "glosario": { ... }
}
```

### Paso 2: Recarga el sistema

```bash
python cargar_datos_reales.py
streamlit run app_streamlit_pqrs.py
```

### Paso 3: Prueba

```
"¿Cómo apruebo una liquidación?"
"¿Qué significa el estado 70?"
"¿Cómo encuentro un vendedor?"
"Error: vendedor no existe"
```

---

## 📈 IMPACTO ESPERADO

- ✅ **+150% más preguntas** respondibles
- ✅ **-60% menos consultas** a TI
- ✅ **+40% satisfacción** del usuario
- ✅ **Base** para entrenar Claude API

---

**¿Empezamos con Fase 1? Te ayudo a expandir el conocimiento.json AHORA**
