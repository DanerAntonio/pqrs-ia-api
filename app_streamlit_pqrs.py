import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import re
from pathlib import Path

st.set_page_config(
    page_title="Agente AI - PQRS Inteligente",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    :root {
        --primary: #6366f1; --primary-dark: #4f46e5; --secondary: #ec4899;
        --success: #10b981; --warning: #f59e0b; --danger: #ef4444;
        --background: #0f172a; --surface: #1e293b; --surface-light: #334155;
        --text: #f1f5f9; --text-muted: #94a3b8; --border: #334155;
    }
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%); border-right: 1px solid var(--border); }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: var(--text); font-weight: 500; }
    .main-header { background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%); padding: 2rem; border-radius: 16px; margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(99,102,241,0.3); animation: slideDown 0.6s ease-out; }
    .main-header h1 { color: white; font-size: 2.5rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
    .main-header p { color: rgba(255,255,255,0.9); font-size: 1.1rem; margin-top: 0.5rem; font-weight: 300; }
    .metric-card { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; transition: all 0.3s ease; animation: fadeIn 0.6s ease-out; }
    .metric-card:hover { transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0,0,0,0.3); border-color: var(--primary); }
    .metric-value { font-size: 2.5rem; font-weight: 700; background: linear-gradient(135deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0.5rem 0; }
    .metric-label { color: var(--text-muted); font-size: 0.9rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; }
    .chat-message { padding: 1rem 1.5rem; border-radius: 12px; margin: 0.5rem 0; }
    .chat-message.user { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; margin-left: 20%; }
    .chat-message.assistant { background: var(--surface-light); color: var(--text); margin-right: 20%; border: 1px solid var(--border); }
    .stButton > button { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; border: none; border-radius: 8px; padding: 0.75rem 2rem; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(99,102,241,0.3); }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(99,102,241,0.4); }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); padding: 0.75rem 1rem; font-size: 1rem; }
    .stProgress > div > div > div { background: linear-gradient(90deg, var(--primary), var(--secondary)); border-radius: 4px; }
    .badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.85rem; font-weight: 600; margin: 0.25rem; }
    .badge-success { background: rgba(16,185,129,0.2); color: var(--success); border: 1px solid var(--success); }
    .badge-warning { background: rgba(245,158,11,0.2); color: var(--warning); border: 1px solid var(--warning); }
    .badge-info { background: rgba(99,102,241,0.2); color: var(--primary); border: 1px solid var(--primary); }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideIn { from { opacity: 0; transform: translateX(-10px); } to { opacity: 1; transform: translateX(0); } }
    ::-webkit-scrollbar { width: 8px; } ::-webkit-scrollbar-track { background: var(--background); }
    ::-webkit-scrollbar-thumb { background: var(--surface-light); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--primary); }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: var(--surface); padding: 0.5rem; border-radius: 12px; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 8px; color: var(--text-muted); font-weight: 500; padding: 0.75rem 1.5rem; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, var(--primary), var(--primary-dark)); color: white; }
    .stSelectbox > div > div { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; }
    .stRadio > div { background: var(--surface); padding: 1rem; border-radius: 12px; border: 1px solid var(--border); }
    .streamlit-expanderHeader { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; color: var(--text); font-weight: 500; }
</style>
""", unsafe_allow_html=True)

sys.path.append(str(Path(__file__).parent))

try:
    from sistema_pqrs_v4_ia import SistemaPQRSIA as SistemaPQRSUltra
    SISTEMA_DISPONIBLE = True
except:
    st.error("⚠️ No se encontró el sistema PQRS")
    SistemaPQRSUltra = None
    SISTEMA_DISPONIBLE = False

@st.cache_resource
def inicializar_sistema():
    if SISTEMA_DISPONIBLE:
        return SistemaPQRSUltra()
    return None

if 'sistema' not in st.session_state:
    st.session_state.sistema = inicializar_sistema()

# ════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='font-size: 2.5rem; margin: 0;'>🤖</h1>
            <h3 style='color: #6366f1; margin: 0.5rem 0;'>Agente AI</h3>
            <p style='color: #94a3b8; font-size: 0.9rem;'>Sistema Inteligente de PQRS</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio(
        "Navegación",
        ["🏠 Inicio", "💬 Chat AI", "🔍 Resolver PQRS", "🛡️ Validación Auto",
         "📋 Guías Paso a Paso", "📚 Enseñar Caso", "📊 Métricas", "⚙️ Configuración"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    if st.session_state.sistema:
        try:
            total_casos = len(st.session_state.sistema.obtener_todos_casos())
        except:
            total_casos = 27
        st.markdown(f"""
            <div style='background:rgba(99,102,241,0.1);padding:1rem;border-radius:8px;border:1px solid #6366f1;'>
                <p style='color:#94a3b8;font-size:0.8rem;margin:0;'>CASOS EN BASE</p>
                <p style='color:#6366f1;font-size:1.5rem;font-weight:700;margin:0.5rem 0 0 0;'>{total_casos}</p>
            </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════
