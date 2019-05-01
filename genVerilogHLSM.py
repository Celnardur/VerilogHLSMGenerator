#!/usr/bin/env python3

import os
import json
import sys
import math

def regNotation(iSize):
	if iSize < 2:
		return ""

	return '[' + str(iSize - 1) + ':0]'

def finder(lList, strToFind):
	for index, string in enumerate(lList):
		if string == strToFind:
			return index


if __name__ == '__main__':
	strFilePath = sys.argv[1]

	if os.path.isfile(strFilePath):
		with open(strFilePath) as fshlsm:
			hlsm = json.load(fshlsm)
	else:
		print("File you entered doesn't exist.")

	states = hlsm["states"]
	internalRegisters = hlsm["internalRegisters"]
	module = hlsm["module"]

	registers = internalRegisters.copy()
	registers.update(module["output"])

	stages = {}
	ctrlSigs = {}
	for reg in registers:
		stages[reg] = []

	for state in states:
		for reg, equals in states[state]["actions"].items():
			if not equals in stages[reg]:
				stages[reg].append(equals)

	for reg in stages:
		ctrlSigs[reg] = []
		ctrlSigs[reg].append("en_" + str(reg))
		if len(stages[reg]) > 1:
			ctrlSigs[reg].append("s_" + str(reg))
			ctrlSigs[reg].append(str(math.ceil(math.log2(len(stages[reg])))))

	dconditions = {}
	count = 0

	for state in states:
		for condition in states[state]["transitions"]:
			if condition == 'goto' or condition == 'else':
				continue
			else:
				lcondition = condition.split()
				dconditions[condition] = lcondition[0] + '_flag' + str(count)
				count = count + 1

	print(json.dumps(stages, indent=4))
	print(json.dumps(ctrlSigs, indent=4))
	print(json.dumps(dconditions, indent=4))

	strProcessor = "module {}Processor (\n".format(module["name"])
	strProcessor += "\tinput clk,\n\tinput reset,\n"
	for item, value in module["input"].items():
		strProcessor += "\tinput {} {},\n".format(regNotation(value), item)
	for item, value in module["output"].items():
		strProcessor += "\toutput {} {},\n".format(regNotation(value), item)
	strProcessor += ");\n\n"

	for reg, value in ctrlSigs.items():
		strProcessor += "wire {};\n".format(value[0])
		if len(value) > 1:
			bits = math.ceil(math.log2(int(value[2])))
			strProcessor += "wire {} {};\n".format(regNotation(bits), value[1])

	for con, value in dconditions.items():
		strProcessor += "wire {};\n".format(value)

	modname = "{}Datapath".format(module["name"])
	strDatapath = "module " + modname + " (\n"
	strDatapath += "\tinput clk,\n"

	strProcessor += "\n{} {} (\n".format(modname, modname)
	strProcessor += "\t.clk(clk),\n"

	for reg in ctrlSigs:
		strDatapath += "\tinput " + ctrlSigs[reg][0] + ",\n"
		strProcessor += "\t.{0}({0}),\n".format(ctrlSigs[reg][0])
		if len(ctrlSigs[reg]) > 1:
			strDatapath += "\tinput " + regNotation(int(ctrlSigs[reg][2])) + " " + ctrlSigs[reg][1] + ",\n"
			strProcessor += "\t.{0}({0}),\n".format(ctrlSigs[reg][1])

	for reg in module["input"]:
		strDatapath += "\tinput " + regNotation(module["input"][reg]) + " " + reg + ",\n"
		strProcessor += "\t.{0}({0}),\n".format(reg)

	for reg in module["output"]:
		strDatapath += "\toutput reg " + regNotation(module["output"][reg]) + " " + reg + ",\n"
		strProcessor += "\t.{0}({0}),\n".format(reg)

	for con in dconditions:
		strDatapath += "\toutput " + dconditions[con] + ",\n"
		strProcessor += "\t.{0}({0}),\n".format(dconditions[con])

	strDatapath += ");\n"
	strProcessor += ");\n"

	strDatapath += "\n// Parameter Declarations\n"
	for param, value in hlsm["parameters"].items():
		strDatapath += "parameter {} = {}'d{};\n".format(param, value[0], value[1])

	strDatapath += "\n// Internal Registers\n"
	for reg, length in internalRegisters.items():
		strDatapath += "reg " + regNotation(length) + " " + reg + ";\n"

	strDatapath += "\n// Sequential Logic\n"
	for reg, options in stages.items():
		if len(options) == 0:
			continue
		strDatapath += "always @(posedge clk)\n"
		strDatapath += "\tif (" + ctrlSigs[reg][0] + ")\n"
		if len(options) == 1:
			strDatapath += "\t\t" + reg + " <= " + options[0] + ";\n"
		elif len(options) == 2:
			strDatapath += "\t\tif (" + ctrlSigs[reg][1] + ")\n"
			strDatapath += "\t\t\t" + reg + " <= " + options[1] + ";\n"
			strDatapath += "\t\telse\n"
			strDatapath += "\t\t\t" + reg + " <= " + options[0] + ";\n"
		else:
			strDatapath += "\t\tcase (" + ctrlSigs[reg][1] + ")\n"
			for index, equals in enumerate(options):
				strDatapath += "\t\t\t" + str(index) + ": " + equals + ";\n"
			strDatapath += "\t\tendcase\n"
		strDatapath += "\n"

	strDatapath += "\n// Combinational Logic\n"
	for con, flag in dconditions.items():
		strDatapath += "assgin {} = {};\n".format(flag, con)
	strDatapath += "endmodule\n"

	with open("{}.v".format(modname), "w+") as file:
		file.write(strDatapath)

	strController = "module " + module["name"] + "Controller (\n"
	strController += "\tinput clk,\n"
	strController += "\tinput reset,\n"

	strProcessor += "\n{0} {0} (\n".format(module["name"] + "Controller")
	strProcessor += "\t.{0}({0}),\n".format("clk")
	strProcessor += "\t.{0}({0}),\n".format("reset")


	for reg in ctrlSigs:
		strController += "\toutput reg " + ctrlSigs[reg][0] + ",\n"
		strProcessor += "\t.{0}({0}),\n".format(ctrlSigs[reg][0])
		if len(ctrlSigs[reg]) > 1:
			strController += "\toutput reg " + regNotation(int(ctrlSigs[reg][2])) + " " + ctrlSigs[reg][1] + ",\n"
			strProcessor += "\t.{0}({0}),\n".format(ctrlSigs[reg][1])

	for con in dconditions:
		strController += "\tinput " + dconditions[con] + ",\n"
		strProcessor += "\t.{0}({0}),\n".format(dconditions[con])

	strController += ");\n\n"
	strProcessor += ");\n"
	strProcessor += "endmodule\n"

	count = 0
	bits = math.ceil(math.log2(len(states)))
	for state in states:
		strController += "parameter {} = {}'d{};\n".format(state, bits, count)
		count += 1

	strController += "\nreg {} state, next_state;\n\n".format(regNotation(bits))

	strController += "always @(posedge clk)\n\tif (reset)\n"
	strController += "\t\tstate <= INIT;\n\telse\n\t\tstate <= next_state;\n\n"

	strController += "always @(*) begin\n"
	for reg, sigs in ctrlSigs.items():
		strController += "\t{} = 0;\n".format(sigs[0])
		if len(sigs) > 1:
			strController += "\t{} = 0;\n".format(sigs[1])

	strController += "\tnext_state = INIT;\n"
	strController += "\tcase (state)\n"

	for state, options in states.items():
		count = 0
		strController += "\t\t{}: begin\n".format(state)
		for reg, action in options["actions"].items():
			strController += "\t\t\t{} = 1;\n".format(ctrlSigs[reg][0])
			strController += "\t\t\t{} = {};\n".format(ctrlSigs[reg][1], finder(stages[reg], action))
		if len(options["transitions"]) == 1:
			strController += "\t\t\tnext_state = {};\n".format(options["transitions"]["goto"])
		else:
			for con, goto in options["transitions"].items():
				if con == "else":
					strController += "\t\t\telse\n"
				elif count == 0:
					strController += "\t\t\tif ({})\n".format(dconditions[con])
				else:
					strController += "\t\t\telse if ({})\n".format(dconditions[con])
				strController += "\t\t\t\tnext_state = {};\n".format(goto)
				count += 1

		strController += "\t\tend\n"

	strController += "\tendcase\n"
	strController += "end\n"
	strController += "endmodule\n"

	filename = "{}Controller.v".format(module["name"])

	with open(filename, "w+") as file:
		file.write(strController)


	filename = "{}Processor.v".format(module["name"])

	with open(filename, "w+") as file:
		file.write(strProcessor)


