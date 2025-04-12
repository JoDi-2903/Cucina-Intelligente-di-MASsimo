from enum import Enum


class RatingStrategy(Enum):
    MAX = 0,
    RANDOM = 1,

    @staticmethod
    def get_from_str(value: str):
        """
        Get the rating strategy from the given string value.
        :param value: The string value of the rating strategy.
        :return: The rating strategy if found, otherwise the default rating strategy (MAX).
        """
        for rating_strategy in RatingStrategy:
            if rating_strategy.name == value.upper():
                return rating_strategy

        return RatingStrategy.MAX
