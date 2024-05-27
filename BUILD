# Pants (pantsbuild.org) BUILD file for open-interpreter dependencies.
python_requirement(
    name="setuptools",
    requirements=["setuptools"],
    resolve="base",
)

python_sources(
    sources = ["interpreter/**/*.py"],
    resolve = "base",
    dependencies = [
        ":poetry#ipykernel",
        ":poetry#matplotlib",
    ]
)

python_tests(
    name = "tests",
    sources = ["interpreter/**/*_test.py"],
    resolve = "base",
)

poetry_requirements(
    name="poetry",   
    resolve="base",
)
