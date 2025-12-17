import numpy as np
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq
import math
from database import save_calculation

def generate_signal(signal_type, frequency, amplitude, duration, sample_rate=10000, phase=0, dc_offset=0):
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    if signal_type == 'sine':
        signal = amplitude * np.sin(2 * np.pi * frequency * t + np.radians(phase)) + dc_offset
    elif signal_type == 'cosine':
        signal = amplitude * np.cos(2 * np.pi * frequency * t + np.radians(phase)) + dc_offset
    elif signal_type == 'square':
        signal = amplitude * scipy_signal.square(2 * np.pi * frequency * t + np.radians(phase)) + dc_offset
    elif signal_type == 'sawtooth':
        signal = amplitude * scipy_signal.sawtooth(2 * np.pi * frequency * t + np.radians(phase)) + dc_offset
    elif signal_type == 'triangle':
        signal = amplitude * scipy_signal.sawtooth(2 * np.pi * frequency * t + np.radians(phase), width=0.5) + dc_offset
    else:
        signal = np.zeros_like(t)
        signal_type = 'unknown'
    
    result = {
        'time': t.tolist(),
        'signal': signal.tolist(),
        'signal_type': signal_type,
        'frequency': frequency,
        'amplitude': amplitude,
        'sample_rate': sample_rate,
        'duration': duration,
        'rms': float(np.sqrt(np.mean(signal**2))),
        'peak_to_peak': float(np.max(signal) - np.min(signal))
    }
    
    save_calculation('signal_generator',
        {'type': signal_type, 'frequency': frequency, 'amplitude': amplitude},
        {'rms': result['rms'], 'peak_to_peak': result['peak_to_peak']}, '')
    
    return result

