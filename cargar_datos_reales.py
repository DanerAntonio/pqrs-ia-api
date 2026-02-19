#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar la base de conocimiento con datos reales
Estados, Bancos y Usuarios de tu sistema
"""

import json
import os

def actualizar_base_conocimiento():
    """Actualiza el archivo conocimiento_base.json con datos reales"""
    
    # Leer archivo actual si existe
    archivo = 'conocimiento_base.json'
    
    if os.path.exists(archivo):
        with open(archivo, 'r', encoding='utf-8') as f:
            conocimiento = json.load(f)
    else:
        conocimiento = {}
    
    # ============================================================
    # ESTADOS REALES DEL SISTEMA
    # ============================================================
    
    conocimiento['estados_sistema'] = {
        "descripcion": "Catálogo completo de estados del sistema (tabla Status)",
        "valores": {
            # Estados generales
            "0": "Sin Procesar",
            "1": "Provisionado",
            "2": "Pagado",
            "3": "Aprobado",
            "4": "Rechazado",
            "5": "Iniciado",
            "6": "Finalizado",
            "7": "Con Errores",
            "10": "Enviado",
            "15": "Eliminado",
            "20": "Asignado",
            
            # Estados de seguridad social
            "21": "Pendiente seguridad social",
            "22": "Pendiente RF y pendiente validar",
            "23": "Validado",
            "24": "Proceso Pago",
            
            # Estados de inscripción
            "25": "No inscrita",
            "26": "Pre-inscrita",
            "27": "Inscrita",
            
            # Estados de vinculación
            "40": "No Vinculado",
            "41": "No Registrado",
            "42": "Registrado",
            "43": "Registro Completo",
            "44": "Visado",
            
            # Estados de planeación y comercial
            "50": "Pendiente Asignar Ejecutivo Comercial",
            "51": "Pendiente Asignar Vendedor",
            "52": "Pendiente Aprobacion Planeacion",
            "53": "Rechazado Planeacion",
            "54": "Aprobado Planeación",
            "55": "Vendedor y Concesionario Asignados",
            "56": "Rechazado Financiera",
            "57": "Enviado a Pagos",
            "58": "Pendiente Aprobación Valores",
            "59": "Rechazado Valores",
            "60": "Comision No Calculada",
            
            # Estados de liquidación (MÁS IMPORTANTES)
            "70": "Sin Liquidar",
            "71": "Pendiente Aprobación Asesor",
            "72": "Aprobados Asesor",
            "73": "Sin Convenio",
            "74": "No Aplica",
            "75": "Sin Vendedor",
            "76": "Usuario NR/NA",
            "77": "Aprobados Jefe-Coordinador",  # ← EL MÁS USADO
            "78": "Aprobados Especialista",
            "79": "Liquidacion Manual",
            "80": "N/A Credito Directo",
            "81": "Seguro Calculado",
            "83": "En proceso",
            "84": "Pagos en proceso",
            "85": "Pendiente de pago",
            "86": "Cargue con novedades",
            "87": "Pendiente validacion",
            "88": "Descargar archivos",
            
            # Estados de aprobación por niveles
            "100": "Pendiente Aprobacion Nivel I",
            "101": "Pendiente Aprobacion Nivel II",
            "102": "Pendiente de Registro en Fisapay",
            "103": "Proceso Registro en Fisapay",
            "104": "Pendiente de confirmación",
            "105": "Rechazado por Nivel I",
            "106": "Rechazado por Nivel II",
            "107": "Registrado DAV",
            "108": "Vinculacion Finalizada",
            
            # Estados PQRS
            "121": "RADICADO",
            "122": "ASIGNADO",
            "123": "ESCALADO",
            "124": "OBSERVACIÓN",
            "125": "DESCARTADO",
            "126": "FINALIZADO",
            "127": "RESPUESTA ESCALADO",
            "128": "REACTIVADO",
            "129": "RE-ASIGNACIÓN",
            
            # Estados de facturas
            "130": "Factura Recibida",
            "131": "Evento 030",
            "132": "Evento 032",
            "133": "Evento 033",
            "134": "Evento 031",
            "135": "Rechazado DIAN",
            "136": "Facturas Asignada",
            "137": "Aprobado N1",
            "138": "Aprobado N2",
            "139": "Aprobado N3",
            "140": "Pendiente Aprob Final",
            "141": "Aprobado N4",
            "142": "Factura enviada a Siigo",
            
            # Estados de validación
            "143": "Validacion Usuarios Novedades",
            "144": "Validacion Usuarios Exitosa",
            "145": "Planilla Lista Envio",
            "146": "Error Creando Planilla",
            "147": "Planilla Creada",
            "148": "Reversado",
            "149": "Pendiente de envio",
            "150": "null",
            "151": "Cruce completo",
            "152": "Cruce parcial",
            
            # Estados Palig
            "155": "Radicada",
            "156": "En Proceso",
            "157": "Liquidada",
            "158": "Liquidada con glosa",
            "159": "Devuelta",
            "160": "Pagada con Glosa",
            "161": "Auditoria Médica",
            "162": "Migrado Pagado",
            "163": "Pendiente Validación Fisapay",
            "164": "Rechazado Fisapay",
            "165": "Gastos Bancarios Enviados",
            "166": "Valor Servicio Enviado"
        },
        "notas": [
            "Estado 77 (Aprobados Jefe-Coordinador) es el más común para aprobar pagos",
            "Estado 71 (Pendiente Aprobación Asesor) es el estado inicial de liquidación",
            "Estados 70-88 son específicos de liquidación de comisiones",
            "Estados 121-129 son para gestión de PQRS"
        ]
    }
    
    # ============================================================
    # BANCOS REALES
    # ============================================================
    
    conocimiento['bancos'] = {
        "descripcion": "Catálogo de bancos y entidades financieras del sistema",
        "bancos_principales": {
            "1": {"nombre": "BANCO DE BOGOTÁ", "codigo": "1001"},
            "2": {"nombre": "BANCOLOMBIA", "codigo": "1007"},
            "4": {"nombre": "AV VILLAS", "codigo": "1052"},
            "5": {"nombre": "BANCO AGRARIO", "codigo": "1040"},
            "6": {"nombre": "CORPBANCA", "codigo": "1006"},
            "7": {"nombre": "BANCO DE BOGOTÁ", "codigo": "1001"},
            "8": {"nombre": "BANCO FALABELLA", "codigo": "1062"},
            "9": {"nombre": "BANCO GNB SUDAMERIS", "codigo": "1012"},
            "10": {"nombre": "BANCO PICHINCHA", "codigo": "1060"},
            "11": {"nombre": "BANCO POPULAR", "codigo": "1002"},
            "12": {"nombre": "BANCO SANTANDER", "codigo": "1065"},
            "13": {"nombre": "MIBANCO", "codigo": "1067"},
            "14": {"nombre": "BANCOOMEVA", "codigo": "1061"},
            "15": {"nombre": "BBVA COLOMBIA", "codigo": "1013"},
            "16": {"nombre": "CAJA SOCIAL", "codigo": "1032"},
            "18": {"nombre": "SCOTIABANK COLPATRIA", "codigo": "1019"},
            "19": {"nombre": "COLPATRIA", "codigo": "1019"},
            "30": {"nombre": "ITAÚ", "codigo": "1014"}
        },
        "entidades_financieras": {
            "20": "COLTEFINANCIERA PROVEEDORES",
            "21": "PROVEEDORES DAVIVIENDA",
            "23": "FINANCIERA JURISCOOP",
            "24": "BANCO FINANDINA",
            "31": "TFS (Toyota Financial Services)",
            "34": "FINANZAUTO",
            "35": "CONFIRMEZA",
            "36": "FINESA",
            "37": "RCI",
            "39": "PLANAUTOS",
            "41": "CREDILIKE",
            "42": "RENTING COLOMBIA",
            "44": "PORSCHE MOVILIDAD",
            "48": "INTERCREDITO",
            "52": "PORSCHE COLOMBIA",
            "53": "AUTOFINANCIERA",
            "54": "FONBIENES",
            "73": "BAN100"
        },
        "codigos_ach": {
            "BANCOLOMBIA": "00560007",
            "DAVIVIENDA": "00589514",
            "BANCO_BOGOTA": "00560001",
            "AV_VILLAS": "00540209",
            "BANCO_PICHINCHA": "00560060",
            "COLPATRIA": "00560019"
        }
    }
    
    # ============================================================
    # FLUJOS DE LIQUIDACIÓN
    # ============================================================
    
    conocimiento['flujos_liquidacion'] = {
        "flujo_normal": [
            "70: Sin Liquidar",
            "71: Pendiente Aprobación Asesor",
            "77: Aprobados Jefe-Coordinador",
            "79: Pagado"
        ],
        "flujo_con_rechazo": [
            "71: Pendiente Aprobación Asesor",
            "73: Sin Convenio / 75: Sin Vendedor → Rechazado",
            "Corrección manual",
            "77: Aprobados Jefe-Coordinador"
        ],
        "transiciones_comunes": {
            "71 → 77": "Aprobación directa de asesor a jefe",
            "71 → 72": "Aprobación por asesor",
            "72 → 77": "Aprobación final por jefe",
            "77 → 79": "Pago ejecutado",
            "cualquier_estado → 70": "Bloqueo temporal para corrección"
        }
    }
    
    # ============================================================
    # CAMPOS IMPORTANTES
    # ============================================================
    
    conocimiento['campos_criticos'] = {
        "formatexceldlle": {
            "CreditNumber": "Número de crédito (13-16 dígitos)",
            "EstadoLiquidacionVendedor": "Estado de liquidación del vendedor (tabla Status)",
            "EstadoLiquidacionConcesionario": "Estado de liquidación del concesionario (tabla Status)",
            "FirstName": "Nombre del vendedor",
            "LastName": "Apellido del vendedor",
            "Cedula": "Cédula del vendedor",
            "ValueCommission": "Valor total de comisión",
            "ValueCommissionVendedor": "Comisión del vendedor",
            "ValueCommissionConsecionario": "Comisión del concesionario",
            "FactorMillon": "Factor millón total"
        },
        "user": {
            "UserID": "ID único del usuario",
            "TypeUserID": "Tipo de usuario (1=Vendedor, 2=Empresa, 6=Admin)",
            "Identification": "Cédula o NIT",
            "FirstName": "Nombre",
            "BankID": "ID del banco asociado",
            "TypeAccountBankID": "Tipo de cuenta (1=Ahorros, 2=Corriente)"
        },
        "bank": {
            "BankID": "ID del banco",
            "Name": "Nombre del banco",
            "CodeID": "Código del banco",
            "CodeRepublicBank": "Código ACH"
        }
    }
    
    # Guardar
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(conocimiento, f, indent=2, ensure_ascii=False)
    
    print("✅ Base de conocimiento actualizada con:")
    print(f"   - {len(conocimiento['estados_sistema']['valores'])} estados")
    print(f"   - {len(conocimiento['bancos']['bancos_principales'])} bancos principales")
    print(f"   - {len(conocimiento['bancos']['entidades_financieras'])} entidades financieras")
    print(f"   - Flujos de liquidación documentados")
    print(f"   - Campos críticos de tablas principales")
    print(f"\n📄 Archivo guardado: {archivo}")

if __name__ == "__main__":
    actualizar_base_conocimiento()
    print("\n🎯 Ahora reinicia la app de Streamlit para que cargue el nuevo conocimiento")
