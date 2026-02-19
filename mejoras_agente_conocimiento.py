"""
MEJORAS PARA AGENTE_CONVERSACIONAL.PY
Agregar estas funciones al archivo agente_conversacional.py
"""

# ============================================================
# AGREGAR ESTAS FUNCIONES DESPUÉS DE _chat_basico
# ============================================================

def _buscar_en_procedimientos(self, mensaje_lower):
    """Busca en procedimientos documentados"""
    if not BASE_CONOCIMIENTO_DISPONIBLE:
        return None
    
    procedimientos = base_conocimiento.conocimiento.get('procedimientos', {})
    
    # Detectar qué procedimiento busca
    if any(palabra in mensaje_lower for palabra in ['aprobar', 'liquidación', 'liquidacion', 'cambiar estado']):
        proc = procedimientos.get('cambiar_estado_liquidacion')
    elif 'vendedor' in mensaje_lower and ('actualizar' in mensaje_lower or 'cambiar' in mensaje_lower):
        proc = procedimientos.get('actualizar_vendedor')
    elif 'comisión' in mensaje_lower or 'comision' in mensaje_lower:
        proc = procedimientos.get('corregir_valores_comision')
    elif 'buscar' in mensaje_lower and 'vendedor' in mensaje_lower:
        proc = procedimientos.get('buscar_vendedor_por_cedula')
    elif 'banco' in mensaje_lower and 'verificar' in mensaje_lower:
        proc = procedimientos.get('verificar_datos_banco')
    else:
        return None
    
    if not proc:
        return None
    
    # Formatear respuesta
    respuesta = f"📋 **{proc['titulo']}**\n\n"
    respuesta += f"{proc['descripcion']}\n\n"
    respuesta += "**Pasos a seguir:**\n"
    for paso in proc.get('pasos', []):
        respuesta += f"{paso}\n"
    
    if proc.get('sql_ejemplo'):
        respuesta += f"\n**Ejemplo de SQL:**\n```sql\n{proc['sql_ejemplo']}\n```\n"
    
    if proc.get('precauciones'):
        respuesta += "\n**⚠️ Precauciones:**\n"
        for prec in proc['precauciones']:
            respuesta += f"• {prec}\n"
    
    return respuesta

def _buscar_en_faqs(self, mensaje_lower):
    """Busca en preguntas frecuentes"""
    if not BASE_CONOCIMIENTO_DISPONIBLE:
        return None
    
    faqs = base_conocimiento.conocimiento.get('preguntas_frecuentes', {})
    
    # Buscar coincidencias
    for key, faq in faqs.items():
        palabras_clave = faq.get('palabras_clave', [])
        
        # Si alguna palabra clave coincide
        if any(palabra in mensaje_lower for palabra in palabras_clave):
            respuesta = f"**{faq['pregunta']}**\n\n"
            respuesta += faq['respuesta']
            
            if faq.get('relacionado'):
                respuesta += f"\n\n💡 **Ver también:** {', '.join(faq['relacionado'][:3])}"
            
            return respuesta
    
    return None

def _buscar_en_errores(self, mensaje_lower):
    """Busca soluciones a errores comunes"""
    if not BASE_CONOCIMIENTO_DISPONIBLE:
        return None
    
    if 'error' not in mensaje_lower and 'problema' not in mensaje_lower and 'no funciona' not in mensaje_lower:
        return None
    
    errores = base_conocimiento.conocimiento.get('errores_comunes', {})
    
    # Detectar tipo de error
    for key, error in errores.items():
        palabras_clave = error.get('palabras_clave', [])
        
        if any(palabra in mensaje_lower for palabra in palabras_clave):
            respuesta = f"🔧 **Solución al error: {error['error']}**\n\n"
            respuesta += f"**Causa:** {error['causa']}\n\n"
            respuesta += f"**Solución:** {error['solucion']}\n"
            
            if error.get('sql_diagnostico'):
                respuesta += f"\n**SQL de diagnóstico:**\n```sql\n{error['sql_diagnostico']}\n```"
            
            return respuesta
    
    return None

