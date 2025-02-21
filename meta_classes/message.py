from abc import ABCMeta


class MessageMeta(ABCMeta):
    def __call__(cls, step: int, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.step = step
        return instance
