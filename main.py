from models import restaurant_model

model = restaurant_model.RestaurantModel()

while model.running and model.steps < 100:
    model.step()
