import pytest

from lib.normalize import normalize, denormalize, infer_type
from lib.ir import (
    IRComment,
    IRPrint,
    IRVarAssign,
    IRForRange,
    IRIfStatement,
    IRWhileLoop,
)
from lib.parser import parse_to_ir
from src.translator import translate


class TestNormalize:
    """
    normalize() converts code expressions into Python style formatting
    """

    # Equality tests
    def test_strict_equality_to_equality(self):
        assert normalize("i === i") == "i == i"

    def test_loose_equality_not_changed(self):
        assert normalize("i == i") == "i == i"

    def test_strict_inequality_to_inequality(self):
        assert normalize("i !== j") == "i != j"

    def test_loose_inequality_not_changed(self):
        assert normalize("i != j") == "i != j"

    # Boolean value tests
    def test_true_uncapitalized(self):
        assert normalize("true") == "True"

    def test_false_uncapitalized(self):
        assert normalize("false") == "False"

    def test_python_true_unchanged(self):
        assert normalize("True") == "True"

    def test_python_false_unchanged(self):
        assert normalize("False") == "False"

    # Null / None tests
    def test_null_to_none(self):
        assert normalize("null") == "None"

    def test_NULL_to_none(self):
        assert normalize("NULL") == "None"

    def test_none_unchanged(self):
        assert normalize("None") == "None"

    # Logical operator tests
    def test_and_operator(self):
        assert normalize("i&&j") == "i and j"

    def test_or_operator(self):
        assert normalize("i||j") == "i or j"

    def test_not_operator(self):
        assert normalize("!value") == "not value"

    def test_not_does_not_affect_notequal(self):
        result = normalize("i != j")
        assert "not" not in result
        assert result == "i != j"

    # Compound expression test
    def test_compound_expression(self):
        result = normalize("i === true && y !== null")
        assert "True" in result
        assert "and" in result
        assert "None" in result

    # Whitespace strip test
    def test_whitespace_stripped(self):
        assert normalize("   true   ") == "True"


class TestDenormalize:
    """
    denormalize() converts neutral Python style formatting to chosen language
    """

    def test_python_unchanged(self):
        assert denormalize("True", "python") == "True"

    def test_true_to_js(self):
        assert denormalize("True", "javascript") == "true"

    def test_true_to_java(self):
        assert denormalize("True", "java") == "true"

    def test_none_to_null_js(self):
        assert denormalize("None", "javascript") == "null"

    def test_none_to_null_c(self):
        assert denormalize("None", "c") == "NULL"

    def test_and_to_js(self):
        assert denormalize("i and j", "javascript") == "i && j"

    def test_or_to_java(self):
        assert denormalize("i or j", "java") == "i || j"

    def test_not_to_c(self):
        assert denormalize("not value", "c") == "!value"


class TestTypeInferance:
    """
    infer_type() determines the IR type from a normalized value string
    """

    def test_integer(self):
        assert infer_type("57") == "int"

    def test_negative_integer(self):
        assert infer_type("-74") == "int"

    def test_float(self):
        assert infer_type("7.3") == "float"

    def test_float_f_suffix(self):
        assert infer_type("2.2f") == "float"

    def test_double_quote_string(self):
        assert infer_type('"93467"') == "str"

    def test_single_quote_string(self):
        assert infer_type("'01312'") == "str"

    def test_bool_true(self):
        assert infer_type("True") == "bool"

    def test_bool_false(self):
        assert infer_type("False") == "bool"

    def test_unknown_expression(self):
        assert infer_type("jibberJabber") == "unknown"

    def test_unknown_call(self):
        assert infer_type("foo()") == "unknown"


