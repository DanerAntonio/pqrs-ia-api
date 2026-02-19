"""
MEJORAS DE UX PARA PAGINA_CHAT.PY
Versión con botones de sugerencias, feedback y mejor experiencia
"""

import streamlit as st
from agente_conversacional import crear_agente


def mostrar_pagina_chat():
    """Muestra la interfaz de chat con UX mejorada"""
    
    # Verificar sistema
    if "sistema" not in st.session_state or st.session_state.sistema is None:
        st.error("⚠️ Sistema PQRS no inicializado. Ve primero a Inicio.")
        return
    
    # Inicializar agente
    if "agente_chat" not in st.session_state:
        api_key = st.session_state.get("claude_api_key")
        st.session_state.agente_chat = crear_agente(
            api_key=api_key,
            sistema_pqrs=st.session_state.sistema
        )
    
    # Inicializar historial
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = []
    
    # Inicializar temas consultados
    if "temas_consultados" not in st.session_state:
        st.session_state.temas_consultados = []
    
    # Mostrar estado API
    modo_actual = st.session_state.agente_chat.modo
    
    if modo_actual == "BASICO":
        st.warning("⚠️ Modo Básico activo. Configura Claude API para mejor experiencia.")
    else:
        st.success("✅ Claude API Activo")
    
    st.divider()
    
    # ============================================================
    # BOTONES DE SUGERENCIAS RÁPIDAS (NUEVO)
    # ============================================================
    
    if len(st.session_state.mensajes_chat) == 0:
        st.markdown("### 💡 Preguntas Frecuentes")
        st.markdown("*Click en cualquier pregunta para empezar:*")
        
        col1, col2, col3 = st.columns(3)
        
        preguntas_rapidas = {
            "col1": [
                ("¿Cómo aprobar liquidación?", "¿Cómo apruebo una liquidación?"),
                ("¿Qué es el estado 77?", "¿Qué es el estado 77?"),
                ("Buscar vendedor", "¿Cómo busco un vendedor por cédula?")
            ],
            "col2": [
                ("Código de Davivienda", "¿Cuál es el código del banco Davivienda?"),
                ("Estados de liquidación", "¿Cuáles son los estados de liquidación?"),
                ("Flujo de estados", "¿Cuál es el flujo de estados de liquidación?")
            ],
            "col3": [
                ("Campos de formatexceldlle", "¿Qué campos tiene la tabla formatexceldlle?"),
                ("Tipos de cuenta", "¿Qué significan los tipos de cuenta bancaria?"),
                ("Diferencia comisiones", "¿Cuál es la diferencia entre las comisiones?")
            ]
        }
        
        for col_name, col in zip(["col1", "col2", "col3"], [col1, col2, col3]):
            with col:
                for label, pregunta in preguntas_rapidas[col_name]:
                    if st.button(label, key=f"quick_{label}", use_container_width=True):
                        procesar_pregunta_rapida(pregunta)
                        st.rerun()
    
    # ============================================================
    # HISTORIAL DE MENSAJES
    # ============================================================
    
    for idx, mensaje in enumerate(st.session_state.mensajes_chat):
        with st.chat_message(mensaje["role"]):
            st.markdown(mensaje["content"])
            
            # Agregar feedback SOLO en mensajes del asistente (NUEVO)
            if mensaje["role"] == "assistant" and idx > 0:
                col1, col2, col3 = st.columns([0.5, 0.5, 9])
                
                with col1:
                    if st.button("👍", key=f"like_{idx}"):
                        registrar_feedback(idx, "positivo")
                        st.success("¡Gracias por tu feedback!")
                
                with col2:
                    if st.button("👎", key=f"dislike_{idx}"):
                        st.session_state[f"feedback_negativo_{idx}"] = True
    
    # ============================================================
    # FORMULARIO DE FEEDBACK NEGATIVO (NUEVO)
    # ============================================================
    
    for idx in range(len(st.session_state.mensajes_chat)):
        if st.session_state.get(f"feedback_negativo_{idx}", False):
            with st.expander("💬 ¿Qué podemos mejorar?", expanded=True):
                motivo = st.text_area(
                    "Cuéntanos qué no te funcionó:",
                    key=f"motivo_{idx}",
                    placeholder="Ej: La respuesta no era clara, faltó información, etc."
                )
                
                if st.button("Enviar feedback", key=f"enviar_{idx}"):
                    guardar_sugerencia(idx, motivo)
                    st.success("✅ Gracias, tu feedback nos ayuda a mejorar")
                    st.session_state[f"feedback_negativo_{idx}"] = False
                    st.rerun()
    
    # ============================================================
    # INPUT DE CHAT
    # ============================================================
    
    mensaje_usuario = st.chat_input("Escribe tu mensaje...")
    
    if mensaje_usuario:
        # Obtener respuesta
        with st.chat_message("assistant"):
            with st.spinner("🤖 Pensando..."):
                respuesta = st.session_state.agente_chat.chat(mensaje_usuario)
                st.markdown(respuesta)
        
        # Guardar en historial
        st.session_state.mensajes_chat.append({
            "role": "user",
            "content": mensaje_usuario
        })
        
        st.session_state.mensajes_chat.append({
            "role": "assistant",
            "content": respuesta
        })
        
        # Registrar tema consultado (NUEVO)
        tema = detectar_tema(mensaje_usuario)
        if tema and tema not in st.session_state.temas_consultados:
            st.session_state.temas_consultados.append(tema)
        
        st.rerun()
    
    st.divider()
    
    # ============================================================
    # CONTROLES ADICIONALES
    # ============================================================
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("🔄 Nueva Conversación", use_container_width=True):
            st.session_state.mensajes_chat = []
            st.session_state.agente_chat.limpiar_conversacion()
            st.rerun()
    
    # ============================================================
    # SUGERENCIAS CONTEXTUALES (NUEVO)
    # ============================================================
    
    if len(st.session_state.mensajes_chat) > 0:
        ultimo_tema = detectar_tema(st.session_state.mensajes_chat[-1]['content'])
        
        if ultimo_tema:
            st.markdown("### 🔗 Preguntas relacionadas")
            
            sugerencias_por_tema = {
                "estados": [
                    "¿Cuál es el flujo completo de estados?",
                    "¿Qué es el estado 71?",
                    "¿Qué es el estado 79?"
                ],
                "bancos": [
                    "¿Qué bancos hay disponibles?",
                    "¿Cómo verifico datos bancarios?",
                    "¿Qué son los códigos ACH?"
                ],
                "vendedores": [
                    "¿Cómo actualizo un vendedor?",
                    "¿Cómo busco por cédula?",
                    "¿Qué es el TypeUserID?"
                ],
                "liquidacion": [
                    "¿Cómo aprobar una liquidación?",
                    "¿Qué verificar antes de aprobar?",
                    "¿Cuáles son los errores comunes?"
                ]
            }
            
            sugerencias = sugerencias_por_tema.get(ultimo_tema, [])
            
            if sugerencias:
                cols = st.columns(len(sugerencias))
                for i, (col, sugerencia) in enumerate(zip(cols, sugerencias)):
                    with col:
                        if st.button(sugerencia, key=f"sug_{i}_{ultimo_tema}"):
                            procesar_pregunta_rapida(sugerencia)
                            st.rerun()
    
    # ============================================================
    # HISTORIAL DE TEMAS (NUEVO)
    # ============================================================
    
    if len(st.session_state.temas_consultados) > 0:
        with st.expander("📚 Temas consultados en esta sesión"):
            for tema in st.session_state.temas_consultados:
                st.write(f"• {tema.capitalize()}")


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def procesar_pregunta_rapida(pregunta):
    """Procesa una pregunta de los botones rápidos"""
    respuesta = st.session_state.agente_chat.chat(pregunta)
    
    st.session_state.mensajes_chat.append({
        "role": "user",
        "content": pregunta
    })
    
    st.session_state.mensajes_chat.append({
        "role": "assistant",
        "content": respuesta
    })
    
    # Registrar tema
    tema = detectar_tema(pregunta)
    if tema and tema not in st.session_state.temas_consultados:
        st.session_state.temas_consultados.append(tema)


