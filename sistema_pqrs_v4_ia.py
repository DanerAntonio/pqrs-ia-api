#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  SISTEMA INTELIGENTE DE PQRS - VERSIÓN 4.0 CON IA REAL
  
  ✨ Embeddings con Sentence-BERT para búsqueda semántica
  ✨ Entiende el significado real de los problemas
  ✨ Encuentra casos aunque uses palabras completamente diferentes
═══════════════════════════════════════════════════════════════════
"""

import sqlite3
import re
from difflib import SequenceMatcher
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SistemaPQRSIA:
    
    def __init__(self):
        self.db = 'pqrs_sistema.db'
        self.conn = None
        
        # Cargar modelo de embeddings (pequeño y rápido)
        print("🔄 Cargando modelo de IA...")
        self.modelo_embeddings = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Modelo cargado")
        
        # Cache de embeddings
        self.cache_embeddings = {}
        self.cache_file = 'embeddings_cache.pkl'
        
        # DICCIONARIO DE SINÓNIMOS
        self.sinonimos = {
            # Acciones
            'eliminar': ['borrar', 'quitar', 'remover', 'sacar', 'anular', 'cancelar'],
            'actualizar': ['modificar', 'cambiar', 'editar', 'corregir', 'ajustar'],
            'crear': ['generar', 'agregar', 'añadir', 'insertar', 'registrar'],
            'consultar': ['ver', 'revisar', 'buscar', 'verificar'],
            'asignar': ['asociar', 'vincular', 'relacionar'],
            
            # Entidades
            'comision': ['comisión', 'fee', 'cargo'],
            'credito': ['crédito', 'prestamo', 'préstamo'],
            'vendedor': ['asesor', 'comercial'],
            'concesionario': ['dealer'],
            'liquidacion': ['liquidación', 'settlement'],
            'estado': ['status', 'estatus'],
            'certificado': ['certificate'],
            'factura': ['invoice', 'recibo'],
        }
        
        self.inicializar()
        self.cargar_cache_embeddings()
    
    def inicializar(self):
        """Inicializa base de datos"""
        self.conn = sqlite3.connect(self.db, check_same_thread=False)
        c = self.conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS casos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT,
                problema TEXT,
                sql TEXT,
                respuesta TEXT,
                usos INTEGER DEFAULT 0,
                efectividad INTEGER DEFAULT 0,
                conceptos_clave TEXT,
                complejidad INTEGER DEFAULT 1
            )
        ''')
        
        self.conn.commit()
        
        # Cargar casos desde archivo si la BD está vacía
        c.execute('SELECT COUNT(*) FROM casos')
        if c.fetchone()[0] == 0:
            self.cargar_desde_archivo()
    
    def normalizar_texto(self, texto):
        """Normaliza texto removiendo tildes y convirtiendo a minúsculas"""
        texto = texto.lower()
        reemplazos = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        for viejo, nuevo in reemplazos.items():
            texto = texto.replace(viejo, nuevo)
        return texto
    
    def extraer_conceptos_clave(self, texto):
        """Extrae conceptos clave del texto"""
        texto_norm = self.normalizar_texto(texto)
        conceptos = set()
        
        palabras = re.findall(r'\b\w+\b', texto_norm)
        
        for palabra in palabras:
            if palabra in self.sinonimos:
                conceptos.add(palabra)
                conceptos.update(self.sinonimos[palabra][:2])
            
            for concepto, sinonimos in self.sinonimos.items():
                if palabra in sinonimos:
                    conceptos.add(concepto)
        
        # Detectar entidades
        if re.search(r'\d{13,}', texto):
            conceptos.add('credito')
        if re.search(r'comision|liquidacion', texto_norm):
            conceptos.add('comision')
            conceptos.add('liquidacion')
        if re.search(r'vendedor|asesor', texto_norm):
            conceptos.add('vendedor')
        if re.search(r'certificado', texto_norm):
            conceptos.add('certificado')
        
        return list(conceptos)
    
    def detectar_complejidad(self, problema):
        """Detecta el nivel de complejidad del caso"""
        lineas = problema.count('\n')
        palabras = len(problema.split())
        
        tiene_credito = bool(re.search(r'\d{13,}', problema))
        tiene_valores = bool(re.search(r'\$\s*[\d,.]+', problema))
        
        complejidad = 1
        
        if palabras > 50 or lineas > 5:
            complejidad = 2
        
        if (palabras > 100 or lineas > 10) and (tiene_valores or tiene_credito):
            complejidad = 3
        
        return complejidad
    
    def verificar_informacion_suficiente(self, problema):
        """Verifica si el problema tiene información suficiente"""
        palabras = problema.split()
        
        # Si es muy corto
        if len(palabras) < 10:
            return False, "El problema es demasiado corto. Necesito más detalles."
        
        # Si no tiene número de crédito u otro identificador
        tiene_identificador = bool(re.search(r'\d{8,}', problema))
        
        if not tiene_identificador and len(palabras) < 20:
            return False, "Incluye el número de crédito, cédula, o ID del caso."
        
        # Todo bien
        return True, "OK"
    
    def generar_embedding(self, texto):
        """Genera embedding del texto usando el modelo"""
        # Limpiar y normalizar
        texto_limpio = texto.strip()
        
        # Generar embedding
        embedding = self.modelo_embeddings.encode(texto_limpio, convert_to_numpy=True)
        
        return embedding
    
    def cargar_cache_embeddings(self):
        """Carga embeddings en cache si existe"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.cache_embeddings = pickle.load(f)
                print(f"✅ Cache de embeddings cargado: {len(self.cache_embeddings)} casos")
            except:
                self.cache_embeddings = {}
    
    def guardar_cache_embeddings(self):
        """Guarda embeddings en cache"""
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.cache_embeddings, f)
    
    def calcular_embedding_caso(self, caso_id, problema):
        """Calcula y cachea el embedding de un caso"""
        if caso_id not in self.cache_embeddings:
            self.cache_embeddings[caso_id] = self.generar_embedding(problema)
            self.guardar_cache_embeddings()
        
        return self.cache_embeddings[caso_id]
    
    def cargar_desde_archivo(self):
        """Carga PQRS desde archivo de texto"""
        archivo = 'PQRS_NUEVAS_CON_SQL.txt'
        
        if not os.path.exists(archivo):
            print(f"⚠️  Archivo {archivo} no encontrado")
            return
        
        print(f"🔄 Cargando casos desde {archivo}...")
        
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        bloques = contenido.split('========================')
        casos_cargados = 0
        
        for bloque in bloques:
            if '--- PROBLEMA ---' not in bloque:
                continue
            
            try:
                # Extraer categoría
                cat_match = re.search(r'CATEGOR[ÍI]A:\s*(.+)', bloque)
                categoria = cat_match.group(1).strip() if cat_match else "General"
                
                # Extraer problema
                prob_match = re.search(r'--- PROBLEMA ---\s*(.+?)\s*---', bloque, re.DOTALL)
                problema = prob_match.group(1).strip() if prob_match else ""
                
                # Extraer SQL
                sql_match = re.search(r'--- SOLUCI[ÓO]N T[ÉE]CNICA.*?---\s*(.+?)\s*(?:TIEMPO:|ESTADO:|$)', bloque, re.DOTALL)
                sql = sql_match.group(1).strip() if sql_match else ""
                
                # Extraer respuesta
                resp_match = re.search(r'--- SOLUCI[ÓO]N ---\s*(.+?)\s*---', bloque, re.DOTALL)
                respuesta = resp_match.group(1).strip() if resp_match else ""
                
                if problema and sql:
                    # Extraer conceptos
                    conceptos = self.extraer_conceptos_clave(problema)
                    conceptos_str = ','.join(conceptos)
                    complejidad = self.detectar_complejidad(problema)
                    
                    c = self.conn.cursor()
                    c.execute('''
                        INSERT INTO casos (categoria, problema, sql, respuesta, conceptos_clave, complejidad)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (categoria, problema, sql, respuesta, conceptos_str, complejidad))
                    
                    caso_id = c.lastrowid
                    
                    # Generar embedding
                    self.calcular_embedding_caso(caso_id, problema)
                    
                    casos_cargados += 1
            
            except Exception as e:
                print(f"⚠️ Error procesando bloque: {e}")
                continue
        
        self.conn.commit()
        print(f"✅ {casos_cargados} casos cargados correctamente")
        print(f"✅ {len(self.cache_embeddings)} embeddings generados")
    
    def buscar_similar_ia(self, problema):
        """Busca casos similares usando IA (embeddings)"""
        c = self.conn.cursor()
        c.execute('SELECT id, categoria, problema, sql, respuesta, conceptos_clave, complejidad FROM casos')
        casos = c.fetchall()
        
        if not casos:
            return None
        
        # Generar embedding del problema nuevo
        embedding_nuevo = self.generar_embedding(problema)
        
        # Extraer números clave del problema nuevo (créditos, IDs, cédulas)
        numeros_nuevo = set(re.findall(r'\d{5,}', problema))
        
        # Calcular similitudes
        ranking = []
        
        for caso in casos:
            caso_id, cat, prob_bd, sql, resp, conceptos, complejidad = caso
            
            # Obtener embedding del caso
            embedding_caso = self.calcular_embedding_caso(caso_id, prob_bd)
            
            # Calcular similitud coseno (IA REAL)
            similitud_ia = cosine_similarity(
                embedding_nuevo.reshape(1, -1),
                embedding_caso.reshape(1, -1)
            )[0][0]
            
            # Bonus por conceptos clave en común
            conceptos_nuevo = set(self.extraer_conceptos_clave(problema))
            conceptos_bd = set(conceptos.split(',')) if conceptos else set()
            
            bonus_conceptos = 0
            if conceptos_nuevo and conceptos_bd:
                comunes = len(conceptos_nuevo & conceptos_bd)
                total = len(conceptos_nuevo | conceptos_bd)
                bonus_conceptos = (comunes / total) * 0.15 if total > 0 else 0
            
            # Bonus por números/IDs similares (opcional)
            numeros_bd = set(re.findall(r'\d{5,}', prob_bd))
            bonus_numeros = 0
            if numeros_nuevo and numeros_bd:
                if numeros_nuevo & numeros_bd:  # Si hay IDs en común
                    bonus_numeros = 0.05
            
            # Similitud total (máximo 1.0)
            similitud_total = min(similitud_ia + bonus_conceptos + bonus_numeros, 1.0)
            
            ranking.append({
                'id': caso_id,
                'categoria': cat,
                'problema': prob_bd,
                'sql': sql,
                'respuesta': resp,
                'similitud': float(similitud_total),  # Convertir a float nativo
                'similitud_ia': float(similitud_ia),
                'bonus_conceptos': float(bonus_conceptos),
                'complejidad': complejidad
            })
        
        # Ordenar por similitud
        ranking.sort(key=lambda x: x['similitud'], reverse=True)
        
        return ranking
    
    def extraer_valores(self, texto):
        """Extrae valores del texto"""
        valores = {}
        
        # Créditos
        creditos = re.findall(r'\d{13,}', texto)
        if creditos:
            valores['credito'] = creditos[0]
        
        # IDs
        ids = re.findall(r'(?:ID|id)[:\s]*(\d{5,})', texto, re.IGNORECASE)
        if ids:
            valores['id'] = ids[0]
        
        # Cédulas/NITs
        cedulas = re.findall(r'(?:CC|NIT|cedula|nit)[:\s]*(\d+)', texto, re.IGNORECASE)
        if cedulas:
            valores['cedula'] = cedulas[0]
        
        # Nombres
        nombres = re.findall(r'(?:Nombre|nombre)[:\s]+([A-Z][a-záéíóúñ]+(?:\s+[A-Z][a-záéíóúñ]+)*)', texto)
        if nombres:
            valores['nombre_completo'] = nombres[0]
        
        # Valores monetarios
        montos = re.findall(r'\$\s*([\d,.]+)', texto)
        if montos:
            valores['montos'] = [m.replace(',', '').replace('.', '') for m in montos]
        
        # Estados
        estados = re.findall(r'estado[:\s]+([A-Z][a-záéíóúñ\s]+)', texto, re.IGNORECASE)
        if estados:
            valores['estado'] = estados[0].strip()
        
        return valores
    
    def reemplazar_valores(self, sql, valores):
        """Reemplaza valores en el SQL"""
        sql_final = sql
        
        # Reemplazar créditos
        if 'credito' in valores:
            sql_final = re.sub(r"creditnumber\s*=\s*'\d{13,}'", f"creditnumber = '{valores['credito']}'", sql_final, flags=re.IGNORECASE)
        
        # Reemplazar cédulas
        if 'cedula' in valores:
            sql_final = re.sub(r"identification\s*=\s*'\d+'", f"identification = '{valores['cedula']}'", sql_final, flags=re.IGNORECASE)
        
        # Reemplazar IDs generales
        if 'id' in valores:
            sql_final = re.sub(r"userid\s*=\s*\d+", f"userid = {valores['id']}", sql_final, flags=re.IGNORECASE)
        
        return sql_final
    
    def guardar_caso_nuevo(self, categoria, problema, sql, respuesta):
        """Guarda un caso nuevo"""
        conceptos = self.extraer_conceptos_clave(problema)
        conceptos_str = ','.join(conceptos)
        complejidad = self.detectar_complejidad(problema)
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO casos (categoria, problema, sql, respuesta, conceptos_clave, complejidad)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (categoria or "General", problema, sql, respuesta, conceptos_str, complejidad))
        self.conn.commit()
        
        caso_id = c.lastrowid
        
        # Generar embedding
        self.calcular_embedding_caso(caso_id, problema)
        
        return caso_id
    
    def obtener_todos_casos(self):
        """Obtiene todos los casos de la base de datos"""
        c = self.conn.cursor()
        c.execute('SELECT * FROM casos')
        return c.fetchall()
    
    def agregar_caso(self, categoria, problema, sql, respuesta):
        """
        Agrega un nuevo caso a la base de datos
        
        Args:
            categoria: Categoría del caso
            problema: Descripción del problema
            sql: Query SQL de solución
            respuesta: Respuesta para el usuario
        
        Returns:
            ID del caso creado
        """
        return self.guardar_caso_nuevo(categoria, problema, sql, respuesta)

# Para compatibilidad con el código anterior
SistemaPQRSUltra = SistemaPQRSIA
