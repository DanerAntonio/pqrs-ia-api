#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  VALIDADOR AUTOMÁTICO - Sistema PQRS
  
  Valida operaciones antes de ejecutar usando reglas de negocio
═══════════════════════════════════════════════════════════════════
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json

# Importar reglas de negocio
try:
    from reglas_negocio import *
except ImportError:
    print("⚠️ No se encontró reglas_negocio.py - Usando valores por defecto")
    # Valores por defecto si no existe el archivo
    ESTADOS_LIQUIDACION = {}
    REGLAS_COMISIONES = {}


class ValidadorAutomatico:
    """
    Valida operaciones PQRS antes de ejecutar
    Decide si puede ejecutarse automáticamente o requiere aprobación humana
    """
    
    def __init__(self, sistema_pqrs=None):
        """
        Inicializa el validador
        
        Args:
            sistema_pqrs: Instancia del sistema PQRS para consultas a BD
        """
        self.sistema = sistema_pqrs
        self.historial_validaciones = []
    
    def validar_operacion_completa(self, sql: str, tipo_operacion: str, datos_contexto: dict) -> dict:
        """
        Validación completa de una operación
        
        Args:
            sql: Código SQL a validar
            tipo_operacion: "cambio_estado", "cambio_comision", etc.
            datos_contexto: Contexto de la operación (crédito, valores, etc.)
        
        Returns:
            dict: {
                "puede_ejecutar": bool,
                "requiere_aprobacion": bool,
                "nivel_aprobacion": str,
                "validaciones": list,
                "advertencias": list,
                "errores": list,
                "razon_principal": str,
                "sql_validado": str
            }
        """
        resultado = {
            "puede_ejecutar": True,
            "requiere_aprobacion": False,
            "nivel_aprobacion": "automatico",
            "validaciones": [],
            "advertencias": [],
            "errores": [],
            "razon_principal": "",
            "sql_validado": sql,
            "timestamp": datetime.now().isoformat()
        }
        
        # VALIDACIÓN 1: Seguridad del SQL
        validacion_sql = self._validar_seguridad_sql(sql)
        resultado["validaciones"].append(validacion_sql)
        
        if validacion_sql["bloqueado"]:
            resultado["puede_ejecutar"] = False
            resultado["errores"].append(validacion_sql["razon"])
            resultado["razon_principal"] = "SQL bloqueado por seguridad"
            return resultado
        
        resultado["advertencias"].extend(validacion_sql.get("advertencias", []))
        
        # VALIDACIÓN 2: Tipo de operación
        if tipo_operacion == "cambio_estado":
            validacion_estado = self._validar_cambio_estado_completo(datos_contexto)
            resultado["validaciones"].append(validacion_estado)
            
            if not validacion_estado["permitido"]:
                resultado["puede_ejecutar"] = False
                resultado["errores"].append(validacion_estado["razon"])
                resultado["razon_principal"] = validacion_estado["razon"]
                return resultado
            
            resultado["requiere_aprobacion"] = validacion_estado["requiere_aprobacion"]
            resultado["nivel_aprobacion"] = self._determinar_nivel_aprobacion(validacion_estado)
            resultado["razon_principal"] = validacion_estado["razon"]
        
        elif tipo_operacion == "cambio_comision":
            validacion_comision = self._validar_cambio_comision_completo(datos_contexto)
            resultado["validaciones"].append(validacion_comision)
            
            if not validacion_comision["permitido"]:
                resultado["puede_ejecutar"] = False
                resultado["errores"].append(validacion_comision["razon"])
                resultado["razon_principal"] = validacion_comision["razon"]
                return resultado
            
            resultado["requiere_aprobacion"] = validacion_comision["requiere_aprobacion"]
            resultado["nivel_aprobacion"] = validacion_comision.get("nivel_aprobacion", "supervisor")
            resultado["razon_principal"] = validacion_comision["razon"]
        
        elif tipo_operacion == "actualizar_vendedor":
            validacion_vendedor = self._validar_actualizacion_vendedor(datos_contexto)
            resultado["validaciones"].append(validacion_vendedor)
            
            if not validacion_vendedor["valido"]:
                resultado["puede_ejecutar"] = False
                resultado["errores"].extend(validacion_vendedor["errores"])
                resultado["razon_principal"] = "Datos de vendedor inválidos"
                return resultado
            
            # Actualizar vendedor siempre requiere aprobación
            resultado["requiere_aprobacion"] = True
            resultado["nivel_aprobacion"] = "supervisor"
            resultado["razon_principal"] = "Cambios en tabla user requieren aprobación"
        
        else:
            # Tipo desconocido - requiere aprobación por defecto
            resultado["requiere_aprobacion"] = True
            resultado["nivel_aprobacion"] = "supervisor"
            resultado["razon_principal"] = f"Tipo de operación '{tipo_operacion}' requiere revisión"
        
        # VALIDACIÓN 3: Verificar datos en BD (si hay sistema disponible)
        if self.sistema:
            validacion_bd = self._validar_datos_en_bd(datos_contexto)
            resultado["validaciones"].append(validacion_bd)
            
            if validacion_bd.get("errores"):
                resultado["errores"].extend(validacion_bd["errores"])
                resultado["puede_ejecutar"] = False
                resultado["razon_principal"] = validacion_bd["errores"][0]
        
        # Guardar en historial
        self.historial_validaciones.append(resultado.copy())
        
        return resultado
    
    def _validar_seguridad_sql(self, sql: str) -> dict:
        """Valida que el SQL sea seguro"""
        try:
            return validar_sql_seguro(sql)
        except:
            # Si no existe la función, validación básica
            sql_upper = sql.upper()
            
            bloqueado = any(palabra in sql_upper for palabra in [
                "DROP", "TRUNCATE", "DELETE FROM user"
            ])
            
            return {
                "seguro": not bloqueado,
                "bloqueado": bloqueado,
                "advertencias": [],
                "razon": "Operación bloqueada" if bloqueado else "SQL válido"
            }
    
    def _validar_cambio_estado_completo(self, datos: dict) -> dict:
        """Validación completa de cambio de estado"""
        estado_actual = datos.get("estado_actual")
        estado_nuevo = datos.get("estado_nuevo")
        
        if not estado_actual or not estado_nuevo:
            return {
                "permitido": False,
                "requiere_aprobacion": False,
                "razon": "Estados no especificados"
            }
        
        try:
            return validar_cambio_estado(estado_actual, estado_nuevo)
        except:
            # Validación básica si no existe la función
            estados_criticos = [77, 79]
            requiere_aprobacion = estado_nuevo in estados_criticos
            
            return {
                "permitido": True,
                "requiere_aprobacion": requiere_aprobacion,
                "puede_ejecutar_automatico": not requiere_aprobacion,
                "razon": f"Estado {estado_nuevo} {'es crítico' if requiere_aprobacion else 'es seguro'}",
                "criticidad": "alta" if requiere_aprobacion else "baja"
            }
    
    def _validar_cambio_comision_completo(self, datos: dict) -> dict:
        """Validación completa de cambio de comisión"""
        valor_actual = datos.get("valor_actual", 0)
        valor_nuevo = datos.get("valor_nuevo", 0)
        
        try:
            return validar_cambio_comision(valor_actual, valor_nuevo)
        except:
            # Validación básica
            limite = 500000
            requiere_aprobacion = valor_nuevo > limite
            
            return {
                "permitido": True,
                "requiere_aprobacion": requiere_aprobacion,
                "nivel_aprobacion": "supervisor" if requiere_aprobacion else "automatico",
                "razon": f"Monto ${valor_nuevo:,.0f} {'excede' if requiere_aprobacion else 'dentro de'} límite"
            }
    
    def _validar_actualizacion_vendedor(self, datos: dict) -> dict:
        """Validación de actualización de vendedor"""
        vendedor_data = datos.get("vendedor_data", {})
        
        try:
            return validar_datos_vendedor(vendedor_data)
        except:
            # Validación básica
            campos_requeridos = ["UserID", "Identification", "FirstName", "LastName"]
            errores = []
            
            for campo in campos_requeridos:
                if campo not in vendedor_data:
                    errores.append(f"Falta campo: {campo}")
            
            return {
                "valido": len(errores) == 0,
                "errores": errores,
                "advertencias": []
            }
    
    def _validar_datos_en_bd(self, datos: dict) -> dict:
        """Valida que los datos existan en la BD"""
        validacion = {
            "valido": True,
            "errores": [],
            "advertencias": []
        }
        
        # Validar crédito si existe
        if "credit_number" in datos:
            credit_number = datos["credit_number"]
            # Aquí iría la consulta real a la BD
            # Por ahora solo validamos formato
            if not re.match(r'^\d{13,16}$', str(credit_number)):
                validacion["errores"].append(f"Formato de crédito inválido: {credit_number}")
                validacion["valido"] = False
        
        return validacion
    
    def _determinar_nivel_aprobacion(self, validacion: dict) -> str:
        """Determina el nivel de aprobación requerido"""
        if validacion.get("puede_ejecutar_automatico"):
            return "automatico"
        
        criticidad = validacion.get("criticidad", "media")
        
        if criticidad == "alta":
            return "director"
        elif criticidad == "media":
            return "supervisor"
        else:
            return "automatico"
    
    def generar_resumen_validacion(self, resultado_validacion: dict) -> str:
        """Genera un resumen legible de la validación"""
        resumen = []
        
        # Título
        if resultado_validacion["puede_ejecutar"]:
            if resultado_validacion["requiere_aprobacion"]:
                resumen.append("⚠️ **REQUIERE APROBACIÓN**")
            else:
                resumen.append("✅ **PUEDE EJECUTARSE AUTOMÁTICAMENTE**")
        else:
            resumen.append("❌ **OPERACIÓN BLOQUEADA**")
        
        # Razón principal
        resumen.append(f"\n**Razón:** {resultado_validacion['razon_principal']}")
        
        # Nivel de aprobación
        if resultado_validacion["requiere_aprobacion"]:
            nivel = resultado_validacion["nivel_aprobacion"]
            emoji = {"automatico": "✅", "supervisor": "👤", "director": "👔", "junta_directiva": "🏛️"}
            resumen.append(f"\n**Nivel de aprobación:** {emoji.get(nivel, '❓')} {nivel.upper()}")
        
        # Errores
        if resultado_validacion["errores"]:
            resumen.append("\n**❌ Errores:**")
            for error in resultado_validacion["errores"]:
                resumen.append(f"  • {error}")
        
        # Advertencias
        if resultado_validacion["advertencias"]:
            resumen.append("\n**⚠️ Advertencias:**")
            for adv in resultado_validacion["advertencias"]:
                resumen.append(f"  • {adv}")
        
        # Validaciones pasadas
        validaciones_ok = [v for v in resultado_validacion["validaciones"] if v.get("seguro") or v.get("valido") or v.get("permitido")]
        if validaciones_ok:
            resumen.append(f"\n**✅ Validaciones exitosas:** {len(validaciones_ok)}")
        
        return "\n".join(resumen)
    
    def exportar_historial(self, archivo: str = "historial_validaciones.json"):
        """Exporta el historial de validaciones a un archivo"""
        try:
            with open(archivo, 'w', encoding='utf-8') as f:
                json.dump(self.historial_validaciones, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error exportando historial: {e}")
            return False


# ═══════════════════════════════════════════════════════════════
# FUNCIÓN HELPER PARA INTEGRACIÓN RÁPIDA
# ═══════════════════════════════════════════════════════════════

def validar_pqrs_rapido(sql: str, tipo: str, datos: dict = None) -> dict:
    """
    Función helper para validación rápida
    
    Args:
        sql: SQL a validar
        tipo: Tipo de operación
        datos: Datos de contexto (opcional)
    
    Returns:
        dict: Resultado de validación
    
    Ejemplo:
        >>> resultado = validar_pqrs_rapido(
        ...     sql="UPDATE formatexceldlle SET Estado = 77 WHERE Credit = '123'",
        ...     tipo="cambio_estado",
        ...     datos={"estado_actual": 71, "estado_nuevo": 77}
        ... )
        >>> print(resultado["puede_ejecutar"])
        False  # Requiere aprobación porque 77 es crítico
    """
    validador = ValidadorAutomatico()
    return validador.validar_operacion_completa(sql, tipo, datos or {})


__all__ = [
    'ValidadorAutomatico',
    'validar_pqrs_rapido'
]