def _buscar_en_glosario(self, mensaje_lower):
    """Busca definiciones en el glosario"""
    if not BASE_CONOCIMIENTO_DISPONIBLE:
        return None
    
    if 'qué es' not in mensaje_lower and 'que es' not in mensaje_lower and 'qué significa' not in mensaje_lower:
        return None
    
    glosario = base_conocimiento.conocimiento.get('glosario', {})
    
    # Buscar el término
    for termino, definicion in glosario.items():
        if termino in mensaje_lower:
            return f"📖 **{termino.capitalize()}:** {definicion}"
    
    return None

# ============================================================
# REEMPLAZAR EL MÉTODO _chat_basico CON ESTA VERSIÓN MEJORADA
# ============================================================

def _chat_basico_mejorado(self) -> str:
    """Chat básico MEJORADO con conocimiento expandido"""
    ultimo_mensaje = self.conversacion[-1]["content"]
    ultimo_mensaje_lower = ultimo_mensaje.lower()
    
    # PRIMERO: Buscar en conocimiento expandido
    palabras_pregunta = ['qué', 'que', 'cual', 'cuál', 'cómo', 'como']
    es_pregunta = any(p in ultimo_mensaje_lower for p in palabras_pregunta)
    
    if es_pregunta and BASE_CONOCIMIENTO_DISPONIBLE:
        # 1. Buscar en procedimientos
        respuesta = self._buscar_en_procedimientos(ultimo_mensaje_lower)
        if respuesta:
            return respuesta
        
        # 2. Buscar en FAQs
        respuesta = self._buscar_en_faqs(ultimo_mensaje_lower)
        if respuesta:
            return respuesta
        
        # 3. Buscar en glosario
        respuesta = self._buscar_en_glosario(ultimo_mensaje_lower)
        if respuesta:
            return respuesta
        
        # 4. Buscar en bancos (código existente)
        if 'banco' in ultimo_mensaje_lower:
            # ... código existente de bancos ...
            pass
        
        # 5. Buscar en estados (código existente)
        elif 'estado' in ultimo_mensaje_lower:
            # ... código existente de estados ...
            pass
    
    # Buscar soluciones a errores
    if 'error' in ultimo_mensaje_lower or 'problema' in ultimo_mensaje_lower:
        respuesta = self._buscar_en_errores(ultimo_mensaje_lower)
        if respuesta:
            return respuesta
    
    # RESTO DEL CÓDIGO EXISTENTE...
    # (búsqueda de PQRS, preguntas predefinidas, etc.)

# ============================================================
# INSTRUCCIONES DE INSTALACIÓN
# ============================================================

"""
PASOS PARA INSTALAR ESTAS MEJORAS:

1. Abre agente_conversacional.py

2. Agrega las 4 funciones nuevas después de _chat_basico:
   - _buscar_en_procedimientos
   - _buscar_en_faqs
   - _buscar_en_errores
   - _buscar_en_glosario

3. Modifica _chat_basico para que llame a estas funciones:
   
   Agrega ANTES de la búsqueda de bancos:
   
   # Buscar en procedimientos
   respuesta = self._buscar_en_procedimientos(ultimo_mensaje_lower)
   if respuesta:
       return respuesta
   
   # Buscar en FAQs
   respuesta = self._buscar_en_faqs(ultimo_mensaje_lower)
   if respuesta:
       return respuesta
   
   # Buscar en errores
   if 'error' in ultimo_mensaje_lower:
       respuesta = self._buscar_en_errores(ultimo_mensaje_lower)
       if respuesta:
           return respuesta
   
   # Buscar en glosario
   if 'qué es' in ultimo_mensaje_lower:
       respuesta = self._buscar_en_glosario(ultimo_mensaje_lower)
       if respuesta:
           return respuesta

4. Guarda el archivo

5. Ejecuta:
   python integrar_conocimiento.py
   streamlit run app_streamlit_pqrs.py

6. Prueba con preguntas como:
   - "¿Cómo apruebo una liquidación?"
   - "¿Qué es el estado 77?"
   - "Error: vendedor no existe"
   - "¿Qué es liquidación?"
"""
