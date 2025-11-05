import sys
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector, plot_histogram
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

# Ensure UTF-8 stdout on Windows terminals
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

# --- Function to prepare initial qubit state ---
def prepare_initial_state(qc: QuantumCircuit, state_input: str):
    state_input = state_input.strip()
    if state_input == "0":
        pass  # default |0⟩
    elif state_input == "1":
        qc.x(0)  # flip to |1⟩
    else:
        raise ValueError("Unsupported initial state. Only '0' or '1' allowed.")
    return qc

# --- Build quantum circuit with selected gate ---
def build_circuit(gate_name: str, initial_state: str) -> QuantumCircuit:
    name = gate_name.lower()

    # If it's a CNOT, we need 2 qubits and 2 classical bits
    if name in ("cnot", "cx", "controlled-not", "controlled x"):
        qc = QuantumCircuit(2, 2)
        # Prepare initial state on control qubit (qubit 0)
        qc = prepare_initial_state(qc, initial_state)
        qc.cx(0, 1)  # Apply CNOT: control=0, target=1
        return qc
    else:
        # Single-qubit circuit
        qc = QuantumCircuit(1, 1)
        qc = prepare_initial_state(qc, initial_state)

        if name in ("h", "hadamard"):
            qc.h(0)
        elif name in ("x", "pauli-x", "pauli x"):
            qc.x(0)
        elif name in ("y", "pauli-y", "pauli y"):
            qc.y(0)
        elif name in ("z", "pauli-z", "pauli z"):
            qc.z(0)
        else:
            raise ValueError(f"Unsupported gate: {gate_name}")
        return qc

# --- Visualize Bloch sphere + measurement histogram ---
def visualize(qc: QuantumCircuit, gate_label: str):
    print("\nCircuit:")
    print(qc.draw(output='text'))

    simulator = AerSimulator()

    # --- Bloch sphere visualization ---
    try:
        # Works for 1-qubit states
        qc_sv = qc.copy()
        qc_sv.save_statevector()
        result = simulator.run(qc_sv).result()
        statevector = result.get_statevector()
        if qc.num_qubits == 1:
            plot_bloch_multivector(statevector)
            plt.suptitle(f"Bloch Sphere — {gate_label}", y=0.95)
            plt.show()
        else:
            print("\nNote: Bloch sphere shown only for single-qubit circuits.")
    except Exception:
        print("Could not generate Bloch sphere for this circuit.")

    # --- Measurement histogram ---
    qc_meas = qc.copy()
    qc_meas.measure_all()
    job2 = simulator.run(qc_meas, shots=1024)
    res2 = job2.result()
    counts = res2.get_counts()
    print("\nMeasurement counts (shots=1024):", counts)

    plot_histogram(counts)
    plt.suptitle(f"Measurement Histogram — {gate_label}", y=0.95)
    plt.show()

# --- Interactive prompt ---
def interactive_loop():
    print("""
Interactive Quantum Gate Visualizer with Qubit Input
- Choose initial state of qubit 0: 0 or 1
- Choose a quantum gate: H, X, Y, Z, or CNOT
- Type 'q' to quit
""")
    while True:
        state_input = input("Enter initial state of qubit 0 (0/1, q to quit): ").strip()
        if state_input.lower() in ("q", "quit"):
            print("Exiting...")
            break
        if state_input not in ("0", "1"):
            print("Invalid input. Only '0' or '1' allowed.")
            continue

        gate_input = input("Enter gate (H/X/Y/Z/CNOT): ").strip()
        if gate_input.lower() in ("q", "quit"):
            print("Exiting...")
            break

        synonyms = {
            "h": "Hadamard", "hadamard": "Hadamard",
            "x": "Pauli-X", "pauli-x": "Pauli-X", "pauli x": "Pauli-X",
            "y": "Pauli-Y", "pauli-y": "Pauli-Y", "pauli y": "Pauli-Y",
            "z": "Pauli-Z", "pauli-z": "Pauli-Z", "pauli z": "Pauli-Z",
            "cnot": "CNOT", "cx": "CNOT", "controlled-not": "CNOT", "controlled x": "CNOT"
        }
        gate_key = gate_input.strip().lower()
        gate_label = synonyms.get(gate_key, gate_input)

        try:
            qc = build_circuit(gate_label, state_input)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        visualize(qc, f"{gate_label} | initial={state_input} ⟩")

# --- Run ---
if __name__ == "__main__":
    interactive_loop()

  