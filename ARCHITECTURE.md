# EZT Template Engine Architecture

This document provides a deep technical explanation of how the EZT (EaZy Templating) engine works internally. Understanding these concepts is essential for maintaining and extending ezt.py.

## Overview

EZT is a two-phase template engine:

1. **Parsing Phase** (`_parse()`): Reads template text and produces a _program_
2. **Execution Phase** (`_execute()`): Runs the program against data to produce output

This separation allows templates to be parsed once and executed multiple times with different data.

## Core Concepts

### The Program

A **program** is the compiled intermediate representation of a template. It is a flat list containing:

- **Strings**: Literal template text to be written to output
- **Tuples**: Instruction tuples with format: `(function, arguments, filename, line_number)`

Example program structure:
```python
[
    'Hello ',
    (_cmd_print, (transforms, valref), 'template.ezt', 5),
    '\n',
    (_cmd_for, (args, true_section, else_section), 'template.ezt', 7),
    'Name: ',
    (_cmd_print, (transforms, valref), 'template.ezt', 8),
    '\n',
]
```

During execution, strings are written directly to output, and tuples are unpacked and their functions invoked.

### Value References (valref)

A **value reference** (or valref) is a 3-tuple: `(refname, start, rest)`

It represents a dotted reference path like `person.address.city` in an optimized form for fast runtime lookup:

