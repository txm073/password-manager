from string import *
import shutil
import os, sys, stat
import base64
import numpy as np
import threading
from threading import Thread as _thread
from six.moves import input as raw_input
import time, timeit
import ctypes
import traceback
import pkg_resources
import functools
import inspect

chars = ascii_letters + digits + punctuation + " £"
char2int = {c: i for i, c in enumerate(chars, 1)}
int2char = {i: c for i, c in enumerate(chars, 1)}

# Errors
class AuthenticationError(Exception): ...
class InvalidFileException(Exception): ...
class ThreadStillAliveError(Exception): ...

# Decorators
def pipe(filename):
    def wrapper(fn):
        def inner(*args, **kwargs):
            value = fn(*args, **kwargs)
            with open(filename) as f:
                f.write(str(value))
            return value
        return inner
    return wrapper

def catch(exc=Exception, verbose=False):
    def wrapper(fn):
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except exc as e:
                if verbose:
                    print(e.__class__.__name__ + ": " + str(e))
        return inner
    return wrapper

def log(filename, exceptions=True):
    def wrapper(fn):
        def inner(*args, **kwargs):
            e = None
            try:
                value = fn(*args, **kwargs)
            except Exception as e:
                if not exceptions:
                    raise
            finally:
                with open(filename, "a") as f:
                    f.write(str(value) + "\n" + traceback.format_exc(e) if e else "")
                return value
        return inner
    return wrapper

def timed(fn):
    def inner(*args, **kwargs):
        start = timeit.default_timer()
        value = fn(*args, **kwargs)
        delta = timeit.default_timer() - start
        return value, delta
    return inner

def repeat(times):
    def wrapper(fn):
        def inner(*args, **kwargs):
            return [fn(*args, **kwargs) for i in range(times)]
        return inner
    return wrapper

def threaded(terminate_after=0):
    def wrapper(fn):    
        def inner(*args, **kwargs):
            thread = Thread(target=fn, args=args, kwargs=kwargs, group=None, 
                name=next(_gen), terminate_after=terminate_after, _timer=bool(terminate_after)
            )
            fn.thread = thread
            fn.get = thread._get
            return fn
        return inner
    return wrapper

def lazy_init(init):
    arg_names, def_kwargs = get_params(init)
    @functools.wraps(init)
    def inner(self, *args, **kwargs):
        def_kwargs.update(kwargs)
        for name, value in zip(arg_names[1:], args):
            try:
                setattr(self, name, value)
            except Exception as e:
                pass
        for name, value in def_kwargs.items():
            try:
                setattr(self, name, value)
            except Exception:
                pass
        init(self, *args, **kwargs)
    return inner

# Utility functions
def replace(string, a, b):
    if type(a) == list:
        for char in a:
            string = string.replace(char, b)
        return string
    else:
        return string.replace(a, b)

def get_params(fn):
    fn_args = []
    fn_kwargs = {}
    params = inspect.signature(fn)
    for param in str(params)[1:-1].split(", "):
        param = param.split("=", 1)
        if len(param) > 1:
            fn_kwargs[param[0]] = param[1]
        else:
            fn_args.append(param[0])
    return fn_args, fn_kwargs

def levenshtein(token1, token2):
    m, n = len(token1), len(token2)  
    matrix = np.zeros([m+1, n+1])
    for i in range(m):
        matrix[i][0] = i
    for i in range(n):
        matrix[0][i] = i
    a, b, c = 0, 0, 0
    for i in range(1, m+1):
        for j in range(1, n+1):
            if token1[i-1] == token2[j-1]:
                matrix[i][j] = matrix[i - 1][j - 1]
            else:
                a = matrix[i][j - 1]
                b = matrix[i - 1][j]
                c = matrix[i - 1][j - 1]
                if a <= b and a <= c:
                    matrix[i][j] = a + 1
                elif b <= a and b <= c:
                    matrix[i][j] = b + 1
                else:
                    matrix[i][j] = c + 1
    return matrix[m][n]

def most_likely(strings, target, threshold=5):
    scores = [levenshtein(string, target) for string in strings]
    return strings[scores.index(min(scores))] if min(scores) <= threshold else None

def encrypt(string=None, key=None, layers=1, _rec_level=0, verbose=False):    
    temp_key_ints = [char2int[char] for char in key]
    
    string = base64.b64encode(string.encode()).decode()

    key_ints = []
    for index, i in enumerate(temp_key_ints):
        if index % 2 == 0:
            key_ints.append(i ** 2)
        else:
            key_ints.append(i * 2)

    string_ints = []
    for index, integer in enumerate([char2int[char] for char in string], 1):
        shift = integer + index + sum(key_ints)
        if shift <= len(chars):
            string_ints.append(shift)
        else:
            if shift % len(chars) == 0:
                string_ints.append(len(chars))
            else:
                string_ints.append(shift % len(chars))

    enc = "".join([int2char[i] for i in string_ints])
    if verbose:
        print(f"Layer {_rec_level + 1} encryption: {enc}")
    if layers > 1:
        _rec_level += 1
        layers -= 1 
        enc = encrypt(enc, key, layers, _rec_level)    
    return enc

