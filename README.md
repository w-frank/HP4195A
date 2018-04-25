# HP4195A Reader

A basic program for connecting to and interfacing with a HP4195A Network/Spectrum Analyser.

## Requirements

### Hardware
- HP4195A Network/Spectrum Analyser
- Prologix GPIB-ETHERNET (GPIB-LAN) Controller 1.2

### Software
- Python 3.0 +
- pyqt5
- telnetlib
- numpy
- matplotlib

### Supporting Documents
- [4195A-4395A GPIB Command Correspondence Table](http://www.tentech.ca/downloads/hardware/HP4195A/4195A-4395A%20GPIB%20Command%20Correspondance.pdf)
- [4195A Network/Spectrum Analyser Operation Manual](https://www.keysight.com/upload/cmc_upload/All/04195_90000_final.pdf)
- [Prologix GPIB-ETHERNET Controller User Manual](http://prologix.biz/downloads/PrologixGpibEthernetManual.pdf)

### Installing

To run the program install the dependencies as specified above using pip, conda or a similar package management system. Then clone this repository, navigate to the project directory in a command terminal and type

```python
python hp4195a_reader.py
```

The software can also be built into an executable with cx_Freeze. From the project directory run the following command in a terminal window

```python
python setup.py build
```

### Authors

* [Will Frank](https://github.com/w-frank)

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
