"""
Página de Resolución PQRS - VERSION MEJORADA
- Respuestas más humanas
- Muestra múltiples casos similares
- Explica qué encontró y por qué
- Sugiere opciones cuando no es exacto
"""

import streamlit as st
import re


def mostrar_pagina_resolver_mejorada():
    """Página mejorada de resolución PQRS"""

    # NO poner header aquí, ya está en app_streamlit_pqrs.py

    if "sistema" not in st.session_state or st.session_state.sistema is None:
        st.error("⚠️ Sistema PQRS no inicializado.")
        return

    # Input del problema
    st.markdown("### 💬 Describe tu problema")

    problema = st.text_area(
        "Escribe aquí tu consulta o PQRS",
        placeholder="Ejemplo: me puedes ayudar con cambio de estado 71 a 77",
        height=110,
        key="problema_input_mejorado"
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        buscar = st.button("🔍 Buscar Solución", use_container_width=True, type="primary")
    with col2:
        limpiar = st.button("🔄 Limpiar", use_container_width=True)

    if limpiar:
        st.rerun()

    if buscar and problema:
        with st.spinner("🤖 Analizando tu consulta..."):
            ranking = st.session_state.sistema.buscar_similar_ia(problema)

        if not ranking or len(ranking) == 0:
            _mostrar_sin_resultados(problema)
            return

        _mostrar_resultados_humanos(problema, ranking)


# ─────────────────────────────────────────────────────────────
# MOSTRAR RESULTADOS DE FORMA HUMANA
# ─────────────────────────────────────────────────────────────

def _mostrar_resultados_humanos(problema: str, ranking: list):
    """Muestra resultados con explicación humana"""

    mejor = ranking[0]
    similitud = mejor['similitud'] * 100

    # ── Evaluación de confianza ──────────────────────────────
    if similitud >= 85:
        nivel = "alta"
        color = "#10b981"
        icono = "✅"
        mensaje = "Encontré una solución muy precisa para tu caso."
    elif similitud >= 65:
        nivel = "media"
        color = "#f59e0b"
        icono = "⚠️"
        mensaje = "Encontré un caso parecido, pero revisa si aplica exactamente a tu situación."
    else:
        nivel = "baja"
        color = "#ef4444"
        icono = "🔎"
        mensaje = "No encontré un caso muy similar. Te muestro lo más cercano, pero puede que necesites ajustarlo."

    # ── Banner de confianza ──────────────────────────────────
    st.markdown(f"""
        <div style="background:{color}18; border-left:4px solid {color};
                    border-radius:8px; padding:1rem 1.2rem; margin:1rem 0;">
            <span style="font-size:1.3rem;">{icono}</span>
            <strong style="color:{color}; font-size:1.1rem; margin-left:0.5rem;">
                Confianza {nivel.upper()} — {similitud:.0f}%
            </strong>
            <p style="color:#cbd5e1; margin:0.4rem 0 0 0;">{mensaje}</p>
        </div>
    """, unsafe_allow_html=True)

    # ── Interpretación de la pregunta ────────────────────────
    st.markdown("### 🧠 Así interpreté tu pregunta")
    interpretacion = _interpretar_problema(problema)
    st.info(interpretacion)

    # ── MEJOR RESULTADO ──────────────────────────────────────
    st.markdown("### 🥇 Mejor Solución Encontrada")

    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**Categoría:** `{mejor['categoria']}`")
            st.markdown(f"**Caso base:** _{mejor['problema']}_")
        with col2:
            st.metric("Similitud", f"{similitud:.0f}%")

        # SQL con valores reemplazados
        valores = st.session_state.sistema.extraer_valores(problema)
        sql_final = st.session_state.sistema.reemplazar_valores(mejor['sql'], valores)

        st.markdown("#### 💻 SQL para ejecutar:")
        st.code(sql_final, language="sql")

        # Advertencia si el SQL no parece correcto para la pregunta
        _advertir_si_sql_dudoso(problema, sql_final)

        # Respuesta
        st.markdown("#### 📋 Respuesta sugerida para el usuario:")
        st.success(mejor['respuesta'])

    # ── OTROS CASOS SIMILARES ────────────────────────────────
    if len(ranking) > 1:
        st.markdown("---")
        st.markdown("### 📚 Otros Casos Similares")
        st.markdown("_¿El resultado anterior no era exactamente lo que buscabas? Revisa estas opciones:_")

        for i, caso in enumerate(ranking[1:5], 2):  # Mostrar hasta 4 casos más
            sim_i = caso['similitud'] * 100
            color_i = "#10b981" if sim_i >= 70 else "#f59e0b" if sim_i >= 50 else "#94a3b8"

            with st.expander(
                f"Opción {i}: {caso['categoria']} — {sim_i:.0f}% similitud",
                expanded=(i == 2)  # Segunda opción expandida por defecto
            ):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Caso:** _{caso['problema']}_")
                with col2:
                    st.markdown(f"<span style='color:{color_i}; font-size:1.2rem; font-weight:700;'>{sim_i:.0f}%</span>",
                                unsafe_allow_html=True)

                sql_i = st.session_state.sistema.reemplazar_valores(caso['sql'], valores)

                st.markdown("**SQL:**")
                st.code(sql_i, language="sql")

                st.markdown("**Respuesta:**")
                st.info(caso['respuesta'])

                if st.button(f"✅ Usar esta solución", key=f"usar_caso_{i}"):
                    st.success(f"✅ Solución seleccionada: {caso['categoria']}")
                    st.code(sql_i, language="sql")

    # ── AVISO SI CONFIANZA BAJA ──────────────────────────────
    if nivel == "baja":
        st.markdown("---")
        st.warning("""
⚠️ **La confianza es baja** — Esto puede significar que:
- El caso aún no está en la base de conocimiento
- Intenta describir el problema con más detalles
- Incluye el número de crédito, el estado actual y el deseado

💡 **Consejo:** Si resuelves este caso manualmente, guárdalo en "📚 Enseñar Caso" 
para que el sistema aprenda y lo reconozca en el futuro.
        """)

    # ── SUGERENCIA DE GUÍA PASO A PASO ──────────────────────
    tipo_detectado = _detectar_tipo_simple(problema)
    if tipo_detectado != "general":
        st.markdown("---")
        st.markdown("### 📋 ¿Quieres instrucciones paso a paso?")
        st.markdown(f"Detecté que esto es un caso de **{tipo_detectado}**.")
        st.info("Ve a la sección **📋 Guías Paso a Paso** del menú para obtener instrucciones detalladas con cada SQL y checklist de verificación.")


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _interpretar_problema(problema: str) -> str:
    """Genera una interpretación humana del problema"""
    p = problema.lower()
    partes = []

    # Detectar acción
    if "cambio" in p or "cambiar" in p:
        partes.append("Quieres **cambiar** algo")
    elif "actualizar" in p or "update" in p:
        partes.append("Quieres **actualizar** un registro")
    elif "ver" in p or "consultar" in p or "mostrar" in p:
        partes.append("Quieres **consultar** información")
    elif "ayudar" in p or "ayuda" in p:
        partes.append("Necesitas **ayuda** para resolver algo")
    else:
        partes.append("Tienes una **consulta**")

    # Detectar sobre qué
    if "estado" in p:
        estados = re.findall(r'\b(7[0-9])\b', problema)
        if len(estados) >= 2:
            partes.append(f"del **estado {estados[0]} → {estados[1]}** en liquidaciones")
        elif len(estados) == 1:
            partes.append(f"del **estado {estados[0]}** en liquidaciones")
        else:
            partes.append("del **estado de liquidación**")

    if "comision" in p or "comisión" in p:
        partes.append("relacionado con **comisiones**")

    if "vendedor" in p:
        partes.append("de un **vendedor**")

    # Detectar crédito
    creditos = re.findall(r'\b\d{13,16}\b', problema)
    if creditos:
        partes.append(f"para el crédito **{creditos[0]}**")

    if partes:
        return " ".join(partes) + "."
    return "Consulta general sobre el sistema PQRS."


def _advertir_si_sql_dudoso(problema: str, sql: str) -> None:
    """Advierte si el SQL generado no parece correcto para la pregunta"""
    p = problema.lower()
    sql_upper = sql.upper()

    # Pidió cambiar pero le dio un SELECT
    if ("cambio" in p or "cambiar" in p or "actualizar" in p) and sql_upper.strip().startswith("SELECT"):
        st.warning("""
⚠️ **Atención:** Pediste un **cambio** pero el sistema generó una **consulta (SELECT)**.

Esto pasa cuando el caso guardado más similar es una consulta.
Revisa los otros casos similares abajo, o agrega el caso correcto en "📚 Enseñar Caso".
        """)

    # UPDATE sin WHERE
    if "UPDATE" in sql_upper and "WHERE" not in sql_upper:
        st.error("❌ **PELIGRO:** El SQL no tiene cláusula WHERE — afectaría TODOS los registros. No ejecutes esto.")


def _detectar_tipo_simple(problema: str) -> str:
    """Detecta tipo de problema de forma simple"""
    p = problema.lower()
    if "estado" in p:
        return "cambio de estado"
    elif "comision" in p or "comisión" in p:
        return "cambio de comisión"
    elif "vendedor" in p:
        return "actualización de vendedor"
    return "general"


def _mostrar_sin_resultados(problema: str):
    """Muestra mensaje amigable cuando no hay resultados"""
    st.error("❌ No encontré ningún caso similar en la base de conocimiento.")
    st.markdown("""
### 💡 ¿Qué puedes hacer?

1. **Intenta con más detalles:**
   - Incluye el número de crédito
   - Menciona el estado actual y el deseado
   - Usa palabras como "cambiar", "actualizar", "comisión", "estado"

2. **Ejemplo de consulta buena:**
   > *"Para el crédito 5800325002956151 necesito cambiar el estado de 71 a 77"*

3. **Si sabes la solución:**
   - Ve a **📚 Enseñar Caso** y agrega este caso
   - La próxima vez el sistema lo encontrará

4. **Revisa las guías:**
   - Ve a **📋 Guías Paso a Paso** para instrucciones manuales
    """)


__all__ = ['mostrar_pagina_resolver_mejorada']
