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
            self.__window_size: int = config["window_size"]
            self.__retrain_interval: int = config["retrain_interval"]
            self.__pretrain_epochs: int = config["pretrain_epochs"]
            self.__use_heuristic_for_first_step_prediction: bool = bool(config["use_heuristic_for_first_step_prediction"])
            self.__overwrite_lstm_training_dataset: bool = bool(config["overwrite_lstm_training_dataset"])
            self.__endless_mode: bool = bool(config["endless_mode"])
            self.__reject_unservable_customers: bool = bool(config["reject_unservable_customers"])
            self.__clear_old_logs: bool = bool(config["clear_old_logs"])
        else:
            raise ValueError("No default values for run settings available.")

    @property
    def step_amount(self) -> int:
        return self.__step_amount

    @property
    def full_day_cycle_period(self) -> int:
        return self.__full_day_cycle_period

    @property
    def window_size(self) -> int:
        return self.__window_size

    @property
    def retrain_interval(self) -> int:
        return self.__retrain_interval

    @property
    def pretrain_epochs(self) -> int:
        return self.__pretrain_epochs

    @property
    def use_heuristic_for_first_step_prediction(self) -> bool:
        return self.__use_heuristic_for_first_step_prediction

    @property
    def overwrite_lstm_training_dataset(self) -> bool:
        return self.__overwrite_lstm_training_dataset

    @property
    def endless_mode(self) -> bool:
        return self.__endless_mode

    @property
    def reject_unservable_customers(self) -> bool:
        return self.__reject_unservable_customers

    @property
    def clear_old_logs(self) -> bool:
        return self.__clear_old_logs
