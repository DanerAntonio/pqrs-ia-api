#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  BASE DE CONOCIMIENTO DEL SISTEMA PQRS
  
  Información clave que el agente usa para responder mejor:
  - Estados y códigos
  - Tablas y campos
  - Reglas de negocio
  - Bancos
  - Procedimientos
═══════════════════════════════════════════════════════════════════
"""

import json
import os

class BaseConocimiento:
    
    def __init__(self):
        self.archivo_conocimiento = 'conocimiento_base.json'
        self.conocimiento = self.cargar_conocimiento()
    
    def cargar_conocimiento(self):
        """Carga el conocimiento base desde archivo"""
        if os.path.exists(self.archivo_conocimiento):
            try:
                with open(self.archivo_conocimiento, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # Conocimiento por defecto
        return self.crear_conocimiento_inicial()
    
    def crear_conocimiento_inicial(self):
        """Crea la base de conocimiento inicial"""
        conocimiento = {
            "estados_liquidacion": {
                "descripcion": "Estados del proceso de liquidación de comisiones",
                "valores": {
                    "70": "Bloqueado (temporalmente inactivo)",
                    "71": "Pendiente Aprobación Asesor",
                    "72": "Aprobado Asesor",
                    "73": "Rechazado Asesor",
                    "74": "Pendiente Aprobación Coordinador",
                    "75": "Aprobado Coordinador",
                    "76": "Rechazado Coordinador",
                    "77": "Aprobados Jefe Coordinador",
                    "78": "Rechazado Jefe Coordinador",
                    "79": "Pagado",
                    "80": "Anulado"
                },
                "notas": "Estado 77 es el más común para aprobar pagos de comisiones"
            },
            
            "tablas_principales": {
                "formatexceldlle": {
                    "descripcion": "Tabla principal de liquidación de comisiones",
                    "campos_importantes": [
                        "CreditNumber: Número de crédito (13-16 dígitos)",
                        "EstadoLiquidacionVendedor: Estado de liquidación del vendedor",
                        "EstadoLiquidacionConcesionario: Estado de liquidación del concesionario",
                        "FirstName: Nombre del vendedor",
                        "LastName: Apellido del vendedor",
                        "Cedula: Cédula del vendedor",
                        "ValueCommission: Valor total de la comisión",
                        "ValueCommissionVendedor: Comisión del vendedor",
                        "ValueCommissionConsecionario: Comisión del concesionario",
                        "FactorMillon: Factor millón total",
                        "FactorMillonConcesionario: Factor del concesionario"
                    ],
                    "relaciones": [
                        "Se relaciona con formatexceldllecommission por FormatExcelDlleID",
                        "Se relaciona con user por Cedula"
                    ]
                },
                
                "formatexceldllecommission": {
                    "descripcion": "Detalle de comisiones asociadas a liquidaciones",
                    "campos_importantes": [
                        "FormatExcelDlleCommissionID: ID único de la comisión",
                        "FormatExcelDlleID: ID de la liquidación padre",
                        "UserID: ID del usuario asociado",
                        "CommissionValue: Valor de la comisión"
                    ]
                },
                
                "user": {
                    "descripcion": "Información de usuarios (vendedores, clientes, proveedores)",
                    "campos_importantes": [
                        "UserID: ID único del usuario",
                        "Identification: Cédula o NIT",
                        "FirstName: Nombre",
                        "LastName: Apellido",
                        "UserType: Tipo de usuario (Vendedor, Cliente, etc.)"
                    ]
                },
                
                "certificatefileuser": {
                    "descripcion": "Certificados tributarios de proveedores",
                    "campos_importantes": [
                        "CertificateFileUserID: ID del certificado",
                        "UserID: ID del proveedor",
                        "CertificateFileID: Tipo de certificado (ReteIVA, ReteFuente)",
                        "ValorBase: Base gravable",
                        "ValorDeduccion: Valor de la retención",
                        "FileName: Nombre del archivo PDF",
                        "URI: URL del certificado"
                    ]
                },
                
                "status": {
                    "descripcion": "Catálogo de estados del sistema",
                    "campos_importantes": [
                        "StatusID: ID del estado",
                        "Name: Nombre del estado",
                        "Description: Descripción del estado"
                    ]
                }
            },
            
            "reglas_negocio": {
                "liquidaciones": [
                    "Solo se pueden pagar comisiones en estado 77 (Aprobados Jefe Coordinador)",
                    "El estado debe cambiar primero de 71 → 77 para aprobar",
                    "Si hay rechazo, se usa estado 73, 76 o 78 según el nivel",
                    "Estado 70 se usa para bloquear temporalmente mientras se hacen correcciones",
                    "Cambios de vendedor requieren actualizar tanto FormatExcelDlle como FormatExcelDlleCommission"
                ],
                
                "certificados": [
                    "Los certificados se generan por mes y por tipo",
                    "ReteIVA: CertificateFileID = 349",
                    "ReteFuente: Verificar en tabla CertificateFile",
                    "El URI debe apuntar a Azure Blob Storage",
                    "Formato de URI: https://fisapay.blob.core.windows.net/fisapay-archivos/CertificateFile/[AÑO]/[TIPO]/[MES]/[archivo].pdf"
                ],
                
                "comisiones": [
                    "ValueCommission = ValueCommissionVendedor + ValueCommissionConsecionario + ValueCommissionTercero",
                    "FactorMillon se calcula sobre el valor del crédito",
                    "Típicamente: FactorMillon = 10000 para vendedor y concesionario"
                ]
            },
            
            "bancos_entidades": {
                "descripcion": "Bancos y entidades del sistema",
                "lista": [
                    "Davivienda",
                    "Bancolombia",
                    "Banco de Bogotá",
                    "Banco Popular",
                    "BBVA",
                    "Scotiabank Colpatria",
                    "Itaú",
                    "Banco Caja Social",
                    "Banco AV Villas"
                ],
                "notas": "Cada banco puede tener diferentes rutas y códigos en el sistema"
            },
            
            "canales_desembolso": {
                "descripcion": "Canales por los que se desembolsan créditos",
                "valores": [
                    "Concesionario: Desembolso directo al concesionario",
                    "Banco: Desembolso a cuenta bancaria del cliente",
                    "Libranza: Descuento por nómina",
                    "Mixto: Combinación de canales"
                ]
            },
            
            "procedimientos_comunes": {
                "cambiar_estado_liquidacion": {
                    "pasos": [
                        "1. Validar el crédito en formatexceldlle",
                        "2. Verificar estado actual",
                        "3. Consultar tabla Status para confirmar código del nuevo estado",
                        "4. Ejecutar UPDATE para cambiar estado",
                        "5. Validar que el cambio se haya aplicado"
                    ],
                    "ejemplo_sql": """
