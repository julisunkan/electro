import numpy as np
import math
from database import save_calculation

ENGINEERING_CONSTANTS = {
    'speed_of_light': 299792458,
    'planck_constant': 6.62607015e-34,
    'electron_charge': 1.602176634e-19,
    'boltzmann_constant': 1.380649e-23,
    'avogadro_number': 6.02214076e23,
    'permittivity_free_space': 8.854187817e-12,
    'permeability_free_space': 1.2566370614e-6,
    'pi': math.pi,
    'euler_number': math.e
}

UNIT_PREFIXES = {
    'T': 1e12, 'G': 1e9, 'M': 1e6, 'k': 1e3,
    '': 1, 'm': 1e-3, 'u': 1e-6, 'n': 1e-9, 'p': 1e-12
}

def convert_unit(value, from_prefix, to_prefix):
    base_value = value * UNIT_PREFIXES.get(from_prefix, 1)
    return base_value / UNIT_PREFIXES.get(to_prefix, 1)

def ohms_law(voltage=None, current=None, resistance=None):
    warnings = []
    result = {}
    
    if voltage is not None and current is not None:
        result['resistance'] = voltage / current if current != 0 else float('inf')
        result['power'] = voltage * current
    elif voltage is not None and resistance is not None:
        result['current'] = voltage / resistance if resistance != 0 else float('inf')
        result['power'] = (voltage ** 2) / resistance if resistance != 0 else float('inf')
    elif current is not None and resistance is not None:
        result['voltage'] = current * resistance
        result['power'] = (current ** 2) * resistance
    else:
        warnings.append("Please provide at least two values")
        return result, warnings
    
    if result.get('power', 0) > 100:
        warnings.append("High power dissipation! Consider heat management.")
    if result.get('current', 0) > 10:
        warnings.append("High current! Ensure proper wire gauge.")
    
    save_calculation('ohms_law', 
        {'voltage': voltage, 'current': current, 'resistance': resistance},
        result, '; '.join(warnings))
    
    return result, warnings

def rc_circuit(resistance, capacitance, frequency=None):
    warnings = []
    tau = resistance * capacitance
    
    result = {
        'time_constant': tau,
        'cutoff_frequency': 1 / (2 * math.pi * tau),
        'charge_time_63': tau,
        'charge_time_95': 3 * tau,
        'charge_time_99': 5 * tau
    }
    
    if frequency:
        xc = 1 / (2 * math.pi * frequency * capacitance)
        impedance = math.sqrt(resistance**2 + xc**2)
        phase = math.degrees(math.atan(-xc / resistance))
        result['capacitive_reactance'] = xc
        result['impedance'] = impedance
        result['phase_angle'] = phase
        result['gain'] = resistance / impedance
    
    if tau < 1e-9:
        warnings.append("Very fast time constant - may require high-speed components")
    elif tau > 1:
        warnings.append("Slow time constant - consider application requirements")
    
    save_calculation('rc_circuit',
        {'resistance': resistance, 'capacitance': capacitance, 'frequency': frequency},
        result, '; '.join(warnings))
    
    return result, warnings

def rl_circuit(resistance, inductance, frequency=None):
    warnings = []
    tau = inductance / resistance
    
    result = {
        'time_constant': tau,
        'cutoff_frequency': resistance / (2 * math.pi * inductance),
        'rise_time_63': tau,
        'rise_time_95': 3 * tau,
        'rise_time_99': 5 * tau
    }
    
    if frequency:
        xl = 2 * math.pi * frequency * inductance
        impedance = math.sqrt(resistance**2 + xl**2)
        phase = math.degrees(math.atan(xl / resistance))
        result['inductive_reactance'] = xl
        result['impedance'] = impedance
        result['phase_angle'] = phase
        result['gain'] = resistance / impedance
    
    if tau < 1e-9:
        warnings.append("Very fast response - suitable for high-frequency applications")
    
    save_calculation('rl_circuit',
        {'resistance': resistance, 'inductance': inductance, 'frequency': frequency},
        result, '; '.join(warnings))
    
    return result, warnings

def rlc_circuit(resistance, inductance, capacitance, frequency=None):
    warnings = []
    
    resonant_freq = 1 / (2 * math.pi * math.sqrt(inductance * capacitance))
    q_factor = (1 / resistance) * math.sqrt(inductance / capacitance)
    bandwidth = resonant_freq / q_factor if q_factor > 0 else float('inf')
    damping_factor = resistance / (2 * math.sqrt(inductance / capacitance))
    
    result = {
        'resonant_frequency': resonant_freq,
        'q_factor': q_factor,
        'bandwidth': bandwidth,
        'damping_factor': damping_factor
    }
    
    if damping_factor < 1:
        result['response_type'] = 'Underdamped (oscillatory)'
    elif damping_factor == 1:
        result['response_type'] = 'Critically damped'
    else:
        result['response_type'] = 'Overdamped'
    
    if frequency:
        xl = 2 * math.pi * frequency * inductance
        xc = 1 / (2 * math.pi * frequency * capacitance)
        x_total = xl - xc
        impedance = math.sqrt(resistance**2 + x_total**2)
        phase = math.degrees(math.atan(x_total / resistance)) if resistance != 0 else 90
        
        result['inductive_reactance'] = xl
        result['capacitive_reactance'] = xc
        result['net_reactance'] = x_total
        result['impedance'] = impedance
        result['phase_angle'] = phase
    
    if q_factor > 100:
        warnings.append("Very high Q factor - narrow bandwidth, may be sensitive to component tolerances")
    elif q_factor < 0.5:
        warnings.append("Low Q factor - heavily damped response")
    
    save_calculation('rlc_circuit',
        {'resistance': resistance, 'inductance': inductance, 'capacitance': capacitance, 'frequency': frequency},
        result, '; '.join(warnings))
    
    return result, warnings

