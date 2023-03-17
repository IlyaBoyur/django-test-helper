from typing import Iterable, List, Dict, Tuple, Generator
import re
from textwrap import dedent


class TestViewsetImportsBuilder:
    def __init__(self, models, outfile):
        self.models = models
        self.outfile = outfile
    
    def dump_test_imports(self):
        if not self.models:
            raise RuntimeError("Модели для импорта не предоставлены")
        factories = ", ".join(model + "Factory" for model in self.models)
        import_lines = (
            f'import pytest\n\n'
            f'from rest_framework.reverse import reverse\n'
            f'from rest_framework.status import HTTP_200_OK\n\n'
            f'from .factories import {factories}\n\n\n'
        )
        self.dump_test_data(import_lines)

    def dump_test_data(self, data: Iterable[str]):
        with open(self.outfile, "a") as file:
            file.writelines(data)


class TestViewsetBuilder:
    def __init__(self, infile: str, outfile: str):
        self.infile = infile
        self.outfile = outfile

    @staticmethod
    def camel_2_snake_case(string):
        return ''.join(['_' + char.lower() if char.isupper()
                       else char for char in string]).lstrip('_')

    @staticmethod
    def text_indenter(text: str, times=1) -> Generator[str, None, None]:
        return (times * " " * 4 + line + "\n" for line in text.split("\n"))

    def build_schema(self, model):
        self.model = [model, self._build_view_set_name(model)]

    def _build_view_set_name(self, camel_name):
        return f"{camel_name}ViewSet"

    def _build_test_class_name(self, viewset, test_before=True):
        return  f"Test{viewset}" if test_before else f"class {viewset}Test"

    def _build_url_name(self, snake_name: str, type: str):
        return f"{snake_name.upper()}_{type.upper()}_URL"


    def dump_test_class(self, methods=tuple()):
        self.dump_test_class_header()
        if "list" in methods:
            self.dump_test_list()
        if "detail" in methods:
            self.dump_test_detail()
        if "specs" in methods:
            self.dump_test_specs()
        if "facets" in methods:
            self.dump_test_facets()
        if "filter" in methods:
            self.dump_test_filter()
        self.dump_test_class_footer()

    def dump_test_class_header(self):
        camel_name, viewset_name = self.model
        snake_name = self.camel_2_snake_case(camel_name)

        header_lines = (
            f'class {self._build_test_class_name(viewset_name)}:\n'
            f'    {self._build_url_name(snake_name, "list")} = reverse("{snake_name}s-list")\n'
            f'    {self._build_url_name(snake_name, "specs")} = reverse("{snake_name}s-specs")\n'
            f'    {self._build_url_name(snake_name, "facets")} = reverse("{snake_name}s-facets")\n\n'
        )
        self.dump_test_data(header_lines)


    def dump_test_list(self):
        camel_name, _ = self.model
        snake_name = self.camel_2_snake_case(camel_name)

        list_lines = dedent(f"""
            @pytest.mark.django_db
            def test_list(self, django_assert_num_queries, client):
                {snake_name}s = [{camel_name}Factory() for _ in range(3)]

                with django_assert_num_queries(1):
                    response = client.get(self.{self._build_url_name(snake_name, "list")})

                assert response.status_code == HTTP_200_OK
                assert len(response.json()) == len({snake_name}s)
        """)
        text = self.text_indenter(list_lines)
        self.dump_test_data(text)

    def dump_test_detail(self):
        camel_name, _ = self.model
        snake_name = self.camel_2_snake_case(camel_name)
        detail_url = self._build_url_name(snake_name, "detail")

        detail_lines = dedent(f"""
            @pytest.mark.django_db
            def test_retrieve(self, django_assert_num_queries, client):
                {snake_name} = {camel_name}Factory()
                {detail_url} = reverse("{snake_name}s-detail", args=[{snake_name}.id])

                with django_assert_num_queries(1):
                    response = client.get({detail_url})

                assert response.status_code == HTTP_200_OK
                assert response.json()["id"] == {snake_name}.id
        """)
        text = self.text_indenter(detail_lines)
        self.dump_test_data(text)

    def dump_test_specs(self):
        specs_lines = ""
        self.dump_test_data(specs_lines)

    def dump_test_facets(self):
        facets_lines = ""
        self.dump_test_data(facets_lines)

    def dump_test_filter(self):
        filter_lines = ""
        self.dump_test_data(filter_lines)

    def dump_test_class_footer(self):
        footer_lines = "\n\n"
        self.dump_test_data(footer_lines)

    def dump_test_data(self, data: Iterable[str]):
        with open(self.outfile, "a") as file:
            file.writelines(data)
