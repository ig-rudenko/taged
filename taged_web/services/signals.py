from typing import Callable, Any

signal_callback = Callable[..., Any]


class _Signals:
    def __init__(self) -> None:
        self.signals: dict[str, list[signal_callback]] = {}

    def connect(self, signal: str, callback: signal_callback):
        if signal not in self.signals:
            self.signals[signal] = []
        self.signals[signal].append(callback)

    def emit(self, signal: str, **context):
        context["signal_name"] = signal
        if signal in self.signals:
            for callback in self.signals[signal]:
                callback(**context)

    def disconnect(self, signal: str, callback: signal_callback):
        if signal in self.signals:
            self.signals[signal].remove(callback)


signals = _Signals()


def register(*signals_names: str):
    def decorator(callback: signal_callback):
        for signal in signals_names:
            signals.connect(signal, callback)

        return callback

    return decorator
