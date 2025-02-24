import logging
import os
from datetime import datetime as dt

# Set the SINGLE_FILE flag to True if you want to log all loggers to a single file
SINGLE_FILE = False

# Ensure the log directory exists
log_directory = os.path.join("log")
if not os.path.exists(log_directory):
    os.makedirs(log_directory)


def setup_logger(name):
    """Function to setup as many loggers as you want"""

    # Create a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler
    file_handler = logging.FileHandler(
        os.path.join(log_directory,
                     f"{dt.now().strftime('%Y%m%d_%H%M%S')}.log" if SINGLE_FILE
                     else f"{dt.now().strftime('%Y%m%d_%H%M%S')}_{name}.log")
    )
    file_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the file handler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s") if SINGLE_FILE \
        else logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    # Disable propagation to the root logger
    logger.propagate = False

    return logger


# Create loggers for each module
customer_logger = setup_logger("customer")
service_logger = setup_logger("service")
manager_logger = setup_logger("manager")
restaurant_logger = setup_logger("restaurant")
route_logger = setup_logger("route")
machine_learning_logger = setup_logger("machine_learning")
