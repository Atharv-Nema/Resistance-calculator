# Resistance Calculator

This is a tool to that allows users to build a circuit consisting on multiple resistors and a battery and calculates various features of the circuit, including the net resistance, the current through individual wires and the voltage at every node. This is
especially useful for physics students at school and university.

## Features

- **Zero resistance wires**: Allows for zero resistance wires to be connected and treats them as such, i.e. algorithm does not treat zero resistances as extremely small resistances. Instead, they are treated as **real zeros**, leading to higher precision. For example, the voltages of two nodes connected by a zero resistance wire are guaranteed to be equal.
- **Works for any well behaved circuit**: No matter how complicated the circuit is, if
a single solution exists, the algorithm is guaranteed to find it.
- **User-Friendly Interface**: The tool comes with a simple user interface built in pygame that allows users to build the circuit interactively.
- **Undefined current and infinite current detection**: The algorithm can detect whether the current in a wire is infinite or undefined.

## 📝 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [How It Works](#how-it-works)
- [Dependencies](#dependencies)
- [License](#license)

## 💻 Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/resistance-calculator.git
   cd resistance-calculator
