from rest_framework.pagination import PageNumberPagination


class CoursePagination(PageNumberPagination):
    """Пагинация для курсов"""
    page_size = 5  # Количество элементов на странице
    page_size_query_param = 'page_size'  # Позволяет клиенту менять размер страницы
    max_page_size = 50  # Максимальный размер страницы


class LessonPagination(PageNumberPagination):
    """Пагинация для уроков"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100