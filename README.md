# AstroGeeks Actuator Control
This repository contains the code to control various actuators of the AstroPlant kit and our custom Tec controller.

You can find more info about our project [here](http://astrogeeksgent.wordpress.com).

# Configure actuators
You can modify the configuration for the actuators in `config.json`.

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
To run the daemon, do:
```bash
./controld (port = 4130)
```
Example:
```bash
./controld 5555
```

# Control an actuator
To control an actuator, do:
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

# Crontab compatibility

Example:
```bash
@reboot sudo pigpiod
@reboot cd path-to-actuator-control && ./controld

# From 6:00 to 17:59
* 6-17 * * * cd path-to-actuator-control && ./control "Led.Blue" 20.0
* 6-17 * * * cd path-to-actuator-control && ./control "Led.Red" 80.0
* 6-17 * * * cd path-to-actuator-control && ./control "Led.FarRed" 80.0
* 6-17 * * * cd path-to-actuator-control && ./control "Fan" 1
* 6-17 * * * cd path-to-actuator-control && ./control "Temp" 25.0

# From 18:00 to 5:59
* 18-23,0-5 * * * cd path-to-actuator-control && ./control "Led.Blue" 10.0
* 18-23,0-5 * * * cd path-to-actuator-control && ./control "Led.Red" 40.0
* 18-23,0-5 * * * cd path-to-actuator-control && ./control "Led.FarRed" 40.0
* 18-23,0-5 * * * cd path-to-actuator-control && ./control "Fan" 1
* 18-23,0-5 * * * cd path-to-actuator-control && ./control "Temp" 15.0
```