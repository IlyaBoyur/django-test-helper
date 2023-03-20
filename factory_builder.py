from typing import List


class FactoryFileBuilder:
    def __init__(self, models: List[str], out: List[str]=None):
        self.models = models or []
        self.out = out or []
 
    def build(self) -> None:
        self.build_schema()
        self.dump_imports()
        self.dump_factories()
    
    def build_schema(self) -> None:
        model_names = self.models or self._parse_models()
        if not model_names:
            raise RuntimeError("Модели не определены")

        self.model_names = model_names

    def _parse_models(self) -> List[str]:
        with open(self.infile) as infile:
            pass
        raise NotImplementedError("Парсинг файла")

    def _generate_factory(self, model: str) -> str:
        # fields = generate_factory_field()
        fields = ""
        name = model + "Factory"
        template = (f"class {name}(factory.django.DjangoModelFactory):\n"
                    f"{fields}\n    class Meta:\n        model = {model}\n")
        return template

    def _generate_factories(self):
        return (self._generate_factory(model) for model in self.model_names)
    
    def dump_imports(self):
        models = ", ".join(self.model_names)
        self.out.append(f"import factory.fuzzy\n")
        self.out.append(f"from ..models import {models}\n\n\n")

    def dump_factories(self):
        self.out.extend("\n".join(self._generate_factories()))