def detectar_tema(mensaje):
    """Detecta el tema principal del mensaje"""
    mensaje_lower = mensaje.lower()
    
    if 'estado' in mensaje_lower or 'liquidación' in mensaje_lower or 'liquidacion' in mensaje_lower:
        return "estados"
    elif 'banco' in mensaje_lower or 'cuenta' in mensaje_lower:
        return "bancos"
    elif 'vendedor' in mensaje_lower or 'asesor' in mensaje_lower:
        return "vendedores"
    elif 'comisión' in mensaje_lower or 'comision' in mensaje_lower:
        return "liquidacion"
    elif 'credito' in mensaje_lower or 'crédito' in mensaje_lower:
        return "creditos"
    else:
        return None


def registrar_feedback(indice, tipo):
    """Registra el feedback del usuario"""
    import json
    from datetime import datetime
    
    feedback = {
        'timestamp': datetime.now().isoformat(),
        'tipo': tipo,
        'mensaje_indice': indice,
        'contenido': st.session_state.mensajes_chat[indice]['content'][:100]
    }
    
    try:
        with open('feedback_usuarios.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback, ensure_ascii=False) + '\n')
    except:
        pass  # Silenciar errores de escritura


def guardar_sugerencia(indice, motivo):
    """Guarda una sugerencia de mejora"""
    import json
    from datetime import datetime
    
    sugerencia = {
        'timestamp': datetime.now().isoformat(),
        'mensaje_indice': indice,
        'motivo': motivo,
        'contexto': st.session_state.mensajes_chat[indice]['content'][:100]
    }
    
    try:
        with open('sugerencias_mejora.json', 'a', encoding='utf-8') as f:
            f.write(json.dumps(sugerencia, ensure_ascii=False) + '\n')
    except:
        pass


__all__ = ["mostrar_pagina_chat"]


# ============================================================
# INSTRUCCIONES DE INSTALACIÓN
# ============================================================

"""
PASOS PARA INSTALAR ESTAS MEJORAS:

1. HAZ BACKUP de tu pagina_chat.py actual:
   mv pagina_chat.py pagina_chat_OLD.py

2. Copia ESTE archivo como pagina_chat.py

3. Reinicia Streamlit:
   streamlit run app_streamlit_pqrs.py

4. Prueba las nuevas funcionalidades:
   ✅ Botones de preguntas rápidas
   ✅ Feedback con 👍/👎
   ✅ Sugerencias contextuales
   ✅ Historial de temas

NUEVAS FUNCIONALIDADES:

1. BOTONES DE PREGUNTAS RÁPIDAS
   - Al inicio muestra 9 preguntas comunes
   - Click y listo, no necesitas escribir

2. FEEDBACK DEL USUARIO
   - 👍/👎 en cada respuesta
   - Captura qué no funcionó
   - Se guarda en feedback_usuarios.json

3. SUGERENCIAS CONTEXTUALES
   - Después de cada respuesta
   - Preguntas relacionadas al tema
   - Facilita navegación

4. HISTORIAL DE TEMAS
   - Muestra qué temas consultaste
   - Expandible en la parte inferior

ARCHIVOS GENERADOS:
- feedback_usuarios.json (feedback positivo/negativo)
- sugerencias_mejora.json (cuando algo no funciona)
"""
