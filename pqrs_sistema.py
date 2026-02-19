#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
═══════════════════════════════════════════════════════════════════
  SISTEMA INTELIGENTE DE PQRS - VERSIÓN DEFINITIVA
  
  Sistema que aprende de casos anteriores y genera SQL automáticamente
═══════════════════════════════════════════════════════════════════
"""

import sqlite3
import re
from difflib import SequenceMatcher
import os

class SistemaPQRS:
    
    def __init__(self):
        self.db = 'pqrs_sistema.db'
        self.conn = None
        self.inicializar()
    
    def inicializar(self):
        """Inicializa base de datos"""
        self.conn = sqlite3.connect(self.db)
        c = self.conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS casos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categoria TEXT,
                problema TEXT,
                sql TEXT,
                respuesta TEXT,
                usos INTEGER DEFAULT 0,
                efectividad INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        
        # Cargar casos desde archivo si la BD está vacía
        c.execute('SELECT COUNT(*) FROM casos')
        if c.fetchone()[0] == 0:
            self.cargar_desde_archivo()
    
    def cargar_desde_archivo(self):
        """Carga PQRS desde archivo de texto"""
        archivo = 'PQRS_NUEVAS_CON_SQL.txt'
        
        if not os.path.exists(archivo):
            print(f"⚠️  Archivo {archivo} no encontrado")
            print("💡 Coloca el archivo en la misma carpeta")
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
                    c = self.conn.cursor()
                    c.execute('''
                        INSERT INTO casos (categoria, problema, sql, respuesta)
                        VALUES (?, ?, ?, ?)
                    ''', (categoria, problema, sql, respuesta))
                    casos_cargados += 1
            
            except Exception as e:
                continue
        
        self.conn.commit()
        print(f"✅ {casos_cargados} casos cargados correctamente")
    
    def buscar_similar(self, problema):
        """Busca el caso más similar al problema dado"""
        c = self.conn.cursor()
        c.execute('SELECT id, categoria, problema, sql, respuesta FROM casos')
        casos = c.fetchall()
        
        if not casos:
            return None
        
        prob_lower = problema.lower()
        palabras_problema = set(re.findall(r'\w+', prob_lower))
        
        # Crear ranking de similitud
        ranking = []
        
        for caso in casos:
            caso_id, cat, prob_bd, sql, resp = caso
            prob_bd_lower = prob_bd.lower()
            palabras_bd = set(re.findall(r'\w+', prob_bd_lower))
            
            # 1. Similitud de texto directa (70% del peso)
            similitud_texto = SequenceMatcher(None, prob_lower, prob_bd_lower).ratio() * 0.7
            
            # 2. Palabras clave en común (20% del peso)
            if palabras_problema and palabras_bd:
                comunes = len(palabras_problema & palabras_bd)
                total = len(palabras_problema | palabras_bd)
                similitud_palabras = (comunes / total) * 0.2 if total > 0 else 0
            else:
                similitud_palabras = 0
            
            # 3. Categoría similar (10% del peso)
            similitud_categoria = 0
            palabras_cat = set(cat.lower().split())
            if any(p in prob_lower for p in palabras_cat):
                similitud_categoria = 0.1
            
            # Similitud total
            similitud_total = similitud_texto + similitud_palabras + similitud_categoria
            
            ranking.append({
                'id': caso_id,
                'categoria': cat,
                'problema': prob_bd,
                'sql': sql,
                'respuesta': resp,
                'similitud': similitud_total
            })
        
        # Ordenar por similitud y retornar el mejor
        ranking.sort(key=lambda x: x['similitud'], reverse=True)
        return ranking[0] if ranking else None
    
    def extraer_valores(self, texto):
        """Extrae valores importantes del texto"""
        valores = {}
        
        # Créditos (13+ dígitos)
        creditos = re.findall(r'\d{13,}', texto)
        if creditos:
            valores['credito'] = creditos[0]
        
        # IDs - Mejorado para detectar más formatos
        ids = re.findall(r'(?:ID|id)\s*(?:de\s*)?(?:comisi[óo]n)?[:\s]*(\d+)', texto, re.IGNORECASE)
        if not ids:
            # Buscar "comisión 123456" o "comisionID 123456"
            ids = re.findall(r'comisi[óo]n[:\s]+(\d{5,})', texto, re.IGNORECASE)
        if ids:
            valores['id'] = ids[0]
        
        # Cédulas/NITs - Mejorado
        cedulas = re.findall(r'(?:C\.?C\.?|c\.?c\.?|NIT|nit|C[ÉE]DULA|cedula)[:\s]*(\d+)', texto, re.IGNORECASE)
        if cedulas:
            valores['cedula'] = cedulas[0]
        
        # Documentos (para casos de cambio de documento)
        documentos = re.findall(r'documento[:\s]+(\d+)', texto, re.IGNORECASE)
        if documentos:
            valores['documento_origen'] = documentos[0]
            if len(documentos) > 1:
                valores['documento_destino'] = documentos[1]
        
        # Valores monetarios
        montos = re.findall(r'\$\s*([\d,.]+)', texto)
        if montos:
            # Limpiar y convertir
            valores['montos'] = [m.replace(',', '').replace('.', '') for m in montos]
        
        # Fechas
        fechas = re.findall(r'\d{1,2}[-/]\w{3}[-/]\d{2,4}', texto)
        if not fechas:
            fechas = re.findall(r'\d{2}/\d{2}/\d{4}', texto)
        if fechas:
            valores['fecha'] = fechas[0]
        
        # Números de factura
        facturas = re.findall(r'(?:FACTURA|FAC|factura)[:\s]*(\w+)', texto, re.IGNORECASE)
        if facturas:
            valores['factura'] = facturas[0]
        
        return valores
    
    def reemplazar_valores(self, sql, valores):
        """Reemplaza placeholders en SQL con valores reales"""
        sql_final = sql
        
        # Reemplazar créditos
        if 'credito' in valores:
            sql_final = re.sub(r"'?\[?CREDITO\]?'?", f"'{valores['credito']}'", sql_final, flags=re.IGNORECASE)
            sql_final = re.sub(r"creditnumber\s*=\s*'\d{13,}'", f"creditnumber = '{valores['credito']}'", sql_final, flags=re.IGNORECASE)
        
        # Reemplazar IDs - MEJORADO
        if 'id' in valores:
            # Reemplazar placeholders
            sql_final = re.sub(r'\[?ID\]?', valores['id'], sql_final, flags=re.IGNORECASE)
            # Reemplazar IDs existentes en el SQL
            sql_final = re.sub(r'CommissionID\s*=\s*\d+', f"CommissionID = {valores['id']}", sql_final, flags=re.IGNORECASE)
            sql_final = re.sub(r'ID\s*=\s*\d+', f"ID = {valores['id']}", sql_final, flags=re.IGNORECASE)
        
        # Reemplazar cédulas/NITs
        if 'cedula' in valores:
            sql_final = re.sub(r"'?\[?(?:CEDULA|NIT)\]?'?", f"'{valores['cedula']}'", sql_final, flags=re.IGNORECASE)
            sql_final = re.sub(r"identification\s*=\s*'\d+'", f"identification = '{valores['cedula']}'", sql_final, flags=re.IGNORECASE)
        
        # Reemplazar facturas
        if 'factura' in valores:
            sql_final = re.sub(r"'?\[?NUM_FACTURA\]?'?", f"'{valores['factura']}'", sql_final, flags=re.IGNORECASE)
            sql_final = re.sub(r"numerofactura\s*=\s*'[^']+'", f"numerofactura = '{valores['factura']}'", sql_final, flags=re.IGNORECASE)
        
        # Reemplazar montos - MEJORADO
        if 'montos' in valores and valores['montos']:
            # Si hay valores en el SQL tipo "SET field = numero"
            # Intentar reemplazarlos por los montos detectados
            matches = re.findall(r'=\s*(\d+)', sql_final)
            if matches and len(valores['montos']) >= len(matches):
                for i, match in enumerate(matches):
                    if i < len(valores['montos']):
                        sql_final = sql_final.replace(f"= {match}", f"= {valores['montos'][i]}", 1)
        
        return sql_final
    
    def resolver_pqrs(self):
        """Resolver una PQRS nueva"""
        print("\n" + "═"*70)
        print("  📝 RESOLVER PQRS NUEVA")
        print("═"*70)
        
        print("\n💬 Ingrese el problema (escriba END y presione Enter para terminar):\n")
        
        lineas = []
        while True:
            try:
                linea = input()
                if linea.strip().upper() == 'END':
                    break
                lineas.append(linea)
            except (EOFError, KeyboardInterrupt):
                break
        
        problema = '\n'.join(lineas).strip()
        
        if not problema:
            print("❌ No se ingresó ningún problema")
            return
        
        print("\n🔍 Buscando solución similar...")
        
        caso = self.buscar_similar(problema)
        
        if not caso:
            print("❌ No se encontró ningún caso en la base de datos")
            print("💡 Use la opción 2 para enseñar este caso")
            return
        
        # UMBRAL DE SIMILITUD MÍNIMO
        UMBRAL_MINIMO = 0.60  # 60% de similitud mínima
        
        if caso['similitud'] < UMBRAL_MINIMO:
            print("\n" + "⚠️ " + "─"*66 + " ⚠️")
            print(f"  ❌ NO CONOZCO ESTE TIPO DE PROBLEMA")
            print(f"  📊 Similitud más cercana: {caso['similitud']*100:.0f}% (mínimo: {UMBRAL_MINIMO*100:.0f}%)")
            print(f"  📁 Caso más parecido: {caso['categoria']}")
            print("  " + "─"*66)
            print("\n💡 Este problema es nuevo para mí.")
            print("   Necesito que me enseñes cómo resolverlo.\n")
            
            ensenar = input("¿Deseas enseñarme la solución ahora? (s/n): ").strip().lower()
            
            if ensenar == 's':
                self.ensenar_caso_corregido(problema)
            else:
                print("\n💭 Tip: Usa la opción 2 del menú cuando tengas la solución")
            
            return
        
        # Si la similitud es suficiente, continuar normal
        # Extraer valores del problema
        valores = self.extraer_valores(problema)
        
        # Reemplazar en SQL
        sql_final = self.reemplazar_valores(caso['sql'], valores)
        
        # Mostrar resultado
        print(f"\n📊 Caso similar encontrado: {caso['categoria']}")
        print(f"🎯 Similitud: {caso['similitud']*100:.0f}%")
        
        if valores:
            print(f"\n🔍 Valores detectados:")
            for clave, valor in valores.items():
                if isinstance(valor, list):
                    print(f"   • {clave}: {', '.join(valor)}")
                else:
                    print(f"   • {clave}: {valor}")
        
        print("\n╔" + "═"*68 + "╗")
        print("║" + "  💻 SQL PARA COPIAR Y PEGAR  ".center(68) + "║")
        print("╠" + "═"*68 + "╣")
        
        lineas_sql = sql_final.split('\n')
        for linea in lineas_sql:
            if len(linea) > 66:
                print("║ " + linea[:66] + " ║")
            else:
                print("║ " + linea.ljust(66) + " ║")
        
        print("╚" + "═"*68 + "╝")
        
        print(f"\n📝 Respuesta para el usuario:")
        print(f"   {caso['respuesta']}")
        
        # Feedback
        print("\n" + "─"*70)
        feedback = input("¿Esta solución funcionó correctamente? (s/n): ").strip().lower()
        
        c = self.conn.cursor()
        
        if feedback == 's':
            c.execute('UPDATE casos SET usos = usos + 1, efectividad = efectividad + 1 WHERE id = ?', (caso['id'],))
            self.conn.commit()
            print("✅ ¡Excelente! El sistema aprendió de este caso")
        elif feedback == 'n':
            c.execute('UPDATE casos SET usos = usos + 1, efectividad = efectividad - 1 WHERE id = ?', (caso['id'],))
            self.conn.commit()
            print("❌ Entendido. ¿Desea enseñar la solución correcta?")
            corregir = input("   (s/n): ").strip().lower()
            if corregir == 's':
                self.ensenar_caso_corregido(problema)
    
    def ensenar_caso_corregido(self, problema):
        """Enseña la solución correcta para un caso que falló"""
        print("\n" + "─"*70)
        print("  📚 ENSEÑAR SOLUCIÓN CORRECTA")
        print("─"*70)
        
        categoria = input("\n📁 Categoría (ej: Comisiones, Pagos): ").strip()
        
        print("\n💻 SQL correcto (escriba END y presione Enter para terminar):\n")
        lineas = []
        while True:
            linea = input()
            if linea.strip().upper() == 'END':
                break
            lineas.append(linea)
        sql = '\n'.join(lineas).strip()
        
        respuesta = input("\n📝 Respuesta para el usuario: ").strip()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO casos (categoria, problema, sql, respuesta)
            VALUES (?, ?, ?, ?)
        ''', (categoria or "General", problema, sql, respuesta))
        self.conn.commit()
        
        print("✅ Caso guardado correctamente")
    
    def ensenar_caso_nuevo(self):
        """Enseñar un caso completamente nuevo"""
        print("\n" + "═"*70)
        print("  📚 ENSEÑAR CASO NUEVO")
        print("═"*70)
        
        categoria = input("\n📁 Categoría: ").strip()
        
        print("\n💬 Problema (escriba END para terminar):\n")
        lineas = []
        while True:
            linea = input()
            if linea.strip().upper() == 'END':
                break
            lineas.append(linea)
        problema = '\n'.join(lineas).strip()
        
        print("\n💻 SQL (escriba END para terminar):\n")
        lineas = []
        while True:
            linea = input()
            if linea.strip().upper() == 'END':
                break
            lineas.append(linea)
        sql = '\n'.join(lineas).strip()
        
        respuesta = input("\n📝 Respuesta para usuario: ").strip()
        
        c = self.conn.cursor()
        c.execute('''
            INSERT INTO casos (categoria, problema, sql, respuesta)
            VALUES (?, ?, ?, ?)
        ''', (categoria or "General", problema, sql, respuesta))
        self.conn.commit()
        
        print("✅ Caso guardado correctamente")
    
    def ver_casos(self):
        """Ver todos los casos en la base de datos"""
        c = self.conn.cursor()
        c.execute('SELECT id, categoria, problema, usos, efectividad FROM casos ORDER BY id')
        casos = c.fetchall()
        
        if not casos:
            print("\n📚 No hay casos en la base de datos")
            return
        
        print("\n" + "═"*70)
        print(f"  📚 CASOS EN LA BASE DE DATOS ({len(casos)} total)")
        print("═"*70)
        
        for caso_id, cat, prob, usos, efect in casos:
            print(f"\n[{caso_id:3d}] {cat}")
            # Mostrar primeras líneas del problema
            lineas_prob = prob.split('\n')
            if len(lineas_prob[0]) > 60:
                print(f"      {lineas_prob[0][:60]}...")
            else:
                print(f"      {lineas_prob[0]}")
            print(f"      📊 Usado: {usos} veces | Efectividad: {efect:+d}")
    
    def borrar_caso(self):
        """Borrar un caso mal aprendido"""
        self.ver_casos()
        
        try:
            caso_id = int(input("\n🗑️  ID del caso a borrar: ").strip())
            
            confirmar = input(f"⚠️  ¿Confirma que desea borrar el caso {caso_id}? (s/n): ").strip().lower()
            
            if confirmar == 's':
                c = self.conn.cursor()
                c.execute('DELETE FROM casos WHERE id = ?', (caso_id,))
                self.conn.commit()
                print("✅ Caso borrado exitosamente")
            else:
                print("❌ Operación cancelada")
        except ValueError:
            print("❌ ID inválido")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def estadisticas(self):
        """Mostrar estadísticas del sistema"""
        c = self.conn.cursor()
        
        print("\n" + "═"*70)
        print("  📊 ESTADÍSTICAS DEL SISTEMA")
        print("═"*70)
        
        # Total de casos
        c.execute('SELECT COUNT(*) FROM casos')
        total = c.fetchone()[0]
        print(f"\n📚 Total de casos: {total}")
        
        # Por categoría
        c.execute('''
            SELECT categoria, COUNT(*) 
            FROM casos 
            GROUP BY categoria 
            ORDER BY COUNT(*) DESC
        ''')
        print("\n📁 Por categoría:")
        for cat, count in c.fetchall():
            print(f"   • {cat}: {count} caso(s)")
        
        # Más usados
        c.execute('''
            SELECT problema, usos, efectividad 
            FROM casos 
            WHERE usos > 0 
            ORDER BY usos DESC 
            LIMIT 5
        ''')
        print("\n🔥 Casos más utilizados:")
        for prob, usos, efect in c.fetchall():
            print(f"   • {prob[:50]}... ({usos} usos, efectividad: {efect:+d})")
        
        # Precisión general
        c.execute('''
            SELECT 
                SUM(CASE WHEN efectividad > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
            FROM casos 
            WHERE usos > 0
        ''')
        resultado = c.fetchone()[0]
        if resultado:
            print(f"\n📈 Precisión general: {resultado:.1f}%")
    
    def recargar_casos(self):
        """Recarga casos desde el archivo (útil si se agregaron nuevos)"""
        print("\n⚠️  Esto borrará todos los casos actuales y recargará desde el archivo")
        confirmar = input("¿Continuar? (s/n): ").strip().lower()
        
        if confirmar != 's':
            print("❌ Operación cancelada")
            return
        
        c = self.conn.cursor()
        c.execute('DELETE FROM casos')
        self.conn.commit()
        
        self.cargar_desde_archivo()
    
    def menu(self):
        """Menú principal"""
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║              🤖 SISTEMA INTELIGENTE DE PQRS                      ║
║                                                                   ║
║          Sistema que aprende y genera SQL automáticamente        ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
        """)
        
        while True:
            print("\n" + "═"*70)
            print("  MENÚ PRINCIPAL")
            print("═"*70)
            print("\n  1. 📝 Resolver PQRS nueva")
            print("  2. 📚 Enseñar caso nuevo")
            print("  3. 👀 Ver todos los casos")
            print("  4. 🗑️  Borrar caso mal aprendido")
            print("  5. 📊 Ver estadísticas")
            print("  6. 🔄 Recargar casos desde archivo")
            print("  7. 🚪 Salir")
            print("\n" + "═"*70)
            
            opcion = input("\n👉 Seleccione una opción: ").strip()
            
            try:
                if opcion == '1':
                    self.resolver_pqrs()
                elif opcion == '2':
                    self.ensenar_caso_nuevo()
                elif opcion == '3':
                    self.ver_casos()
                elif opcion == '4':
                    self.borrar_caso()
                elif opcion == '5':
                    self.estadisticas()
                elif opcion == '6':
                    self.recargar_casos()
                elif opcion == '7':
                    print("\n👋 ¡Hasta pronto!")
                    self.conn.close()
                    break
                else:
                    print("❌ Opción inválida. Intente de nuevo.")
            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    sistema = SistemaPQRS()
    sistema.menu()
