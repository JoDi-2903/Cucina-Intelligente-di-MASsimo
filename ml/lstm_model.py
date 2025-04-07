import numpy as np
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

from data_structures.config.config import Config
from data_structures.config.logging_config import machine_learning_logger

logger = machine_learning_logger


class LSTMModel:
    def __init__(self):
        """
        Initialization method for the LSTM model.
        
        The model receives two features per timestep (visitor count and satisfaction score).
       
        Two internal histories are maintained:
           - self.customer_count_history: dictionary with keys as timestep indices and values as visitor counts
           - self.rating_history: dictionary with keys as timestep indices and values as ratings
        """
        self.window_size = Config().run.full_day_cycle_period - 1  # Number of timesteps to consider for training and prediction
        self.feature_dim = 2  # Two features: visitor count and rating
        self.customer_count_history: dict[int, int] = {}  # Dict to store visitor counts over time
        self.rating_history: dict[int, float] = {}  # Dict to store past ratings

        # Build a larger LSTM model with two LSTM layers and dropout for regularization
        self.model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.window_size, self.feature_dim)),
            Dropout(0.2),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        logger.info("LSTM model initialized.")

    def forecast(self, customer_added_history: list[int], rating_history: list[float], n: int) -> list[int]:
        """
        Forecast the visitor count for the next n time steps.
        For the forecast beyond the known history, the rating is held constant to the last observed rating.
        :param customer_added_history: List of past visitor counts (e.g., [t1: count1, t2: count2, ...])
        :param rating_history: List of past ratings (e.g., [t1: rating1, t2: rating2, ...])
        :param n: Number of time steps to forecast
        :return: List with n predicted visitor counts (e.g., [4, 5, 3, 4, ...])
        """
        # Ensure there are enough values for the input window.
        if len(customer_added_history) < self.window_size:
            logger.info(f"Insufficient history for prediction. Padding with first value. len(customer_added_history): {len(customer_added_history)}, window_size: {self.window_size}")
            pad_length = self.window_size - len(customer_added_history)
            # Use the first value for padding.
            pad_visitor = [customer_added_history[0]] * pad_length
            pad_rating = [rating_history[0]] * pad_length
            customer_added_history = pad_visitor + customer_added_history
            rating_history = pad_rating + rating_history
            logger.info(f"Padding input history with {pad_length} values.")
        else:
            # Use only the last window_size values.
            customer_added_history = customer_added_history[-self.window_size:]
            rating_history = rating_history[-self.window_size:]
            logger.info(f"Using the last {self.window_size} values for input. customer_added_history: {customer_added_history}, rating_history: {rating_history}")

        # Create the input array with shape (1, window_size, feature_dim)
        current_input = np.array([[[v, r] for v, r in zip(customer_added_history, rating_history)]])

        predictions = []

        # Iterative forecasting: Update the input sequence after each prediction
        for _ in range(n):
            pred = self.model.predict(current_input, verbose=0)
            pred_value = pred[0][0]
            predictions.append(int(round(pred_value)))

            # Dynamically update the rating value:
            # If enough values are available, extrapolate the trend of the last two ratings.
            if current_input.shape[1] > 1:
                last_rating = current_input[0, -1, 1]
                prev_rating = current_input[0, -2, 1]
                delta_rating = last_rating - prev_rating
                new_rating = last_rating + delta_rating
            else:
                new_rating = current_input[0, -1, 1]

            # New timestep with the predicted visitor count and the updated rating.
            new_step = np.array([[pred_value, new_rating]])
            # Shorten the current input sequence by the oldest timestep and append the new one.
            current_input = np.concatenate((current_input[:, 1:, :], new_step.reshape(1, 1, self.feature_dim)), axis=1)

        logger.info(f"Forecasted {n} steps ahead. Predicted visitor counts: {predictions}")
        return predictions

    def update(self, last_step: int, customer_count: int, satisfaction_rating: float) -> None:
        """
        Update the model with the actual visitor count and rating received in the latest timestep.

        Parameters:
          - last_step: Index of the latest timestep for which real simulation data is available.
          - customer_count: The observed visitor count
          - satisfaction_rating: The observed satisfaction rating

        The method stores both counts and ratings in dictionaries keyed by last_step.
        Once enough data points (window_size + 1) exist, a training batch is constructed using the most recent window_size entries for both counts and ratings.
        The model is trained on this single batch.

        Note: Online learning in machine learning refers to a training paradigm where the model learns incrementally from data as it becomes available, 
            rather than relying on a pre-collected and fixed dataset (as in offline or batch learning). In the context of Long Short-Term Memory (LSTM) networks,
            online learning becomes particularly relevant for applications involving streaming or sequential data, such as time series forecasting.
        """
        # Store observations in dictionaries
        self.customer_count_history[last_step] = customer_count
        self.rating_history[last_step] = satisfaction_rating

        # Check if it is time for a new training, based on the interval specified in config
        if last_step % Config().run.retrain_interval != 0:
            return

        # Check how many timesteps we have in total
        all_steps = sorted(self.customer_count_history.keys())
        if len(all_steps) < self.window_size-1:
            # Not enough data to train
            return

        # Take only the last (window_size-1) timesteps
        recent_steps = all_steps[-(self.window_size-1):]
        # Separate the timesteps into input range and target step
        input_steps = recent_steps[:-1]
        target_step = recent_steps[-1]

        # Collect input features (visitor counts, ratings)
        input_seq = []
        input_ratings = []
        for s in input_steps:
            if s not in self.rating_history:
                logger.warning(f"Missing rating for timestep {s}, skipping update.")
                return
            input_seq.append(self.customer_count_history[s])
            input_ratings.append(self.rating_history[s])

        # Prepare training batch
        x_train = np.array([[[cnt, rt] for cnt, rt in zip(input_seq, input_ratings)]])
        y_train = np.array([[self.customer_count_history[target_step]]])

        # Train the model on the new batch
        loss = self.model.train_on_batch(x_train, y_train)
        logger.info(f"Model updated at step {last_step}. Training loss: {loss:.4f}")