def decrypt(string=None, key=None, layers=1, _rec_level=0, verbose=False):    
    temp_key_ints = [char2int[char] for char in key]

    key_ints = []
    for index, i in enumerate(temp_key_ints):
        if index % 2 == 0:
            key_ints.append(i ** 2)
        else:
            key_ints.append(i * 2)

    string_ints = []
    for index, integer in enumerate([char2int[char] for char in string], 1):
        shift = integer - index - sum(key_ints)
        if shift > 0:
            string_ints.append(shift)
        else:
            if shift % len(chars) == 0:
                string_ints.append(len(chars))
            else:
                string_ints.append(shift % len(chars))

    msg = "".join([int2char[i] for i in string_ints])
    if verbose:
        print(f"Layer {layers} decryption: {msg}")
    msg = base64.b64decode(msg.encode()).decode()
    if layers > 1:
        _rec_level += 1
        layers -= 1
        msg = decrypt(msg, key, layers, _rec_level)    
    return msg

def lock():
    os.system("Rundll32.exe user32.dll,LockWorkStation")

def get_dependencies(package_name, tree=True, rlevel=1, pre=False):
    try:
        package = pkg_resources.working_set.by_key[package_name]
    except KeyError:
        return None
    deps = [re.split("[^A-Za-z0-9\- ]", str(r))[0] for r in package.requires()]
    if pre:
        return deps
    if rlevel == 1:
        if tree:
            print(package_name + ":" if deps else package_name)
        global global_deps 
        global_deps = []
    for dep in deps:
        output = ("  " * rlevel) + "- " + dep
        if tree:
            print(output + ":" if get_dependencies(dep, tree=tree, pre=True) else output)
        global_deps.extend(get_dependencies(dep, tree=tree, rlevel=rlevel+1))
        
    if rlevel != 1:
        return deps
    return list(set(global_deps))


class FilePreserver:    
    paused = False

    @lazy_init
    def __init__(self, path, writable=False):    
        self.run()

    @threaded(terminate_after=None)
    def run(self):
        folder = os.path.dirname(self.path)
        file = os.path.basename(self.path)
        if os.path.splitext(file)[1] == "db":
            database = True
        copies = []
        if not self.writable:
            with open(self.path, "rb") as f:
                initial = f.read()    
        while True:
            modified = False
            if len(copies) == 3:
                del copies[0]
            items = os.listdir(folder)                                                      
            try:
                with open(self.path, "rb") as f:
                    contents = f.read()
                if not self.writable:
                    if contents != initial:
                        modified = True
                        if self.paused:
                            initial = contents
                        continue
            except OSError:
                pass
            if file not in items or modified:
                if modified and not self.writable:
                    print(f"\nFile '{self.path}' has been modified, restoring previous version...")
                    with open(self.path, "wb") as f:
                        f.write(initial)
                else:
                    print(f"\nFile '{self.path}' has been deleted, restoring...")
                    with open(self.path, "wb") as f:
                        f.write(copies[-1])

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

# Custom classes
class ThreadReturnValue:
    def __init__(self, obj):
        self.obj = obj
        
    def __repr__(self):
        return f"<{self.__class__.__name__}: {repr(self.obj)}>" 

    def get(self):
        return self.obj

class ThreadInProgress: ...
class Thread(_thread):

    @lazy_init
    def __init__(self, target=None, args=(), 
                 kwargs={}, name=None, group=None, 
                 daemon=None, terminate_after=None, _timer=False
        ):
        #print(f"Initialising new thread with name '{name}' and target function '{target.__name__}'")
        super(Thread, self).__init__(
            target=target, args=args, kwargs=kwargs, name=name, group=group, daemon=daemon
        )
        self.return_value = None
        self.start()
             
    # Override run method
    def run(self):
        if self.terminate_after:
            @threaded(terminate_after=0)
            def _fn(thread_to_kill, delay):
                #print(f"Sleeping for {delay}")
                time.sleep(delay + 0.05)
                #print("Killing functional thread")
                thread_to_kill.stop()
                
            timer_thread = _fn(self, self.terminate_after)
            timer_thread.thread.stop()
        #print(f"Running function '{self.target.__name__}' in thread '{self.name}'")
        self.return_value = ThreadReturnValue(self.target(*self.args, **self.kwargs))

    def _get(self):
        if self.return_value:
            return self.return_value.get()
        return ThreadInProgress

    # Get ID of this thread
    def get_id(self):
        if hasattr(self, "_thread_id"):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
  
    # Kill this thread
    def stop(self, kill_all=False):
        thread_id = self.get_id()
        resp = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if resp > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            raise ThreadStillAliveError(
                "Thread cannot be stopped!"
            ) 
        if kill_all:
            os._exit(0)


def _input(msg=""):
    user_input = None
    try:
        user_input = input(msg)
    except KeyboardInterrupt:
        print()
    finally:
        return user_input


def _gen_n(n=1000000000000000):
    for i in range(n):
        yield i

_gen = _gen_n()

if __name__ == "__main__":    
    #pre = preserve_file(os.path.expandvars("C:\\Users\\$USERNAME\\master.rtf"))
    file = "D:\\Python\\Voice Assistant\\assistant\\security\\manager\\master.rtf"
    pre = FilePreserver(file, writable=False)
    print(f"Now protecting file '{file}'...")

    try:
        while True:
            command = _input("Enter a command: ")
            if command == "pause":
                print("File not protected")
                pre.pause()
            elif command == "resume":
                pre.resume()
                print("File is now protected")
            
    except KeyboardInterrupt:
        print("\nStopping thread:", pre.thread)
        pre.thread.stop()
