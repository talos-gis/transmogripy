# Transmogripy
## About
Transmogripy is a tool to convert short pascal scripts to python. It is originally meant to convert TaLoS scripts but can be easily adapted to many other environments.
## Requirements
Transmogripy is intentionally meant to be run in bare-bones environments, so the only requirements are python >= 3.6, it can even run in embeddable systems like QGIS's python environment.
### On Numpy
numpy is not a requirement, and is not even used. However, numpy might appear in the output script. This can be prevented by explicitly setting the `allow_numpy` parameter to `False`.
## Usage
The main function is the `convert` function.
```python
from transmogripy import convert

print(convert("""
var
   a: integer;
begin
   str := GetVal(Sym[j], 'Name') + ':' + IntToStr(Count[j]);
   a := 10; { do something
   also this}
   (* repeat until loop execution *)
   repeat
      writeln('repeat until loop execution: ', a);
      a := a + log10(12);
      l := floattoint(12.5);
   until a = 20;
end
"""
))
```
prints:
```text
"""
this script was automatically converted from pascal using transmogripy v...
"""

from talos import *
import math


def main():
   str = GetVal(Sym[j], 'Name') + ':' + str(count[j])
   a = 10  # do something
   # also this
   # repeat until loop execution
   while True:
      writeln('repeat until loop execution: ', a)
      a = a + math.log10(12)
      l = int(12.5)
      if a == 20: break
```
### Behaviour of `Result :=`
There are many different ways to handle pascal's `Result:=` code, and can be set with `convert`'s `result_behaviour` parameter:
* `"variable"`: a temporary variable `__Return__` will be created and only returned at the end of the script
* `"return"`: `Result:=` will be converted to `return` and a check for an early return will not be made.
* `"warn"`: as `"return"`, except a warning will be issued if an early return is detected
* `"try"` (default): as `"warn"`, but if an early warning is detected, the conversion will be re-tried with the `"variable"` option
### Comments and inline comments
The conversion attempts to convert comments, however, all inline comments (comments that have code after them in the same line) will be removed:
```pascal
var
    a: integer;
begin
    a := 0;
    Result := 0;
    while a <> 10 do {end of line comment}
    begin
        Result := Result {inline comment} + a;
        a := a+1; // end-of line comment
    end;
end
```
converts to
```python
"""
this script was automatically converted from pascal using transmogripy v...
"""

from talos import *


def main():
    a = 0
    __Return__ = 0
    while a != 10:  # end of line comment
        __Return__ = __Return__  + a
        a = a+1  # end-of line comment
    return __Return__
```
This behaviour can be changed with the `remove_inline_comments` parameter, setting it to `False` will instead raise an exception when an inline comment is encountered 
### Imports, headers, and segments
Some pascal function, like `log`, require python libraries to be imported. Transmorgopy automatically adds libraries that are referenced in the converted code.
```pascal
var
    a: integer;

begin
    a := 0;
    Result := 0;
    while a <> 10 do
    begin
        Result := Result + log10(a);
        a := a+1;
    end;
end
```
converts to
```python
"""
this script was automatically converted from pascal using transmogripy v...
"""

from talos import *
import math


def main():
    a = 0
    __Return__ = 0
    while a != 10:
        __Return__ = __Return__ + math.log10(a)
        a = a+1
    return __Return__
```

In addition, additional lines can be added before/after the converted code using the `pre_words`/`post_words` parameters. (note: `pre_words`'s default is`(from talos import *,)`, resulting in the `from talos import *` line)
### Code checking
By default, Transmogripy checks the syntax of the output script, and issues a warning if any errors are found. This can be changed by setting the `check_syntax` parameter to `False`.
### Not Supported
The following Pascal/Delphi features are not supported and will raise an error:
* pre-compiler directives (`foo({$IFDEF bar}bar{$ENDIF})`)
* `goto` statements (`goto foo`)
* all clauses and keywords (if/while/etc...) must be in lowercase (`While`)
* `else if` -> `elif` is only supported if `else` and `if` are on the same line 
    * in general, only properly formatted scripts are supported