def filter_design(filter_type, cutoff_freq, resistance=None, capacitance=None):
    warnings = []
    result = {}
    
    if filter_type == 'lowpass':
        if resistance and cutoff_freq:
            capacitance = 1 / (2 * math.pi * resistance * cutoff_freq)
            result['capacitance'] = capacitance
        elif capacitance and cutoff_freq:
            resistance = 1 / (2 * math.pi * capacitance * cutoff_freq)
            result['resistance'] = resistance
        result['filter_type'] = 'Low-pass RC filter'
        result['cutoff_frequency'] = cutoff_freq
        result['rolloff'] = '-20 dB/decade'
        
    elif filter_type == 'highpass':
        if resistance and cutoff_freq:
            capacitance = 1 / (2 * math.pi * resistance * cutoff_freq)
            result['capacitance'] = capacitance
        elif capacitance and cutoff_freq:
            resistance = 1 / (2 * math.pi * capacitance * cutoff_freq)
            result['resistance'] = resistance
        result['filter_type'] = 'High-pass RC filter'
        result['cutoff_frequency'] = cutoff_freq
        result['rolloff'] = '+20 dB/decade (below cutoff)'
    
    save_calculation('filter_design',
        {'filter_type': filter_type, 'cutoff_freq': cutoff_freq, 'resistance': resistance, 'capacitance': capacitance},
        result, '; '.join(warnings))
    
    return result, warnings

def amplifier_gain(input_voltage, output_voltage=None, gain_db=None, gain_linear=None):
    warnings = []
    result = {}
    
    if output_voltage:
        gain_linear = output_voltage / input_voltage if input_voltage != 0 else 0
        gain_db = 20 * math.log10(abs(gain_linear)) if gain_linear != 0 else float('-inf')
    elif gain_db is not None:
        gain_linear = 10 ** (gain_db / 20)
        output_voltage = input_voltage * gain_linear
    elif gain_linear is not None:
        gain_db = 20 * math.log10(abs(gain_linear)) if gain_linear != 0 else float('-inf')
        output_voltage = input_voltage * gain_linear
    
    result = {
        'input_voltage': input_voltage,
        'output_voltage': output_voltage,
        'gain_linear': gain_linear,
        'gain_db': gain_db
    }
    
    if gain_db is not None and abs(gain_db) > 60:
        warnings.append("Very high gain - consider stability and noise")
    
    save_calculation('amplifier_gain',
        {'input_voltage': input_voltage, 'output_voltage': output_voltage, 'gain_db': gain_db},
        result, '; '.join(warnings))
    
    return result, warnings

def tolerance_analysis(nominal_value, tolerance_percent):
    warnings = []
    tolerance_fraction = tolerance_percent / 100
    
    result = {
        'nominal': nominal_value,
        'tolerance_percent': tolerance_percent,
        'min_value': nominal_value * (1 - tolerance_fraction),
        'max_value': nominal_value * (1 + tolerance_fraction),
        'absolute_tolerance': nominal_value * tolerance_fraction
    }
    
    if tolerance_percent > 20:
        warnings.append("High tolerance - may affect circuit accuracy")
    
    save_calculation('tolerance_analysis',
        {'nominal_value': nominal_value, 'tolerance_percent': tolerance_percent},
        result, '; '.join(warnings))
    
    return result, warnings

def power_rating_check(voltage, current, rated_power, derating_factor=0.8):
    warnings = []
    actual_power = voltage * current
    derated_power = rated_power * derating_factor
    
    result = {
        'actual_power': actual_power,
        'rated_power': rated_power,
        'derated_power': derated_power,
        'power_margin': derated_power - actual_power,
        'utilization_percent': (actual_power / rated_power) * 100
    }
    
    if actual_power > derated_power:
        warnings.append("DANGER: Power exceeds derated limit! Component may fail.")
        result['status'] = 'FAIL'
    elif actual_power > rated_power * 0.7:
        warnings.append("WARNING: Operating near power limit. Consider upgrading component.")
        result['status'] = 'WARNING'
    else:
        result['status'] = 'OK'
    
    save_calculation('power_rating',
        {'voltage': voltage, 'current': current, 'rated_power': rated_power},
        result, '; '.join(warnings))
    
    return result, warnings

def what_if_analysis(base_params, param_to_vary, variation_range, calculation_func):
    results = []
    for variation in variation_range:
        params = base_params.copy()
        params[param_to_vary] = variation
        result, _ = calculation_func(**params)
        results.append({'param_value': variation, 'result': result})
    return results

def series_resistance(resistances):
    total = sum(resistances)
    return {'total_resistance': total, 'count': len(resistances)}

def parallel_resistance(resistances):
    if 0 in resistances:
        return {'total_resistance': 0, 'warning': 'Short circuit detected'}
    total = 1 / sum(1/r for r in resistances)
    return {'total_resistance': total, 'count': len(resistances)}

def voltage_divider(vin, r1, r2):
    vout = vin * r2 / (r1 + r2)
    current = vin / (r1 + r2)
    power_r1 = current**2 * r1
    power_r2 = current**2 * r2
    
    result = {
        'output_voltage': vout,
        'current': current,
        'power_r1': power_r1,
        'power_r2': power_r2,
        'ratio': r2 / (r1 + r2)
    }
    
    save_calculation('voltage_divider',
        {'vin': vin, 'r1': r1, 'r2': r2},
        result, '')
    
    return result, []
