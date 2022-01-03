import sys

obj_dunders = [
    "__class__", "__dict__", "__module__", "__doc__", "__weakref__"
]

builtin = [
    "__builtins__", "__cached__", "__doc__", "__file__", 
    "__loader__", "__name__", "__package__", "__spec__"
]

def _dir(obj=None):
    return [attr for attr in dir(obj) if attr not in builtin + obj_dunders]

def classattrs(obj):
    return [attr for attr in obj.__dict__.keys() if attr not in builtin + obj_dunders]

def isbuiltin(class_):
    return hasattr(class_, "__dict__")

def get_attrs(obj, rlevel=0):
    if rlevel == 0:
        global attributes
        attributes = []
    attrs = _dir(obj)
    for attr_name in attrs:
        attr = getattr(obj, attr_name)
        if attr.__class__.__name__ == "type":
            attributes.extend(
                [f"{obj.__name__}.{attr_name}.{classattr}" for classattr in (classattrs(attr))]
            )
        attributes.append(f"{obj.__name__}.{attr_name}")
    if rlevel == 0:
        return attributes

def remove_whitespace(code):
    return "\n".join([line for line in code.split("\n") if len(line.replace(" ", ""))] + [""])

def get_indent_level(line, tab_size):
    spaces = 0
    for char in line:
        if char.isspace():
            spaces += 1
        else:
            break
    return spaces // tab_size

def find_class(code, class_, tab_size):
    indent_level = None
    start_line, end_line = 0, len(code.split("\n")) 
    declaration = f"class {class_}"
    for i, line in enumerate(code.split("\n")):
        if declaration in line:
            indent_level = get_indent_level(line, tab_size)
            start_line = i
        else:
            if indent_level is not None:
                if get_indent_level(line, tab_size) == indent_level:
                    end_line = i
                    break
    return "\n".join(code.split("\n")[start_line:end_line])

def find(code=None, py_file=None, fn=None, class_=None, tab_size=4):
    if code is None and py_file is not None:
        with open(py_file, "r") as f:
            code = f.read()
    indent_level = None
    declaration = f"def {fn}"
    code = remove_whitespace(code)
    if class_ is not None:
        code = find_class(code, class_, tab_size)
    start_line, end_line = 0, len(code.split("\n")) 
    for i, line in enumerate(code.split("\n")):
        if declaration in line:
            indent_level = get_indent_level(line, tab_size)
            start_line = i
        else:
            if indent_level is not None:
                if get_indent_level(line, tab_size) == indent_level:
                    end_line = i
                    break
    return "\n".join(code.split("\n")[start_line:end_line])

def get_code(file):
    def wrapper(fn):
        def inner(*args, **kwargs):
            full_name = fn.__qualname__.split(".")
            method = fn.__name__
            class_ = None
            if len(full_name) > 1:
                class_ = full_name[full_name.index(method) - 1]
            code = find(py_file=file, fn=method, class_=class_)
            return fn(*args, **kwargs), code
        return inner
    return wrapper



    