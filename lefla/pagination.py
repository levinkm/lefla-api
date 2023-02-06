from rest_framework import pagination


class LargeResultsSetPagination(pagination.PageNumberPagination):
    """Class for Custom Pagination"""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 1000