-- Paso 1: Validar crédito
SELECT * FROM formatexceldlle WHERE creditnumber = '[CREDITO]';

-- Paso 2: Verificar estados disponibles
SELECT * FROM Status;

-- Paso 3: Actualizar estados
UPDATE formatexceldlle
SET EstadoLiquidacionVendedor = 77,
    EstadoLiquidacionConcesionario = 77
WHERE creditnumber = '[CREDITO]';
                    """
                },
                
                "actualizar_vendedor": {
                    "pasos": [
                        "1. Buscar vendedor en tabla user por cédula",
                        "2. Validar crédito en formatexceldlle",
                        "3. Actualizar datos del vendedor en formatexceldlle",
                        "4. Actualizar UserID en formatexceldllecommission si existe"
                    ],
                    "ejemplo_sql": """
-- Paso 1: Buscar vendedor
SELECT * FROM [user] WHERE identification = '[CEDULA]';

-- Paso 2: Actualizar en formatexceldlle
UPDATE formatexceldlle
SET firstname = '[NOMBRE]',
    lastname = '[APELLIDO]',
    cedula = '[CEDULA]'
WHERE creditnumber = '[CREDITO]';

-- Paso 3: Actualizar comisión
UPDATE formatexceldllecommission
SET userid = [USER_ID]
WHERE formatexceldlleid = [FORMATEXCELDLLE_ID];
                    """
                },
                
                "corregir_certificado": {
                    "pasos": [
                        "1. Validar proveedor por NIT",
                        "2. Buscar certificado en certificatefileuser",
                        "3. Actualizar valores y archivo",
                        "4. Validar cambios"
                    ],
                    "ejemplo_sql": """
-- Paso 1: Validar proveedor
SELECT * FROM [user] WHERE identification = '[NIT]';

-- Paso 2: Actualizar certificado
UPDATE certificatefileuser
SET valorbase = [VALOR_BASE],
    valordeduccion = [VALOR_RETENCION],
    filename = '[NOMBRE_ARCHIVO].pdf',
    uri = '[URL_COMPLETA]'