- `refname`: The original full reference string (for error messages)
- `start`: The first component in the path (or the literal string if it's a constant)
- `rest`: Remaining components as a list (or `None` if it's a string constant)

Example transformations:
- Input: `"person.address.city"` → Output: `('person.address.city', 'person', ['address', 'city'])`
- Input: `"hardcoded text"` → Output: `(None, 'hardcoded text', None)`

### Transforms (Format Specifiers)

A **transform** is a formatting function applied to values during printing. Multiple transforms can be chained:

- `FORMAT_RAW`: No transformation
- `FORMAT_HTML`: Escape for HTML
- `FORMAT_XML`: Escape for XML
- `FORMAT_JS`: Escape for JavaScript
- `FORMAT_URL`: URL-encode

Transforms are stored in a stack (`printers`) during parsing to handle nested `[format]` blocks. Each transform is a callable that takes a value and returns an escaped string.

## Parsing Phase

The parsing phase transforms template text into a program using a regex-based lexer and a stack-based parser for nested block structures.

### Lexical Analysis

The regex `_re_parse` splits template text into tokens:

```python
(\r?\n)           # Group 1: Newline
|
\[(%s(?: +%s)*)\] # Group 2: Directive like [command arg1 arg2]
|
(\[\[\])          # Group 3: Literal [[ (escaped bracket)
|
\[#[^\]]*\]       # Comment (dropped, not grouped)
```

When split, this produces a flat list: `[TEXT, NEWLINE, TEXT, DIRECTIVE, TEXT, BRACKET, ...]`

The parse loop processes these tokens by their position modulo 4:
- Position 0 (mod 4): TEXT
- Position 1 (mod 4): NEWLINE
- Position 2 (mod 4): DIRECTIVE (not directly used; extracted from captured group 2)
- Position 3 (mod 4): BRACKET

### Directive Processing

Three main directive categories are recognized:

#### **Block Directives**: `[if-any]`, `[for]`, `[is]`, `[define]`, `[format]`

   These directives open a scope that must be closed with `[end]`. The parser uses a stack to track open blocks:
   ```python
   stack = [
       [cmd, idx, args, true_section, line_number],  # Per block
       ...
   ]
   ```
   
   When a block directive is encountered:
   1. Extract and validate arguments
   2. Prepare value references for arguments
   3. Push `[cmd, current_program_index, prepared_args, None, line_number]` onto stack
   4. Continue parsing; subsequent instructions are added to the program
   
   When `[else]` is encountered:
   1. Pop the stack frame and capture everything added since the block directive as `true_section`
   2. Update the stack frame to store this section
   3. Continue parsing; subsequent instructions will become the `else_section`
   
   When `[end]` is encountered:
   1. Pop the stack frame
   2. Capture everything since the last `[else]` (or since the block opened) as the section to execute
   3. Generate a command tuple: `(function_for_cmd, (prepared_args, true_section, else_section), filename, line_number)`
   4. Replace the placeholder in the program at `idx` with this tuple
   Special case for `[format]`: pop the printer stack instead

#### **Leaf Directives**: `[include]`, `[insertfile]`, `[if-any]`, Print commands
   These are processed immediately:
   - `[if-any]`: Similar to block directives but stores condition references instead of processed args
   - `[include]` with dynamic filename: Creates a runtime command tuple
   - `[include]` with static filename: Parse and inline the included template at parse time
   - Print commands: Arguments are prepared references and wrapped in `_cmd_print` or `_cmd_subst` tuples

#### **Special Directives**: `[else]`, `[end]`
   These are handled in conjunction with block directives (see above).

### Whitespace Compression

If `compress_whitespace` is enabled:
- Multiple spaces/tabs within a line become a single space
- Newlines preceded by whitespace collapse into a single `\n`

This prevents template formatting from affecting output (common in web templates).

### Reference Preparation (`_prepare_ref`)

Before storing references, they are "prepared" by `_prepare_ref()` which:
- **Detects string constants**: If the reference starts with `"`, extract the literal string
- **Splits dotted references**: `person.address.city` → `['person', 'address', 'city']`
- **Handles include arguments**: References like `arg0`, `arg1` are resolved through the `file_args` list passed from parent includes
- **Detects for-loop scoping**: For each prefix of the dotted path (from longest to shortest), check if it's an active for-loop variable name
  If found, the reference is scoped to that loop: return the original refname, the loop var, and remaining path components

Example: In `[for items][is item.name "Bob"][end]`, the reference `item.name` is prepared as `('item.name', 'item', ['name'])` with `item` recognized as a for-loop variable.

## Execution Phase

The execution phase runs the program against data and writes output to a file object.

### Context (`_context`)

The execution context tracks:
- `data`: The root data object passed to `generate()`
- `for_index`: Dict mapping for-loop variable names to `[items, current_index]`
- `defines`: Dict mapping variable names to defined values (set by `[define]`)

### Program Execution (`_execute`)

The executor is a simple loop:
```python
for step in program:
    if isinstance(step, str):
        fp.write(step)
    else:
        function, arguments, filename, line_number = step
        function(arguments, fp, ctx, filename, line_number)
```

String steps are written directly to output. Tuple steps are unpacked and their handler function is called with the parsed arguments.

### Value Resolution (`_get_value`)

Given a prepared valref, `_get_value()` performs a namespace lookup with precedence:
1. **For-loop scope**: Check if `start` is in `ctx.for_index`
   If yes, get the current item from the loop: `items[current_index]`
2. **Defined variables**: Check if `start` is in `ctx.defines`
   If yes, use the defined value
3. **Data attributes**: Check if `ctx.data` has an attribute named `start`
   If yes, get the attribute
4. **Error**: Raise `UnknownReference`

Once the starting object is obtained, the algorithm walks the remaining components:
```python
for attr in rest:
    ob = getattr(ob, attr)  # May raise AttributeError
```

Finally, type conversion:
- Numeric types (`int`, `long`, `float`) → Convert to string
- `None` → Return empty string
- Everything else → Return as-is (string or sequence for iteration)

### Command Handlers

Each directive has a handler method prefixed with `_cmd_`:

- `_cmd_print(transforms, valref)`: Resolves the valref, applies transforms in sequence, and writes to output. Handles stream objects (files) by reading chunks and transforming them.
- `_cmd_subst(transforms, valref, args)`: Resolves a format string (valref) containing numbered placeholders like `%1`, `%2`, etc. Replaces them with corresponding arg values (transformed) and writes output.
- `_cmd_for(valref, unused, section)`: Resolves valref to a sequence, registers it in `for_index`, and executes the section once per item, incrementing the index.
- `_cmd_define(name, unused, section)`: Executes the section into a `StringIO` buffer, captures the result, and stores it in `defines`.
- `_cmd_if_any(valrefs, true_section, false_section)`: Checks if any valref resolves to a truthy value. Executes the appropriate section.
- `_cmd_if_index(valref_value_pair, true_section, false_section)`: Queries the for-loop index for a variable and evaluates against index predicates: `even`, `odd`, `first`, `last`, or a specific index number.
- `_cmd_is(left_ref, right_ref, true_section, false_section)`: Case-insensitive string comparison between two resolved references.
- `_cmd_include(valref, reader, printer)`: Dynamically parses and executes an included template file (passed via the reader) with the current context.
- `_cmd_insertfile(valref, reader, printer)`: Reads a raw file and inserts its text directly without parsing.

## Key Design Patterns

### Lazy Preparation of References

References are prepared at parse time (`_prepare_ref`) but resolved at execution time (`_get_value`). This allows:
- For-loop variables to be recognized early (by name)
- Template data objects to be arbitrary (not pre-defined)
- Same template to work with different data shapes

### Stack-Based Block Management

Nested blocks are managed by a stack during parsing:
- Opening a block: Push `[cmd, index, args, None, line_number]`
- Encountering `[else]`: Capture current program contents as `true_section`
- Encountering `[end]`: Capture final section, create command tuple, replace placeholder at original index

This allows arbitrary nesting and proper `else`/`end` matching without recursive parsing.

### Format Stack for Nested Transforms

Format specifiers are nested via a printer stack:
- `[format html][format js]...[end][end]` → Stacked transforms applied left-to-right
- Each `[format]` block pushes/pops from the printer stack
- Leaf directives use the top printer in the stack

### Single-Pass Execution

The program is executed in a single pass: no graph traversal, no preprocessing. Sections (true/else branches) are only executed when needed, reducing memory and improving efficiency.

## Error Handling

- Errors during parsing (syntax errors) are caught immediately with filename and line number information.
- Errors during execution (reference resolution, type errors) also include filename and line number from the directive that caused them, enabling precise debugging of template issues.
- Errors inherit from `EZTException` which formats them with file/line context for user-friendly output.

## Future Considerations

- **Caching**: Programs could be cached by template filename to avoid reparsing
- **Analysis**: Static analysis could validate references before execution
- **Debugging**: Step-through debugging could be added by instrumentation
- **Performance**: Bytecode compilation or AST optimization could improve execution speed
