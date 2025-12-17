import numpy as np
import math
from database import save_calculation

SPEED_OF_LIGHT = 299792458
RF_CONSTANTS = {
    'speed_of_light': SPEED_OF_LIGHT,
    'free_space_impedance': 377,
    'permittivity_free_space': 8.854187817e-12,
    'permeability_free_space': 1.2566370614e-6
}

def frequency_to_wavelength(frequency):
    wavelength = SPEED_OF_LIGHT / frequency
    return {
        'frequency_hz': frequency,
        'frequency_mhz': frequency / 1e6,
        'frequency_ghz': frequency / 1e9,
        'wavelength_m': wavelength,
        'wavelength_cm': wavelength * 100,
        'wavelength_mm': wavelength * 1000
    }

def wavelength_to_frequency(wavelength):
    frequency = SPEED_OF_LIGHT / wavelength
    return {
        'wavelength_m': wavelength,
        'frequency_hz': frequency,
        'frequency_mhz': frequency / 1e6,
        'frequency_ghz': frequency / 1e9
    }

def dipole_antenna(frequency, wire_diameter=0.002):
    warnings = []
    wavelength = SPEED_OF_LIGHT / frequency
    
    half_wave_length = wavelength / 2
    quarter_wave_length = wavelength / 4
    
    velocity_factor = 0.95
    practical_length = half_wave_length * velocity_factor
    
    radiation_resistance = 73
    input_impedance = 73 + 42.5j
    
    gain_dbi = 2.15
    gain_dbd = 0
    
    effective_aperture = (wavelength**2 * 10**(gain_dbi/10)) / (4 * math.pi)
    
    beamwidth_e = 78
    beamwidth_h = 360
    
    result = {
        'frequency_mhz': frequency / 1e6,
        'wavelength_m': wavelength,
        'half_wave_length_m': half_wave_length,
        'practical_length_m': practical_length,
        'quarter_wave_length_m': quarter_wave_length,
        'radiation_resistance_ohm': radiation_resistance,
        'input_impedance': str(input_impedance),
        'gain_dbi': gain_dbi,
        'gain_dbd': gain_dbd,
        'effective_aperture_m2': effective_aperture,
        'beamwidth_e_plane': beamwidth_e,
        'beamwidth_h_plane': beamwidth_h,
        'velocity_factor': velocity_factor
    }
    
    if frequency < 1e6:
        warnings.append("Low frequency - antenna will be very long")
    if frequency > 30e9:
        warnings.append("Very high frequency - consider manufacturing tolerances")
    
    if wire_diameter > wavelength / 100:
        warnings.append("Wire diameter is significant compared to wavelength")
    
    save_calculation('dipole_antenna',
        {'frequency': frequency, 'wire_diameter': wire_diameter},
        result, '; '.join(warnings))
    
    return result, warnings

def yagi_antenna(frequency, num_elements=3, boom_length_wavelengths=None):
    warnings = []
    wavelength = SPEED_OF_LIGHT / frequency
    
    if num_elements < 3:
        warnings.append("Yagi antenna requires minimum 3 elements")
        num_elements = 3
    
    driven_length = 0.475 * wavelength
    reflector_length = 0.5 * wavelength
    director_length = 0.45 * wavelength
    
    reflector_spacing = 0.25 * wavelength
    director_spacing = 0.3 * wavelength
    
    if boom_length_wavelengths is None:
        boom_length_wavelengths = 0.25 + (num_elements - 2) * 0.3
    boom_length = boom_length_wavelengths * wavelength
    
    base_gain = 7.0
    gain_per_element = 1.5
    gain_dbi = base_gain + (num_elements - 3) * gain_per_element
    
    base_fb = 15
    fb_per_element = 3
    front_to_back = base_fb + (num_elements - 3) * fb_per_element
    
    beamwidth = 60 / (num_elements - 1) if num_elements > 1 else 60
    
    input_impedance = 20 + 0j
    
    bandwidth_percent = 5 / num_elements * 3
    
    result = {
        'frequency_mhz': frequency / 1e6,
        'wavelength_m': wavelength,
        'num_elements': num_elements,
        'driven_element_length_m': driven_length,
        'reflector_length_m': reflector_length,
        'director_length_m': director_length,
        'reflector_spacing_m': reflector_spacing,
        'director_spacing_m': director_spacing,
        'boom_length_m': boom_length,
        'gain_dbi': gain_dbi,
        'front_to_back_db': front_to_back,
        'beamwidth_degrees': beamwidth,
        'input_impedance_ohm': str(input_impedance),
        'bandwidth_percent': bandwidth_percent
    }
    
    if num_elements > 10:
        warnings.append("Many elements - mechanical stability may be challenging")
    if gain_dbi > 15:
        warnings.append("High gain - narrow beamwidth, precise aiming required")
    
    save_calculation('yagi_antenna',
        {'frequency': frequency, 'num_elements': num_elements},
        result, '; '.join(warnings))
    
    return result, warnings

