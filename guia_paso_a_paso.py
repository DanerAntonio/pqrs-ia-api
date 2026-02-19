#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  MOTOR DE SUGERENCIAS PASO A PASO
  
  Guía al usuario con instrucciones detalladas para resolver PQRS
  NO requiere conexión a base de datos
═══════════════════════════════════════════════════════════════════
"""

from typing import List, Dict, Optional
from datetime import datetime
import json


class GuiaPasoAPaso:
    """
    Genera guías paso a paso según el tipo de problema
    """
    
    def __init__(self):
        self.guias = self._cargar_guias()
    
    def _cargar_guias(self) -> Dict:
        """Carga todas las guías disponibles"""
        return {
            "cambio_estado": self._guia_cambio_estado(),
            "cambio_comision": self._guia_cambio_comision(),
            "actualizar_vendedor": self._guia_actualizar_vendedor(),
            "generico": self._guia_generica()
        }
    
    def obtener_guia(self, tipo_problema: str, contexto: Dict = None) -> Dict:
        """
        Obtiene la guía para un tipo de problema específico
        
        Args:
            tipo_problema: Tipo de problema a resolver
            contexto: Información adicional del caso
        
        Returns:
            Dict con los pasos a seguir
        """
        guia_base = self.guias.get(tipo_problema)
        
        if not guia_base:
            return self._guia_generica()
        
        # Personalizar con contexto
        if contexto:
            guia_base = self._personalizar_guia(guia_base, contexto)
        
        return guia_base
    
    def _guia_cambio_estado(self) -> Dict:
        """Guía para cambiar estado de liquidación"""
        return {
            "tipo": "cambio_estado",
            "titulo": "Cambiar Estado de Liquidación",
            "descripcion": "Proceso completo para actualizar el estado de una liquidación",
            "tiempo_estimado": 5,
            "dificultad": "Fácil",
            "pasos": [
                {
                    "numero": 1,
                    "titulo": "Identificar el Crédito",
                    "descripcion": "Localiza el número de crédito en la PQRS (13-16 dígitos)",
                    "tipo": "preparacion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Busca en el correo/ticket el número de crédito",
                        "Verifica que tenga el formato correcto (solo números)",
                        "Anota el número para los siguientes pasos"
                    ],
                    "ejemplo": "Ejemplo: 5800325002956151",
                    "advertencias": [
                        "⚠️ Asegúrate de copiar todos los dígitos",
                        "⚠️ No confundir con número de cuenta o cédula"
                    ]
                },
                {
                    "numero": 2,
                    "titulo": "Verificar Estado Actual",
                    "descripcion": "Consulta el estado actual del crédito",
                    "tipo": "consulta",
                    "tiempo": 1,
                    "sql": "SELECT CreditNumber, EstadoLiquidacionVendedor FROM formatexceldlle WHERE CreditNumber = '[CREDITO]'",
                    "instrucciones": [
                        "Ejecuta el SQL reemplazando [CREDITO]",
                        "Anota el estado actual",
                        "Verifica que el registro existe"
                    ]
                },
                {
                    "numero": 3,
                    "titulo": "Generar SQL de Actualización",
                    "descripcion": "Crea la consulta UPDATE",
                    "tipo": "accion",
                    "tiempo": 1,
                    "sql": "UPDATE formatexceldlle SET EstadoLiquidacionVendedor = [NUEVO_ESTADO] WHERE CreditNumber = '[CREDITO]'",
                    "instrucciones": [
                        "Reemplaza [NUEVO_ESTADO] con el número del estado",
                        "Reemplaza [CREDITO] con el número de crédito",
                        "Revisa que el SQL esté correcto"
                    ],
                    "ejemplo": "UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE CreditNumber = '5800325002956151'"
                },
                {
                    "numero": 4,
                    "titulo": "Ejecutar y Verificar",
                    "descripcion": "Ejecuta el cambio y confirma",
                    "tipo": "ejecucion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Ejecuta el SQL UPDATE",
                        "Verifica que diga '1 row affected'",
                        "Ejecuta de nuevo el SELECT del paso 2"
                    ]
                },
                {
                    "numero": 5,
                    "titulo": "Responder al Usuario",
                    "descripcion": "Notifica que el cambio fue exitoso",
                    "tipo": "comunicacion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Confirma al usuario que se realizó el cambio",
                        "Indica el estado anterior y el nuevo",
                        "Da próximos pasos si aplica"
                    ]
                }
            ],
            "notas_adicionales": [
                "📝 Documenta el cambio en el sistema de tickets",
                "📊 Si es estado 77, notifica a finanzas"
            ]
        }
    
    def _guia_cambio_comision(self) -> Dict:
        """Guía para cambiar valor de comisión"""
        return {
            "tipo": "cambio_comision",
            "titulo": "Cambiar Valor de Comisión",
            "descripcion": "Proceso para corregir o actualizar montos de comisión",
            "tiempo_estimado": 7,
            "dificultad": "Media",
            "pasos": [
                {
                    "numero": 1,
                    "titulo": "Identificar Crédito y Valor Actual",
                    "descripcion": "Localiza el crédito y consulta el valor actual",
                    "tipo": "preparacion",
                    "tiempo": 2,
                    "sql": "SELECT CreditNumber, ValueCommission, ValueCommissionConcesionario FROM formatexceldlle WHERE CreditNumber = '[CREDITO]'",
                    "instrucciones": [
                        "Busca el número de crédito en la PQRS",
                        "Ejecuta el SQL",
                        "Anota los valores actuales"
                    ]
                },
                {
                    "numero": 2,
                    "titulo": "Verificar Valor Nuevo",
                    "descripcion": "Valida que el valor nuevo sea correcto",
                    "tipo": "validacion",
                    "tiempo": 2,
                    "instrucciones": [
                        "Confirma el valor nuevo con la PQRS",
                        "Verifica que tenga sentido",
                        "Si es mayor a $500,000 requiere aprobación"
                    ]
                },
                {
                    "numero": 3,
                    "titulo": "Generar SQL de Actualización",
                    "descripcion": "Crea el UPDATE",
                    "tipo": "accion",
                    "tiempo": 1,
                    "sql": "UPDATE formatexceldlle SET ValueCommission = [VALOR] WHERE CreditNumber = '[CREDITO]'",
                    "instrucciones": [
                        "Reemplaza [VALOR] con el monto nuevo",
                        "Reemplaza [CREDITO] con el número",
                        "Revisa la sintaxis"
                    ]
                },
                {
                    "numero": 4,
                    "titulo": "Ejecutar y Verificar",
                    "descripcion": "Aplica el cambio",
                    "tipo": "ejecucion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Ejecuta el UPDATE",
                        "Verifica '1 row affected'",
                        "Ejecuta SELECT para confirmar"
                    ]
                },
                {
                    "numero": 5,
                    "titulo": "Documentar y Notificar",
                    "descripcion": "Registra el cambio",
                    "tipo": "comunicacion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Documenta en el ticket",
                        "Si es cambio grande, notifica a finanzas",
                        "Responde al usuario"
                    ]
                }
            ]
        }
    
    def _guia_actualizar_vendedor(self) -> Dict:
        """Guía para actualizar datos de vendedor"""
        return {
            "tipo": "actualizar_vendedor",
            "titulo": "Actualizar Datos de Vendedor",
            "descripcion": "Cambiar o corregir información de un vendedor",
            "tiempo_estimado": 8,
            "dificultad": "Media-Alta",
            "pasos": [
                {
                    "numero": 1,
                    "titulo": "Identificar el Vendedor",
                    "descripcion": "Busca el vendedor por cédula",
                    "tipo": "preparacion",
                    "tiempo": 2,
                    "sql": "SELECT UserID, FirstName, LastName, BankID, AccountNumber FROM user WHERE Identification = '[CEDULA]' AND TypeUserID = 1",
                    "instrucciones": [
                        "Busca por cédula",
                        "TypeUserID = 1 significa vendedor",
                        "Anota el UserID"
                    ]
                },
                {
                    "numero": 2,
                    "titulo": "Preparar los Datos Nuevos",
                    "descripcion": "Recopila la información nueva",
                    "tipo": "preparacion",
                    "tiempo": 2,
                    "instrucciones": [
                        "Confirma el banco nuevo",
                        "Verifica el número de cuenta (mínimo 8 dígitos)",
                        "Confirma el tipo de cuenta (1=Ahorros, 2=Corriente)"
                    ]
                },
                {
                    "numero": 3,
                    "titulo": "Generar SQL de Actualización",
                    "descripcion": "Crea el UPDATE",
                    "tipo": "accion",
                    "tiempo": 2,
                    "sql": "UPDATE user SET BankID = [BANCO], AccountNumber = '[CUENTA]', TypeAccountBankID = [TIPO] WHERE UserID = [USERID]",
                    "instrucciones": [
                        "Reemplaza los valores",
                        "SIEMPRE usa WHERE UserID",
                        "Revisa 2 veces antes de ejecutar"
                    ],
                    "advertencias": [
                        "⚠️ NUNCA ejecutes UPDATE sin WHERE",
                        "⚠️ Cambios en tabla user son CRÍTICOS"
                    ]
                },
                {
                    "numero": 4,
                    "titulo": "Ejecutar con Precaución",
                    "descripcion": "Aplica el cambio",
                    "tipo": "ejecucion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Verifica el SQL 2 veces",
                        "Ejecuta",
                        "DEBE decir '1 row affected'"
                    ]
                },
                {
                    "numero": 5,
                    "titulo": "Verificación Final",
                    "descripcion": "Confirma que se aplicó",
                    "tipo": "verificacion",
                    "tiempo": 1,
                    "sql": "SELECT BankID, AccountNumber FROM user WHERE UserID = [USERID]",
                    "instrucciones": [
                        "Ejecuta el SELECT",
                        "Verifica que los valores son los nuevos",
                        "Confirma al usuario"
                    ]
                }
            ],
            "notas_adicionales": [
                "🚨 Tabla user es CRÍTICA",
                "📝 TODO cambio debe estar respaldado"
            ]
        }
    
    def _guia_generica(self) -> Dict:
        """Guía genérica para problemas no categorizados"""
        return {
            "tipo": "generico",
            "titulo": "Resolución de PQRS - Guía General",
            "descripcion": "Pasos generales para resolver una PQRS",
            "tiempo_estimado": 10,
            "dificultad": "Variable",
            "pasos": [
                {
                    "numero": 1,
                    "titulo": "Entender el Problema",
                    "descripcion": "Lee y analiza la PQRS",
                    "tipo": "preparacion",
                    "tiempo": 2,
                    "instrucciones": [
                        "Lee completa la PQRS",
                        "Identifica: ¿Qué necesita el usuario?",
                        "Extrae datos clave"
                    ]
                },
                {
                    "numero": 2,
                    "titulo": "Buscar Casos Similares",
                    "descripcion": "Usa el sistema de búsqueda",
                    "tipo": "consulta",
                    "tiempo": 2,
                    "instrucciones": [
                        "Usa el sistema de búsqueda inteligente",
                        "Busca palabras clave",
                        "Revisa casos resueltos anteriormente"
                    ]
                },
                {
                    "numero": 3,
                    "titulo": "Generar Solución",
                    "descripcion": "Crea el SQL necesario",
                    "tipo": "accion",
                    "tiempo": 3,
                    "instrucciones": [
                        "Basado en casos similares, genera el SQL",
                        "Valida la sintaxis",
                        "Revisa que use WHERE apropiado"
                    ]
                },
                {
                    "numero": 4,
                    "titulo": "Ejecutar",
                    "descripcion": "Aplica la solución",
                    "tipo": "ejecucion",
                    "tiempo": 2,
                    "instrucciones": [
                        "Ejecuta el SQL",
                        "Verifica el resultado",
                        "Confirma que funcionó"
                    ]
                },
                {
                    "numero": 5,
                    "titulo": "Responder al Usuario",
                    "descripcion": "Notifica la solución",
                    "tipo": "comunicacion",
                    "tiempo": 1,
                    "instrucciones": [
                        "Confirma que se resolvió",
                        "Explica qué se hizo",
                        "Da próximos pasos si aplica"
                    ]
                }
            ]
        }
    
    def _personalizar_guia(self, guia: Dict, contexto: Dict) -> Dict:
        """Personaliza una guía con el contexto específico"""
        for paso in guia.get("pasos", []):
            if "sql" in paso:
                sql = paso["sql"]
                for key, value in contexto.items():
                    placeholder = f"[{key.upper()}]"
                    if placeholder in sql:
                        sql = sql.replace(placeholder, str(value))
                paso["sql"] = sql
        
        return guia
    
    def generar_checklist_texto(self, guia: Dict) -> str:
        """Genera un checklist en texto plano"""
        lineas = []
        lineas.append("═" * 60)
        lineas.append(f"  {guia['titulo'].upper()}")
        lineas.append("═" * 60)
        lineas.append(f"\nDescripción: {guia['descripcion']}")
        lineas.append(f"Tiempo estimado: {guia['tiempo_estimado']} minutos")
        lineas.append(f"Dificultad: {guia['dificultad']}\n")
        lineas.append("─" * 60)
        
        for paso in guia.get("pasos", []):
            lineas.append(f"\n[ ] PASO {paso['numero']}: {paso['titulo']}")
            lineas.append(f"    ⏱️ {paso.get('tiempo', 1)} min")
            lineas.append(f"\n    {paso['descripcion']}")
            
            if "sql" in paso:
                lineas.append(f"\n    📝 SQL:")
                lineas.append(f"    {paso['sql']}")
            
            if "instrucciones" in paso:
                lineas.append(f"\n    📋 Instrucciones:")
                for inst in paso["instrucciones"]:
                    lineas.append(f"       • {inst}")
            
            if "advertencias" in paso:
                lineas.append(f"\n    ⚠️ Advertencias:")
                for adv in paso["advertencias"]:
                    lineas.append(f"       {adv}")
            
            lineas.append("\n" + "─" * 60)
        
        if "notas_adicionales" in guia:
            lineas.append("\n📌 NOTAS ADICIONALES:")
            for nota in guia["notas_adicionales"]:
                lineas.append(f"   {nota}")
        
        lineas.append("\n" + "═" * 60)
        
        return "\n".join(lineas)


def detectar_tipo_problema(descripcion: str) -> str:
    """Detecta el tipo de problema basado en la descripción"""
    desc_lower = descripcion.lower()
    
    if "estado" in desc_lower and ("cambiar" in desc_lower or "actualizar" in desc_lower):
        return "cambio_estado"
    elif "comision" in desc_lower or "comisión" in desc_lower:
        return "cambio_comision"
    elif "vendedor" in desc_lower and ("actualizar" in desc_lower or "cambiar" in desc_lower or "datos" in desc_lower):
        return "actualizar_vendedor"
    else:
        return "generico"


__all__ = ['GuiaPasoAPaso', 'detectar_tipo_problema']