"""
Configuración de Paginación - SnackApp.

Este módulo define los estándares de segmentación de datos para las listas 
de la API. Controla el tamaño de las respuestas para optimizar el consumo 
de ancho de banda y la velocidad de carga en el cliente.
"""

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """
    Paginación estándar basada en números de página.

    Esta clase transforma las respuestas de lista en objetos paginados 
    que incluyen enlaces de navegación y el conteo total de registros.

    Atributos:
        page_size (int): Cantidad de elementos por defecto (5).
        page_size_query_param (str): Parámetro de URL para personalizar el 
            tamaño de página (ej. ?page_size=20).
        max_page_size (int): Límite máximo permitido para evitar sobrecarga (100).

    Estructura de Respuesta:
        {
            "count": 100,
            "next": "http://api.snackapp.co/v1/videos/?page=2",
            "previous": null,
            "results": [...]
        }
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100