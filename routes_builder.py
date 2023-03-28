from textwrap import dedent
from typing import Dict, Generator, Iterable, List, Tuple

UrlData = Tuple[str, str]


class TestRouteFileBuilder:
    def __init__(
        self, models: List[str], data: UrlData, methods: List[str] = None, out: List[str] = None
    ):
        self.models = models
        self.data = data
        self.methods = methods or []
        self.out = out or []

    def build(self):
        for builder in [
            TestRouteImportsBuilder(self.models),
            TestRouteBuilder(self.data, methods=self.methods),
        ]:
            builder.build()
            self.out.extend(builder.out)


class TestRouteImportsBuilder:
    """
    Routes test imports builder
    """

    def __init__(self, models: List[str], out: List[str] = None):
        self.models = models
        self.out = out or []

    def build(self):
        if not self.models:
            raise RuntimeError("Модели для импорта не предоставлены")
        self._dump_test_imports()

    def _dump_test_imports(self):
        factories = ", ".join(model + "Factory" for model in self.models)
        import_lines = (
            f"import pytest\n\n"
            f"from rest_framework.reverse import reverse\n\n"
            f"from .factories import {factories}\n\n\n"
        )
        self._dump_test_data(import_lines)

    def _dump_test_data(self, lines: Iterable[str]):
        # with open(self.outfile, "a") as file:
        #     file.writelines(data)
        self.out.extend(lines)


class TestRouteBuilder:
    """
    Routes tests builder
    """

    def __init__(self, data: UrlData, methods: List[str] = None, out: List[str] = None):
        prefix, basename = data
        self.prefix = prefix
        self.basename = basename
        self.methods = methods or []
        self.out = out or []

    @staticmethod
    def text_indenter(text: str, times=1) -> Generator[str, None, None]:
        return (times * " " * 4 + line + "\n" for line in text.split("\n"))

    def build(self):
        self.dump_routes_test()

    def get_detailname(self):
        return self.basename[:-1]

    def dump_routes_test(self):
        self.dump_test_header()

        if "list" in self.methods:
            self.dump_test_list_route(self.prefix, self.basename)
        if "detail" in self.methods:
            detailname = self.get_detailname()
            self.dump_test_detail_route(self.prefix, self.basename, detailname)
        if "specs" in self.methods:
            self.dump_test_specs_route(self.prefix, self.basename)
        if "facets" in self.methods:
            self.dump_test_facets_route(self.prefix, self.basename)

        self.dump_test_footer()

    def dump_test_header(self):
        header_lines = dedent(
            """
        @pytest.mark.django_db
        def test_routes():
            \"\"\"
            URL-адрес, рассчитанный через имя,
            соответствует ожидаемому видимому URL.
            \"\"\"

            routes = {
        """
        )
        text = self.text_indenter(header_lines, 0)
        self._dump_test_data(text)

    def dump_test_list_route(self, prefix: str, basename: str):
        list_lines = f'"/api/{prefix}/": reverse("{basename}-list"),'
        text = self.text_indenter(list_lines, 2)
        self._dump_test_data(text)

    def dump_test_detail_route(self, prefix: str, basename: str, detailname: str):
        detail_lines = f'f"/api/{prefix}/{{{detailname}.id}}/": reverse("{basename}-detail", args=[{detailname}.id]),'
        text = self.text_indenter(detail_lines, 2)
        self._dump_test_data(text)

    def dump_test_specs_route(self, prefix: str, basename: str):
        specs_lines = f'"/api/{prefix}/specs/": reverse("{basename}-specs"),'
        text = self.text_indenter(specs_lines, 2)
        self._dump_test_data(text)

    def dump_test_facets_route(self, prefix: str, basename: str):
        facets_lines = f'"/api/{prefix}/facets/": reverse("{basename}-facets"),'
        text = self.text_indenter(facets_lines, 2)
        self._dump_test_data(text)

    def dump_test_footer(self):
        footer_lines = dedent(
            """
        }
        for url, reversed_url in routes.items():
            assert url == reversed_url\n\n
        """
        )
        text = self.text_indenter(footer_lines)
        self._dump_test_data(text)

    def _dump_test_data(self, lines: Iterable[str]):
        # with open(self.outfile, "a") as file:
        #     file.writelines(lines)
        self.out.extend(lines)
