from abc import ABC
from abc import abstractmethod
import time
from logging import Logger
from inspect import getmodule

logger = Logger("Recorder")


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
    def __init__(self):
        self.reset()

    def reset(self, prefix="recording"):
        self._mute = False
        t = time.strftime("%Y%m%d-%H%M%S")
        self._filename = f"{prefix}-{t}.py"
        self._objects = {}
        self._mute_in_recording()
        
    def _mute_in_recording(self):
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
            call = f"{assign}={{receiver}}.{func.__name__}({{argstr}})"

            def wrapper(other_self, *args, **kwargs):
                _strargs = [f'"{a}"' for a in args]
                _strkwargs = self._process_kwargs(kwargs, captures) if captures else []
                _receiver = self._resolve_assignment(other_self)
                _argsstr = ",".join([*_strargs, *_strkwargs])
                self._flush(call.format(argstr=_argsstr, receiver=_receiver))
                res = func(other_self, *args, **kwargs)
                self._record_assignment(assign, res)
                return res

            return wrapper

        return decorator

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
