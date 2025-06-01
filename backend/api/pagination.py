from rest_framework.pagination import PageNumberPagination
from django.conf import settings


class CustomPagination(PageNumberPagination):
    page_size = settings.PAGINATION_PAGE_SIZE
    page_size_query_param = "limit"
