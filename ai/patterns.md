# Coding Patterns and Rules
This file dictates the patterns and rules to use when generating code for this repository. As an AI Agent you need to respect these rules and always follow them. Analyze the sections below to understand how to process the request.

## Communication 
When communicating with the user:
- Always use clear and concise language.
- Do not use overly complex sentences or jargon that may not be understood. 
- Be direct. 
- No fluff, just facts. 
- Do not tell the user what files you are reading, analyzing, examining or any other process.
- Do not describe the issues found while still iterating on the code.

## Workflow:
Always follow the workflow below to generate code:

1. Analyze the request carefully and understand what is being asked.
2. Analyze the rest of the contents of this file and understand the rules and patterns that you need to follow.
3. If generating source code, analyze the `src` directory and the existing code patterns in it.
4. If generating test code, analyze the `tests` directory and the existing code patterns in it. Pay close attention to the type of tests that are being generated, whether they are integration tests or unit tests. This will determine which directory to look for patterns in.
5. Create a clear and concise step-by-step plan to generate the code. Show the plan to user as you are executing it.
6. Once you have generated the code, iterate on it to ensure
   - It meets the patterns and rules outlined in this file.
   - It meets the patterns and rules of the existing code in the `src` or `tests` directory, depending on whether you are generating source code or test code.
   - The tests pass.
   - If the code is not passing the tests, iterate on it until it does.
   - If the generate code is tests, and they are not passing, iterate on it until it does.

## How to create a Step-by-Step Plan
When creating a step-by-step plan, always follow these rules:

Use the following format to create a todo list:
```markdown
- Step 1: Description of the first step
- Step 2: Description of the second step
- Step 3: Description of the third step
```
Do not ever use HTML tags or any other formatting for the todo list, as it will not be rendered correctly. Always use the markdown format shown above.

## How to check that the tests pass
When generating source code you can run the tests by executing the following command:
```pytest ./tests```

When generating integration tests you can run the tests by executing the following command:
```pytest ./tests/integration```

When generating unit tests you can run the tests by executing the following command:
```pytest ./tests/unit```

# General Rules
When generating any code, be it source code or test code, always follow these general rules:
- Never include comments about the file name or module name at the top of the code.
- Never add comments.
- Never add docstrings.
- Custom object typehints should not be quoted, they should be directly imported instead.
- Never import starting with `src`, always use the project module instead.
- User early return patterns to avoid deep nesting and else statements.
- If function calls are fairly short, do not use explanatory variables. Instead, call the function directly where it is necessary.
- Always do full imports at the top of the file, never use relative imports.
- Do not import modules that are not used in the code.

## Source Code Generation
When you generate source code always follow these general rules:
- Use type annotations for all function signatures. Including parameters and return types.
- Use OOP patterns.
- Use SOLID principles.
- Focus on maintainability and testability.
- Methods should have a single responsibility

## Test Code Generation
When you generate test code always follow these general rules:
- Use type annotations for all function signatures. Including parameters and return types. Test methods should have the type hint `None` for the return type.
- Use `pytest` as the testing framework. Do not use `unittest`.
- Always use test functions instead of test classes.
- Mocking should be done using the `pytest-mock` library.
  - Never use `monkeypatch`.
  - Use the `mocker` fixture provided by `pytest-mock` for mocking. The type hint for it is `pytest_mock.MockerFixture`.
  - Always assign the `mocker.patch` calls to mock objects, and assert the functionality of the mock objects is being called.
  - When mocking class methods decorated with @property decorator, you should pass the `new_callable` argument to `mocker.patch` with the `mocker.PropertyMock` type. Additionally, in these cases do not use the `mocker.patch.object` method, instead use `mocker.patch` with the full path to the class and property being mocked.
  - When creating mock objects, use the `mocker.MagicMock` type. This allows you to set return values and assert calls on the mock object. Do not use `mocker.Mock` as it does not allow setting return values. Do not use `mocker.create_autospec` as it is unnecessary.
  - When mocking modules using a full path, always use the path to that class or function from within the scope of the module being tested, instead of the absolute path.
- Check all directories up from the one that the tests will be implemented in, for `conftest.py` files and reuse already defined fixtures that may be useful. Stop scanning for `conftest.py` files when you reach the `/tests` directory.
- When checking assert_called_once_with calls make sure there are actual parameters being passed in. If there are none use assert_called_once() instead.
- Assertions are always expected value first and then actual value. Example `assert expected == actual`. Except in the case for None conditions. Then the assertion should be like `assert actual is None` or `assert actual is not None`.
- Assertions for boolean values should use `is` or `is not`.
- Assertions for non boolean values should use `==` or `!=`.
- Always use `pytest.mark.parametrize` for tests in which the same logic is being tested with different parameters. Only parametrize objects/values that are different for each iterration. Objects/values that are the same for each case should be defined inside the test method itself. Parametrized arguments should be passed in first to the test function, followed by any fixtures that are needed. Parametrized arguments should be type hinted with the type of the object being passed in.
- Each test should test a single method of the class being tested. If a test is testing multiple methods, it should be split into multiple tests.

### Integration Tests
When generating integration tests, always follow these general rules:
- Mock only the lowest level functionality, instead of the class methods themselves.
- Follow the existing code patterns in the tests/integration directory.

### Unit Tests
When generating unit tests, always follow these general rules:
- Mock the class methods themselves instead of the lowest level functionality.
- Follow the existing code patterns in the tests/unit directory.