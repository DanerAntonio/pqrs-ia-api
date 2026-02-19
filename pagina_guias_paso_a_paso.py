"""
Página de Guías Paso a Paso - Interactiva
"""

import streamlit as st
from guia_paso_a_paso import GuiaPasoAPaso, detectar_tipo_problema
import re
from typing import Dict
import pandas as pd


def mostrar_pagina_guias():
    """Página con guías paso a paso interactivas"""
    
    # UN SOLO HEADER (sin duplicar)
    # Ya está definido en app_streamlit_pqrs.py, NO repetir aquí
    
    # Inicializar motor de guías
    if "motor_guias" not in st.session_state:
        st.session_state.motor_guias = GuiaPasoAPaso()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Nueva Guía", "📚 Guías Disponibles", "📊 Mis Guías"])
    
    with tab1:
        mostrar_nueva_guia()
    
    with tab2:
        mostrar_catalogo_guias()
    
    with tab3:
        mostrar_historial_guias()


def mostrar_nueva_guia():
    """Genera una guía nueva para un problema"""
    
    st.markdown("### Describe el problema")
    
    problema = st.text_area(
        "¿Qué PQRS necesitas resolver?",
        placeholder="Ejemplo: Para el crédito 5800325002956151 necesito cambiar el estado de liquidación a Aprobado Jefe",
        height=100,
        key="problema_guia"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        generar = st.button("🚀 Generar Guía", type="primary", use_container_width=True)
    
    with col2:
        limpiar = st.button("🔄 Limpiar", use_container_width=True)
    
    if limpiar:
        st.rerun()
    
    if generar and problema:
        with st.spinner("🤖 Generando guía personalizada..."):
            # Detectar tipo
            tipo = detectar_tipo_problema(problema)
            
            # Extraer contexto
            contexto = extraer_contexto_problema(problema)
            
            # Obtener guía
            guia = st.session_state.motor_guias.obtener_guia(tipo, contexto)
            
            # Guardar en sesión
            if "guia_actual" not in st.session_state:
                st.session_state.guia_actual = {}
            
            st.session_state.guia_actual = {
                "guia": guia,
                "problema": problema,
                "contexto": contexto,
                "pasos_completados": [],
                "timestamp": str(pd.Timestamp.now())
            }
            
            # Mostrar guía
            mostrar_guia_interactiva(guia, problema, contexto)


def mostrar_guia_interactiva(guia, problema, contexto):
    """Muestra la guía de forma interactiva"""
    
    st.markdown("---")
    
    # Header de la guía
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### {guia['titulo']}")
        st.markdown(f"*{guia['descripcion']}*")
    
    with col2:
        st.metric("⏱️ Tiempo", f"{guia['tiempo_estimado']} min")
    
    with col3:
        st.metric("🎯 Dificultad", guia.get('dificultad', 'Media'))
    
    # Barra de progreso
    st.markdown("<br>", unsafe_allow_html=True)
    total_pasos = len(guia['pasos'])
    completados = len(st.session_state.guia_actual.get('pasos_completados', []))
    progreso = completados / total_pasos if total_pasos > 0 else 0
    
    st.markdown(f"**Progreso: {completados}/{total_pasos} pasos**")
    st.progress(progreso)
    
    # Mostrar pasos
    st.markdown("---")
    st.markdown("### 📝 Pasos a Seguir")
    
    for paso in guia['pasos']:
        mostrar_paso_interactivo(paso, contexto)
    
    # Sección de notas adicionales
    if "notas_adicionales" in guia:
        st.markdown("---")
        st.markdown("### 📌 Notas Adicionales")
        for nota in guia["notas_adicionales"]:
            st.info(nota)
    
    # Botones de acción
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Guardar Guía", use_container_width=True):
            guardar_guia_historial(guia, problema)
            st.success("✅ Guía guardada")
    
    with col2:
        checklist = st.session_state.motor_guias.generar_checklist_texto(guia)
        st.download_button(
            label="📋 Exportar TXT",
            data=checklist,
            file_name=f"guia_{guia['tipo']}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col3:
        if st.button("🔄 Nueva Guía", use_container_width=True):
            st.session_state.guia_actual = {}
            st.rerun()


def mostrar_paso_interactivo(paso, contexto):
    """Muestra un paso individual de forma interactiva"""
    
    # Check si está completado
    completados = st.session_state.guia_actual.get('pasos_completados', [])
    esta_completado = paso['numero'] in completados
    
    # Icono según estado
    icono = "✅" if esta_completado else "⏳"
    estado = "Completado" if esta_completado else "Pendiente"
    
    with st.expander(f"{icono} **Paso {paso['numero']}: {paso['titulo']}** ({estado})", expanded=not esta_completado):
        
        st.markdown(f"**{paso['descripcion']}**")
        st.markdown(f"⏱️ Tiempo estimado: {paso.get('tiempo', 1)} minuto(s)")
        
        st.markdown("---")
        
        # SQL si existe
        if "sql" in paso:
            st.markdown("#### 💻 SQL a Ejecutar:")
            
            # Reemplazar contexto
            sql = paso["sql"]
            for key, value in contexto.items():
                placeholder = f"[{key.upper()}]"
                if placeholder in sql:
                    sql = sql.replace(placeholder, str(value))
            
            st.code(sql, language="sql")
        
        # Instrucciones
        if "instrucciones" in paso:
            st.markdown("#### 📋 Instrucciones:")
            for inst in paso["instrucciones"]:
                st.markdown(f"• {inst}")
        
        # Advertencias
        if "advertencias" in paso:
            st.markdown("#### ⚠️ Advertencias:")
            for adv in paso["advertencias"]:
                st.warning(adv)
        
        # Ejemplo
        if "ejemplo" in paso:
            st.markdown("#### 💡 Ejemplo:")
            st.info(paso["ejemplo"])
        
        # Botón de completar
        st.markdown("---")
        if not esta_completado:
            if st.button(f"✅ Marcar como Completado", key=f"complete_{paso['numero']}", type="primary"):
                completados.append(paso['numero'])
                st.session_state.guia_actual['pasos_completados'] = completados
                st.rerun()
        else:
            if st.button(f"↩️ Marcar como Pendiente", key=f"uncomplete_{paso['numero']}"):
                completados.remove(paso['numero'])
                st.session_state.guia_actual['pasos_completados'] = completados
                st.rerun()


def mostrar_catalogo_guias():
    """Muestra el catálogo de guías disponibles"""
    
    st.markdown("### 📚 Catálogo de Guías Disponibles")
    
    guias_disponibles = {
        "🔄 Cambio de Estado": {
            "tipo": "cambio_estado",
            "descripcion": "Actualizar el estado de liquidación de un crédito",
            "tiempo": "5 min",
            "dificultad": "Fácil"
        },
        "💰 Cambio de Comisión": {
            "tipo": "cambio_comision",
            "descripcion": "Corregir o actualizar valores de comisión",
            "tiempo": "7 min",
            "dificultad": "Media"
        },
        "👤 Actualizar Vendedor": {
            "tipo": "actualizar_vendedor",
            "descripcion": "Cambiar datos bancarios u otra info del vendedor",
            "tiempo": "8 min",
            "dificultad": "Media-Alta"
        },
        "📝 Guía General": {
            "tipo": "generico",
            "descripcion": "Pasos generales para resolver cualquier PQRS",
            "tiempo": "10 min",
            "dificultad": "Variable"
        }
    }
    
    for nombre, info in guias_disponibles.items():
        with st.expander(f"{nombre}"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**Descripción:** {info['descripcion']}")
            
            with col2:
                st.markdown(f"**Tiempo:** {info['tiempo']}")
            
            with col3:
                st.markdown(f"**Dificultad:** {info['dificultad']}")
            
            if st.button(f"📖 Ver Guía Completa", key=f"ver_{info['tipo']}"):
                guia = st.session_state.motor_guias.obtener_guia(info['tipo'])
                st.session_state.guia_actual = {
                    "guia": guia,
                    "problema": f"Guía de: {nombre}",
                    "contexto": {},
                    "pasos_completados": []
                }
                st.rerun()


def mostrar_historial_guias():
    """Muestra el historial de guías usadas"""
    
    st.markdown("### 📊 Tu Historial de Guías")
    
    if "historial_guias" not in st.session_state or not st.session_state.historial_guias:
        st.info("📋 Aún no has guardado ninguna guía. Genera una y guárdala para verla aquí.")
        return
    
    for i, item in enumerate(reversed(st.session_state.historial_guias), 1):
        with st.expander(f"Guía #{i} - {item['guia']['titulo']}"):
            st.markdown(f"**Problema:** {item['problema']}")
            st.markdown(f"**Fecha:** {item.get('fecha', 'N/A')}")
            
            progreso = len(item.get('pasos_completados', []))
            total = len(item['guia']['pasos'])
            st.markdown(f"**Progreso:** {progreso}/{total} pasos")
            
            if st.button(f"🔄 Cargar Esta Guía", key=f"load_{i}"):
                st.session_state.guia_actual = item
                st.rerun()


def extraer_contexto_problema(problema: str) -> Dict:
    """Extrae información relevante del problema"""
    contexto = {}
    
    # Buscar número de crédito
    creditos = re.findall(r'\b\d{13,16}\b', problema)
    if creditos:
        contexto['credito'] = creditos[0]
    
    # Buscar valores (montos)
    valores = re.findall(r'\$?(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)', problema)
    if valores:
        valor = valores[0].replace(',', '').replace('.', '')
        contexto['valor'] = valor
    
    # Buscar estados
    estados = re.findall(r'\b(7[0-9])\b', problema)
    if estados:
        contexto['estado'] = estados[0]
    
    # Buscar cédulas
    cedulas = re.findall(r'\b\d{8,11}\b', problema)
    if cedulas:
        for cedula in cedulas:
            if len(cedula) < 13:
                contexto['cedula'] = cedula
                break
    
    return contexto


def guardar_guia_historial(guia, problema):
    """Guarda una guía en el historial"""
    if "historial_guias" not in st.session_state:
        st.session_state.historial_guias = []
    
    item = {
        "guia": guia,
        "problema": problema,
        "fecha": str(pd.Timestamp.now()),
        "pasos_completados": st.session_state.guia_actual.get('pasos_completados', [])
    }
    
    st.session_state.historial_guias.append(item)


__all__ = ['mostrar_pagina_guias']