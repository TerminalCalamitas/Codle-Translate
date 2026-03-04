from lib.generators.python_generator import PythonGenerator
from lib.generators.javascript_generator import JavaScriptGenerator
from lib.generators.java_generator import JavaGenerator
from lib.generators.c_generator import CGenerator
from lib.parser import parse_to_ir

_GENERATORS = {
    "python": PythonGenerator,
    "javascript": JavaScriptGenerator,
    "java": JavaGenerator,
    "c": CGenerator,
}


def translate(input_lang: str, output_lang: str, source: str) -> str:
    """
    Translates `source` written in `input_lang` to `output_lang`
    """

    input_language = input_lang.lower()
    output_language = output_lang.lower()

    if input_language not in _GENERATORS:
        raise ValueError(f"Unsupported input language: {input_lang}")
    if output_language not in _GENERATORS:
        raise ValueError(f"Unsupported output language: {output_lang}")

    intermediate_rep = parse_to_ir(source, input_language)
    generator = _GENERATORS[output_language]()
    return generator.generate(intermediate_rep)
