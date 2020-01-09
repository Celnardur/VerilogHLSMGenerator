# VerilogHlsmGenerator

This is a python script that makes it easier to make Verilog HLSMs.
It takes a json file that represents the HLSM in a easy to read and write format
and compiles it into Verilog modules that implement the HLSM.

## Installation

Just clone the repository to get the script. 

```bash
git clone https://github.com/Celnardur/VerilogHLSMGenerator.git
```

## Usage

To use the script, you make a json file that represent your HLSM then run the 
script like this with your json HLSM as the first argument. 
There are no additional command line arguments or options. 

```bash
./genVerilogHLSM.py myHLSM.json
```

This creates three verilog modules that implement this max finder. 
The Processor is the top level module and the Controller and Datapath implement
the HLSM.

I provided an example json file that represents a HLSM which finds the max value in 
a ram/rom module that can be wired to this generated module. 
You can run the example like this. 

```bash
./genVerilogHLSM.py maxFinderHLSM.json
```

## Contributing

I'm no longer working on this project so if anyone wants to improve or take over 
this project just contact me and I'll give you permissions to this repository.

## License
MIT

