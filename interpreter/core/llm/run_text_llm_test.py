
import dataclasses
import itertools
from interpreter.core.llm import run_text_llm
from parameterized import parameterized
import unittest
from typing import TypeAlias


NestedDict: TypeAlias = 'dict[str, str | NestedDict]'


@dataclasses.dataclass
class _TestCase:
    example: str
    expected_code: str


_TEST_STR_NO_MARKDOWN = _TestCase(
    example="Response with some backticks `` but no code.", 
    expected_code=""
)


_TEST_STR_MARKDOWN_BLOCK = _TestCase(
    example="""
Example string that includes markdown and text.
```python
print("hello python")
```
Yep, this will print the string "hello python".
""", 
    expected_code="""
print("hello python")
"""
)


_TEST_MARKDOWN_BLOCK_NO_LANGUAGE = _TestCase(
    example="""
Here's a program that prints "hello world".
```
print("hello world")
```
""", 
    expected_code="""
print("hello world")
"""
)


_TEST_ONLY_MARKDOWN_BLOCK = _TestCase(
    example="""```
print("only markdown")
```""", 
    expected_code="""
print("only markdown")
""")

def _make_chunk(content: str):
    """Simulate a streaming response from LiteLLM."""
    return dict(
        choices=[
            dict(
                index=0, 
                delta=dict(content=content, role='assistant'),
            )
        ]
    )


@dataclasses.dataclass
class _TestInterpreter:
    os: bool = False
    verbose: bool = True


class _TestLLM:
    """Base class for test LLMs."""

    def __init__(self, message: str):
        self._message = message
        self.execution_instructions = None
        self.interpreter = _TestInterpreter()


class _NoStreamSplitLLM(_TestLLM):
    """Return the whole string as a single delta."""

    def completions(self, **_):
        return [_make_chunk(self._message)]


class _SplitEveryCharacterLLM(_TestLLM):
    """Return each character from the string one by one."""

    def completions(self, **_):
        return [_make_chunk(c) for c in self._message]


_TEST_CASES = list(itertools.product(
    [
        _NoStreamSplitLLM, 
        _SplitEveryCharacterLLM
    ],
    [
        _TEST_STR_NO_MARKDOWN, 
        _TEST_STR_MARKDOWN_BLOCK,
        _TEST_MARKDOWN_BLOCK_NO_LANGUAGE,
        _TEST_ONLY_MARKDOWN_BLOCK,
    ]
))

class RunTxtLlmTest(unittest.TestCase):

    @parameterized.expand(_TEST_CASES)
    def test_whole_string_match(self, llm_cls, test_case):
        llm = llm_cls(test_case.example)
        message = [delta["content"] for delta in run_text_llm.run_text_llm(llm, dict(messages=[]))]
        self.assertEqual("".join(message), test_case.example)

    @parameterized.expand(_TEST_CASES)
    def test_code_match(self, llm_cls, test_case):
        llm = llm_cls(test_case.example)
        code_message = [
            delta["content"] for delta in run_text_llm.run_text_llm(llm, dict(messages=[]))
            if delta["type"] == "code"]
        self.assertEqual("".join(code_message), test_case.expected_code)

if __name__ == "__main__":
    unittest.main()
