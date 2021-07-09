import time


class Progress():
    def __init__(self, value, limit):
        self.value = value
        self.limit = limit

    def __get_progress_percent(self):
        divide = self.value / self.limit
        if divide != 0:
            return divide * 100
        return 0

    @staticmethod
    def __half_to_int(half: bool) -> int:
        if half:
            return 1
        else:
            return 0

    def to_string(self) -> str:
        percent = self.__get_progress_percent()
        text = str(int(percent)) + '% |'
        wholes = percent / 10
        for i in range(0, int(wholes)):
            text += '█'
        half = False
        if wholes != 10:
            half = percent % 10 != 0
            if half:
                text += '▌'
        for i in range(0, 10 - int(wholes) - self.__half_to_int(half)):
            text += ' '
        text += '|'
        return text
