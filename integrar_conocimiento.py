#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para integrar el conocimiento expandido al sistema
"""

import json
import os

def integrar_conocimiento_expandido():
    """Integra el conocimiento expandido al archivo principal"""
    
    # Cargar conocimiento actual
    archivo_actual = 'conocimiento_base.json'
    archivo_expandido = 'conocimiento_expandido.json'
    
    if os.path.exists(archivo_actual):
        with open(archivo_actual, 'r', encoding='utf-8') as f:
            conocimiento_actual = json.load(f)
        print(f"✅ Conocimiento actual cargado: {len(conocimiento_actual)} secciones")
    else:
        conocimiento_actual = {}
        print("⚠️ No existe conocimiento_base.json, se creará uno nuevo")
    
    # Cargar conocimiento expandido
    if os.path.exists(archivo_expandido):
        with open(archivo_expandido, 'r', encoding='utf-8') as f:
            conocimiento_expandido = json.load(f)
        print(f"✅ Conocimiento expandido cargado: {len(conocimiento_expandido)} secciones")
    else:
        print("❌ Error: No se encontró conocimiento_expandido.json")
        return False
    
    # Integrar (merge)
    for seccion, contenido in conocimiento_expandido.items():
        if seccion in conocimiento_actual:
            # Si ya existe, combinar
            if isinstance(contenido, dict):
                conocimiento_actual[seccion].update(contenido)
                print(f"🔄 Sección '{seccion}' actualizada")
            else:
                conocimiento_actual[seccion] = contenido
                print(f"🔄 Sección '{seccion}' reemplazada")
        else:
            # Si no existe, agregar
            conocimiento_actual[seccion] = contenido
            print(f"➕ Sección '{seccion}' agregada")
    
    # Guardar
    with open(archivo_actual, 'w', encoding='utf-8') as f:
        json.dump(conocimiento_actual, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Conocimiento integrado exitosamente")
    print(f"📊 Total de secciones: {len(conocimiento_actual)}")
    
    # Resumen
    print("\n📋 RESUMEN DEL CONOCIMIENTO:")
    for seccion, contenido in conocimiento_actual.items():
        if isinstance(contenido, dict):
            print(f"  • {seccion}: {len(contenido)} items")
        else:
            print(f"  • {seccion}: {type(contenido).__name__}")
    
    return True

if __name__ == "__main__":
    print("🚀 Integrando conocimiento expandido...\n")
    exito = integrar_conocimiento_expandido()
    
    if exito:
        print("\n✅ ¡Listo! El sistema ahora tiene conocimiento expandido.")
        print("\n📝 Próximos pasos:")
        print("  1. Reinicia Streamlit: streamlit run app_streamlit_pqrs.py")
        print("  2. Prueba preguntas como:")
        print("     - '¿Cómo busco un vendedor?'")
        print("     - '¿Qué es el estado 77?'")
        print("     - '¿Cuál es el flujo de liquidación?'")
        print("     - 'Error: vendedor no existe'")
    else:
        print("\n❌ Error al integrar conocimiento")
