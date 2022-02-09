import os

def print_env_vars():
    print("\nEnvironment variables:")
    for key, value in os.environ.items():
        print("{}={}".format(key, value))
    print("\n")

def print_importable_packages():
    print("\nImportable packages:")
    for package in sorted(["{}.{}".format(mod.__package__, mod.__name__) for mod in list(filter(lambda mod: hasattr(mod, "__package__"), globals().values()))]):
        print(package)
    print("\n")

# print_importable_packages()

print(help('modules'))