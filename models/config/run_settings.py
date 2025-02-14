class RunSettings:
    """
    Class to store the run configuration of the simulation.
    """

    def __init__(self, config: dict[str, int] = None):
        """
        Initialize the run object with the passed configuration or default values.
        :param config: The configuration to initialize the object with.
        """
        if config is not None:
            self.__step_amount: int = config["step_amount"]
            self.__full_day_cycle_period: int = config["full_day_cycle_period"]
        else:
            raise ValueError("No default values for run settings available.")

    @property
    def step_amount(self) -> int:
        return self.__step_amount

    @property
    def full_day_cycle_period(self) -> int:
        return self.__full_day_cycle_period
