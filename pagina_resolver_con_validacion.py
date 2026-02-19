"""
Página de Resolución de PQRS con Validación Automática - SIN HEADERS DUPLICADOS
"""

import streamlit as st
from validador_automatico import ValidadorAutomatico
import re


def mostrar_pagina_resolver_con_validacion():
    """Página para resolver PQRS con validación automática"""
    
    # NO PONER HEADER AQUÍ - Ya está en app_streamlit_pqrs.py
    
    # Verificar que el sistema esté disponible
    if "sistema" not in st.session_state or st.session_state.sistema is None:
        st.error("⚠️ Sistema PQRS no inicializado.")
        return
    
    # Inicializar validador
    if "validador" not in st.session_state:
        st.session_state.validador = ValidadorAutomatico(st.session_state.sistema)
    
    # Tabs para diferentes modos
    tab1, tab2, tab3 = st.tabs(["🔍 Resolver Nuevo", "📋 Historial", "⚙️ Configuración"])
    
    with tab1:
        mostrar_formulario_resolucion()
    
    with tab2:
        mostrar_historial_validaciones()
    
    with tab3:
        mostrar_configuracion_validacion()


def mostrar_formulario_resolucion():
    """Formulario principal de resolución"""
    
    st.markdown("### Describe el problema (PQRS)")
    
    # Input del problema
    problema = st.text_area(
        "Descripción del caso",
        placeholder="Ejemplo: Para el crédito 5800325002956151 necesito cambiar el estado de liquidación a Aprobado Jefe Coordinador",
        height=120,
        key="problema_validacion"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        buscar = st.button("🔍 Analizar y Validar", use_container_width=True, type="primary")
    
    with col2:
        limpiar = st.button("🔄 Limpiar", use_container_width=True)
    
    if limpiar:
        st.rerun()
    
    if buscar and problema and st.session_state.sistema:
        with st.spinner("🤖 Analizando y validando..."):
            # PASO 1: Buscar solución
            ranking = st.session_state.sistema.buscar_similar_ia(problema)
            
            if not ranking or len(ranking) == 0:
                st.warning("No se encontró solución similar.")
                return
            
            mejor_caso = ranking[0]
            
            # PASO 2: Generar SQL
            valores = st.session_state.sistema.extraer_valores(problema)
            sql_generado = st.session_state.sistema.reemplazar_valores(mejor_caso['sql'], valores)
            
            # PASO 3: Detectar tipo de operación
            tipo_operacion = detectar_tipo_operacion(problema, sql_generado)
            
            # PASO 4: Extraer datos de contexto
            datos_contexto = extraer_datos_contexto(problema, sql_generado, tipo_operacion)
            
            # PASO 5: VALIDAR AUTOMÁTICAMENTE
            resultado_validacion = st.session_state.validador.validar_operacion_completa(
                sql=sql_generado,
                tipo_operacion=tipo_operacion,
                datos_contexto=datos_contexto
            )
            
            # Mostrar resultados
            mostrar_resultado_validacion(
                mejor_caso=mejor_caso,
                sql_generado=sql_generado,
                tipo_operacion=tipo_operacion,
                validacion=resultado_validacion
            )


def mostrar_resultado_validacion(mejor_caso, sql_generado, tipo_operacion, validacion):
    """Muestra el resultado de la validación"""
    
    # Card de resultado general
    if validacion["puede_ejecutar"]:
        if validacion["requiere_aprobacion"]:
            color = "#f59e0b"
            icono = "⚠️"
            titulo = "REQUIERE APROBACIÓN"
        else:
            color = "#10b981"
            icono = "✅"
            titulo = "PUEDE EJECUTARSE AUTOMÁTICAMENTE"
    else:
        color = "#ef4444"
        icono = "❌"
        titulo = "OPERACIÓN BLOQUEADA"
    
    st.markdown(f"""
        <div style='background: {color}20; border: 2px solid {color}; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;'>
            <h2 style='color: {color}; margin: 0;'>{icono} {titulo}</h2>
            <p style='color: #cbd5e1; margin-top: 0.5rem;'>{validacion['razon_principal']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Información del caso encontrado
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.metric("📦 Caso Similar", mejor_caso['categoria'])
        st.metric("🎯 Similitud", f"{mejor_caso['similitud']*100:.0f}%")
    
    with col2:
        st.metric("🔧 Tipo de Operación", tipo_operacion.replace('_', ' ').title())
        st.metric("👤 Nivel Aprobación", validacion.get('nivel_aprobacion', 'N/A').title())
    
    # SQL Generado
    st.markdown("### 💻 SQL Generado")
    st.code(sql_generado, language="sql")
    
    # Resumen de validación
    st.markdown("### 📋 Resumen de Validación")
    resumen = st.session_state.validador.generar_resumen_validacion(validacion)
    st.markdown(resumen)
    
    # Acciones disponibles
    st.markdown("### 🎯 Acciones Disponibles")
    
    if validacion["puede_ejecutar"]:
        if validacion["requiere_aprobacion"]:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("✅ Aprobar y Ejecutar", key="aprobar", use_container_width=True):
                    st.success("✅ Operación aprobada y ejecutada (SIMULADO)")
                    st.balloons()
            
            with col2:
                if st.button("❌ Rechazar", key="rechazar", use_container_width=True):
                    st.error("Operación rechazada")
            
            with col3:
                if st.button("💬 Más Información", key="mas_info", use_container_width=True):
                    with st.expander("📊 Detalles Completos", expanded=True):
                        st.json(validacion)
        else:
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🚀 Ejecutar Automáticamente", key="ejecutar_auto", type="primary", use_container_width=True):
                    st.success("✅ Ejecutado automáticamente (SIMULADO)")
                    st.balloons()
            
            with col2:
                if st.button("📋 Solo Copiar SQL", key="copiar", use_container_width=True):
                    st.success("✅ SQL copiado (simulado)")
    else:
        st.error("⛔ Esta operación está bloqueada y no puede ejecutarse")
    
    # Respuesta para el usuario final
    st.markdown("### 📨 Respuesta Sugerida")
    st.info(mejor_caso['respuesta'])


def mostrar_historial_validaciones():
    """Muestra el historial de validaciones"""
    
    st.markdown("### 📋 Historial de Validaciones")
    
    if not hasattr(st.session_state, "validador") or not st.session_state.validador.historial_validaciones:
        st.info("No hay validaciones en el historial")
        return
    
    historial = st.session_state.validador.historial_validaciones
    
    # Estadísticas
    col1, col2, col3, col4 = st.columns(4)
    
    total = len(historial)
    aprobadas = sum(1 for v in historial if not v.get("requiere_aprobacion"))
    bloqueadas = sum(1 for v in historial if not v.get("puede_ejecutar"))
    pendientes = total - aprobadas - bloqueadas
    
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Auto-aprobadas", aprobadas)
    with col3:
        st.metric("Requieren Aprobación", pendientes)
    with col4:
        st.metric("Bloqueadas", bloqueadas)
    
    # Lista
    st.markdown("---")
    
    for i, val in enumerate(reversed(historial), 1):
        with st.expander(f"Validación #{total - i + 1} - {val['razon_principal'][:50]}..."):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Timestamp:** {val['timestamp']}")
                st.write(f"**Puede ejecutar:** {'✅' if val['puede_ejecutar'] else '❌'}")
            
            with col2:
                st.write(f"**Requiere aprobación:** {'⚠️' if val.get('requiere_aprobacion') else '✅'}")
                st.write(f"**Nivel:** {val.get('nivel_aprobacion', 'N/A')}")
            
            st.code(val.get("sql_validado", ""), language="sql")
    
    # Exportar
    if st.button("💾 Exportar Historial"):
        if st.session_state.validador.exportar_historial():
            st.success("✅ Exportado a historial_validaciones.json")


def mostrar_configuracion_validacion():
    """Configuración del validador"""
    
    st.markdown("### ⚙️ Configuración de Validación")
    
    st.info("🚧 Próximamente")
    
    st.checkbox("Ejecutar automáticamente operaciones de bajo riesgo", value=True, disabled=True)
    st.checkbox("Notificar por email cuando se requiere aprobación", value=False, disabled=True)
    st.slider("Umbral de similitud mínima", 0, 100, 50, disabled=True)


def detectar_tipo_operacion(problema: str, sql: str) -> str:
    """Detecta el tipo de operación"""
    problema_lower = problema.lower()
    sql_upper = sql.upper()
    
    if "estado" in problema_lower and "SET ESTADOLIQUIDACION" in sql_upper:
        return "cambio_estado"
    elif "comision" in problema_lower or "comisión" in problema_lower:
        return "cambio_comision"
    elif "vendedor" in problema_lower and "USERID" in sql_upper:
        return "actualizar_vendedor"
    else:
        return "operacion_general"


def extraer_datos_contexto(problema: str, sql: str, tipo: str) -> dict:
    """Extrae datos de contexto"""
    contexto = {}
    
    # Extraer crédito
    creditos = re.findall(r'\d{13,16}', problema)
    if creditos:
        contexto["credit_number"] = creditos[0]
    
    # Según tipo
    if tipo == "cambio_estado":
        matches = re.findall(r'EstadoLiquidacion\w+\s*=\s*(\d+)', sql, re.IGNORECASE)
        if matches:
            contexto["estado_nuevo"] = int(matches[0])
        contexto["estado_actual"] = 71  # Placeholder
    
    elif tipo == "cambio_comision":
        matches = re.findall(r'ValueCommission\s*=\s*(\d+)', sql, re.IGNORECASE)
        if matches:
            contexto["valor_nuevo"] = int(matches[0])
        contexto["valor_actual"] = 250000  # Placeholder
    
    return contexto


__all__ = ['mostrar_pagina_resolver_con_validacion']