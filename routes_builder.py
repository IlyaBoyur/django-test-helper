from typing import Iterable, List, Dict, Tuple, Generator
from textwrap import dedent
import re



class TestRouteImportsBuilder:
    """
    Routes test imports builder
    """

    def __init__(self, models: List[str], outfile: str):
        self.models = models
        self.outfile = outfile

    def build(self):
        if not self.models:
            raise RuntimeError("Модели для импорта не предоставлены")
        self._dump_test_imports()
    
    def _dump_test_imports(self):
        factories = ", ".join(model + "Factory" for model in self.models)
        import_lines = (
            f'import pytest\n\n'
            f'from rest_framework.reverse import reverse\n\n'
            f'from .factories import {factories}\n\n\n'
        )
        self._dump_test_data(import_lines)

    def _dump_test_data(self, data: Iterable[str]):
        with open(self.outfile, "a") as file:
            file.writelines(data)


ViewsetData = Tuple[str, str, List[str]]


class TestRouteBuilder:
    """
    Routes tests builder
    """

    def __init__(self, data: ViewsetData, outfile: str):
        self.data = data
        self.outfile = outfile

    @staticmethod
    def text_indenter(text: str, times=1) -> Generator[str, None, None]:
        return (times * " " * 4 + line + "\n" for line in text.split("\n"))

    def build(self):
        prefix, basename, methods = self.data
        self.dump_routes_test(prefix, basename, methods)

    def dump_routes_test(self, prefix: str, basename: str, methods=tuple()):
        self.dump_test_header()

        if "list" in methods:
            self.dump_test_list_route(prefix, basename)
        if "detail" in methods:
            detailname = basename[:-1]
            self.dump_test_detail_route(prefix, basename, detailname)
        if "specs" in methods:
            self.dump_test_specs_route(prefix, basename)
        if "facets" in methods:
            self.dump_test_facets_route(prefix, basename)

        self.dump_test_footer()

    def dump_test_header(self):
        header_lines = dedent("""
        @pytest.mark.django_db
        def test_routes():
            \"\"\"
            URL-адрес, рассчитанный через имя,
            соответствует ожидаемому видимому URL.
            \"\"\"

            routes = {
        """)
        text = self.text_indenter(header_lines, 0)
        self.dump_test_data(text)

    def dump_test_list_route(self, prefix: str, basename: str):
        list_lines = f'"/api/{prefix}/": reverse("{basename}-list"),'
        text = self.text_indenter(list_lines, 2)
        self.dump_test_data(text)

    def dump_test_detail_route(self, prefix: str, basename: str, detailname: str):
        detail_lines = (
            f'f"/api/{prefix}/{{{detailname}.id}}/": reverse("{basename}-detail", args=[{detailname}.id]),'
        )
        text = self.text_indenter(detail_lines, 2)
        self.dump_test_data(text)

    def dump_test_specs_route(self, prefix: str, basename: str):
        specs_lines = f'"/api/{prefix}/specs/": reverse("{basename}-specs"),'
        text = self.text_indenter(specs_lines, 2)
        self.dump_test_data(text)

    def dump_test_facets_route(self, prefix: str, basename: str):
        facets_lines = f'"/api/{prefix}/facets/": reverse("{basename}-facets"),'
        text = self.text_indenter(facets_lines, 2)
        self.dump_test_data(text)

    def dump_test_footer(self):
        footer_lines = dedent("""
        }
        for url, reversed_url in routes.items():
            assert url == reversed_url\n\n
        """)
        text = self.text_indenter(footer_lines)
        self.dump_test_data(text)

    def dump_test_data(self, data: Iterable[str]):
        with open(self.outfile, "a") as file:
            file.writelines(data)