class TestIRParser:
    """
    parse_to_ir() returns IR nodes for each language
    """

    # Comment tests
    def test_js_comment(self):
        ir = parse_to_ir("// Hello World", "javascript")
        assert len(ir) == 1
        assert isinstance(ir[0], IRComment)
        assert ir[0].text == "Hello World"

    def test_py_comment(self):
        ir = parse_to_ir("# Hello World", "python")
        assert len(ir) == 1
        assert isinstance(ir[0], IRComment)
        assert ir[0].text == "Hello World"

    def test_java_comment(self):
        ir = parse_to_ir("// Hello World", "java")
        assert len(ir) == 1
        assert isinstance(ir[0], IRComment)
        assert ir[0].text == "Hello World"

    def test_c_comment(self):
        ir = parse_to_ir("// Hello World", "c")
        assert len(ir) == 1
        assert isinstance(ir[0], IRComment)
        assert ir[0].text == "Hello World"

    def test_block_c_comment(self):
        ir = parse_to_ir("/* Hello World */", "c")
        assert len(ir) == 1
        assert isinstance(ir[0], IRComment)
        assert ir[0].text == "Hello World"

    # Variable assignments
    def test_js_int_var(self):
        ir = parse_to_ir("let i = 5;", "javascript")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "5"
        assert node.var_type == "int"

    def test_js_float_var(self):
        ir = parse_to_ir("let i = 5.5;", "javascript")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "5.5"
        assert node.var_type == "float"

    def test_js_bool_var(self):
        ir = parse_to_ir("let i = true;", "javascript")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "True"
        assert node.var_type == "bool"

    def test_js_string_var(self):
        ir = parse_to_ir("let i = 'Hello World';", "javascript")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "'Hello World'"
        assert node.var_type == "str"

    def test_py_int_var(self):
        ir = parse_to_ir("i = 5", "python")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "5"
        assert node.var_type == "int"

    def test_java_int_var(self):
        ir = parse_to_ir("int i = 5;", "java")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "5"
        assert node.var_type == "int"

    def test_c_int_var(self):
        ir = parse_to_ir("int i = 5;", "c")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert node.value == "5"
        assert node.var_type == "int"

    # For Loop Tests
    # JavaScript
    def test_js_for_loop_fields(self):
        ir = parse_to_ir("for (let i = 0; i < 10; i++) {}", "javascript")
        assert len(ir) == 1
        node = ir[0]
        assert isinstance(node, IRForRange), f"Expected IRForRange, got {type(node)}"
        assert node.var == "i"
        assert node.start == "0"
        assert node.end == "10"
        assert node.step == "1"

    def test_js_for_loop_nonzero_start(self):
        ir = parse_to_ir("for (let i = 5; i < 10; i++) {}", "javascript")
        node = ir[0]
        assert node.start == "5"
        assert node.end == "10"

    def test_js_for_loop_custom_step(self):
        ir = parse_to_ir("for (let i = 0; i < 10; i += 5) {}", "javascript")
        node = ir[0]
        assert node.step == "5"

    # Python
    def test_python_for_range_one_arg(self):
        ir = parse_to_ir("for i in range(10):\n    pass", "python")
        node = ir[0]
        assert isinstance(node, IRForRange)
        assert node.var == "i"
        assert node.start == "0"
        assert node.end == "10"
        assert node.step == "1"

    def test_python_for_range_two_args(self):
        ir = parse_to_ir("for i in range(5, 10):\n    pass", "python")
        node = ir[0]
        assert node.start == "5"
        assert node.end == "10"

    def test_python_for_range_three_args(self):
        ir = parse_to_ir("for i in range(0, 10, 5):\n    pass", "python")
        node = ir[0]
        assert node.step == "5"

    # Java
    def test_java_for_loop_fields(self):
        ir = parse_to_ir("for (int i = 0; i < 10; i++) {}", "java")
        node = ir[0]
        assert isinstance(node, IRForRange)
        assert node.var == "i"
        assert node.start == "0"
        assert node.end == "10"

    # C
    def test_c_for_loop_fields(self):
        ir = parse_to_ir("for (int i = 0; i < 10; i++) {}", "c")
        node = ir[0]
        assert isinstance(node, IRForRange)
        assert node.var == "i"
        assert node.start == "0"
        assert node.end == "10"

    # While Loop Tests
    # JavaScript
    def test_js_while_loop(self):
        ir = parse_to_ir("while (i < 10) {}", "javascript")
        assert isinstance(ir[0], IRWhileLoop)
        assert ir[0].condition == "i < 10"

    def test_while_condition_normalized(self):
        ir = parse_to_ir("while (i < 10 && j > 0) {}", "javascript")
        assert isinstance(ir[0], IRWhileLoop)
        assert "and" in ir[0].condition
        assert "&&" not in ir[0].condition

    # Python
    def test_python_while_loop(self):
        ir = parse_to_ir("while i < 10:\n   pass", "python")
        assert isinstance(ir[0], IRWhileLoop)
        assert ir[0].condition == "i < 10"

    # Java
    def test_java_while_loop(self):
        ir = parse_to_ir("while (i < 10) {}", "java")
        assert isinstance(ir[0], IRWhileLoop)
        assert ir[0].condition == "i < 10"

    # C
    def test_c_while_loop(self):
        ir = parse_to_ir("while (i < 10) {}", "c")
        assert isinstance(ir[0], IRWhileLoop)
        assert ir[0].condition == "i < 10"

    # If Statement Tests
    def test_js_if_statement(self):
        ir = parse_to_ir("if (i === 10) {}", "javascript")
        assert isinstance(ir[0], IRIfStatement)
        assert ir[0].condition == "i == 10"

    # Print Statement Tests
    def test_js_console_log(self):
        ir = parse_to_ir("console.log('Hello World');", "javascript")
        node = ir[0]
        assert isinstance(node, IRPrint)
        assert "'Hello World'" in node.value

    def test_py_print(self):
        ir = parse_to_ir("print('Hello World')", "python")
        node = ir[0]
        assert isinstance(node, IRPrint)
        assert "'Hello World'" in node.value

    def test_java_println(self):
        ir = parse_to_ir("System.out.println('Hello World');", "java")
        node = ir[0]
        assert isinstance(node, IRPrint)
        assert "'Hello World'" in node.value

    def test_js_printf(self):
        ir = parse_to_ir("printf('Hello World');", "c")
        node = ir[0]
        assert isinstance(node, IRPrint)
        assert "'Hello World'" in node.value

    # Increment / Decrement Tests
    def js_increment_to_var_assign(self):
        ir = parse_to_ir("i++;", "javascript")
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert "1" in node.value

    def js_decrement_to_var_assign(self):
        ir = parse_to_ir("i--;", "javascript")
        node = ir[0]
        assert isinstance(node, IRVarAssign)
        assert node.name == "i"
        assert "1" in node.value

    def test_java_increment(self):
        ir = parse_to_ir("i++;", "java")
        node = ir[0]
        assert isinstance(node, IRVarAssign)

    def test_c_increment(self):
        ir = parse_to_ir("i++;", "c")
        node = ir[0]
        assert isinstance(node, IRVarAssign)

    # Nested Body Node Tests
    def test_for_body_has_print(self):
        src = "for (let i = 0; i < 10; i++) { console.log('i'); }"
        ir = parse_to_ir(src, "javascript")
        for_node = ir[0]
        assert isinstance(for_node, IRForRange)
        assert any(isinstance(node, IRPrint) for node in for_node.body)

    def test_while_body_has_increment(self):
        src = "while (i < 10) { i++; }"
        ir = parse_to_ir(src, "javascript")
        while_node = ir[0]
        assert isinstance(while_node, IRWhileLoop)
        assert any(isinstance(node, IRVarAssign) for node in while_node.body)


