from typing import List


class FactoryFileBuilder:
    def __init__(self, infile: str, models: List[str], outfile: str):
        self.infile = infile
        self.models = models
        self.outfile = outfile
 
    def build(self):
        self.build_schema()
        self.dump_imports()
        self.dump_factories()
    
    def build_schema(self):
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
        with open(self.outfile, "a") as file:
            file.write(f"import factory.fuzzy\n")
            file.write(f"from ..models import {models}\n\n\n")

    def dump_factories(self):
        with open(self.outfile, "a") as file:
            file.writelines("\n".join(self._generate_factories()))