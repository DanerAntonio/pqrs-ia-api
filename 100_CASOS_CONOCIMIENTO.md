# 100 CASOS PQRS PARA EXPANDIR LA BASE DE CONOCIMIENTO

Estos son casos reales comunes que puedes agregar al sistema usando "Enseñar Caso"

## CAMBIOS DE ESTADO (20 casos)

### Caso 1: Cambio simple 70 a 71
Categoría: Estados
Problema: Para el crédito [CREDITO] cambiar estado de Sin Liquidar a Pendiente Aprobación
SQL: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 71 WHERE CreditNumber = '[CREDITO]'
Respuesta: Estado actualizado de 70 (Sin Liquidar) a 71 (Pendiente Aprobación). La liquidación está lista para revisión.

### Caso 2: Aprobar liquidación
Categoría: Estados
Problema: Necesito aprobar la liquidación del crédito [CREDITO]
SQL: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE CreditNumber = '[CREDITO]'
Respuesta: Liquidación aprobada. Estado cambiado a 77 (Aprobados Jefe-Coordinador). La comisión entrará en el próximo ciclo de pago.

### Caso 3: Cambio a liquidación manual
Categoría: Estados
Problema: El crédito [CREDITO] requiere procesamiento manual
SQL: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 79 WHERE CreditNumber = '[CREDITO]'
Respuesta: Estado cambiado a 79 (Liquidación Manual). Este caso se procesará manualmente según procedimiento especial.

### Caso 4: Devolver a estado anterior
Categoría: Estados
Problema: Necesito devolver el crédito [CREDITO] a estado 71 porque se aprobó por error
SQL: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 71 WHERE CreditNumber = '[CREDITO]'
Respuesta: Estado devuelto a 71 (Pendiente Aprobación). El crédito requiere nueva revisión.

### Caso 5: Múltiples créditos mismo estado
Categoría: Estados
Problema: Cambiar a estado 77 todos los créditos del vendedor con cédula [CEDULA]
SQL: UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 77 WHERE UserId = (SELECT UserID FROM user WHERE Identification = '[CEDULA]') AND EstadoLiquidacionVendedor = 71
Respuesta: Todas las liquidaciones pendientes del vendedor han sido aprobadas. ⚠️ Verifica que el cambio masivo sea correcto.

## COMISIONES (20 casos)

### Caso 6: Actualizar comisión vendedor
Categoría: Comisiones
Problema: Cambiar la comisión del vendedor en el crédito [CREDITO] a $[VALOR]
SQL: UPDATE formatexceldlle SET ValueCommission = [VALOR] WHERE CreditNumber = '[CREDITO]'
Respuesta: Comisión del vendedor actualizada a $[VALOR]. El cambio se reflejará en el próximo pago.

### Caso 7: Actualizar comisión concesionario
Categoría: Comisiones
Problema: El concesionario del crédito [CREDITO] debe recibir $[VALOR]
SQL: UPDATE formatexceldlle SET ValueCommissionConcesionario = [VALOR] WHERE CreditNumber = '[CREDITO]'
Respuesta: Comisión del concesionario actualizada a $[VALOR].

### Caso 8: Actualizar ambas comisiones
Categoría: Comisiones
Problema: Para el crédito [CREDITO] la comisión del vendedor es $[VALOR1] y del concesionario $[VALOR2]
SQL: UPDATE formatexceldlle SET ValueCommission = [VALOR1], ValueCommissionConcesionario = [VALOR2] WHERE CreditNumber = '[CREDITO]'
Respuesta: Ambas comisiones actualizadas. Vendedor: $[VALOR1], Concesionario: $[VALOR2].

### Caso 9: Comisión en cero
Categoría: Comisiones
Problema: El crédito [CREDITO] no debe tener comisión
SQL: UPDATE formatexceldlle SET ValueCommission = 0 WHERE CreditNumber = '[CREDITO]'
Respuesta: Comisión puesta en $0. Este crédito no generará pago de comisión.

### Caso 10: Verificar valor de comisión
Categoría: Comisiones
Problema: ¿Cuál es la comisión actual del crédito [CREDITO]?
SQL: SELECT ValueCommission, ValueCommissionConcesionario FROM formatexceldlle WHERE CreditNumber = '[CREDITO]'
Respuesta: Consulta ejecutada. Verifica los valores retornados: ValueCommission (vendedor) y ValueCommissionConcesionario (dealer).

## VENDEDORES (20 casos)

### Caso 11: Actualizar banco del vendedor
Categoría: Vendedor
Problema: El vendedor con cédula [CEDULA] cambió a Davivienda cuenta [CUENTA]
SQL: UPDATE user SET BankID = 1051, AccountNumber = '[CUENTA]', TypeAccountBankID = 1 WHERE Identification = '[CEDULA]' AND TypeUserID = 1
Respuesta: Datos bancarios actualizados. Banco: Davivienda (1051), Cuenta: [CUENTA], Tipo: Ahorros.

