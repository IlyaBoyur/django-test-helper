from textwrap import dedent
from typing import Generator, Iterable, List


class TestViewsetFileBuilder:
    def __init__(self, models, methods: List[str] = None, out: List[str] = None):
        self.models = models or []
        self.methods = methods or []
        self.out = out or []

    def build(self):
        for builder in [
            TestViewsetImportsBuilder(self.models),
            *[TestViewsetBuilder(model, self.methods) for model in self.models],
        ]:
            builder.build()
            self.out.extend(builder.out)


class TestViewsetImportsBuilder:
    def __init__(self, models: List[str], out: List[str] = None):
        self.models = models
        self.out = out or []

    def build(self):
        factories = ", ".join(model + "Factory" for model in self.models)
        import_lines = (
            f"import pytest\n\n"
            f"from rest_framework.reverse import reverse\n"
            f"from rest_framework.status import HTTP_200_OK\n\n"
            f"from .factories import {factories}\n\n\n"
        )
        self.out.extend(import_lines)


class TestViewsetBuilder:
    def __init__(self, model: str, methods: List[str] = None, out: List[str] = None):
        self.model = model
        self.methods = methods or tuple()
        self.out = out or []

    @staticmethod
    def camel_2_snake_case(string: str):
        return "".join(["_" + char.lower() if char.isupper() else char for char in string]).lstrip(
            "_"
        )

    @staticmethod
    def text_indenter(text: str, times: int = 1) -> Generator[str, None, None]:
        return (times * " " * 4 + line + "\n" for line in text.split("\n"))

    def build(self):
        self.build_schema()
        self.dump_test_class()

    def build_schema(self):
        self.camel = self.model
        self.snake = self.camel_2_snake_case(self.model)
        self.viewset_name = self._build_view_set_name(self.model)

    def _build_view_set_name(self, camel_name):
        return f"{camel_name}ViewSet"

    def _build_test_class_name(self, viewset, test_before=True):
        return f"Test{viewset}" if test_before else f"class {viewset}Test"

    def _build_url_name(self, snake_name: str, type: str):
        return f"{snake_name.upper()}_{type.upper()}_URL"

    def dump_test_class(self):
        self.dump_test_class_header()
        if "list" in self.methods:
            self.dump_test_list()
        if "detail" in self.methods:
            self.dump_test_detail()
        if "specs" in self.methods:
            self.dump_test_specs()
        if "facets" in self.methods:
            self.dump_test_facets()
        if "filter" in self.methods:
            self.dump_test_filter()
        self.dump_test_class_footer()

    def dump_test_class_header(self):
        snake_name = self.snake

        header_lines = (
            f"class {self._build_test_class_name(self.viewset_name)}:\n"
            f'    {self._build_url_name(snake_name, "list")} = reverse("{snake_name}s-list")\n'
        )
        header_lines += (
            f'    {self._build_url_name(snake_name, "specs")} = reverse("{snake_name}s-specs")\n'
            if "specs" in self.methods
            else ""
        )
        header_lines += (
            f'    {self._build_url_name(snake_name, "facets")} = reverse("{snake_name}s-facets")\n'
            if "facets" in self.methods
            else ""
        )
        self.dump_test_data(header_lines)

    def dump_test_list(self):
        camel_name = self.camel
        snake_name = self.snake

        list_lines = dedent(
            f"""
            @pytest.mark.django_db
            def test_list(self, django_assert_num_queries, api_client):
                {snake_name}s = [{camel_name}Factory() for _ in range(3)]

                with django_assert_num_queries(1):
                    response = api_client.get(self.{self._build_url_name(snake_name, "list")})

                assert response.status_code == HTTP_200_OK
                assert len(response.json()) == len({snake_name}s)
        """
        )
        text = self.text_indenter(list_lines)
        self.dump_test_data(text)

    def dump_test_detail(self):
        camel_name = self.camel
        snake_name = self.snake
        detail_url = self._build_url_name(snake_name, "detail")

        detail_lines = dedent(
            f"""
            @pytest.mark.django_db
            def test_retrieve(self, django_assert_num_queries, api_client):
                {snake_name} = {camel_name}Factory()
                {detail_url} = reverse("{snake_name}s-detail", args=[{snake_name}.id])

                with django_assert_num_queries(1):
                    response = api_client.get({detail_url})

                assert response.status_code == HTTP_200_OK
                assert response.json()["id"] == {snake_name}.id
        """
        )
        text = self.text_indenter(detail_lines)
        self.dump_test_data(text)

    def dump_test_specs(self):
        camel_name = self.camel
        snake_name = self.snake

        specs_lines = dedent(
            f"""
            @pytest.mark.django_db
            def test_specs(self, django_assert_num_queries, api_client):
                {snake_name}s = [{camel_name}Factory() for _ in range(3)]

                with django_assert_num_queries(1):
                    response = api_client.get(self.{self._build_url_name(snake_name, "specs")})
                specs = {{spec["name"]: spec.get("choices") or spec.get("range") for spec in response.json()}}
                
                assert response.status_code == HTTP_200_OK
                assert specs["<spec>"] == len(<model>)
        """
        )
        text = self.text_indenter(specs_lines)
        self.dump_test_data(text)

    def dump_test_facets(self):
        camel_name = self.camel
        snake_name = self.snake

        facets_lines = dedent(
            f"""
            @pytest.mark.django_db
            def test_facets(self, django_assert_num_queries, api_client):
                {snake_name}s = [{camel_name}Factory() for _ in range(3)]

                with django_assert_num_queries(1):
                    response = api_client.get(self.{self._build_url_name(snake_name, "facets")})
                json = response.json()
                facets = {{facet["name"]: facet.get("choices") or facet.get("range") for facet in response.json()["facets"]}}
                
                assert response.status_code == HTTP_200_OK
                assert facets["<facet>"] == len(<model>)
                assert json["count"] == len({snake_name}s)
        """
        )
        text = self.text_indenter(facets_lines)
        self.dump_test_data(text)

    def dump_test_filter(self):
        camel_name = self.camel
        snake_name = self.snake

        filter_lines = dedent(
            f"""
            @pytest.mark.django_db
            def test_filter(self, django_assert_num_queries, api_client):
                {snake_name}s = [{camel_name}Factory() for _ in range(3)]

                # <filter>
                data = {{
                    "<filter>": <value>,
                }}
                with django_assert_num_queries(1):
                    response = api_client.get(self.{self._build_url_name(snake_name, "list")}, data=data)
                
                assert response.status_code == HTTP_200_OK
                for {snake_name} in response.json():
                    assert {snake_name}["<filter>"] == <value>
        """
        )
        text = self.text_indenter(filter_lines)
        self.dump_test_data(text)

    def dump_test_class_footer(self):
        footer_lines = "\n\n"
        self.dump_test_data(footer_lines)

    def dump_test_data(self, data: Iterable[str]):
        self.out.extend(data)
