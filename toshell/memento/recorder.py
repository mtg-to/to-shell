import time

class ReplayRecorder:

    def __init__(self):
        t = time.strftime("%Y%m%d-%H%M%S")
        self._filename = f"recording-{t}.py"
    
    def _flush(self, line):
        with open(self._filename, "a") as f:
            f.writelines([line, "\n"])