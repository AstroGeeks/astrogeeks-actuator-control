# AstroGeeks Actuator Control
This repository contains the code to control various actuators of the AstroPlant kit and our custom Tec controller.

More info about our project can be found [here](http://astrogeeksgent.wordpress.com).

# Configure actuators
The configuration for the actuators can be modified in `config.json`.

For example, a basic configuration is as follows:
```json
{
    "actuators": [
        { "className": "Led", "name": "Led.Blue", "pin": 24 },
        { "className": "Led", "name": "Led.Red", "pin": 25 },
        { "className": "Led", "name": "Led.FarRed", "pin": 18 },
        { "className": "Fan", "name": "Fan", "pin": 20 },
        { "className": "Fan", "name": "Fan", "pin": 21 }
    ]
}
```
If you would like to use our custom Tec controller, the configuration is as follows:
```json
{
    "actuators": [
        { "className": "Led", "name": "Led.Blue", "pin": 24 },
        { "className": "Led", "name": "Led.Red", "pin": 25 },
        { "className": "Led", "name": "Led.FarRed", "pin": 18 },
        { "className": "Fan", "name": "Fan", "pin": 20 },
        { "className": "Fan", "name": "Fan", "pin": 21 },
        { "className": "Tec", "name": "Temp", "pin": 17 }
    ]
}
```

# Run the daemon
To run the daemon, perform:
```bash
./controld (port = 4130)
```
Example:
```bash
./controld 5555
```

# Control an actuator
To control an actuator, perform:
```bash
./control [name] [target] (port = 4130)
```
Example:
```bash
./control "Led.Blue" 60.0 5555
```


# Supported actuators

## Leds
Example:
```json
{ "className": "Led", "name": "Led.Blue", "pin": 24 }
```

## Fans
Example:
```json
{ "className": "Fan", "name": "Fan", "pin": 20 }
```

## Thermoelectric Coolers
Example:
```json
{ "className": "Tec", "name": "Temp", "pin": 17 }
```

