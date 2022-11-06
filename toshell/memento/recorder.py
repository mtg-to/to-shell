from abc import ABC
from abc import abstractmethod
import time
from logging import Logger
from inspect import getmodule

logger = Logger("Recorder")

class Target(ABC):

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def delegate(self, other_self, *args, **kwargs):
        pass

class MethodTarget(Target):

    def __init__(self, func):
        self._func = func

    def name(self):
        return self._func.__name__

    def delegate(self, other_self, *args, **kwargs):
        return self._func(other_self, *args, **kwargs)

class SpoofTarget(Target):

    def __init__(self, name, res=None):
        self._name = name
        self._res = res

    def name(self):
        return self._name

    def delegate(self, other_self, *args, **kwargs):
        return self._res

class Capture(ABC):
    def __init__(self, name):
        self._name = name

    def name(self):
        return self._name

    @abstractmethod
    def extract(self, id, kwargs):
        pass


class TypeCapture(Capture):
    def __init__(self, name):
        super().__init__(name)

    def extract(self, kwargs):
        if self.name() in kwargs:
            return kwargs[self.name()].__name__
        raise ValueError(f"Expected a named parameter to be passed: {self.name()}")


class ReplayRecorder:

    def __init__(self, prefix="recording"):
        self.reset(prefix)

    def reset(self, prefix):
        self._mute = False
        t = time.strftime("%Y%m%d-%H%M%S")
        self._filename = f"{prefix}-{t}.py"
        self._objects = {}

    def start(self):
        self._flush("from toshell.memento.recorder import recorder")
        self._flush("recorder.mute()")

    def register_import(self, clz):
        _mod = getmodule(clz)
        _strimport = f"from {_mod.__name__} import {clz.__name__}"
        self._flush(_strimport)

    def record_command(self, assign="_", captures=None):
        """
        Records a shell command, with an assumption that all positional args are strings.

        The shell command recording will be in a form of:
        {assign} = {ctx}name({args}, **{captured kwargs})
        Params:
          * prefix - will be used to prefix the function name
          * assign - will be used as an assignment name of the function return
          * captures - a dictionary of "Capture" instances to transform non-string characters
        """

        def decorator(func):
            return self._target_wrapper(MethodTarget(func), assign, captures)

        return decorator

    def _target_wrapper(self, target, assign="_", captures=None):
        call = f"{assign}={{receiver}}.{target.name()}({{argstr}})"
        def wrapper(other_self, *args, **kwargs):
            _strargs = [f'"{a}"' for a in args]
            _strkwargs = self._process_kwargs(kwargs, captures) if captures else []
            _receiver = self._resolve_assignment(other_self)
            _argsstr = ",".join([*_strargs, *_strkwargs])
            res = target.delegate(other_self, *args, **kwargs)
            self._record_assignment(assign, res)
            self._flush(call.format(argstr=_argsstr, receiver=_receiver))
            return res
        return wrapper
        

    def record_init(self, assign):
        def decorator(func):
            call = f"{assign}={{initstr}}"

            def wrapper(other_self, *args, **kwargs):
                clazz = other_self.__class__.__name__
                self._flush(call.format(initstr=f"{clazz}()"))
                self._record_assignment(assign, other_self)
                return func(other_self, *args, **kwargs)

            return wrapper

        return decorator

    def spoof_command(self, func_name, assign="_", res=None):
       return self._target_wrapper(SpoofTarget(func_name, res=res), assign)

    def _process_kwargs(self, kwargs, captures):
        return [f"{capture.name()}={capture.extract(kwargs)}" for capture in captures]

    def _record_assignment(self, assign, obj):
        if assign != "_":
            self._objects[id(obj)] = assign

    def _resolve_assignment(self, obj):
        return self._objects.get(id(obj), "_")

    def mute(self):
        self._mute = True

    def _flush(self, line):
        if self._mute:
            return
        with open(self._filename, "a") as f:
            f.writelines([line, "\n"])


recorder = ReplayRecorder()
