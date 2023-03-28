import argparse

from constants import SUPPORTED_TESTS
from factory_builder import FactoryFileBuilder
from routes_builder import TestRouteFileBuilder
from viewset_builders import TestViewsetFileBuilder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test boilerplate code builder")
    parser.add_argument("-m", "--models", default="")
    parser.add_argument("-tr", "--test-routes", default="")
    parser.add_argument("-tv", "--test-views", default="")
    parser.add_argument("-f", "--factories", default="")
    args = parser.parse_args()

    models_file = args.models or "models.txt"
    factories_file = args.factories or "out/factories.py"
    test_view_file = args.test_views or "out/test_viewsets.py"
    test_routes_file = args.test_routes or "out/test_routes_TEMP.py"

    MODELS = [model.strip() for model in open(models_file).readlines()] if models_file else []

    for builder, filename in [
        [FactoryFileBuilder(models=MODELS), factories_file],
        [TestViewsetFileBuilder(models=MODELS, methods=SUPPORTED_TESTS), test_view_file],
        [
            TestRouteFileBuilder(
                models=MODELS, data=["actions", "actions"], methods=SUPPORTED_TESTS
            ),
            test_routes_file,
        ],
    ]:
        builder.build()
        with open(filename, "w") as file:
            file.writelines(builder.out)