def impedance_matching(source_impedance, load_impedance, frequency):
    warnings = []
    wavelength = SPEED_OF_LIGHT / frequency
    
    zs = complex(source_impedance) if isinstance(source_impedance, str) else source_impedance
    zl = complex(load_impedance) if isinstance(load_impedance, str) else load_impedance
    
    gamma = (zl - zs) / (zl + zs)
    vswr = (1 + abs(gamma)) / (1 - abs(gamma)) if abs(gamma) < 1 else float('inf')
    
    return_loss = -20 * np.log10(abs(gamma)) if abs(gamma) > 0 else float('inf')
    mismatch_loss = 10 * np.log10(1 - abs(gamma)**2) if abs(gamma) < 1 else float('-inf')
    
    if abs(zl.imag) < 1e-10 and abs(zs.imag) < 1e-10:
        q = math.sqrt(max(zs.real, zl.real) / min(zs.real, zl.real) - 1)
        
        if zs.real > zl.real:
            xl = q * zl.real
            xc = zs.real / q
        else:
            xc = zl.real / q
            xl = q * zs.real
        
        l_match = {
            'series_reactance': xl,
            'shunt_reactance': xc,
            'series_inductor_h': xl / (2 * math.pi * frequency),
            'shunt_capacitor_f': 1 / (2 * math.pi * frequency * xc)
        }
    else:
        l_match = {'note': 'Complex impedance matching requires Smith chart analysis'}
    
    result = {
        'source_impedance': str(zs),
        'load_impedance': str(zl),
        'reflection_coefficient': abs(gamma),
        'reflection_coefficient_db': float(return_loss),
        'vswr': vswr,
        'return_loss_db': float(return_loss),
        'mismatch_loss_db': float(mismatch_loss),
        'l_network_match': l_match,
        'frequency_mhz': frequency / 1e6
    }
    
    if vswr > 3:
        warnings.append("High VSWR - significant power reflection")
    if vswr > 1.5:
        warnings.append("Moderate mismatch - matching network recommended")
    
    save_calculation('impedance_matching',
        {'source': str(source_impedance), 'load': str(load_impedance), 'frequency': frequency},
        result, '; '.join(warnings))
    
    return result, warnings

def link_budget(tx_power_dbm, tx_gain_dbi, rx_gain_dbi, distance_km, frequency):
    warnings = []
    wavelength = SPEED_OF_LIGHT / frequency
    
    fspl_db = 20 * np.log10(distance_km * 1000) + 20 * np.log10(frequency) - 147.55
    
    eirp_dbm = tx_power_dbm + tx_gain_dbi
    
    rx_power_dbm = eirp_dbm - fspl_db + rx_gain_dbi
    
    thermal_noise_dbm = -174 + 10 * np.log10(1e6)
    
    snr_db = rx_power_dbm - thermal_noise_dbm
    
    result = {
        'tx_power_dbm': tx_power_dbm,
        'tx_gain_dbi': tx_gain_dbi,
        'rx_gain_dbi': rx_gain_dbi,
        'distance_km': distance_km,
        'frequency_mhz': frequency / 1e6,
        'wavelength_m': wavelength,
        'eirp_dbm': float(eirp_dbm),
        'fspl_db': float(fspl_db),
        'rx_power_dbm': float(rx_power_dbm),
        'estimated_snr_db': float(snr_db)
    }
    
    if rx_power_dbm < -100:
        warnings.append("Very weak received signal - may be below sensitivity")
    if fspl_db > 150:
        warnings.append("High path loss - consider higher gain antennas or repeaters")
    
    save_calculation('link_budget',
        {'tx_power': tx_power_dbm, 'distance': distance_km, 'frequency': frequency},
        result, '; '.join(warnings))
    
    return result, warnings

def get_rf_constants():
    return RF_CONSTANTS

def get_band_info(frequency):
    freq_mhz = frequency / 1e6
    
    bands = [
        (0.003, 0.03, 'VLF', 'Very Low Frequency'),
        (0.03, 0.3, 'LF', 'Low Frequency'),
        (0.3, 3, 'MF', 'Medium Frequency'),
        (3, 30, 'HF', 'High Frequency'),
        (30, 300, 'VHF', 'Very High Frequency'),
        (300, 3000, 'UHF', 'Ultra High Frequency'),
        (3000, 30000, 'SHF', 'Super High Frequency'),
        (30000, 300000, 'EHF', 'Extremely High Frequency')
    ]
    
    for low, high, abbr, name in bands:
        if low <= freq_mhz < high:
            return {'band': abbr, 'name': name, 'range_mhz': f'{low}-{high}'}
    
    return {'band': 'Unknown', 'name': 'Outside defined bands', 'range_mhz': 'N/A'}