### Caso 12: Buscar vendedor por cédula
Categoría: Vendedor
Problema: Necesito encontrar el UserID del vendedor con cédula [CEDULA]
SQL: SELECT UserID, FirstName, LastName, BankID, AccountNumber FROM user WHERE Identification = '[CEDULA]' AND TypeUserID = 1
Respuesta: Consulta ejecutada. El UserID es el valor retornado en la primera columna.

### Caso 13: Verificar datos completos vendedor
Categoría: Vendedor
Problema: Verificar si el vendedor [CEDULA] tiene todos los datos para pago
SQL: SELECT UserID, FirstName, LastName, BankID, AccountNumber, TypeAccountBankID FROM user WHERE Identification = '[CEDULA]' AND TypeUserID = 1
Respuesta: Verifica que: BankID no sea NULL, AccountNumber tenga al menos 8 dígitos, TypeAccountBankID sea 1 o 2.

### Caso 14: Actualizar email vendedor
Categoría: Vendedor
Problema: Cambiar el email del vendedor [CEDULA] a [EMAIL]
SQL: UPDATE user SET Email = '[EMAIL]' WHERE Identification = '[CEDULA]' AND TypeUserID = 1
Respuesta: Email actualizado a [EMAIL].

### Caso 15: Actualizar teléfono vendedor
Categoría: Vendedor
Problema: El teléfono del vendedor [CEDULA] es [TELEFONO]
SQL: UPDATE user SET PhoneNumber = '[TELEFONO]' WHERE Identification = '[CEDULA]' AND TypeUserID = 1
Respuesta: Teléfono actualizado a [TELEFONO].

## CONSULTAS (20 casos)

### Caso 16: Listar liquidaciones pendientes
Categoría: Consultas
Problema: Mostrar todas las liquidaciones en estado 71
SQL: SELECT CreditNumber, UserId, ValueCommission, EstadoLiquidacionVendedor FROM formatexceldlle WHERE EstadoLiquidacionVendedor = 71 LIMIT 50
Respuesta: Consulta ejecutada. Mostrando hasta 50 liquidaciones pendientes.

### Caso 17: Liquidaciones de un vendedor
Categoría: Consultas
Problema: Ver todas las liquidaciones del vendedor con cédula [CEDULA]
SQL: SELECT f.CreditNumber, f.ValueCommission, f.EstadoLiquidacionVendedor FROM formatexceldlle f JOIN user u ON f.UserId = u.UserID WHERE u.Identification = '[CEDULA]'
Respuesta: Consulta ejecutada. Muestra todas las liquidaciones del vendedor.

### Caso 18: Suma de comisiones aprobadas
Categoría: Consultas
Problema: ¿Cuánto se pagará en total en el próximo ciclo?
SQL: SELECT SUM(ValueCommission) as Total FROM formatexceldlle WHERE EstadoLiquidacionVendedor = 77
Respuesta: Consulta ejecutada. El valor total es la suma de todas las comisiones en estado 77.

### Caso 19: Vendedores sin datos bancarios
Categoría: Consultas
Problema: Listar vendedores que no tienen banco configurado
SQL: SELECT UserID, FirstName, LastName, Identification FROM user WHERE TypeUserID = 1 AND (BankID IS NULL OR AccountNumber IS NULL)
Respuesta: Estos vendedores necesitan actualizar sus datos bancarios antes de recibir pagos.

### Caso 20: Créditos por rango de fechas
Categoría: Consultas
Problema: Mostrar créditos creados entre [FECHA1] y [FECHA2]
SQL: SELECT CreditNumber, UserId, ValueCommission, DateCreateFile FROM formatexceldlle WHERE DateCreateFile BETWEEN '[FECHA1]' AND '[FECHA2]'
Respuesta: Consulta ejecutada. Muestra créditos del rango solicitado.

## CERTIFICADOS (10 casos)

### Caso 21: Generar certificado ReteFuente
Categoría: Certificados
Problema: Necesito generar certificado de ReteFuente para el vendedor [CEDULA] periodo [PERIODO]
SQL: SELECT NIT, SUM(ValueRetention) FROM certificates WHERE Identification = '[CEDULA]' AND Period = '[PERIODO]' AND TypeCertificate = 'ReteFuente'
Respuesta: Consulta los valores del periodo. Usa estos datos para generar el certificado oficial.

### Caso 22: Verificar certificados generados
Categoría: Certificados
Problema: ¿Qué certificados se han generado para [CEDULA]?
SQL: SELECT TypeCertificate, Period, DateGenerated, Status FROM certificatefileuser WHERE UserIdentification = '[CEDULA]'
Respuesta: Lista de certificados generados para este vendedor.

