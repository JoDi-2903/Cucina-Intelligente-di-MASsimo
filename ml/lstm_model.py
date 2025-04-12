import os

import numpy as np
import pandas as pd
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential

from data_structures.config.config import Config
from data_structures.config.logging_config import machine_learning_logger

logger = machine_learning_logger


class LSTMModel:
    def __init__(self, pretrained_csv_path: str = None, pretrain_epochs: int = 10):
        """
        Initialize the LSTM model.
    
        The model takes two features per timestep (visitor count and satisfaction rating)
        and predicts two outputs:
          - visitor count for the next timestep,
          - satisfaction rating for the next timestep.
    
        This implementation includes data normalization to improve LSTM performance.
    
        Parameters:
            pretrained_csv_path (str): Optional path to a CSV file for pretraining.
                Expected CSV format: "step, customer_count, satisfaction_rating".
            pretrain_epochs (int): Number of epochs to use during the pretraining phase.
        """
        self.window_size = Config().run.window_size
        self.retrain_interval = Config().run.retrain_interval
        self.feature_dim = 2  # Two features: visitor count and satisfaction rating
        self.customer_count_history: dict[int, int] = {}  # To store visitor counts over time
        self.rating_history: dict[int, float] = {}  # To store satisfaction ratings over time
        
        # Parameters for data normalization
        self.max_customer_count = Config().restaurant.grid_width * Config().restaurant.grid_height
        self.min_customer_count = 0
        self.max_satisfaction_rating = float(Config().rating.rating_max)
        self.min_satisfaction_rating = float(Config().rating.rating_min)
    
        # Build the LSTM model with two LSTM layers and dropout for regularization.
        # The final Dense layer outputs 2 values: [visitor_count, rating]
        self.model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.window_size, self.feature_dim)),
            Dropout(0.2),
            LSTM(32),
            Dense(16, activation='relu'),
            Dense(2)
        ])
        self.model.compile(optimizer='adam', loss='mean_squared_error')
        logger.info("LSTM model initialized.")
    
        # If a pretraining CSV file is provided, perform pretraining using historical data.
        if Config().run.experienced_manager and pretrained_csv_path is not None:
            self.pretrain(pretrained_csv_path, pretrain_epochs)
    
    def normalize_data(self, customer_count: int, satisfaction_rating: float) -> tuple[float, float]:
        """
        Normalize the input data to the range [0, 1].
        
        Parameters:
            customer_count (int): Raw visitor count.
            satisfaction_rating (float): Raw satisfaction rating.
            
        Returns:
            tuple[float, float]: Normalized (customer_count, satisfaction_rating).
        """
        norm_count = (customer_count - self.min_customer_count) / (self.max_customer_count - self.min_customer_count)
        norm_rating = (satisfaction_rating - self.min_satisfaction_rating) / (self.max_satisfaction_rating - self.min_satisfaction_rating)
        
        # Clip values to ensure they stay in [0, 1] range
        norm_count = max(0.0, min(1.0, norm_count))
        norm_rating = max(0.0, min(1.0, norm_rating))
        
        return norm_count, norm_rating
    
    def denormalize_data(self, norm_customer_count: float, norm_satisfaction_rating: float) -> tuple[int, float]:
        """
        Denormalize data from [0, 1] range back to original scale.
        
        Parameters:
            norm_customer_count (float): Normalized visitor count (0-1).
            norm_satisfaction_rating (float): Normalized satisfaction rating (0-1).
            
        Returns:
            tuple[int, float]: (customer_count as int, satisfaction_rating as float).
        """
        customer_count = norm_customer_count * (self.max_customer_count - self.min_customer_count) + self.min_customer_count
        satisfaction_rating = norm_satisfaction_rating * (self.max_satisfaction_rating - self.min_satisfaction_rating) + self.min_satisfaction_rating
        
        # Round customer count to nearest integer
        customer_count_int = int(round(customer_count))
        
        return customer_count_int, satisfaction_rating

    def pretrain(self, csv_path: str, epochs: int = 10) -> None:
        """
        Pretrain the model using historical data from a CSV file.
    
        The CSV file is expected to have rows with format:
            "step, customer_count, satisfaction_rating".
        This method normalizes the data before training to improve model performance.
    
        Parameters:
            csv_path (str): Path to the CSV file containing pretraining data.
            epochs (int): Number of training epochs during pretraining.
        """
        try:
            # Load data from CSV. Assumes the first row is a header.
            data = np.loadtxt(csv_path, delimiter=',', skiprows=1)
        except Exception as e:
            logger.warning(f"Error loading pretraining data from {csv_path}: {e}")
            return
    
        # Sort the data by step (assumed to be the first column)
        data = data[np.argsort(data[:, 0])]
        
        # Extract features from columns 1 and 2: customer_count and satisfaction_rating
        raw_features = data[:, 1:3]  # shape: (num_data_points, 2)
        
        # Normalize the data
        normalized_features = np.zeros_like(raw_features, dtype=np.float32)
        for i in range(raw_features.shape[0]):
            normalized_features[i, 0], normalized_features[i, 1] = self.normalize_data(
                raw_features[i, 0], raw_features[i, 1]
            )
    
        # Create sliding windows for training
        num_samples = normalized_features.shape[0] - self.window_size
        if num_samples <= 0:
            logger.warning("Not enough data in CSV for pretraining.")
            return
    
        X, Y = [], []
        for i in range(num_samples):
            X.append(normalized_features[i : i + self.window_size])
            Y.append(normalized_features[i + self.window_size])
        X = np.array(X)
        Y = np.array(Y)
    
        logger.info(f"Starting pretraining with {num_samples} normalized samples for {epochs} epochs...")
        self.model.fit(X, Y, epochs=epochs, verbose=1)
        logger.info("Pretraining completed.")

    def forecast(self, n: int, first_step: bool = False) -> list[int]:
        """
        Forecast the visitor counts for the next n timesteps.
    
        This function normalizes input data before prediction and denormalizes
        the output to ensure proper scaling.
    
        Parameters:
            n (int): Number of future timesteps to forecast.
            first_step (bool): If True, enables forecasting immediately after pretraining
                without requiring history data. Default is False.
    
        Returns:
            List[int]: A list of predicted visitor counts for each of the next n timesteps.
        """
        # Check if we have enough historical data
        all_steps = sorted(self.customer_count_history.keys())

        # Handle first step prediction when history is not available yet
        if first_step and len(all_steps) < self.window_size:
            logger.info("Using pretrained model for initial forecast.")
            # Create synthetic input with average values
            input_seq = []

            # For the initial prediction, we use a balanced starting point
            # Using middle values from our expected ranges
            avg_count = (self.max_customer_count + self.min_customer_count) / 2
            avg_rating = (self.max_satisfaction_rating + self.min_satisfaction_rating) / 2

            # Normalize these average values
            norm_count, norm_rating = self.normalize_data(avg_count, avg_rating)

            # Create a sequence of the same values to start with
            for _ in range(self.window_size):
                input_seq.append([norm_count, norm_rating])
        else:
            # Regular case: we need sufficient history
            if len(all_steps) < self.window_size:
                logger.warning("Not enough data to make a forecast.")
                return []

            # Build the initial window with normalized values from actual history
            recent_steps = all_steps[-self.window_size:]
            input_seq = []
            for s in recent_steps:
                if s not in self.rating_history:
                    logger.warning(f"Missing rating for timestep {s}, cannot forecast.")
                    return []
                # Normalize the input data
                norm_count, norm_rating = self.normalize_data(
                    self.customer_count_history[s], 
                    self.rating_history[s]
                )
                input_seq.append([norm_count, norm_rating])
    
        # Prepare input data with shape (1, window_size, feature_dim)
        input_data = np.array([input_seq])
        forecasted_counts = []
    
        # Iteratively forecast n timesteps
        for _ in range(n):
            prediction = self.model.predict(input_data, verbose=0)
            norm_next_count = prediction[0, 0]
            norm_next_rating = prediction[0, 1]
            
            # Denormalize the predictions
            next_visitor_count, next_rating = self.denormalize_data(
                norm_next_count, 
                norm_next_rating
            )
            
            # Ensure predictions are within valid ranges
            next_visitor_count = max(0, next_visitor_count)  # No negative visitors
            next_rating = max(self.min_satisfaction_rating, 
                             min(next_rating, self.max_satisfaction_rating))
            
            forecasted_counts.append(next_visitor_count)
    
            # Update input sequence: remove oldest element and append new prediction
            norm_count, norm_rating = self.normalize_data(next_visitor_count, next_rating)
            input_seq = input_seq[1:] + [[norm_count, norm_rating]]
            input_data = np.array([input_seq])
    
        logger.info(f"Predicted visitor counts for next {n} timesteps: {forecasted_counts}")
        return forecasted_counts

    def update(self, last_step: int, customer_count: int, satisfaction_rating: float) -> None:
        """
        Update the model with new observations and perform online training.
    
        Data is normalized before training to improve model performance.
    
        Parameters:
            last_step (int): Latest timestep index.
            customer_count (int): Observed visitor count.
            satisfaction_rating (float): Observed satisfaction rating.
        
        The method stores both counts and ratings in dictionaries keyed by last_step.
        Once enough data points (window_size + 1) exist, a training batch is constructed using the most recent window_size entries for both counts and ratings.

        Note: Online learning in machine learning refers to a training paradigm where the model learns incrementally from data as it becomes available, 
            rather than relying on a pre-collected and fixed dataset (as in offline or batch learning). In the context of Long Short-Term Memory (LSTM) networks,
            online learning becomes particularly relevant for applications involving streaming or sequential data, such as time series forecasting.
        """
        # Store the raw data in history for easier retrieval
        self.customer_count_history[last_step] = customer_count
        self.rating_history[last_step] = satisfaction_rating
    
        # Check if it is time for a new training, based on the interval specified in config
        if last_step % self.retrain_interval != 0:
            return
    
        # Check how many timesteps we have in total
        all_steps = sorted(self.customer_count_history.keys())
        if len(all_steps) < self.window_size + 1:
            # Not enough data to train
            return
    
        # Take only the last (window_size + 1) timesteps
        recent_steps = all_steps[-(self.window_size + 1):]
        # Separate the timesteps into input range and target step
        input_steps = recent_steps[:-1]
        target_step = recent_steps[-1]
    
        # Collect input features (visitor counts, ratings)
        input_seq = []
        for s in input_steps:
            if s not in self.rating_history:
                logger.warning(f"Missing rating for timestep {s}, skipping update.")
                return
            # Normalize input data
            norm_count, norm_rating = self.normalize_data(
                self.customer_count_history[s], 
                self.rating_history[s]
            )
            input_seq.append([norm_count, norm_rating])
    
        # Normalize target data
        norm_target_count, norm_target_rating = self.normalize_data(
            self.customer_count_history[target_step], 
            self.rating_history[target_step]
        )
    
        # Prepare training batch
        x_train = np.array([input_seq])  # Shape: (1, window_size, feature_dim)
        y_train = np.array([[norm_target_count, norm_target_rating]])
    
        # Train the model on the new batch
        loss = self.model.train_on_batch(x_train, y_train)
        logger.info(f"Model updated at step {last_step}. Training loss: {loss:.4f}")

    def save_training_data(self, last_step: int, customer_agents_count: int, satisfaction_rating: float, train_data_path: str = 'ml/train_data.csv') -> None:
        """
        Save the data created during the simulation run to a file for pretraining the LSTM.
        
        Parameters:
          - last_step: Index of the latest timestep for which real simulation data is available.
          - customer_agents_count: The number of customer agents in the restaurant
          - satisfaction_rating: The observed satisfaction rating

        The data is saved in a CSV file. With each function call, a new row is appended to the file.
        The file is created if it does not exist.
        """
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(train_data_path), exist_ok=True)

        # Create a DataFrame with the new data
        new_data = pd.DataFrame({
            'step': [last_step],
            'customer_count': [customer_agents_count],
            'satisfaction_rating': [satisfaction_rating]
        })

        # Append the new data to the CSV file
        if os.path.exists(train_data_path):
            new_data.to_csv(train_data_path, mode='a', header=False, index=False)
        else:
            new_data.to_csv(train_data_path, mode='w', header=True, index=False)
