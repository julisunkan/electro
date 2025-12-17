import numpy as np
import pandas as pd
from scipy import signal
from database import save_energy_data, get_energy_data
import os

def analyze_csv(file_path, time_column='time', power_column='power', cost_per_kwh=0.12):
    warnings = []
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        return {'error': str(e)}, ['Failed to read CSV file']
    
    if time_column not in df.columns:
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                time_column = col
                break
    
    if power_column not in df.columns:
        for col in df.columns:
            if 'power' in col.lower() or 'watt' in col.lower() or 'kw' in col.lower():
                power_column = col
                break
    
    if power_column not in df.columns:
        return {'error': 'Power column not found'}, ['Could not identify power data column']
    
    power_data = df[power_column].dropna()
    
    if len(power_data) > 1:
        time_interval_hours = 1 / len(power_data) * 24
    else:
        time_interval_hours = 1
    
    total_energy_kwh = np.sum(power_data) * time_interval_hours / 1000
    
    peak_load = np.max(power_data)
    avg_load = np.mean(power_data)
    min_load = np.min(power_data)
    
    load_factor = avg_load / peak_load if peak_load > 0 else 0
    
    total_cost = total_energy_kwh * cost_per_kwh
    
    result = {
        'filename': os.path.basename(file_path),
        'total_readings': len(power_data),
        'total_energy_kwh': round(total_energy_kwh, 2),
        'peak_load_w': round(peak_load, 2),
        'average_load_w': round(avg_load, 2),
        'min_load_w': round(min_load, 2),
        'load_factor': round(load_factor, 3),
        'estimated_cost': round(total_cost, 2),
        'cost_per_kwh': cost_per_kwh
    }
    
    if load_factor < 0.3:
        warnings.append("Low load factor - highly variable consumption")
    if peak_load > avg_load * 5:
        warnings.append("High peak-to-average ratio - consider demand management")
    
    save_energy_data(
        result['filename'],
        result['total_energy_kwh'],
        result['peak_load_w'],
        result['load_factor'],
        result['estimated_cost']
    )
    
    return result, warnings

def detect_peaks(power_data, threshold_factor=1.5):
    data = np.array(power_data)
    mean_power = np.mean(data)
    threshold = mean_power * threshold_factor
    
    peaks, properties = signal.find_peaks(data, height=threshold, distance=5)
    
    peak_times = peaks.tolist()
    peak_values = data[peaks].tolist() if len(peaks) > 0 else []
    
    result = {
        'num_peaks': len(peaks),
        'peak_indices': peak_times,
        'peak_values': peak_values,
        'threshold_used': threshold,
        'mean_power': mean_power,
        'max_peak': max(peak_values) if peak_values else 0
    }
    
    return result

def calculate_efficiency(input_energy, output_energy, standby_power=0, operating_hours=24):
    standby_loss = standby_power * operating_hours / 1000
    
    if input_energy > 0:
        efficiency = (output_energy / input_energy) * 100
    else:
        efficiency = 0
    
    losses = input_energy - output_energy
    
    result = {
        'input_energy_kwh': input_energy,
        'output_energy_kwh': output_energy,
        'losses_kwh': losses,
        'efficiency_percent': round(efficiency, 2),
        'standby_loss_kwh': standby_loss,
        'total_losses_kwh': losses + standby_loss
    }
    
    if efficiency < 50:
        result['rating'] = 'Poor'
    elif efficiency < 70:
        result['rating'] = 'Fair'
    elif efficiency < 85:
        result['rating'] = 'Good'
    else:
        result['rating'] = 'Excellent'
    
    return result

def cost_estimation(energy_kwh, rate_structure='flat', flat_rate=0.12, peak_rate=0.20, offpeak_rate=0.08, peak_percentage=0.4):
    if rate_structure == 'flat':
        total_cost = energy_kwh * flat_rate
        breakdown = {'all_hours': {'kwh': energy_kwh, 'rate': flat_rate, 'cost': total_cost}}
    elif rate_structure == 'tou':
        peak_energy = energy_kwh * peak_percentage
        offpeak_energy = energy_kwh * (1 - peak_percentage)
        peak_cost = peak_energy * peak_rate
        offpeak_cost = offpeak_energy * offpeak_rate
        total_cost = peak_cost + offpeak_cost
        breakdown = {
            'peak': {'kwh': peak_energy, 'rate': peak_rate, 'cost': peak_cost},
            'offpeak': {'kwh': offpeak_energy, 'rate': offpeak_rate, 'cost': offpeak_cost}
        }
    else:
        total_cost = energy_kwh * flat_rate
        breakdown = {'default': {'kwh': energy_kwh, 'rate': flat_rate, 'cost': total_cost}}
    
    result = {
        'total_energy_kwh': energy_kwh,
        'rate_structure': rate_structure,
        'total_cost': round(total_cost, 2),
        'cost_breakdown': breakdown,
        'cost_per_kwh_effective': round(total_cost / energy_kwh, 4) if energy_kwh > 0 else 0
    }
    
    return result

def comparative_analysis(datasets):
    comparison = []
    
    for i, data in enumerate(datasets):
        power_data = data.get('power_data', [])
        name = data.get('name', f'Dataset {i+1}')
        
        if power_data:
            total_energy = sum(power_data) / 1000
            peak = max(power_data)
            avg = sum(power_data) / len(power_data)
            load_factor = avg / peak if peak > 0 else 0
        else:
            total_energy = data.get('total_energy', 0)
            peak = data.get('peak_load', 0)
            avg = data.get('avg_load', 0)
            load_factor = data.get('load_factor', 0)
        
        comparison.append({
            'name': name,
            'total_energy_kwh': round(total_energy, 2),
            'peak_load_w': round(peak, 2),
            'average_load_w': round(avg, 2),
            'load_factor': round(load_factor, 3)
        })
    
    if comparison:
        best_efficiency = max(comparison, key=lambda x: x['load_factor'])
        lowest_peak = min(comparison, key=lambda x: x['peak_load_w'])
        lowest_consumption = min(comparison, key=lambda x: x['total_energy_kwh'])
        
        conclusion = {
            'best_load_factor': best_efficiency['name'],
            'lowest_peak_demand': lowest_peak['name'],
            'lowest_consumption': lowest_consumption['name']
        }
    else:
        conclusion = {}
    
    return {
        'comparison_data': comparison,
        'conclusions': conclusion
    }

def generate_recommendations(analysis_result):
    recommendations = []
    
    load_factor = analysis_result.get('load_factor', 0)
    peak_load = analysis_result.get('peak_load_w', 0)
    avg_load = analysis_result.get('average_load_w', 0)
    
    if load_factor < 0.4:
        recommendations.append({
            'priority': 'High',
            'category': 'Load Management',
            'recommendation': 'Improve load factor by distributing energy usage more evenly',
            'potential_savings': '15-25%'
        })
    
    if peak_load > avg_load * 3:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Peak Shaving',
            'recommendation': 'Consider peak shaving strategies or demand response',
            'potential_savings': '10-20%'
        })
    
    if analysis_result.get('total_energy_kwh', 0) > 1000:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Energy Audit',
            'recommendation': 'Conduct detailed energy audit to identify inefficiencies',
            'potential_savings': '5-15%'
        })
    
    recommendations.append({
        'priority': 'Low',
        'category': 'Monitoring',
        'recommendation': 'Implement continuous energy monitoring for trend analysis',
        'potential_savings': 'Varies'
    })
    
    return recommendations

def get_historical_data(limit=20):
    return get_energy_data(limit)
