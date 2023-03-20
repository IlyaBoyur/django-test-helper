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
    
    builder = FactoryFileBuilder(models=MODELS)
    builder.build()
    with open(factories_file, "w") as file:
        file.writelines(builder.out)


    builder = TestViewsetImportsBuilder(models=MODELS)
    builder.build()
    with open(test_view_file, "w") as file:
        file.writelines(builder.out)

    for model in MODELS:
        builder = TestViewsetBuilder(model, methods=SUPPORTED_TESTS)
        builder.build()
        with open(test_view_file, "a") as file:
            file.writelines(builder.out)
    
    


        
    # builder = TestRouteImportsBuilder(["Action"], outfile="out/test_routes_TEMP.py")
    # builder.build()

    # builder = TestRouteBuilder(
    #     ["actions", "actions", SUPPORTED_TESTS],
    #     outfile="out/test_routes_TEMP.py"
    # )
    # builder.build()
    