# INICIO
# ════════════════════════════════════════
if page == "🏠 Inicio":
    st.markdown("<div class='main-header'><h1>🤖 Agente AI para PQRS</h1><p>Sistema inteligente de automatización impulsado por IA</p></div>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("<div class='metric-card'><p class='metric-label'>Casos Totales</p><p class='metric-value'>27</p><p style='color:#10b981;font-size:0.9rem;'>↑ Base inicial</p></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><p class='metric-label'>Precisión IA</p><p class='metric-value'>92%</p><p style='color:#10b981;font-size:0.9rem;'>↑ Alta confianza</p></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-card'><p class='metric-label'>Tiempo Ahorrado</p><p class='metric-value'>85%</p><p style='color:#10b981;font-size:0.9rem;'>↑ vs. manual</p></div>", unsafe_allow_html=True)
    with col4:
        st.markdown("<div class='metric-card'><p class='metric-label'>Ahorro Mensual</p><p class='metric-value'>$4.8K</p><p style='color:#10b981;font-size:0.9rem;'>↑ USD/mes</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='metric-card'><h3 style='color:#6366f1;margin-top:0;'>✨ Características</h3><ul style='color:#cbd5e1;line-height:1.8;'><li><strong>Búsqueda Semántica:</strong> Entiende el significado</li><li><strong>Generación SQL:</strong> Automática</li><li><strong>Aprendizaje:</strong> Mejora con cada caso</li><li><strong>Guías:</strong> Paso a paso</li></ul></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-card'><h3 style='color:#ec4899;margin-top:0;'>🚀 Próximos Pasos</h3><ul style='color:#cbd5e1;line-height:1.8;'><li><strong>Claude API:</strong> Conversación natural</li><li><strong>Conexión BD:</strong> Validación real</li><li><strong>Multi-área:</strong> RH, Finanzas</li><li><strong>Dashboard:</strong> Analíticas avanzadas</li></ul></div>", unsafe_allow_html=True)

# ════════════════════════════════════════
# CHAT AI
# ════════════════════════════════════════
elif page == "💬 Chat AI":
    st.markdown("<div class='main-header'><h1>💬 Chat con el Agente AI</h1><p>Conversa de forma natural con el asistente</p></div>", unsafe_allow_html=True)
    try:
        from pagina_chat import mostrar_pagina_chat
        mostrar_pagina_chat()
    except ImportError:
        st.error("⚠️ Módulo de chat no disponible")

# ════════════════════════════════════════
# RESOLVER PQRS  ← SOLO UNA VEZ
# ════════════════════════════════════════
elif page == "🔍 Resolver PQRS":
    st.markdown("<div class='main-header'><h1>🔍 Resolver PQRS</h1><p>Describe tu problema y el AI encontrará la solución más adecuada</p></div>", unsafe_allow_html=True)

    problema = st.text_area(
        "💬 Describe tu consulta o problema",
        placeholder="Ejemplo: me puedes ayudar con cambio de estado 71 a 77 para el crédito 5800325002956151",
        height=110,
        key="problema_input"
    )

    col1, col2 = st.columns(2)
    with col1:
        buscar = st.button("🔍 Buscar Solución", use_container_width=True, type="primary")
    with col2:
        limpiar = st.button("🔄 Limpiar", use_container_width=True)

    if limpiar:
        st.rerun()

    if buscar and problema and st.session_state.sistema:
        with st.spinner("🤔 Déjame revisar mis casos... un momento..."):
            ranking = st.session_state.sistema.buscar_similar_ia(problema)

        if not ranking or len(ranking) == 0:
            st.markdown("""
<div style="background:#ef444418;border-left:5px solid #ef4444;border-radius:8px;padding:1.2rem 1.5rem;margin:1rem 0;">
<strong style="color:#ef4444;font-size:1.1rem;">😔 Hmm, no encontré nada parecido en mis casos guardados</strong><br><br>
<span style="color:#cbd5e1;">Todavía no tengo este caso en mi base de conocimiento.</span>
</div>
            """, unsafe_allow_html=True)
            st.markdown("""
**¿Qué puedes hacer?**

👉 **Intenta describir diferente**, con más detalles:
- *"Para el crédito 5800325002956151 cambiar estado de 71 a 77"*
- *"Actualizar comisión del vendedor con cédula 12345678"*

👉 **¿Ya sabes la solución?** Enséñamela en **📚 Enseñar Caso**
y la próxima vez la encontraré sola 😊
            """)
        else:
            mejor = ranking[0]
            similitud = mejor['similitud'] * 100

            # Banner confianza - más humano
            if similitud >= 85:
                color_b, icono_b = "#10b981", "✅"
                titulo_b = "¡Encontré exactamente lo que necesitas!"
                texto_b = f"Tengo un caso muy parecido al tuyo con {similitud:.0f}% de similitud. Revisa el SQL abajo."
            elif similitud >= 60:
                color_b, icono_b = "#f59e0b", "🤔"
                titulo_b = "Encontré algo parecido, pero verifica"
                texto_b = f"Este caso es similar en un {similitud:.0f}% pero puede que no sea exactamente lo que buscas. Revisa también las otras opciones abajo."
            else:
                color_b, icono_b = "#ef4444", "🔎"
                titulo_b = "No estoy muy seguro de esta respuesta"
                texto_b = f"Solo hay un {similitud:.0f}% de similitud con casos guardados. Te muestro lo más cercano que tengo, pero revisa bien las otras opciones y si ninguna sirve, enséñame el caso correcto."

            st.markdown(f"""
                <div style="background:{color_b}18;border-left:5px solid {color_b};
                            border-radius:8px;padding:1.2rem 1.5rem;margin:1rem 0 1.5rem 0;">
                    <strong style="color:{color_b};font-size:1.15rem;">{icono_b} {titulo_b}</strong><br>
                    <span style="color:#cbd5e1;font-size:0.95rem;">{texto_b}</span>
                </div>
            """, unsafe_allow_html=True)

            # Interpretación humana
            p = problema.lower()
            estados = re.findall(r'\b(7[0-9])\b', problema)
            creditos = re.findall(r'\b\d{13,16}\b', problema)

            if ("cambio" in p or "cambiar" in p or "ayudar" in p) and "estado" in p and len(estados) >= 2:
                cr = f" del crédito **{creditos[0]}**" if creditos else ""
                st.info(f"🧠 Claro, me parece que quieres **cambiar el estado de {estados[0]} a {estados[1]}**{cr}. Aquí te ayudo con eso:")
            elif ("cambio" in p or "cambiar" in p or "ayudar" in p) and "estado" in p:
                st.info("🧠 Entendí que necesitas **cambiar el estado** de una liquidación. ¿Puedes indicarme el estado actual y el que deseas?")
            elif "comision" in p or "comisión" in p:
                st.info("🧠 Veo que tu consulta es sobre **comisiones**. Aquí tienes lo que encontré:")
            elif "vendedor" in p:
                st.info("🧠 Entendí que necesitas **actualizar datos de un vendedor**. Aquí tienes los pasos:")
            elif "certificado" in p:
                st.info("🧠 Entendí que necesitas algo relacionado con **certificados**. Mira esto:")
            elif "banco" in p or "cuenta" in p:
                st.info("🧠 Parece que tienes una consulta sobre **datos bancarios**. Aquí te ayudo:")
            else:
                st.info(f"🧠 Encontré casos relacionados con **{mejor['categoria']}**. Revisa si esto te sirve:")

            # Mejor resultado
            st.markdown("### 🥇 Mejor Solución Encontrada")
            valores = st.session_state.sistema.extraer_valores(problema)
            sql_final = st.session_state.sistema.reemplazar_valores(mejor['sql'], valores)

            # Advertir si pidió cambio pero llegó SELECT
            if ("cambio" in p or "cambiar" in p or "ayudar" in p) and sql_final.strip().upper().startswith("SELECT"):
                st.warning(
                    "🤔 **Ojo:** Pediste un **cambio** pero el caso más parecido que tengo guardado "
                    "es una **consulta** (SELECT, que solo lee datos). Probablemente lo que necesitas "
                    "está en las **Otras Opciones** de abajo. Si ninguna sirve, "
                    "enséñame el caso correcto en **📚 Enseñar Caso** 👇"
                )

            st.markdown(f"**Categoría:** `{mejor['categoria']}` &nbsp;&nbsp; **Similitud:** `{similitud:.0f}%`")
            st.markdown(f"*Caso base: {mejor['problema']}*")
            st.markdown("**💻 SQL generado:**")
            st.code(sql_final, language="sql")
            st.markdown("**💬 Respuesta sugerida:**")
            st.success(mejor['respuesta'])

            # ── OTROS CASOS SIMILARES con SQL y respuesta completa ──
            if len(ranking) > 1:
                st.markdown("---")
                st.markdown("### 📚 Otras Opciones que Pueden Ayudarte")
                st.caption("¿El resultado de arriba no era lo que buscabas? Aquí hay más casos parecidos. Cada uno tiene su SQL y respuesta — revísalos, puede que uno de estos sea exactamente lo que necesitas 👇")

                for i, caso in enumerate(ranking[1:5], 2):
                    sim_i = caso['similitud'] * 100
                    color_i = "#10b981" if sim_i >= 70 else "#f59e0b" if sim_i >= 45 else "#94a3b8"
                    sql_i = st.session_state.sistema.reemplazar_valores(caso['sql'], valores)

                    with st.expander(
                        f"📌 Opción {i}: {caso['categoria']} — {sim_i:.0f}% similitud",
                        expanded=(i == 2)
                    ):
                        st.markdown(f"**Caso guardado:** _{caso['problema']}_")
                        st.markdown("**💻 SQL:**")
                        st.code(sql_i, language="sql")
                        st.markdown("**💬 Respuesta:**")
                        st.info(caso['respuesta'])
                        if st.button("✅ Usar esta solución", key=f"usar_{i}"):
                            st.success("✅ Seleccionada. Copia el SQL de arriba.")

            # Aviso si confianza baja
            if similitud < 60:
                st.markdown("---")
                st.warning("""
😊 **No te preocupes si no encontraste lo que buscabas**

El sistema todavía está aprendiendo y aún no tiene este caso.
Puedes ayudarlo a mejorar:

1. Ve a **📚 Enseñar Caso**
2. Escribe el problema tal como te llega
3. Agrega el SQL correcto y la respuesta
4. Guárdalo — la próxima vez lo encontrará con 90%+ de precisión

¡Entre más casos le enseñes, más inteligente se vuelve! 🚀
                """)

# ════════════════════════════════════════
# VALIDACIÓN AUTO
# ════════════════════════════════════════
elif page == "🛡️ Validación Auto":
    st.markdown("<div class='main-header'><h1>🛡️ Resolución con Validación Automática</h1><p>Sistema inteligente que valida y aprueba operaciones</p></div>", unsafe_allow_html=True)
    try:
        from pagina_resolver_con_validacion import mostrar_pagina_resolver_con_validacion
        mostrar_pagina_resolver_con_validacion()
    except ImportError as e:
        st.error(f"⚠️ Error: {e}")

# ════════════════════════════════════════
# GUÍAS PASO A PASO
# ════════════════════════════════════════
elif page == "📋 Guías Paso a Paso":
    st.markdown("<div class='main-header'><h1>📋 Guías Paso a Paso</h1><p>Sistema inteligente que te guía en cada PQRS</p></div>", unsafe_allow_html=True)
    try:
        from pagina_guias_paso_a_paso import mostrar_pagina_guias
        mostrar_pagina_guias()
    except ImportError as e:
        st.error(f"⚠️ Error: {e}")

# ════════════════════════════════════════
# ENSEÑAR CASO
# ════════════════════════════════════════
elif page == "📚 Enseñar Caso":
    st.markdown("<div class='main-header'><h1>📚 Enseñar Caso Nuevo</h1><p>El sistema aprenderá de este caso para futuras consultas</p></div>", unsafe_allow_html=True)

    st.info("💡 **¿Sabías?** Cada caso que agregas hace al sistema más inteligente. Puede ser un caso con SQL o solo un procedimiento/validación. ¡Todo suma! 🚀")

    # Tabs para dos tipos de casos
    tab1, tab2 = st.tabs(["💻 Caso con SQL", "📋 Procedimiento/Validación"])

    with tab1:
        st.markdown("### Caso que requiere ejecutar SQL")
        st.caption("Ejemplo: Cambiar estado de liquidación, actualizar comisión, etc.")
        
        with st.form("form_caso_sql"):
            categoria_sql = st.selectbox("Categoría",
                ["Estados", "Comisiones", "Vendedor", "Liquidación",
                 "Certificados", "Correcciones", "Bancos", "Otro"],
                key="cat_sql")
            
            problema_sql = st.text_area("¿Qué problema resuelve este caso?", height=100,
                placeholder="Ejemplo: Para el crédito [CREDITO] cambiar estado de 71 a 77 aprobado jefe",
                key="prob_sql")
            
            sql_form = st.text_area("SQL de solución", height=150,
                placeholder="Ejemplo: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE CreditNumber = '[CREDITO]'",
                key="sql_text")
            
            respuesta_sql = st.text_area("Respuesta para el usuario final", height=100,
                placeholder="Ejemplo: Estado actualizado a 77 (Aprobado Jefe). La comisión entrará en el próximo ciclo.",
                key="resp_sql")

            submitted_sql = st.form_submit_button("💾 Guardar Caso SQL", use_container_width=True, type="primary")
            
            if submitted_sql:
                if problema_sql and sql_form and respuesta_sql:
                    try:
                        st.session_state.sistema.agregar_caso(categoria_sql, problema_sql, sql_form, respuesta_sql)
                        st.success("✅ ¡Caso agregado! El sistema ya puede encontrarlo.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Completa todos los campos")

    with tab2:
        st.markdown("### Procedimiento o Validación (sin SQL)")
        st.caption("Ejemplo: Cómo validar un pago, qué revisar cuando hay un reclamo, pasos de escalamiento, etc.")
        
        with st.form("form_procedimiento"):
            categoria_proc = st.selectbox("Categoría",
                ["Validación", "Procedimiento", "Escalamiento", "Soporte",
                 "Consulta", "Reclamo", "Verificación", "Otro"],
                key="cat_proc")
            
            problema_proc = st.text_area("¿Cuándo usar este procedimiento?", height=100,
                placeholder="Ejemplo: El vendedor dice que no le llegó su comisión pero el crédito ya está en estado 77",
                key="prob_proc")
            
            st.markdown("**Pasos del procedimiento:**")
            st.caption("Escribe los pasos que hay que seguir, qué validar, dónde revisar, etc.")
            
            proc_placeholder = """Ejemplo de procedimiento:

Para validar si la comisión se pagó:

1. Verifica que el crédito tenga estado 77 (Aprobado Jefe)
   SQL: SELECT EstadoLiquidacionVendedor FROM formatexceldlle WHERE CreditNumber = '[CREDITO]'

2. Revisa que el vendedor tenga datos bancarios completos
   - Ir a la sección de Vendedores
   - Buscar por cédula
   - Verificar que tenga BankID, AccountNumber y TypeAccountBankID

3. Consulta en el sistema de pagos si ya se procesó
   - Ir a Módulo de Pagos > Filtrar por período actual
   - Buscar el UserID del vendedor

4. Si todo está correcto pero no le llegó:
   - Escalar a nómina con los datos completos
   - Incluir evidencia de estado 77 y datos bancarios"""
            
            procedimiento = st.text_area("Procedimiento detallado", height=250,
                placeholder=proc_placeholder,
                key="proc_text")
            
            respuesta_proc = st.text_area("Resumen para el usuario final", height=100,
                placeholder="Ejemplo: Para validar esto, revisa: 1) Estado del crédito (debe ser 77), 2) Datos bancarios del vendedor, 3) Sistema de pagos. Si todo está bien, escala a nómina.",
                key="resp_proc")

            submitted_proc = st.form_submit_button("💾 Guardar Procedimiento", use_container_width=True, type="primary")
            
            if submitted_proc:
                if problema_proc and procedimiento and respuesta_proc:
                    try:
                        # Guardar como caso con el procedimiento en lugar del SQL
                        st.session_state.sistema.agregar_caso(
                            categoria_proc,
                            problema_proc,
                            procedimiento,  # En vez de SQL, guardamos el procedimiento
                            respuesta_proc
                        )
                        st.success("✅ ¡Procedimiento agregado! El sistema ya puede encontrarlo.")
                        st.balloons()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Completa todos los campos")
        
        st.markdown("---")
        st.info("""
**💡 Ejemplos de procedimientos útiles:**
- "Cómo validar si un pago ya se procesó"
- "Qué revisar cuando un vendedor reclama su comisión"
- "Pasos para escalar un caso a finanzas"
- "Cómo verificar datos bancarios de un vendedor"
- "Qué hacer cuando un crédito está pagado pero sigue pendiente"
        """)
elif page == "📊 Métricas":
    st.markdown("<div class='main-header'><h1>📊 Dashboard de Métricas</h1><p>Analíticas y estadísticas del sistema</p></div>", unsafe_allow_html=True)
    if st.session_state.sistema:
        try:
            casos = st.session_state.sistema.obtener_todos_casos()
        except:
            try:
                c = st.session_state.sistema.conn.cursor()
                c.execute('SELECT * FROM casos')
                casos = c.fetchall()
            except:
                casos = []
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='metric-card'><p class='metric-label'>Total de Casos</p><p class='metric-value'>{len(casos)}</p></div>", unsafe_allow_html=True)
        with col2:
            categorias = {}
            for caso in casos:
                cat = caso[1]; categorias[cat] = categorias.get(cat, 0) + 1
            st.markdown(f"<div class='metric-card'><p class='metric-label'>Categorías</p><p class='metric-value'>{len(categorias)}</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown("<div class='metric-card'><p class='metric-label'>Ahorro Estimado</p><p class='metric-value'>$4.8K</p><p style='color:#94a3b8;font-size:0.85rem;'>USD/mes</p></div>", unsafe_allow_html=True)
        if categorias:
            st.markdown("<br>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Bar(x=list(categorias.keys()), y=list(categorias.values()),
                marker=dict(color=list(categorias.values()), colorscale='Viridis', line=dict(color='#1e293b', width=2)))])
            fig.update_layout(title="Casos por Categoría", template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#f1f5f9'))
            st.plotly_chart(fig, use_container_width=True)

# ════════════════════════════════════════
# CONFIGURACIÓN
# ════════════════════════════════════════
elif page == "⚙️ Configuración":
    st.markdown("<div class='main-header'><h1>⚙️ Configuración</h1><p>Ajustes y preferencias del sistema</p></div>", unsafe_allow_html=True)
    st.markdown("### 🔑 Claude API")
    api_key = st.text_input("API Key (Opcional)", type="password", placeholder="sk-ant-api03-...")
    if st.button("💾 Guardar", type="primary"):
        if api_key:
            st.session_state.claude_api_key = api_key
            st.success("✅ API Key guardada")
        else:
            st.warning("⚠️ Ingresa una API key válida")
    st.markdown("---")
    st.markdown("### ℹ️ Información del Sistema")
    st.markdown("<div class='metric-card'><p><strong>Versión:</strong> 4.0 IA</p><p><strong>Modelo:</strong> Sentence-BERT</p><p><strong>Base de datos:</strong> SQLite</p><p><strong>Desarrollado por:</strong> Daner Mosquera</p></div>", unsafe_allow_html=True)

# ════════════════════════════════════════
# FOOTER
# ════════════════════════════════════════
st.markdown("---")
st.markdown("<div style='text-align:center;color:#64748b;padding:2rem 0;'><p>🤖 Agente AI PQRS v4.0 | Desarrollado con ❤️ usando Streamlit + IA</p><p style='font-size:0.85rem;'>© 2025 | Sistema Inteligente de Automatización | Daner Mosquera</p></div>", unsafe_allow_html=True)