def compute_fft(signal_data, sample_rate):
    signal = np.array(signal_data)
    n = len(signal)
    
    signal_windowed = signal * np.hanning(n)
    
    fft_result = fft(signal_windowed)
    frequencies = fftfreq(n, 1/sample_rate)
    
    positive_freqs = frequencies[:n//2]
    magnitude = np.abs(fft_result[:n//2]) * 2 / n
    phase = np.angle(fft_result[:n//2], deg=True)
    
    magnitude_db = 20 * np.log10(magnitude + 1e-10)
    
    dominant_idx = np.argmax(magnitude[1:]) + 1
    dominant_freq = positive_freqs[dominant_idx]
    
    result = {
        'frequencies': positive_freqs.tolist(),
        'magnitude': magnitude.tolist(),
        'magnitude_db': magnitude_db.tolist(),
        'phase': phase.tolist(),
        'dominant_frequency': float(dominant_freq),
        'dominant_magnitude': float(magnitude[dominant_idx]),
        'dc_component': float(magnitude[0])
    }
    
    return result

def add_noise(signal_data, noise_type='gaussian', snr_db=20):
    signal = np.array(signal_data)
    signal_power = np.mean(signal**2)
    
    snr_linear = 10**(snr_db/10)
    noise_power = signal_power / snr_linear
    
    if noise_type == 'gaussian':
        noise = np.random.normal(0, np.sqrt(noise_power), len(signal))
    elif noise_type == 'uniform':
        noise = np.random.uniform(-np.sqrt(3*noise_power), np.sqrt(3*noise_power), len(signal))
    elif noise_type == 'pink':
        white_noise = np.random.normal(0, 1, len(signal))
        fft_white = fft(white_noise)
        frequencies = fftfreq(len(white_noise))
        frequencies[0] = 1e-10
        pink_filter = 1 / np.sqrt(np.abs(frequencies))
        pink_fft = fft_white * pink_filter
        noise = np.real(np.fft.ifft(pink_fft))
        noise = noise * np.sqrt(noise_power) / np.std(noise)
    else:
        noise = np.zeros_like(signal)
    
    noisy_signal = signal + noise
    
    actual_snr = 10 * np.log10(signal_power / np.mean(noise**2)) if np.mean(noise**2) > 0 else float('inf')
    
    result = {
        'noisy_signal': noisy_signal.tolist(),
        'noise': noise.tolist(),
        'noise_type': noise_type,
        'target_snr_db': snr_db,
        'actual_snr_db': float(actual_snr),
        'noise_rms': float(np.sqrt(np.mean(noise**2)))
    }
    
    return result

def bandwidth_analysis(signal_data, sample_rate, threshold_db=-3):
    fft_result = compute_fft(signal_data, sample_rate)
    
    magnitude_db = np.array(fft_result['magnitude_db'])
    frequencies = np.array(fft_result['frequencies'])
    
    max_magnitude = np.max(magnitude_db)
    threshold = max_magnitude + threshold_db
    
    above_threshold = magnitude_db >= threshold
    
    if np.any(above_threshold):
        freq_above = frequencies[above_threshold]
        lower_freq = float(np.min(freq_above))
        upper_freq = float(np.max(freq_above))
        bandwidth = upper_freq - lower_freq
        center_freq = (upper_freq + lower_freq) / 2
    else:
        lower_freq = 0
        upper_freq = 0
        bandwidth = 0
        center_freq = 0
    
    result = {
        'lower_frequency': lower_freq,
        'upper_frequency': upper_freq,
        'bandwidth': bandwidth,
        'center_frequency': center_freq,
        'threshold_db': threshold_db,
        'peak_magnitude_db': float(max_magnitude)
    }
    
    save_calculation('bandwidth_analysis',
        {'sample_rate': sample_rate, 'threshold_db': threshold_db},
        result, '')
    
    return result

def filter_signal(signal_data, sample_rate, filter_type, cutoff_freq, order=4):
    signal = np.array(signal_data)
    nyquist = sample_rate / 2
    
    if isinstance(cutoff_freq, (list, tuple)):
        normalized_cutoff = [f / nyquist for f in cutoff_freq]
    else:
        normalized_cutoff = cutoff_freq / nyquist
    
    if isinstance(normalized_cutoff, list):
        if any(f >= 1 or f <= 0 for f in normalized_cutoff):
            return {
                'filtered_signal': signal_data,
                'error': 'Cutoff frequency must be between 0 and Nyquist frequency'
            }
    elif normalized_cutoff >= 1 or normalized_cutoff <= 0:
        return {
            'filtered_signal': signal_data,
            'error': 'Cutoff frequency must be between 0 and Nyquist frequency'
        }
    
    if filter_type == 'lowpass':
        b, a = scipy_signal.butter(order, normalized_cutoff, btype='low')
    elif filter_type == 'highpass':
        b, a = scipy_signal.butter(order, normalized_cutoff, btype='high')
    elif filter_type == 'bandpass':
        b, a = scipy_signal.butter(order, normalized_cutoff, btype='band')
    elif filter_type == 'bandstop':
        b, a = scipy_signal.butter(order, normalized_cutoff, btype='bandstop')
    else:
        return {'filtered_signal': signal_data, 'error': 'Unknown filter type'}
    
    filtered = scipy_signal.filtfilt(b, a, signal)
    
    result = {
        'filtered_signal': filtered.tolist(),
        'filter_type': filter_type,
        'cutoff_frequency': cutoff_freq,
        'order': order,
        'original_rms': float(np.sqrt(np.mean(signal**2))),
        'filtered_rms': float(np.sqrt(np.mean(filtered**2)))
    }
    
    return result

def signal_statistics(signal_data):
    signal = np.array(signal_data)
    
    result = {
        'mean': float(np.mean(signal)),
        'std': float(np.std(signal)),
        'rms': float(np.sqrt(np.mean(signal**2))),
        'peak': float(np.max(np.abs(signal))),
        'peak_to_peak': float(np.max(signal) - np.min(signal)),
        'crest_factor': float(np.max(np.abs(signal)) / np.sqrt(np.mean(signal**2))) if np.mean(signal**2) > 0 else 0,
        'min': float(np.min(signal)),
        'max': float(np.max(signal))
    }
    
    return result
