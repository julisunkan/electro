import numpy as np
import math
from scipy import signal
from database import save_lab_report
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from datetime import datetime

EXPERIMENTS = {
    'rc_transient': {
        'name': 'RC Circuit Transient Response',
        'description': 'Analyze charging and discharging behavior of RC circuits',
        'theory': 'The RC circuit time constant τ = RC determines how quickly the capacitor charges/discharges. After 5τ, the capacitor is considered fully charged (99.3%).',
        'parameters': ['resistance', 'capacitance', 'voltage']
    },
    'rlc_resonance': {
        'name': 'RLC Circuit Resonance',
        'description': 'Study resonant frequency and Q-factor of RLC circuits',
        'theory': 'At resonance, inductive and capacitive reactances cancel out. The resonant frequency f₀ = 1/(2π√LC). The Q-factor determines the sharpness of resonance.',
        'parameters': ['resistance', 'inductance', 'capacitance']
    },
    'diode_characteristics': {
        'name': 'Diode I-V Characteristics',
        'description': 'Plot forward and reverse characteristics of a diode',
        'theory': 'A diode follows the Shockley equation: I = Is(e^(V/nVt) - 1). Forward bias shows exponential current increase, reverse bias shows minimal leakage current.',
        'parameters': ['saturation_current', 'ideality_factor', 'temperature']
    },
    'amplifier_gain': {
        'name': 'Amplifier Gain Measurement',
        'description': 'Measure voltage gain and frequency response of amplifiers',
        'theory': 'Amplifier gain Av = Vout/Vin. The bandwidth is limited by internal capacitances. Gain-bandwidth product is constant for most amplifiers.',
        'parameters': ['dc_gain', 'bandwidth', 'input_impedance']
    }
}

def run_rc_transient(resistance, capacitance, voltage, duration_multiplier=5):
    tau = resistance * capacitance
    duration = tau * duration_multiplier
    
    t = np.linspace(0, duration, 1000)
    
    v_charging = voltage * (1 - np.exp(-t / tau))
    i_charging = (voltage / resistance) * np.exp(-t / tau)
    
    v_discharging = voltage * np.exp(-t / tau)
    i_discharging = -(voltage / resistance) * np.exp(-t / tau)
    
    time_63 = tau
    time_95 = 3 * tau
    time_99 = 5 * tau
    
    result = {
        'experiment': 'RC Transient Response',
        'parameters': {
            'resistance_ohm': resistance,
            'capacitance_f': capacitance,
            'voltage_v': voltage
        },
        'time_constant_s': tau,
        'charging': {
            'time': t.tolist(),
            'voltage': v_charging.tolist(),
            'current': i_charging.tolist()
        },
        'discharging': {
            'time': t.tolist(),
            'voltage': v_discharging.tolist(),
            'current': i_discharging.tolist()
        },
        'key_times': {
            'time_63_percent': time_63,
            'time_95_percent': time_95,
            'time_99_percent': time_99
        },
        'conclusion': f'The RC circuit has a time constant of {tau:.6f} seconds. The capacitor reaches 63.2% charge in {time_63:.6f}s, 95% in {time_95:.6f}s, and 99.3% in {time_99:.6f}s.'
    }
    
    return result

def run_rlc_resonance(resistance, inductance, capacitance, freq_start=10, freq_end=100000, points=500):
    f0 = 1 / (2 * math.pi * math.sqrt(inductance * capacitance))
    q_factor = (1 / resistance) * math.sqrt(inductance / capacitance)
    bandwidth = f0 / q_factor if q_factor > 0 else float('inf')
    
    damping = resistance / (2 * math.sqrt(inductance / capacitance))
    if damping < 1:
        response_type = 'Underdamped'
    elif damping == 1:
        response_type = 'Critically Damped'
    else:
        response_type = 'Overdamped'
    
    frequencies = np.logspace(np.log10(freq_start), np.log10(freq_end), points)
    
    impedances = []
    phases = []
    gains = []
    
    for f in frequencies:
        omega = 2 * math.pi * f
        xl = omega * inductance
        xc = 1 / (omega * capacitance)
        z = math.sqrt(resistance**2 + (xl - xc)**2)
        phase = math.degrees(math.atan2(xl - xc, resistance))
        gain_db = 20 * np.log10(resistance / z)
        
        impedances.append(z)
        phases.append(phase)
        gains.append(gain_db)
    
    result = {
        'experiment': 'RLC Resonance',
        'parameters': {
            'resistance_ohm': resistance,
            'inductance_h': inductance,
            'capacitance_f': capacitance
        },
        'resonant_frequency_hz': f0,
        'q_factor': q_factor,
        'bandwidth_hz': bandwidth,
        'damping_factor': damping,
        'response_type': response_type,
        'frequency_response': {
            'frequencies': frequencies.tolist(),
            'impedances': impedances,
            'phases': phases,
            'gains_db': gains
        },
        'conclusion': f'The RLC circuit resonates at {f0:.2f} Hz with a Q-factor of {q_factor:.2f}. The -3dB bandwidth is {bandwidth:.2f} Hz. The circuit is {response_type.lower()}.'
    }
    
    return result

