#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  AGENTE CONVERSACIONAL CON CLAUDE API
  
  Chat inteligente que:
  - Hace preguntas para entender el problema
  - Explica el SQL generado
  - Da sugerencias proactivas
═══════════════════════════════════════════════════════════════════
"""

import os
import re
from typing import List, Dict

# Intentar importar Anthropic
try:
    from anthropic import Anthropic
    ANTHROPIC_DISPONIBLE = True
except ImportError:
    ANTHROPIC_DISPONIBLE = False
    print("⚠️ Anthropic no instalado. Instala con: pip install anthropic")

# Importar base de conocimiento
try:
    from base_conocimiento import base_conocimiento
    BASE_CONOCIMIENTO_DISPONIBLE = True
except ImportError:
    BASE_CONOCIMIENTO_DISPONIBLE = False
    print("⚠️ Base de conocimiento no disponible")

class AgenteConversacional:
    
    def __init__(self, api_key: str = None, sistema_pqrs = None):
        """
        Inicializa el agente conversacional
        
        Args:
            api_key: API key de Anthropic (opcional)
            sistema_pqrs: Instancia del sistema PQRS para buscar casos
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.conversacion = []
        self.sistema_pqrs = sistema_pqrs  # ← NUEVO: Conexión con tu sistema
        
        if ANTHROPIC_DISPONIBLE and self.api_key:
            self.client = Anthropic(api_key=self.api_key)
            self.modo = "CLAUDE_API"
            print("✅ Agente conversacional con Claude API activado")
        else:
            self.client = None
            self.modo = "BASICO"
            print("⚠️ Modo básico (sin API). Para mejor experiencia usa Claude API")
        
        # Contexto del sistema MEJORADO
        self.system_prompt = """Eres un asistente experto en bases de datos y PQRS (Peticiones, Quejas, Reclamos y Sugerencias).

Tu trabajo es ayudar a técnicos de TI a resolver casos de PQRS generando SQL correcto.

PROCESO QUE DEBES SEGUIR:
1. Escuchar el problema completo del usuario
2. Cuando tengas suficiente información, buscar casos similares en la base de conocimiento
3. Generar o adaptar el SQL encontrado
4. Explicar la solución claramente

Base de datos:
- Tabla principal: formatexceldlle (información de créditos y liquidaciones)
- Campos comunes: CreditNumber, EstadoLiquidacionVendedor, EstadoLiquidacionConcesionario
- Tabla user: información de vendedores y clientes
- Tabla certificatefileuser: certificados tributarios

Estados de liquidación comunes:
- 71: Pendiente Aprobación Asesor
- 77: Aprobados Jefe Coordinador

Siempre sé conciso, claro y profesional."""
    
    def agregar_mensaje(self, rol: str, contenido: str):
        """Agrega un mensaje a la conversación"""
        self.conversacion.append({
            "role": rol,
            "content": contenido
        })
    
    def limpiar_conversacion(self):
        """Limpia el historial de conversación"""
        self.conversacion = []
    
    def chat(self, mensaje_usuario: str) -> str:
        """
        Envía un mensaje y recibe respuesta del agente
        
        Args:
            mensaje_usuario: Mensaje del usuario
            
        Returns:
            Respuesta del agente
        """
        # Agregar mensaje del usuario
        self.agregar_mensaje("user", mensaje_usuario)
        
        # Obtener respuesta según el modo
        if self.modo == "CLAUDE_API":
            respuesta = self._chat_con_api()
        else:
            respuesta = self._chat_basico()
        
        # Agregar respuesta del asistente UNA SOLA VEZ aquí
        self.agregar_mensaje("assistant", respuesta)
        
        return respuesta
    
    def _chat_con_api(self) -> str:
        """Chat usando Claude API"""
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                system=self.system_prompt,
                messages=self.conversacion
            )
            
            respuesta = response.content[0].text
            
            return respuesta
            
        except Exception as e:
            return f"❌ Error con Claude API: {str(e)}\n\n💡 Verifica tu API key"
    
    def _chat_basico(self) -> str:
        """Chat básico que USA el sistema PQRS para buscar soluciones"""
        ultimo_mensaje = self.conversacion[-1]["content"]
        ultimo_mensaje_lower = ultimo_mensaje.lower()


        
        
        # ============================================================
        # PRIMERO: Detectar si es PREGUNTA sobre conocimiento
        # ============================================================
        palabras_pregunta = ['qué', 'que', 'cual', 'cuál', 'cómo', 'como']
        es_pregunta = any(p in ultimo_mensaje_lower for p in palabras_pregunta)
        
        if es_pregunta and BASE_CONOCIMIENTO_DISPONIBLE:
            
            # PREGUNTAS SOBRE BANCOS
            if 'banco' in ultimo_mensaje_lower or 'código' in ultimo_mensaje_lower or 'codigo' in ultimo_mensaje_lower:
                bancos_info = base_conocimiento.conocimiento.get('bancos', {})
                if bancos_info:
                    # Buscar banco específico
                    banco_encontrado = None
                    bancos = bancos_info.get('bancos_principales', {})
                    
                    # Buscar por nombre común
                    if 'davivienda' in ultimo_mensaje_lower:
                        for bid, info in bancos.items():
                            if isinstance(info, dict) and 'davivienda' in info.get('nombre', '').lower():
                                banco_encontrado = (bid, info)
                                break
                    elif 'bancolombia' in ultimo_mensaje_lower:
                        for bid, info in bancos.items():
                            if isinstance(info, dict) and 'bancolombia' in info.get('nombre', '').lower():
                                banco_encontrado = (bid, info)
                                break
                    
                    if banco_encontrado:
                        bid, info = banco_encontrado
                        respuesta = f"🏦 **{info['nombre']}**\n\n"
                        respuesta += f"• **ID:** {bid}\n"
                        respuesta += f"• **Código:** {info['codigo']}\n"
                        
                        # Código ACH
                        ach = bancos_info.get('codigos_ach', {})
                        if 'davivienda' in info['nombre'].lower() and 'DAVIVIENDA' in ach:
                            respuesta += f"• **Código ACH:** {ach['DAVIVIENDA']}\n"
                        elif 'bancolombia' in info['nombre'].lower() and 'BANCOLOMBIA' in ach:
                            respuesta += f"• **Código ACH:** {ach['BANCOLOMBIA']}\n"
                        
                        return respuesta
                    else:
                        # Lista de bancos
                        respuesta = "🏦 **Bancos principales:**\n\n"
                        for bid, info in list(bancos.items())[:6]:
                            if isinstance(info, dict):
                                respuesta += f"• {info['nombre']} (Código: {info['codigo']})\n"
                        respuesta += "\n💡 Pregunta por uno específico"
                        return respuesta
            
            # PREGUNTAS SOBRE ESTADOS
            elif 'estado' in ultimo_mensaje_lower:
                estados = base_conocimiento.conocimiento.get('estados_sistema', {})
                if estados:
                    numeros = re.findall(r'\d+', ultimo_mensaje)
                    
                    if numeros:
                        # Estado específico
                        sid = numeros[0]
                        nombre = estados.get('valores', {}).get(sid)
                        if nombre:
                            respuesta = f"✅ **Estado {sid}:** {nombre}"
                            return respuesta
                    else:
                        # Lista de estados de liquidación
                        respuesta = "📊 **Estados de Liquidación:**\n\n"
                        respuesta += "• 71: Pendiente Aprobación Asesor\n"
                        respuesta += "• 77: Aprobados Jefe-Coordinador ⭐\n"
                        respuesta += "• 79: Liquidacion Manual\n"
                        respuesta += "\n💡 Estado 77 es el más usado para aprobar"
                        return respuesta
        
        # ============================================================
        # SEGUNDO: Buscar solución PQRS
        # ============================================================
        
        # Si el mensaje parece completo (tiene crédito + descripción), BUSCAR SOLUCIÓN
        tiene_credito = bool(re.findall(r'\d{10,}', ultimo_mensaje))
        tiene_descripcion = len(ultimo_mensaje.split()) > 15
        
        if (tiene_credito or tiene_descripcion) and self.sistema_pqrs:
            # USAR EL SISTEMA DE BÚSQUEDA INTELIGENTE
            print(f"🔍 Buscando solución para: {ultimo_mensaje[:100]}...")
            
            try:
                ranking = self.sistema_pqrs.buscar_similar_ia(ultimo_mensaje)
                
                if ranking and len(ranking) > 0:
                    mejor_caso = ranking[0]
                    
                    if mejor_caso['similitud'] >= 0.50:  # 50% de similitud mínima
                        # ENCONTRÓ UN CASO SIMILAR
                        
                        # Extraer valores del mensaje
                        valores = self.sistema_pqrs.extraer_valores(ultimo_mensaje)
                        
                        # Generar SQL personalizado
                        sql_generado = self.sistema_pqrs.reemplazar_valores(
                            mejor_caso['sql'], 
                            valores
                        )
                        
                        # Crear respuesta completa
                        respuesta = f"""✅ **Encontré una solución similar** (Similitud: {mejor_caso['similitud']*100:.0f}%)

📁 **Categoría:** {mejor_caso['categoria']}
"""
                        
                        # AGREGAR CONTEXTO DE CONOCIMIENTO
                        if BASE_CONOCIMIENTO_DISPONIBLE:
                            contexto = base_conocimiento.obtener_contexto_para_agente(ultimo_mensaje)
                            if contexto:
                                respuesta += f"\n{contexto}\n"
                        
                        respuesta += f"""
💻 **SQL para ejecutar:**

```sql
{sql_generado}
```

📝 **Explicación:**
{self._explicar_sql_basico(sql_generado)}

💡 **Sugerencias:**
"""
                        # Agregar sugerencias
                        sugerencias = self._sugerencias_basicas(mejor_caso['categoria'])
                        for sug in sugerencias:
                            respuesta += f"\n• {sug}"
                        
                        respuesta += f"\n\n📋 **Respuesta para el usuario:**\n{mejor_caso['respuesta']}"
                        
                        return respuesta
                    
            except Exception as e:
                print(f"⚠️ Error en búsqueda: {e}")
        
        # Si no encontró o el mensaje está incompleto, hacer preguntas
        # (es_pregunta ya está definida arriba)
        
        # Respuestas básicas predefinidas
        if any(palabra in ultimo_mensaje_lower for palabra in ['hola', 'buenos días', 'buenas tardes']):
            respuesta = "¡Hola! Soy tu asistente de PQRS. ¿En qué caso necesitas ayuda hoy?"
        
        elif 'crédito' in ultimo_mensaje_lower or 'credito' in ultimo_mensaje_lower:
            if not re.findall(r'\d{10,}', ultimo_mensaje):
                respuesta = "Entiendo que necesitas ayuda con un crédito. ¿Cuál es el número del crédito?"
            else:
                respuesta = "Perfecto, veo el número de crédito. ¿Qué necesitas hacer exactamente? (cambiar estado, actualizar vendedor, corregir valores, etc.)"
        
        elif 'estado' in ultimo_mensaje_lower or 'liquidación' in ultimo_mensaje_lower or 'liquidacion' in ultimo_mensaje_lower:
            # Intentar responder con conocimiento primero
            if BASE_CONOCIMIENTO_DISPONIBLE and es_pregunta:
                estados = base_conocimiento.conocimiento.get('estados_sistema', {}) or base_conocimiento.conocimiento.get('estados_liquidacion', {})
                if estados:
                    respuesta_base = "📊 **Estados de Liquidación:**\n\n"
                    respuesta_base += "• 71: Pendiente Aprobación Asesor\n"
                    respuesta_base += "• 77: Aprobados Jefe-Coordinador ⭐ (para aprobar)\n"
                    respuesta_base += "• 79: Liquidacion Manual\n"
                    respuesta_base += "\n💡 Para aprobar pagos usa el estado **77**"
                    respuesta = respuesta_base
                else:
                    respuesta = "Entiendo que necesitas cambiar estados de liquidación. Por favor dame:\n• Número de crédito\n• Estado actual\n• Estado deseado"
            else:
                respuesta = "Entiendo que necesitas cambiar estados de liquidación. Por favor dame:\n• Número de crédito\n• Estado actual\n• Estado deseado"
        
        elif 'vendedor' in ultimo_mensaje_lower:
            respuesta = "Para actualizar el vendedor necesito:\n• Número de crédito\n• Nombre completo del vendedor\n• Cédula del vendedor"
        
        elif 'certificado' in ultimo_mensaje_lower:
            respuesta = "Para ayudarte con certificados necesito:\n• NIT del proveedor\n• Tipo de certificado (ReteIVA, ReteFuente, etc.)\n• Valores a actualizar"
        
        elif 'gracias' in ultimo_mensaje_lower:
            respuesta = "¡De nada! ¿Hay algo más en lo que pueda ayudarte?"
        
        else:
            # Mensaje genérico pero útil
            respuesta = """Déjame ayudarte. Por favor proporciona los detalles completos del caso:

📝 **Incluye:**
• Número de crédito / ID / NIT
• Qué necesitas hacer específicamente
• Valores correctos (si aplica)

💡 **Ejemplo:**
"Para el crédito 5800325002956151 necesito cambiar el estado de liquidación del vendedor a Aprobado Jefe Coordinador"

Cuando tengas toda la información, la buscaré en mi base de conocimiento."""
        
        return respuesta
    
    def explicar_sql(self, sql: str, problema: str) -> str:
        """
        Genera una explicación del SQL
        
        Args:
            sql: Código SQL a explicar
            problema: Problema original que resuelve
            
        Returns:
            Explicación clara del SQL
        """
        prompt = f"""Tengo este problema:
{problema}

Y este SQL lo resuelve:
{sql}

Por favor:
1. Explica QUÉ hace este SQL de forma simple
2. Indica QUÉ tablas y campos afecta
3. Advierte sobre posibles precauciones
4. Sugiere 2-3 acciones relacionadas que el usuario podría necesitar

Sé conciso y profesional."""

        if self.modo == "CLAUDE_API":
            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1500,
                    system=self.system_prompt,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            except:
                return self._explicar_sql_basico(sql)
        else:
            return self._explicar_sql_basico(sql)
    
    def _explicar_sql_basico(self, sql: str) -> str:
        """Explicación básica sin API"""
        explicacion = "📝 **Explicación del SQL:**\n\n"
        
        # Detectar tipo de operación
        if 'UPDATE' in sql.upper():
            explicacion += "• **Acción:** Actualiza registros existentes\n"
            
            # Detectar tabla
            import re
            tabla_match = re.search(r'UPDATE\s+(\w+)', sql, re.IGNORECASE)
            if tabla_match:
                explicacion += f"• **Tabla afectada:** {tabla_match.group(1)}\n"
            
            # Detectar campos
            set_match = re.search(r'SET\s+(.+?)(?:WHERE|$)', sql, re.IGNORECASE | re.DOTALL)
            if set_match:
                campos = set_match.group(1).split(',')
                explicacion += f"• **Campos modificados:** {len(campos)} campo(s)\n"
        
        elif 'SELECT' in sql.upper():
            explicacion += "• **Acción:** Consulta datos\n"
        
        elif 'DELETE' in sql.upper():
            explicacion += "• **Acción:** Elimina registros\n⚠️ **Precaución:** Esta acción es permanente\n"
        
        elif 'INSERT' in sql.upper():
            explicacion += "• **Acción:** Inserta nuevos registros\n"
        
        explicacion += "\n💡 **Sugerencias:**\n"
        explicacion += "• Verifica los datos antes de ejecutar\n"
        explicacion += "• Considera hacer un backup si modifica datos importantes\n"
        
        return explicacion
    
    def generar_sugerencias(self, categoria: str, sql: str) -> List[str]:
        """
        Genera sugerencias relacionadas
        
        Args:
            categoria: Categoría del caso
            sql: SQL generado
            
        Returns:
            Lista de sugerencias
        """
        if self.modo == "CLAUDE_API":
            prompt = f"""Para este caso de categoría "{categoria}" con SQL:
{sql}

Dame 3 sugerencias breves de acciones relacionadas que el usuario podría necesitar hacer.
Formato: lista simple, una sugerencia por línea."""

            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                texto = response.content[0].text
                sugerencias = [s.strip('- ').strip() for s in texto.split('\n') if s.strip()]
                return sugerencias[:3]
            except:
                return self._sugerencias_basicas(categoria)
        else:
            return self._sugerencias_basicas(categoria)
    
    def _sugerencias_basicas(self, categoria: str) -> List[str]:
        """Sugerencias básicas sin API"""
        sugerencias_por_categoria = {
            'comisiones': [
                "Verificar valores de comisión después del cambio",
                "Validar que el estado permita el pago",
                "Revisar si hay comisiones pendientes del mismo vendedor"
            ],
            'liquidacion': [
                "Verificar estados de liquidación relacionados",
                "Validar datos del vendedor",
                "Generar reporte de liquidación"
            ],
            'certificados': [
                "Verificar que el archivo PDF esté accesible",
                "Validar que los valores coincidan con el sistema contable",
                "Revisar otros certificados del mismo proveedor"
            ],
            'default': [
                "Validar que los cambios se hayan aplicado correctamente",
                "Revisar casos similares pendientes",
                "Documentar el cambio para referencia futura"
            ]
        }
        
        cat_lower = categoria.lower()
        for clave, sugs in sugerencias_por_categoria.items():
            if clave in cat_lower:
                return sugs
        
        return sugerencias_por_categoria['default']
    
    def validar_sql(self, sql: str) -> Dict[str, any]:
        """
        Valida el SQL antes de ejecutar
        
        Args:
            sql: Código SQL a validar
            
        Returns:
            Diccionario con resultado de validación
        """
        validacion = {
            'valido': True,
            'advertencias': [],
            'errores': []
        }
        
        # Validaciones básicas
        sql_upper = sql.upper()
        
        # Verificar sintaxis básica
        if not any(cmd in sql_upper for cmd in ['SELECT', 'UPDATE', 'INSERT', 'DELETE']):
            validacion['valido'] = False
            validacion['errores'].append("No se detectó comando SQL válido")
        
        # Advertir sobre DELETE sin WHERE
        if 'DELETE' in sql_upper and 'WHERE' not in sql_upper:
            validacion['advertencias'].append("⚠️ DELETE sin WHERE - eliminará TODOS los registros")
        
        # Advertir sobre UPDATE sin WHERE
        if 'UPDATE' in sql_upper and 'WHERE' not in sql_upper:
            validacion['advertencias'].append("⚠️ UPDATE sin WHERE - modificará TODOS los registros")
        
        # Si tiene API, hacer validación más profunda
        if self.modo == "CLAUDE_API":
            prompt = f"""Analiza este SQL y detecta posibles problemas:

{sql}

Responde SOLO con:
- "OK" si está bien
- "ADVERTENCIA: [descripción]" si hay algo a considerar
- "ERROR: [descripción]" si hay un error grave

Una línea por problema encontrado."""

            try:
                response = self.client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=300,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                respuesta = response.content[0].text
                
                if "ERROR:" in respuesta:
                    validacion['valido'] = False
                    validacion['errores'].extend([
                        linea.replace('ERROR:', '').strip() 
                        for linea in respuesta.split('\n') 
                        if 'ERROR:' in linea
                    ])
                
                if "ADVERTENCIA:" in respuesta:
                    validacion['advertencias'].extend([
                        linea.replace('ADVERTENCIA:', '').strip() 
                        for linea in respuesta.split('\n') 
                        if 'ADVERTENCIA:' in linea
                    ])
            except:
                pass
        
        return validacion


# Función helper para usar desde Streamlit
def crear_agente(api_key: str = None, sistema_pqrs = None) -> AgenteConversacional:
    """
    Crea una instancia del agente conversacional
    
    Args:
        api_key: API key de Claude (opcional)
        sistema_pqrs: Sistema PQRS para búsqueda inteligente (IMPORTANTE)
    """
    return AgenteConversacional(api_key=api_key, sistema_pqrs=sistema_pqrs)