# Full Integration Testing

# Source code for each language

SOURCES = {
    "javascript": """\
// For Loop
for (let i = 0; i < 100; i++) {
  console.log("hello");
}
// If Statement
if (i === 1) {
  print(1);
}
// While Loop
while (i < 1) {
  console.log(i);
  i++;
}
// Integer Variable
let integer = 1;
// Float Variable
let floatingpoint = 1.0;
// String Variable
let string = "string";
// Boolean Variable
let boolean = true;
""",
    "python": """\
# For Loop
for i in range(0, 100):
    print("hello")
# If Statement
if i == 1:
    print(1)
# While Loop
while (i < 1):
    print(i)
    i+=1
# Integer Variable
integer = 1
# Float Variable
floatingpoint = 1.0
# String Variable
string = "string"
# Boolean Variable
boolean = True
""",
    "java": """\
// For Loop
for (int i = 0; i < 100; i++) {
    System.out.println("hello");
}
// If Statement
if (i == 1) {
    System.out.println(i);
}
// While Loop
while (i < 1) {
    System.out.println(i);
    i++;
}
// Integer Variable
int integer = 1;
// Float Variable
float floatingpoint = 1.0;
// String Variable
String string = "string";
// Boolean Variable
boolean boolean = true;
""",
    "c": """\
// For Loop
for (int i = 0; i < 100; i++) {
    printf("hello\n");
}
// If Statement
if (i == 1) {
    printf("%d\n", 1);
}
// While Loop
while (i < 1) {
    printf("%d\n", i);
    i++;
}
// Integer Variable
int integer = 1;
// Float Variable
float floatingpoint = 1.0;
// String Variable
char* string = "string";
// Boolean Variable
bool boolean = true;
""",
}