def run_diode_characteristics(saturation_current=1e-12, ideality_factor=1, temperature=300):
    k = 1.380649e-23
    q = 1.602176634e-19
    vt = k * temperature / q
    
    v_forward = np.linspace(0, 0.8, 200)
    i_forward = saturation_current * (np.exp(v_forward / (ideality_factor * vt)) - 1)
    
    v_reverse = np.linspace(-5, 0, 100)
    i_reverse = saturation_current * (np.exp(v_reverse / (ideality_factor * vt)) - 1)
    
    v_on_idx = np.argmax(i_forward > 1e-3)
    v_on = v_forward[v_on_idx] if v_on_idx > 0 else 0.7
    
    result = {
        'experiment': 'Diode I-V Characteristics',
        'parameters': {
            'saturation_current_a': saturation_current,
            'ideality_factor': ideality_factor,
            'temperature_k': temperature
        },
        'thermal_voltage_v': vt,
        'forward_voltage_v': v_on,
        'forward_characteristics': {
            'voltage': v_forward.tolist(),
            'current': i_forward.tolist()
        },
        'reverse_characteristics': {
            'voltage': v_reverse.tolist(),
            'current': i_reverse.tolist()
        },
        'conclusion': f'The diode has a forward voltage of approximately {v_on:.3f}V at 1mA. At {temperature}K, the thermal voltage is {vt*1000:.2f}mV. The reverse leakage current is {saturation_current*1e12:.2f}pA.'
    }
    
    return result

def run_amplifier_gain(dc_gain=100, bandwidth=1e6, input_impedance=10000, freq_start=10, freq_end=1e8, points=500):
    gain_db = 20 * np.log10(dc_gain)
    gbw = dc_gain * bandwidth
    
    frequencies = np.logspace(np.log10(freq_start), np.log10(freq_end), points)
    
    gains = []
    phases = []
    
    for f in frequencies:
        gain = dc_gain / math.sqrt(1 + (f / bandwidth)**2)
        phase = -math.degrees(math.atan(f / bandwidth))
        gains.append(20 * np.log10(gain))
        phases.append(phase)
    
    cutoff_idx = np.argmin(np.abs(np.array(gains) - (gain_db - 3)))
    measured_bandwidth = frequencies[cutoff_idx]
    
    result = {
        'experiment': 'Amplifier Gain Measurement',
        'parameters': {
            'dc_gain_linear': dc_gain,
            'dc_gain_db': gain_db,
            'bandwidth_hz': bandwidth,
            'input_impedance_ohm': input_impedance
        },
        'gain_bandwidth_product': gbw,
        'measured_bandwidth_hz': measured_bandwidth,
        'frequency_response': {
            'frequencies': frequencies.tolist(),
            'gains_db': gains,
            'phases': phases
        },
        'conclusion': f'The amplifier has a DC gain of {dc_gain} ({gain_db:.1f}dB) with a -3dB bandwidth of {measured_bandwidth:.0f}Hz. The gain-bandwidth product is {gbw/1e6:.2f}MHz.'
    }
    
    return result

def add_tolerance_error(value, tolerance_percent):
    error = value * (tolerance_percent / 100) * np.random.uniform(-1, 1)
    return value + error

def run_experiment_with_tolerance(experiment_name, params, tolerance_percent=5):
    params_with_error = {}
    for key, value in params.items():
        if isinstance(value, (int, float)) and value != 0:
            params_with_error[key] = add_tolerance_error(value, tolerance_percent)
        else:
            params_with_error[key] = value
    
    if experiment_name == 'rc_transient':
        result = run_rc_transient(**params_with_error)
    elif experiment_name == 'rlc_resonance':
        result = run_rlc_resonance(**params_with_error)
    elif experiment_name == 'diode_characteristics':
        result = run_diode_characteristics(**params_with_error)
    elif experiment_name == 'amplifier_gain':
        result = run_amplifier_gain(**params_with_error)
    else:
        return {'error': 'Unknown experiment'}
    
    result['tolerance_applied'] = tolerance_percent
    result['actual_parameters'] = params_with_error
    result['nominal_parameters'] = params
    
    return result

def generate_lab_report(experiment_result, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"lab_report_{timestamp}.pdf"
    
    filepath = os.path.join('static', 'plots', filename)
    
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Virtual Electronics Lab Report", styles['Title']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph(f"Experiment: {experiment_result.get('experiment', 'Unknown')}", styles['Heading2']))
    elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Parameters", styles['Heading3']))
    params = experiment_result.get('parameters', {})
    param_data = [['Parameter', 'Value']]
    for key, value in params.items():
        if isinstance(value, float):
            param_data.append([key.replace('_', ' ').title(), f'{value:.6g}'])
        else:
            param_data.append([key.replace('_', ' ').title(), str(value)])
    
    param_table = Table(param_data, colWidths=[200, 200])
    param_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(param_table)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Results", styles['Heading3']))
    
    skip_keys = ['experiment', 'parameters', 'charging', 'discharging', 'frequency_response', 
                 'forward_characteristics', 'reverse_characteristics', 'conclusion',
                 'tolerance_applied', 'actual_parameters', 'nominal_parameters']
    
    result_data = [['Metric', 'Value']]
    for key, value in experiment_result.items():
        if key not in skip_keys and not isinstance(value, (dict, list)):
            if isinstance(value, float):
                result_data.append([key.replace('_', ' ').title(), f'{value:.6g}'])
            else:
                result_data.append([key.replace('_', ' ').title(), str(value)])
    
    if len(result_data) > 1:
        result_table = Table(result_data, colWidths=[200, 200])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(result_table)
    
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Conclusion", styles['Heading3']))
    elements.append(Paragraph(experiment_result.get('conclusion', 'No conclusion available.'), styles['Normal']))
    
    doc.build(elements)
    
    save_lab_report(
        experiment_result.get('experiment', 'Unknown'),
        str(experiment_result.get('parameters', {})),
        experiment_result.get('conclusion', ''),
        filepath
    )
    
    return filepath

def get_experiment_list():
    return EXPERIMENTS

def get_experiment_theory(experiment_name):
    if experiment_name in EXPERIMENTS:
        return EXPERIMENTS[experiment_name]
    return {'error': 'Experiment not found'}