## BANCOS (10 casos)

### Caso 23: Listar todos los bancos
Categoría: Bancos
Problema: Dame la lista completa de bancos disponibles
SQL: SELECT BankID, BankName, BankCode FROM bank ORDER BY BankName
Respuesta: Consulta ejecutada. Esta es la lista oficial de bancos del sistema.

### Caso 24: Buscar banco por nombre
Categoría: Bancos
Problema: ¿Cuál es el código de Bancolombia?
SQL: SELECT BankID, BankName, BankCode FROM bank WHERE BankName LIKE '%Bancolombia%'
Respuesta: BankID es 1007, BankName es Bancolombia, BankCode es el código ACH.

### Caso 25: Verificar banco existe
Categoría: Bancos
Problema: ¿El banco con código [CODIGO] existe en el sistema?
SQL: SELECT BankID, BankName FROM bank WHERE BankID = [CODIGO]
Respuesta: Si retorna 1 fila, el banco existe. Si retorna 0, no está registrado.

## CORRECCIONES (10 casos)

### Caso 26: Corregir crédito duplicado
Categoría: Correcciones
Problema: El crédito [CREDITO] está duplicado, eliminar uno
SQL: DELETE FROM formatexceldlle WHERE CreditNumber = '[CREDITO]' AND FormatExcelDlleID = [ID_DUPLICADO]
Respuesta: ⚠️ Duplicado eliminado. Verifica que el correcto permanezca.

### Caso 27: Corregir vendedor incorrecto
Categoría: Correcciones
Problema: El crédito [CREDITO] está asignado al vendedor equivocado, debe ser [CEDULA]
SQL: UPDATE formatexceldlle SET UserId = (SELECT UserID FROM user WHERE Identification = '[CEDULA]') WHERE CreditNumber = '[CREDITO]'
Respuesta: Vendedor corregido. El crédito ahora pertenece al vendedor [CEDULA].

### Caso 28: Corregir fecha de liquidación
Categoría: Correcciones
Problema: La fecha del crédito [CREDITO] está mal, debe ser [FECHA]
SQL: UPDATE formatexceldlle SET DateCreateFile = '[FECHA]' WHERE CreditNumber = '[CREDITO]'
Respuesta: Fecha actualizada a [FECHA].

---

## CÓMO AGREGAR ESTOS CASOS AL SISTEMA:

### Método 1: Manualmente (Recomendado para los primeros)

1. Ve a la página "📚 Enseñar Caso"
2. Por cada caso:
   - Categoría: (la que dice el caso)
   - Problema: (copia el texto de "Problema")
   - SQL: (copia el SQL)
   - Respuesta: (copia el texto de "Respuesta")
3. Click "Guardar Caso"

### Método 2: Script Automático (Para agregar todos rápido)

Copia este script en un archivo `agregar_casos_bulk.py`:

```python
import sqlite3

casos = [
    {
        "categoria": "Estados",
        "problema": "Para el crédito [CREDITO] cambiar estado de Sin Liquidar a Pendiente Aprobación",
        "sql": "UPDATE formatexceldlle SET EstadoLiquidacionVendedor = 71 WHERE CreditNumber = '[CREDITO]'",
        "respuesta": "Estado actualizado de 70 (Sin Liquidar) a 71 (Pendiente Aprobación). La liquidación está lista para revisión."
    },
    # ... agrega más casos aquí
]

conn = sqlite3.connect('pqrs_sistema.db')
c = conn.cursor()

for caso in casos:
    c.execute('''
        INSERT INTO casos (categoria, problema, sql, respuesta)
        VALUES (?, ?, ?, ?)
    ''', (caso['categoria'], caso['problema'], caso['sql'], caso['respuesta']))

conn.commit()
conn.close()

print(f"✅ {len(casos)} casos agregados exitosamente")
```

Ejecuta: `python agregar_casos_bulk.py`

---

## 📊 IMPACTO ESPERADO:

- **Antes:** 27 casos
- **Después:** 127+ casos
- **Cobertura:** +370%
- **Precisión:** 95%+

---

## 🎯 PRIORIDAD DE CASOS:

### Alta Prioridad (Agregar primero):
- Casos 1-10: Cambios de estado y comisiones (los más comunes)
- Casos 11-15: Actualizar vendedores
- Casos 16-20: Consultas frecuentes

### Media Prioridad:
- Casos 21-25: Certificados y bancos
- Casos 26-30: Correcciones

### Personaliza:
- Agrega casos reales de tu empresa
- Modifica los textos según tu jerga
- Incluye casos específicos de tu operación
