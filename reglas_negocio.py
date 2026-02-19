#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  REGLAS DE NEGOCIO - Sistema PQRS
  
  Todas las reglas de validación y lógica de negocio centralizadas
═══════════════════════════════════════════════════════════════════
"""

# ═══════════════════════════════════════════════════════════════
# ESTADOS DE LIQUIDACIÓN
# ═══════════════════════════════════════════════════════════════

ESTADOS_LIQUIDACION = {
    70: {
        "nombre": "Sin Liquidar",
        "descripcion": "Estado inicial cuando no se ha procesado la liquidación",
        "puede_cambiar_a": [71],
        "requiere_aprobacion_humana": False,
        "puede_ejecutar_automatico": True,
        "es_estado_final": False,
        "criticidad": "baja"
    },
    71: {
        "nombre": "Pendiente Aprobación Asesor",
        "descripcion": "Esperando primera aprobación del asesor",
        "puede_cambiar_a": [72, 77],
        "requiere_aprobacion_humana": False,
        "puede_ejecutar_automatico": True,
        "es_estado_final": False,
        "criticidad": "baja"
    },
    72: {
        "nombre": "Aprobados Asesor",
        "descripcion": "Aprobado por el asesor, falta aprobación de jefe",
        "puede_cambiar_a": [77],
        "requiere_aprobacion_humana": True,  # ← Requiere humano
        "puede_ejecutar_automatico": False,
        "es_estado_final": False,
        "criticidad": "media",
        "razon_aprobacion": "Cambio requiere aprobación de nivel superior"
    },
    77: {
        "nombre": "Aprobados Jefe-Coordinador",
        "descripcion": "Aprobado para pago - Estado crítico",
        "puede_cambiar_a": [79],
        "requiere_aprobacion_humana": True,  # ← CRÍTICO - Siempre requiere humano
        "puede_ejecutar_automatico": False,
        "es_estado_final": False,
        "criticidad": "alta",
        "razon_aprobacion": "Estado crítico - Aprueba el pago de comisión",
        "notificaciones": ["finanzas", "supervisor"],
        "validaciones_extra": [
            "verificar_datos_bancarios_completos",
            "verificar_contrato_vigente",
            "verificar_monto_comision"
        ]
    },
    79: {
        "nombre": "Liquidación Manual",
        "descripcion": "Procesamiento manual - Casos especiales",
        "puede_cambiar_a": [],
        "requiere_aprobacion_humana": True,
        "puede_ejecutar_automatico": False,
        "es_estado_final": True,
        "criticidad": "alta",
        "razon_aprobacion": "Liquidación manual requiere justificación y aprobación",
        "requiere_justificacion": True
    }
}

# ═══════════════════════════════════════════════════════════════
# COMISIONES
# ═══════════════════════════════════════════════════════════════

REGLAS_COMISIONES = {
    "limites_aprobacion": {
        "automatico": 500000,           # Hasta $500K se ejecuta auto
        "supervisor": 2000000,          # $500K - $2M requiere supervisor
        "director": 5000000,            # $2M - $5M requiere director
        "junta": float('inf')           # Más de $5M requiere junta directiva
    },
    
    "validaciones": {
        "cambio_porcentual_maximo": 200,  # No más de 200% de cambio
        "cambio_minimo_absoluto": 10000,   # Mínimo $10K de cambio
        "requiere_contrato": True,
        "debe_coincidir_con_sistema_origen": False,  # Por ahora no validar
    },
    
    "alertas": {
        "cambio_mayor_100_porciento": True,
        "valor_inusualmente_alto": 3000000,  # Alerta si > $3M
        "valor_inusualmente_bajo": 50000      # Alerta si < $50K
    }
}

# ═══════════════════════════════════════════════════════════════
# VENDEDORES
# ═══════════════════════════════════════════════════════════════

REGLAS_VENDEDORES = {
    "validaciones_obligatorias": {
        "debe_existir": True,
        "debe_estar_activo": True,
        "debe_tener_banco": True,
        "debe_tener_cuenta": True,
        "debe_tener_tipo_cuenta": True,
        "debe_pertenecer_a_concesionario": True
    },
    
    "campos_requeridos": [
        "UserID",
        "Identification",
        "FirstName",
        "LastName",
        "BankID",
        "AccountNumber",
        "TypeAccountBankID"
    ],
    
    "type_user_id": {
        1: "Vendedor",
        2: "Cliente",
        3: "Proveedor"
    }
}

# ═══════════════════════════════════════════════════════════════
# OPERACIONES BLOQUEADAS
# ═══════════════════════════════════════════════════════════════

OPERACIONES_BLOQUEADAS = {
    "palabras_prohibidas": [
        "DELETE FROM user",
        "DROP TABLE",
        "DROP DATABASE",
        "TRUNCATE",
        "ALTER TABLE",
        "CREATE TABLE",
        "DROP INDEX"
    ],
    
    "patrones_peligrosos": [
        r"DELETE\s+FROM\s+\w+\s*(?!WHERE)",  # DELETE sin WHERE
        r"UPDATE\s+\w+\s+SET\s+.*?(?!WHERE)",  # UPDATE sin WHERE
        r"DROP\s+",
        r"TRUNCATE\s+",
        r";.*?(DELETE|DROP|TRUNCATE)"  # Múltiples comandos
    ],
    
    "requiere_aprobacion_director": [
        "operaciones_masivas",  # > 10 registros
        "cambios_financieros_grandes",
        "modificar_datos_historicos",
        "cambios_en_tabla_user"
    ]
}

# ═══════════════════════════════════════════════════════════════
# TABLAS Y CAMPOS CRÍTICOS
# ═══════════════════════════════════════════════════════════════

TABLAS_CRITICAS = {
    "user": {
        "criticidad": "alta",
        "requiere_aprobacion": True,
        "puede_modificar_automatico": False,
        "campos_no_modificables": ["UserID", "CreateDate"]
    },
    
    "formatexceldlle": {
        "criticidad": "media",
        "requiere_aprobacion_campos": [
            "ValueCommission",
            "ValueCommissionConcesionario",
            "EstadoLiquidacionVendedor"
        ],
        "campos_no_modificables": ["FormatExcelDlleID", "CreditNumber"]
    },
    
    "bank": {
        "criticidad": "alta",
        "requiere_aprobacion": True,
        "puede_modificar_automatico": False,
        "solo_lectura": True
    }
}

# ═══════════════════════════════════════════════════════════════
# UMBRALES Y LÍMITES
# ═══════════════════════════════════════════════════════════════

UMBRALES = {
    "operaciones_masivas": {
        "maximo_registros_auto": 10,       # Hasta 10 registros = auto
        "maximo_registros_supervisor": 100, # 10-100 = supervisor
        "maximo_registros_director": 1000   # > 1000 = director
    },
    
    "tiempo_ejecucion": {
        "maximo_segundos": 30,  # Si tarda más, abortar
        "advertencia_segundos": 10
    }
}

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE VALIDACIÓN
# ═══════════════════════════════════════════════════════════════

def validar_cambio_estado(estado_actual: int, estado_nuevo: int) -> dict:
    """
    Valida si un cambio de estado es permitido
    
    Returns:
        dict: {
            "permitido": bool,
            "requiere_aprobacion": bool,
            "razon": str,
            "criticidad": str
        }
    """
    # Verificar que los estados existen
    if estado_actual not in ESTADOS_LIQUIDACION:
        return {
            "permitido": False,
            "requiere_aprobacion": False,
            "razon": f"Estado actual {estado_actual} no existe",
            "criticidad": "error"
        }
    
    if estado_nuevo not in ESTADOS_LIQUIDACION:
        return {
            "permitido": False,
            "requiere_aprobacion": False,
            "razon": f"Estado nuevo {estado_nuevo} no existe",
            "criticidad": "error"
        }
    
    config_estado_actual = ESTADOS_LIQUIDACION[estado_actual]
    config_estado_nuevo = ESTADOS_LIQUIDACION[estado_nuevo]
    
    # Verificar flujo permitido
    if estado_nuevo not in config_estado_actual["puede_cambiar_a"]:
        return {
            "permitido": False,
            "requiere_aprobacion": False,
            "razon": f"No se puede cambiar de {config_estado_actual['nombre']} a {config_estado_nuevo['nombre']}. Flujo no permitido.",
            "criticidad": "error"
        }
    
    # Verificar si requiere aprobación
    requiere_aprobacion = config_estado_nuevo.get("requiere_aprobacion_humana", False)
    puede_auto = config_estado_nuevo.get("puede_ejecutar_automatico", False)
    
    return {
        "permitido": True,
        "requiere_aprobacion": requiere_aprobacion,
        "puede_ejecutar_automatico": puede_auto,
        "razon": config_estado_nuevo.get("razon_aprobacion", "Cambio permitido"),
        "criticidad": config_estado_nuevo.get("criticidad", "baja"),
        "estado_nuevo_nombre": config_estado_nuevo["nombre"],
        "validaciones_extra": config_estado_nuevo.get("validaciones_extra", []),
        "notificaciones": config_estado_nuevo.get("notificaciones", [])
    }


def validar_cambio_comision(valor_actual: float, valor_nuevo: float) -> dict:
    """
    Valida si un cambio de comisión es permitido
    
    Returns:
        dict: {
            "permitido": bool,
            "requiere_aprobacion": bool,
            "nivel_aprobacion": str,
            "razon": str
        }
    """
    diferencia = abs(valor_nuevo - valor_actual)
    porcentaje_cambio = (diferencia / valor_actual * 100) if valor_actual > 0 else 100
    
    # Validar cambio porcentual máximo
    if porcentaje_cambio > REGLAS_COMISIONES["validaciones"]["cambio_porcentual_maximo"]:
        return {
            "permitido": False,
            "requiere_aprobacion": True,
            "nivel_aprobacion": "director",
            "razon": f"Cambio de {porcentaje_cambio:.1f}% excede el límite de {REGLAS_COMISIONES['validaciones']['cambio_porcentual_maximo']}%"
        }
    
    # Determinar nivel de aprobación según monto
    limites = REGLAS_COMISIONES["limites_aprobacion"]
    
    if valor_nuevo <= limites["automatico"]:
        return {
            "permitido": True,
            "requiere_aprobacion": False,
            "nivel_aprobacion": "automatico",
            "puede_ejecutar_automatico": True,
            "razon": f"Monto ${valor_nuevo:,.0f} dentro del límite automático"
        }
    
    elif valor_nuevo <= limites["supervisor"]:
        return {
            "permitido": True,
            "requiere_aprobacion": True,
            "nivel_aprobacion": "supervisor",
            "puede_ejecutar_automatico": False,
            "razon": f"Monto ${valor_nuevo:,.0f} requiere aprobación de supervisor"
        }
    
    elif valor_nuevo <= limites["director"]:
        return {
            "permitido": True,
            "requiere_aprobacion": True,
            "nivel_aprobacion": "director",
            "puede_ejecutar_automatico": False,
            "razon": f"Monto ${valor_nuevo:,.0f} requiere aprobación de director"
        }
    
    else:
        return {
            "permitido": True,
            "requiere_aprobacion": True,
            "nivel_aprobacion": "junta_directiva",
            "puede_ejecutar_automatico": False,
            "razon": f"Monto ${valor_nuevo:,.0f} requiere aprobación de junta directiva"
        }


def validar_datos_vendedor(vendedor_data: dict) -> dict:
    """
    Valida que un vendedor tenga todos los datos requeridos
    
    Args:
        vendedor_data: Diccionario con datos del vendedor
    
    Returns:
        dict: {
            "valido": bool,
            "errores": list,
            "advertencias": list
        }
    """
    errores = []
    advertencias = []
    
    # Verificar campos requeridos
    for campo in REGLAS_VENDEDORES["campos_requeridos"]:
        if campo not in vendedor_data or vendedor_data[campo] is None:
            errores.append(f"Campo requerido '{campo}' faltante o NULL")
    
    # Verificar que sea vendedor (TypeUserID = 1)
    if vendedor_data.get("TypeUserID") != 1:
        errores.append(f"TypeUserID debe ser 1 (Vendedor), es {vendedor_data.get('TypeUserID')}")
    
    # Advertencias
    if vendedor_data.get("BankID") and vendedor_data.get("BankID") not in range(1, 100):
        advertencias.append("BankID fuera del rango normal")
    
    if vendedor_data.get("AccountNumber"):
        cuenta = str(vendedor_data["AccountNumber"])
        if len(cuenta) < 8:
            advertencias.append(f"Número de cuenta muy corto ({len(cuenta)} dígitos)")
    
    return {
        "valido": len(errores) == 0,
        "errores": errores,
        "advertencias": advertencias,
        "puede_procesar": len(errores) == 0
    }


def validar_sql_seguro(sql: str) -> dict:
    """
    Valida que un SQL sea seguro para ejecutar
    
    Returns:
        dict: {
            "seguro": bool,
            "bloqueado": bool,
            "advertencias": list,
            "razon": str
        }
    """
    import re
    
    sql_upper = sql.upper()
    advertencias = []
    
    # Verificar palabras prohibidas
    for palabra in OPERACIONES_BLOQUEADAS["palabras_prohibidas"]:
        if palabra.upper() in sql_upper:
            return {
                "seguro": False,
                "bloqueado": True,
                "advertencias": [],
                "razon": f"Operación bloqueada: contiene '{palabra}'"
            }
    
    # Verificar patrones peligrosos
    for patron in OPERACIONES_BLOQUEADAS["patrones_peligrosos"]:
        if re.search(patron, sql, re.IGNORECASE):
            return {
                "seguro": False,
                "bloqueado": True,
                "advertencias": [],
                "razon": "Patrón peligroso detectado (DELETE/UPDATE sin WHERE o múltiples comandos)"
            }
    
    # Advertencias (no bloquean, pero alertan)
    if "DELETE" in sql_upper:
        advertencias.append("⚠️ Operación DELETE - Verifica que sea necesario")
    
    if "UPDATE" in sql_upper and sql.count("WHERE") == 0:
        advertencias.append("⚠️ UPDATE sin WHERE - Afectará TODOS los registros")
    
    # Detectar operaciones masivas (placeholder, necesitaría análisis más profundo)
    if "LIMIT" not in sql_upper and ("UPDATE" in sql_upper or "DELETE" in sql_upper):
        advertencias.append("⚠️ Operación sin LIMIT - Podría afectar muchos registros")
    
    return {
        "seguro": True,
        "bloqueado": False,
        "advertencias": advertencias,
        "razon": "SQL válido"
    }


def obtener_nivel_aprobacion_requerido(tipo_operacion: str, datos: dict) -> str:
    """
    Determina qué nivel de aprobación se requiere para una operación
    
    Args:
        tipo_operacion: "cambio_estado", "cambio_comision", etc.
        datos: Datos de la operación
    
    Returns:
        str: "automatico", "supervisor", "director", "bloqueado"
    """
    if tipo_operacion == "cambio_estado":
        validacion = validar_cambio_estado(
            datos.get("estado_actual"),
            datos.get("estado_nuevo")
        )
        
        if not validacion["permitido"]:
            return "bloqueado"
        
        if validacion.get("puede_ejecutar_automatico"):
            return "automatico"
        else:
            criticidad = validacion.get("criticidad", "media")
            if criticidad == "alta":
                return "director"
            else:
                return "supervisor"
    
    elif tipo_operacion == "cambio_comision":
        validacion = validar_cambio_comision(
            datos.get("valor_actual", 0),
            datos.get("valor_nuevo", 0)
        )
        
        if not validacion["permitido"]:
            return "bloqueado"
        
        return validacion.get("nivel_aprobacion", "supervisor")
    
    else:
        # Tipo desconocido - requiere supervisor por defecto
        return "supervisor"


# ═══════════════════════════════════════════════════════════════
# EXPORTAR TODO
# ═══════════════════════════════════════════════════════════════

__all__ = [
    'ESTADOS_LIQUIDACION',
    'REGLAS_COMISIONES',
    'REGLAS_VENDEDORES',
    'OPERACIONES_BLOQUEADAS',
    'TABLAS_CRITICAS',
    'UMBRALES',
    'validar_cambio_estado',
    'validar_cambio_comision',
    'validar_datos_vendedor',
    'validar_sql_seguro',
    'obtener_nivel_aprobacion_requerido'
]
