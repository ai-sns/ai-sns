# filename: get_weather.py
def get_weather(city):
    city = f"The City:{city}"
    temperature = "25°C"
    description = "Clear Sky"
    print(f"Weather in {city}:")
    print(f"Temperature: {temperature}")
    print(f"Description: {description}")
    return city, temperature, description

#city, temperature, description = get_weather("上海")

#if __name__ == "__main__":
#   get_weather("Shanghai")