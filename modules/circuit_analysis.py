import numpy as np
import math
from database import save_calculation

def dc_analysis(voltage_sources, current_sources, resistances, connections):
    warnings = []
    result = {}
    
    total_voltage = sum(voltage_sources)
    total_resistance = sum(resistances) if resistances else 1
    
    circuit_current = total_voltage / total_resistance if total_resistance > 0 else 0
    
    node_voltages = []
    cumulative_drop = 0
    for r in resistances:
        voltage_drop = circuit_current * r
        cumulative_drop += voltage_drop
        node_voltages.append(total_voltage - cumulative_drop)
    
    power_dissipated = []
    for r in resistances:
        power_dissipated.append(circuit_current**2 * r)
    
    result = {
        'total_voltage': total_voltage,
        'total_resistance': total_resistance,
        'circuit_current': circuit_current,
        'node_voltages': node_voltages,
        'power_dissipated': power_dissipated,
        'total_power': sum(power_dissipated)
    }
    
    if circuit_current > 10:
        warnings.append("High current flow detected")
    if sum(power_dissipated) > 100:
        warnings.append("High power dissipation - consider thermal management")
    
    save_calculation('dc_analysis',
        {'voltage_sources': voltage_sources, 'resistances': resistances},
        result, '; '.join(warnings))
    
    return result, warnings

def ac_analysis(voltage_amplitude, frequency, resistance, inductance=0, capacitance=0):
    warnings = []
    omega = 2 * math.pi * frequency
    
    xl = omega * inductance if inductance > 0 else 0
    xc = 1 / (omega * capacitance) if capacitance > 0 else 0
    x_net = xl - xc
    
    impedance = math.sqrt(resistance**2 + x_net**2)
    phase_angle = math.degrees(math.atan2(x_net, resistance))
    
    current_amplitude = voltage_amplitude / impedance if impedance > 0 else 0
    
    power_apparent = voltage_amplitude * current_amplitude / 2
    power_factor = math.cos(math.radians(phase_angle))
    power_real = power_apparent * power_factor
    power_reactive = power_apparent * math.sin(math.radians(phase_angle))
    
    result = {
        'frequency': frequency,
        'angular_frequency': omega,
        'inductive_reactance': xl,
        'capacitive_reactance': xc,
        'net_reactance': x_net,
        'impedance': impedance,
        'phase_angle': phase_angle,
        'current_amplitude': current_amplitude,
        'power_apparent': power_apparent,
        'power_real': power_real,
        'power_reactive': power_reactive,
        'power_factor': power_factor
    }
    
    if power_factor < 0.8:
        warnings.append("Low power factor - consider power factor correction")
    
    circuit_type = 'resistive'
    if x_net > 0:
        circuit_type = 'inductive'
    elif x_net < 0:
        circuit_type = 'capacitive'
    result['circuit_type'] = circuit_type
    
    save_calculation('ac_analysis',
        {'voltage': voltage_amplitude, 'frequency': frequency, 'R': resistance, 'L': inductance, 'C': capacitance},
        result, '; '.join(warnings))
    
    return result, warnings

def frequency_response(resistance, inductance, capacitance, freq_start=1, freq_end=1e6, points=100):
    frequencies = np.logspace(np.log10(freq_start), np.log10(freq_end), points)
    
    gains = []
    phases = []
    impedances = []
    
    for freq in frequencies:
        omega = 2 * math.pi * freq
        xl = omega * inductance if inductance > 0 else 0
        xc = 1 / (omega * capacitance) if capacitance > 0 else 0
        x_net = xl - xc
        
        impedance = math.sqrt(resistance**2 + x_net**2)
        impedances.append(impedance)
        
        gain_db = 20 * np.log10(resistance / impedance) if impedance > 0 else 0
        gains.append(gain_db)
        
        phase = math.degrees(math.atan2(-x_net, resistance))
        phases.append(phase)
    
    resonant_freq = 1 / (2 * math.pi * math.sqrt(inductance * capacitance)) if inductance > 0 and capacitance > 0 else None
    
    result = {
        'frequencies': frequencies.tolist(),
        'gains_db': gains,
        'phases': phases,
        'impedances': impedances,
        'resonant_frequency': resonant_freq
    }
    
    if resonant_freq:
        q_factor = (1 / resistance) * math.sqrt(inductance / capacitance)
        bandwidth = resonant_freq / q_factor if q_factor > 0 else float('inf')
        result['q_factor'] = q_factor
        result['bandwidth'] = bandwidth
    
    return result

def efficiency_analysis(input_power, output_power, losses=None):
    warnings = []
    
    if losses is None:
        losses = input_power - output_power
    
    efficiency = (output_power / input_power) * 100 if input_power > 0 else 0
    
    result = {
        'input_power': input_power,
        'output_power': output_power,
        'losses': losses,
        'efficiency_percent': efficiency
    }
    
    if efficiency < 50:
        warnings.append("Low efficiency - significant power losses")
        result['rating'] = 'Poor'
    elif efficiency < 70:
        warnings.append("Moderate efficiency - room for improvement")
        result['rating'] = 'Fair'
    elif efficiency < 85:
        result['rating'] = 'Good'
    else:
        result['rating'] = 'Excellent'
    
    save_calculation('efficiency_analysis',
        {'input_power': input_power, 'output_power': output_power},
        result, '; '.join(warnings))
    
    return result, warnings

def comparative_analysis(circuits):
    comparison = []
    
    for i, circuit in enumerate(circuits):
        result, warnings = ac_analysis(**circuit)
        comparison.append({
            'circuit_id': i + 1,
            'parameters': circuit,
            'impedance': result['impedance'],
            'power_factor': result['power_factor'],
            'efficiency': result.get('efficiency', 'N/A'),
            'phase_angle': result['phase_angle'],
            'circuit_type': result['circuit_type']
        })
    
    best_pf = max(comparison, key=lambda x: x['power_factor'])
    lowest_impedance = min(comparison, key=lambda x: x['impedance'])
    
    conclusion = {
        'best_power_factor': best_pf['circuit_id'],
        'lowest_impedance': lowest_impedance['circuit_id'],
        'comparison_data': comparison
    }
    
    return conclusion

def generate_conclusion(analysis_type, result, warnings):
    conclusions = []
    
    if analysis_type == 'dc':
        if result.get('circuit_current', 0) < 0.1:
            conclusions.append("The circuit operates at low current, suitable for signal-level applications.")
        else:
            conclusions.append("The circuit handles significant current flow.")
        
        total_power = result.get('total_power', 0)
        if total_power < 1:
            conclusions.append("Power dissipation is minimal.")
        elif total_power < 10:
            conclusions.append("Moderate power dissipation - passive cooling sufficient.")
        else:
            conclusions.append("High power dissipation - active cooling recommended.")
    
    elif analysis_type == 'ac':
        pf = result.get('power_factor', 0)
        if pf > 0.95:
            conclusions.append("Excellent power factor - minimal reactive power losses.")
        elif pf > 0.8:
            conclusions.append("Good power factor - acceptable for most applications.")
        else:
            conclusions.append("Poor power factor - power factor correction recommended.")
        
        circuit_type = result.get('circuit_type', 'resistive')
        conclusions.append(f"The circuit exhibits {circuit_type} characteristics.")
    
    return ' '.join(conclusions)
