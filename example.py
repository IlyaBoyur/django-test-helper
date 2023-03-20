import argparse

from factory_builder import FactoryFileBuilder
from viewset_builders import TestViewsetImportsBuilder, TestViewsetBuilder
from routes_builder import TestRouteImportsBuilder, TestRouteBuilder
from constants import SUPPORTED_TESTS


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test boilerplate code builder")
    parser.add_argument("-m", "--models", default="")
    parser.add_argument("-tv", "--test-views", default="")
    parser.add_argument("-f", "--factories", default="")
    args = parser.parse_args()

    models_file = args.models or "models.txt"
    factories_file = args.factories or "out/factories.py"
    test_view_file = args.test_views or "out/test_viewsets.py"

    MODELS = open(models_file).readlines() if models_file else []
    
    builder = FactoryFileBuilder(None, models=MODELS)
    builder.build()
    with open(factories_file, "w") as file:
        file.writelines(builder.out)


    with open(test_view_file, "w"):
        pass
    builder = TestViewsetImportsBuilder(MODELS, outfile=test_view_file)
    builder.dump_test_imports()

    builder = TestViewsetBuilder(None, outfile=test_view_file)
    for model in MODELS:
        builder.build_schema(model)
        builder.dump_test_class(methods=SUPPORTED_TESTS)
    # builder = TestRouteImportsBuilder(["Action"], outfile="out/test_routes_TEMP.py")
    # builder.build()

    # builder = TestRouteBuilder(
    #     ["actions", "actions", SUPPORTED_TESTS],
    #     outfile="out/test_routes_TEMP.py"
    # )
    # builder.build()
    