import argparse

from factory_builder import FactoryFileBuilder
from test_builders import TestImportsBuilder, TestViewsetBuilder


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test boilerplate code builder")
    parser.add_argument("-m", "--models", default="")
    parser.add_argument("-tv", "--test-views", default="")
    parser.add_argument("-f", "--factories", default="")
    args = parser.parse_args()

    models_file = args.models 
    factories_file = args.factories or "out/factories.py"
    test_view_file = args.test_views or "out/test_viewsets.py"

    MODELS = open(models_file).readlines() if models_file else []
    
    with open(factories_file, "w"):
        pass
    builder = FactoryFileBuilder(None, models=MODELS, outfile=factories_file)
    builder.build()

    with open(test_view_file, "w"):
        pass
    builder = TestImportsBuilder(MODELS, outfile=test_view_file)
    builder.dump_test_imports()

    builder = TestViewsetBuilder(None, outfile=test_view_file)
    for model in MODELS:
        builder.build_schema(model)
        builder.dump_test_class(("list","detail",))