ALL_LANGS = list(SOURCES.keys())
ALL_PAIRS = [(src, tgt) for src in ALL_LANGS for tgt in ALL_LANGS if src != tgt]

# Helper Functions


def _lines(code: str) -> list[str]:
    # Non-empty stripped lines
    return [line.strip() for line in code.splitlines() if line.strip()]


def _has_for(code: str, lang: str) -> bool:
    if lang == "python":
        return any(
            line.startswith("for ") and "in range(" in line for line in _lines(code)
        )
    return any(line.startswith("for (") for line in _lines(code))


def _has_while(code: str) -> bool:
    return any("while" in line for line in _lines(code))


def _has_if(code: str) -> bool:
    return any(
        line.startswith("if ") or line.startswith("if(") for line in _lines(code)
    )


def _has_comment(code: str, lang: str) -> bool:
    marker = "#" if lang == "python" else "//"
    return any(line.startswith(marker) for line in _lines(code))


def _has_print(code: str, lang: str) -> bool:
    lang_map = {
        "javascript": "console.log(",
        "python": "print(",
        "java": "System.out.println(",
        "c": "printf(",
    }
    return lang_map[lang] in code


def _has_bool_literal(code: str, lang: str) -> bool:
    if lang == "python":
        return "True" in code or "False" in code
    return "true" in code or "false" in code


def _has_augmented_assign(code: str) -> bool:
    return "+=" in code or "-=" in code


