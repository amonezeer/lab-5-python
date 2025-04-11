class Car:
    def __init__(self, make, model, year):
        self.make = make
        self.model = model
        self.year = year
        self.odometer_reading = 0

    def get_descriptive_name(self):
        long_name = str(self.year) + ' ' + self.make + ' ' + self.model
        return long_name.title()

    def read_odometer(self):
        print(f"Цей автомобіль проїхав {self.odometer_reading} кілометрів.")

    def update_odometer(self, km):
        if km >= self.odometer_reading:
            self.odometer_reading = km
        else:
            print("Ви не можете зменшити показники одометра!")

    def increment_odometer(self, kkm):
        self.odometer_reading += kkm

    def fill_petrol_tank(self):
        print("Цей автомобіль оснащений бензобаком.")


class Battery:
    def __init__(self, battery_size=75):
        self.battery_size = battery_size

    def describe_battery(self):
        print(f"Цей автомобіль має батарею на {self.battery_size} кВт·год.")

    def get_range(self):
        range_km = self.battery_size * 4
        print(f"Цей автомобіль може проїхати приблизно {range_km} кілометрів на повному заряді.")


class FastChargeBattery(Battery):
    def get_range(self):
        range_km = self.battery_size * 5
        print(f"Цей автомобіль із швидкою зарядкою може проїхати приблизно {range_km} кілометрів на повному заряді.")


class ElectricCar(Car):
    def __init__(self, make, model, year, battery_size=75, battery_type="standart"):
        super().__init__(make, model, year)

        if battery_type.lower() == "fastcharge":
            self.battery = FastChargeBattery(battery_size)
        else:
            self.battery = Battery(battery_size)

    def describe_battery(self):
        self.battery.describe_battery()

    def get_range(self):
        self.battery.get_range()

    def fill_petrol_tank(self):
        print("Цьому автомобілю не потрібен бензобак, це електромобiль!")


if __name__ == "__main__":
    # Звичайний автомобіль на бензинову двигунi
    my_new_car = Car('citroen', 'c3', 2018)
    print(my_new_car.get_descriptive_name())
    my_new_car.update_odometer(150)
    my_new_car.read_odometer()
    my_new_car.fill_petrol_tank()
    print()

    # Електромобіль зі стандартною батареєю
    my_tesla = ElectricCar('tesla', 'model s', 2018)
    print(my_tesla.get_descriptive_name())
    my_tesla.describe_battery()
    my_tesla.get_range()
    my_tesla.fill_petrol_tank()
    my_tesla.update_odometer(500)
    my_tesla.read_odometer()
    print()

    # Електромобіль з батареєю 100 кВт·год
    my_nissan = ElectricCar('nissan', 'leaf', 2023, battery_size=100)
    print(my_nissan.get_descriptive_name())
    my_nissan.describe_battery()
    my_nissan.get_range()
    print()

    # Електромобіль з батареєю швидкої зарядки 85 кВт·год
    my_bmw = ElectricCar('bmw', 'i4', 2023, battery_size=85, battery_type="fastcharge")
    print(my_bmw.get_descriptive_name())
    my_bmw.describe_battery()
    my_bmw.get_range()