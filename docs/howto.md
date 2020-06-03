##### Mareografie (1)

# When above — Alta e bassa marea — How-to

![«When above — Alta e bassa marea»](resources/photos/20200602_112612.jpg)

+ [**Hardware components**](#hardware-components)
+ [**Cable wiring**](#cable-wiring)
+ [**Raspberry Pi configuration: enabling SPI peripheral**](#raspberry-pi-configuration--enabling-spi-peripheral)
+ [**Raspberry Pi configuration: installing required packages**](#raspberry-pi-configuration--installing-required-packages)
+ [**Software installation and running**](#software-installation-and-running)

### Hardware components

Get the required hardware components:
| . | . |
| :---| :--- |
| ![Raspberry Pi 4 Model B](resources/hardware/raspberry_pi4_model_b.png) | 1 Raspberry Pi Model B single board computer (here a Raspberry Pi 4 Model B). |
| ![MAX7219 8x8 Dot Matrix MCU LED](resources/hardware/max7219_dot_matrix_module.png) | 1 MAX7219 8x8 Dot Matrix MCU LED module. |
| ![Jumper Wire Cable F2F](resources/hardware/jumper_wire_cable_f2f.png) | 5 Female to Female jumper wires. |

### Cable wiring

Connect the hardware components following this scheme:

| MAX7219 Dot Matrix LED Pin | Raspberry Pi Pin |
|:---| :---|
| **1** - VCC - +5V Power | **2** - 5V0 |
| **2** -GND - Ground | **6** - GND |
| **3** - DIN - Data In | **19** - GPIO 10 - MOSI |
| **4** - CS - Chip Select | **24** - GPIO 8 - SPI CE0 |
| **5** - CLK - Clock | **23** - GPIO 11 - SPI CLK |

![Cable wiring](resources/hardware/cable_wiring.png)

### Raspberry Pi configuration: enabling SPI peripheral

Turn on the Raspberry Pi SPI peripheral. The SPI peripheral is not turned on by default: to enable it, use the graphical tool *Raspberry Pi Configuration* (in *Menu > Preferences > Raspberry Pi Configuration*):

![Raspberry Pi SPI configuration](resources/hardware/spi_configuration_01.png)

Click the *OK* button. If prompted to reboot select *Yes* so that the changes will take effect:

![Raspberry Pi SPI configuration](resources/hardware/spi_configuration_02.png)

Alternatively, you can enable SPI peripheral by running the utility *raspi-config* in the command line:
```
sudo raspi-config
```

### Raspberry Pi configuration: installing required packages

*[**Pandas**](https://pandas.pydata.org/)* — a fast, powerful and flexible data analysis and manipulation tool — requires the installation of the following packages:
```
sudo apt install libatlas-base-dev
```

*[**Luma.LED_Matrix**](https://github.com/rm-hull/luma.led_matrix)* — a Python module to drive LED Matrices, 7-Segment Displays (MAX7219) and RGB NeoPixels (WS2812 / APA102) — requires the installation of the following packages:
```
sudo apt install libfreetype6-dev
sudo apt install libjpeg-dev
sudo apt install libopenjp2-7
sudo apt install libtiff5
```

### Software installation and running

Make a new directory, for GitHub projects:
```
mkdir ~/github_projects
cd ~/github_projects
```

Clone the project:
```
git clone https://github.com/antonio-viesti/mareografie.git
cd mareografie
```

Define and activate a Python virtual environment:
```
python3 -m venv ~/github_projects/mareografie/.mareografie
source ~/github_projects/mareografie/.mareografie/bin/activate
```

Install all required Python packages:
```
pip install --upgrade pip
pip install --upgrade setuptools
pip install --upgrade SPARQLWrapper
pip install --upgrade pandas
pip install --upgrade luma.led_matrix
```

Run some diagnostics on the LED panel:
```
python mareografie/led_panel/led_panel_drawings.py
```

Make sure you're connected to the internet, and run the application:
```
python mareografie/when_above.py
```

Enjoy!