# Parameterized Integration Tests
@pytest.mark.parametrize("src_lang, tgt_lang", ALL_PAIRS)
class TestIntegration:
    """
    Tests translate() for all 12 language pairs
    """

    def test_produces_output(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert result.strip(), "translate() returned empty output"

    def test_comment_present(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert _has_comment(result, tgt_lang), (
            f"No {tgt_lang} comment found in output from {src_lang}"
        )

    def test_for_loop_present(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert _has_for(result, tgt_lang), (
            f"No {tgt_lang} for loop found in output from {src_lang}"
        )

    def test_while_loop_present(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert _has_while(result), (
            f"No {tgt_lang} while loop found in output from {src_lang}"
        )

    def test_if_statement_present(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert _has_if(result), (
            f"No {tgt_lang} if statement found in output from {src_lang}"
        )

    def test_print_statement_present(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert _has_print(result, tgt_lang), (
            f"No {tgt_lang} print statement found in output from {src_lang}"
        )

    def test_bool_literal_present(self, src_lang, tgt_lang):
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        assert _has_bool_literal(result, tgt_lang), (
            f"No correct form of {tgt_lang} boolean found in output from {src_lang}"
        )

    def test_no_src_keywords(self, src_lang, tgt_lang):
        # Making sure source specific keywords don't leak to output
        result = translate(src_lang, tgt_lang, SOURCES[src_lang])
        if tgt_lang == "python":
            # Dictionaries aren't supported so python shouldn't have { or } in output
            assert "{" not in result and "}" not in result, (
                f"Curly braces found in Python output from {src_lang}"
            )

            for line in _lines(result):
                if line.startswith("#"):
                    continue
                assert not line.startswith("//")

        # This is basically an else case but if I add
        # another language I won't need to change this test
        if tgt_lang in ("javascript", "java", "c"):
            for line in _lines(result):
                if line.startswith("//"):
                    continue
                assert " True" not in line and "=True" not in line, (
                    f"Python bool 'True' in {tgt_lang} output from {src_lang}: {line!r}"
                )
                assert " False" not in line and "=False" not in line, (
                    f"Python bool 'False' in {tgt_lang} output from {src_lang}: {line!r}"
                )


# Targeted Integration Tests
class TestTargetedTranslations:
    # Python range() testing

    def test_zero_start_uses_range_1_arg(self):
        result = translate("javascript", "python", "for (let i = 0; i < 10; i++) {}")
        assert "range(10)" in result, (
            "for i from 0 should use range(n), not range(0, n)"
        )

    def test_nonzero_start_uses_range_2_arg(self):
        result = translate("javascript", "python", "for (let i = 3; i < 10; i++) {}")
        assert "range(3, 10)" in result

    def test_custom_step_uses_range_3_arg(self):
        result = translate("javascript", "python", "for (let i = 0; i < 10; i += 2) {}")
        assert "range(0, 10, 2)" in result or "range(10, 2)" in result

    # Java type mapping

    def test_int_maps_to_java_int(self):
        result = translate("javascript", "java", "let i = 1;")
        assert "int i" in result

    def test_float_maps_to_java_double(self):
        result = translate("javascript", "java", "let i = 1.5;")
        assert "double i" in result

    def test_string_maps_to_java_String(self):
        result = translate(
            "javascript",
            "java",
            "let i = 'hi';",
        )
        assert "String i" in result

    def test_bool_maps_to_java_boolean(self):
        result = translate("javascript", "java", "let i = true;")
        assert "boolean i" in result

    # C type mapping

    def test_int_maps_to_c_int(self):
        result = translate("javascript", "c", "let i = 1;")
        assert "int i" in result

    def test_float_maps_to_c_float(self):
        result = translate("javascript", "c", "let i = 1.5;")
        assert "float i" in result

    def test_string_maps_to_c_char_ptr(self):
        result = translate("javascript", "c", "let i = 'hi';")
        assert "char*" in result

    def test_c_output_has_stdio_include(self):
        # When a print is present, C output must include stdio.h
        result = translate("javascript", "c", "console.log('hi');")
        assert "#include <stdio.h>" in result

    def test_c_output_no_stdio_without_print(self):
        result = translate("javascript", "c", "let i = 1;")
        assert "#include <stdio.h>" not in result

    # Condition normalization
    def test_strict_equality_normalized_in_if(self):
        result = translate("javascript", "python", "if (i === 1) {}")
        assert "if i == 1:" in result

    def test_bool_condition_js_to_python(self):
        result = translate("javascript", "python", "if (value === true) {}")
        assert "True" in result

    def test_and_operator_js_to_python(self):
        result = translate("javascript", "python", "while (i < 10 && j > 0) {}")
        assert "and" in result
        assert "&&" not in result

    def test_and_operator_python_to_js(self):
        result = translate("python", "javascript", "while i < 10 and j > 0:\n    pass")
        assert "&&" in result
        assert "and" not in result

    # Error Handling
    def test_unsupported_input_lang_raises(self):
        with pytest.raises(ValueError, match="Unsupported input language"):
            translate("ruby", "python", "i = 1")

    def test_unsupported_output_lang_raises(self):
        with pytest.raises(ValueError, match="Unsupported output language"):
            translate("python", "rust", "i = 1")

    def test_empty_source_returns_empty(self):
        result = translate("javascript", "python", "")
        assert result.strip() == ""
