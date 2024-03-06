def es_bisiesto(año):
    return año % 4 == 0 and (año % 100 != 0 or año % 400 == 0)

def calcular_diferencia_tiempo(fecha_actual, fecha_anterior):
    # Definir la cantidad de días por mes
    dias_por_mes = [31, 28 + es_bisiesto(fecha_actual['year']), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Calcular la diferencia en segundos entre las dos fechas
    diferencia_años = fecha_actual['year'] - fecha_anterior['year']
    diferencia_meses = fecha_actual['month'] - fecha_anterior['month']
    diferencia_dias = fecha_actual['day'] - fecha_anterior['day']
    diferencia_horas = fecha_actual['hour'] - fecha_anterior['hour']
    diferencia_minutos = fecha_actual['minute'] - fecha_anterior['minute']
    diferencia_segundos = fecha_actual['second'] - fecha_anterior['second']
    
    # Calcular la diferencia total de días, teniendo en cuenta los años bisiestos y los días por mes
    total_dias = diferencia_dias
    for mes in range(fecha_anterior['month'], fecha_actual['month']):
        total_dias += dias_por_mes[mes - 1]  # Ajustar el índice del mes para la lista
    
    # Sumar los días de los años completos
    for año in range(fecha_anterior['year'], fecha_actual['year']):
        total_dias += 365 + es_bisiesto(año)
    
    # Convertir todo a segundos
    total_segundos = total_dias * 86400 + diferencia_horas * 3600 + diferencia_minutos * 60 + diferencia_segundos
    
    # Convertir la diferencia a un texto legible
    if total_segundos < 60:
        return "hace unos pocos segundos"
    elif total_segundos < 120:
        return "hace 1 minuto"
    elif total_segundos < 3600:
        return f"hace {total_segundos // 60} minutos"
    elif total_segundos < 7200:
        return "hace 1 hora"
    elif total_segundos < 86400:
        return f"hace {total_segundos // 3600} horas"
    elif total_segundos < 172800:
        return "hace 1 día"
    else:
        return f"hace {total_segundos // 86400} días"

# Ejemplo de uso
fecha_actual = {'day': 4, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
fecha_anterior = {'day': 3, 'hour': 22, 'minute': 29, 'month': 3, 'second': 28, 'year': 2024}
print(calcular_diferencia_tiempo(fecha_actual, fecha_anterior))

# Ejemplo 1: Hace unos pocos segundos
fecha_actual = {'day': 5, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
fecha_anterior = {'day': 5, 'hour': 9, 'minute': 3, 'month': 3, 'second': 10, 'year': 2024}
print(calcular_diferencia_tiempo(fecha_actual, fecha_anterior))  # Debería retornar "hace unos pocos segundos"

# Ejemplo 2: Hace 1 minuto
fecha_actual = {'day': 5, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
fecha_anterior = {'day': 5, 'hour': 9, 'minute': 2, 'month': 3, 'second': 17, 'year': 2024}
print(calcular_diferencia_tiempo(fecha_actual, fecha_anterior))  # Debería retornar "hace 1 minuto"

# Ejemplo 3: Hace 2 horas
fecha_actual = {'day': 5, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
fecha_anterior = {'day': 5, 'hour': 7, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
print(calcular_diferencia_tiempo(fecha_actual, fecha_anterior))  # Debería retornar "hace 2 horas"

# Ejemplo 4: Hace 1 día
fecha_actual = {'day': 5, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
fecha_anterior = {'day': 4, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
print(calcular_diferencia_tiempo(fecha_actual, fecha_anterior))  # Debería retornar "hace 1 día"

# Ejemplo 5: Hace 6 días
fecha_actual = {'day': 10, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
fecha_anterior = {'day': 4, 'hour': 9, 'minute': 3, 'month': 3, 'second': 17, 'year': 2024}
print(calcular_diferencia_tiempo(fecha_actual, fecha_anterior))  # Debería retornar "hace 6 días"