WHERE certificatefileuserid = [ID];
                    """
                }
            },
            
            "preguntas_frecuentes": {
                "¿Cómo cambio el estado de liquidación?": "Usa UPDATE en formatexceldlle cambiando EstadoLiquidacionVendedor y/o EstadoLiquidacionConcesionario al código del nuevo estado (consulta tabla Status)",
                
                "¿Qué estado uso para aprobar pago?": "Estado 77 (Aprobados Jefe Coordinador) es el estado final para aprobar pagos",
                
                "¿Cómo actualizo un vendedor?": "Debes actualizar firstname, lastname y cedula en formatexceldlle, y el userid en formatexceldllecommission",
                
                "¿Dónde están los códigos de estado?": "En la tabla Status. Los más usados son: 71 (Pendiente), 77 (Aprobado), 79 (Pagado)",
                
                "¿Cómo corregir valores de comisión?": "Actualiza ValueCommissionVendedor, ValueCommissionConsecionario en formatexceldlle asegurándote que la suma sea igual a ValueCommission"
            }
        }
        
        # Guardar conocimiento inicial
        self.guardar_conocimiento(conocimiento)
        
        return conocimiento
    
    def guardar_conocimiento(self, conocimiento):
        """Guarda el conocimiento en archivo JSON"""
        try:
            with open(self.archivo_conocimiento, 'w', encoding='utf-8') as f:
                json.dump(conocimiento, f, indent=2, ensure_ascii=False)
            print(f"✅ Conocimiento guardado en {self.archivo_conocimiento}")
        except Exception as e:
            print(f"⚠️ Error guardando conocimiento: {e}")
    
    def buscar_estado(self, termino):
        """Busca un estado por nombre o código"""
        termino_lower = str(termino).lower()
        estados = self.conocimiento.get('estados_liquidacion', {}).get('valores', {})
        
        # Buscar por código
        if termino in estados:
            return {
                'codigo': termino,
                'nombre': estados[termino],
                'encontrado': True
            }
        
        # Buscar por nombre
        for codigo, nombre in estados.items():
            if termino_lower in nombre.lower():
                return {
                    'codigo': codigo,
                    'nombre': nombre,
                    'encontrado': True
                }
        
        return {'encontrado': False}
    
    def buscar_tabla(self, nombre_tabla):
        """Busca información de una tabla"""
        tablas = self.conocimiento.get('tablas_principales', {})
        
        nombre_lower = nombre_tabla.lower()
        for tabla, info in tablas.items():
            if nombre_lower in tabla.lower():
                return {
                    'tabla': tabla,
                    'info': info,
                    'encontrado': True
                }
        
        return {'encontrado': False}
    
    def buscar_procedimiento(self, termino):
        """Busca un procedimiento común"""
        procedimientos = self.conocimiento.get('procedimientos_comunes', {})
        
        termino_lower = termino.lower()
        for nombre, info in procedimientos.items():
            if termino_lower in nombre.lower() or any(termino_lower in paso.lower() for paso in info.get('pasos', [])):
                return {
                    'nombre': nombre,
                    'info': info,
                    'encontrado': True
                }
        
        return {'encontrado': False}
    
    def buscar_en_conocimiento(self, query):
        """Busca en toda la base de conocimiento"""
        query_lower = query.lower()
        resultados = []
        
        # Buscar en estados
        if any(palabra in query_lower for palabra in ['estado', 'liquidacion', 'aprobado', 'pendiente']):
            estados = self.conocimiento.get('estados_liquidacion', {})
            resultados.append({
                'tipo': 'Estados de Liquidación',
                'contenido': estados
            })
        
        # Buscar en tablas
        if any(palabra in query_lower for palabra in ['tabla', 'campo', 'formatexcel', 'user', 'certificate']):
            for tabla in query_lower.split():
                info_tabla = self.buscar_tabla(tabla)
                if info_tabla.get('encontrado'):
                    resultados.append({
                        'tipo': f'Tabla: {info_tabla["tabla"]}',
                        'contenido': info_tabla['info']
                    })
        
        # Buscar en reglas
        if any(palabra in query_lower for palabra in ['regla', 'como', 'procedimiento']):
            reglas = self.conocimiento.get('reglas_negocio', {})
            resultados.append({
                'tipo': 'Reglas de Negocio',
                'contenido': reglas
            })
        
        # Buscar en procedimientos
        procedimientos = self.conocimiento.get('procedimientos_comunes', {})
        for nombre, info in procedimientos.items():
            if any(palabra in query_lower for palabra in nombre.split('_')):
                resultados.append({
                    'tipo': f'Procedimiento: {nombre}',
                    'contenido': info
                })
        
        return resultados
    
    def agregar_conocimiento(self, categoria, clave, valor):
        """Agrega nuevo conocimiento a la base"""
        if categoria not in self.conocimiento:
            self.conocimiento[categoria] = {}
        
        self.conocimiento[categoria][clave] = valor
        self.guardar_conocimiento(self.conocimiento)
        
        return True
    
    def obtener_contexto_para_agente(self, problema):
        """
        Obtiene el contexto relevante de conocimiento para un problema
        
        Args:
            problema: El problema descrito por el usuario
            
        Returns:
            String con el contexto relevante
        """
        resultados = self.buscar_en_conocimiento(problema)
        
        if not resultados:
            return ""
        
        contexto = "\n📚 **Información relevante de la base de conocimiento:**\n\n"
        
        for resultado in resultados[:3]:  # Máximo 3 resultados
            contexto += f"**{resultado['tipo']}:**\n"
            
            contenido = resultado['contenido']
            if isinstance(contenido, dict):
                if 'valores' in contenido:
                    # Es un catálogo de valores
                    for k, v in list(contenido['valores'].items())[:5]:
                        contexto += f"  • {k}: {v}\n"
                elif 'pasos' in contenido:
                    # Es un procedimiento
                    for paso in contenido['pasos'][:3]:
                        contexto += f"  {paso}\n"
                elif 'campos_importantes' in contenido:
                    # Es una tabla
                    contexto += f"  {contenido.get('descripcion', '')}\n"
            
            contexto += "\n"
        
        return contexto


# Crear instancia global
base_conocimiento = BaseConocimiento()
