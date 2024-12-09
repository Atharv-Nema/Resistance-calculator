# Resistance Calculator

This is a tool that allows users to build a circuit consisting of multiple resistors and a battery and calculates various features of the circuit, including the net resistance, the current through individual wires, and the voltage at every node. This is
especially useful for physics students at school and university.

## Features

- **Zero resistance wires**: Allows for zero resistance wires to be connected and treats them as such, i.e. the algorithm does not treat zero resistances as extremely small resistances. Instead, they are treated as **real zeros**, leading to higher precision. For example, the voltages of two nodes connected by a zero resistance wire are guaranteed to be equal.
- **Works for any well behaved circuit**: No matter how complicated the circuit is, if
a single solution exists, the algorithm is guaranteed to find it.
- **User-Friendly Interface**: The tool comes with a simple user interface built in pygame that allows users to build the circuit interactively.
- **Undefined current and infinite current detection**: The algorithm can detect whether the current in a wire is infinite or undefined.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)

## Installation

1. **Clone the Repository**:

2. **Install a python virtual environment, activate it, and install the requirements**:
   ```bash
   python -m venv .venv
   source ./.venv/bin/activate
   pip install -r requirements.txt

## Usage

1. **Start the interactive UI**:
   ```bash
   make run

2. **How to use the UI?**:
- The red dots are nodes.
- To spawn a temporary wire, right click on any node.
- To place another node, left click after spawning the temporary wire
- To connect the temporary wire with an existing node, right click on the existing node after spawning the temporary wire
- To turn a wire into a resistor, right click on a wire and press the key R
- You can modify the resistances of the resistors and the voltage of the battery by right clicking the voltage box and typing the new value.
- To reset the circuit, click on the reset button
- To generate the meta data(total resistance, current, voltage) press the build button
- To modify the circuit after the build, press the modify button(note: this will remove the generated meta data from the circuit)

## How it works:

The algorithm calculates the properties of a circuit with \( n \) unknown nodes using the following approach(note, the two nodes connected to the battery are known to be V and 0):

1. **Define Variables**:  
   Assume the voltage at the \( j \)-th node is \( a_j \). Assume total current to be I.

2. **Formulate Equations**:  
   Create \( n + 1 \) equations based on **Kirchhoff's laws** on each of the unknown nodes + the node with voltage V incorporating I.

3. **Solve the System**:  
   Use linear algebra techniques to solve the system of \( n \) equations for the node voltages \( a_j \).

4. **Handle Zero Resistances**:  
   - Zero-resistance wires are treated as **real zeros**, not approximations.
   - The equations are modified to enforce constraints such that nodes connected by zero-resistance wires have equal voltages.

This approach ensures that the tool can handle any well-formed circuit and guarantees finding a solution if one exists.



