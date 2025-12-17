import random
import time
from datetime import datetime, timedelta
from database import save_iot_reading, get_iot_readings

SENSOR_THRESHOLDS = {
    'temperature': {'min': -10, 'max': 50, 'unit': 'C', 'alert_high': 40, 'alert_low': 0},
    'humidity': {'min': 0, 'max': 100, 'unit': '%', 'alert_high': 80, 'alert_low': 20},
    'voltage': {'min': 0, 'max': 500, 'unit': 'V', 'alert_high': 250, 'alert_low': 100},
    'current': {'min': 0, 'max': 100, 'unit': 'A', 'alert_high': 50, 'alert_low': 0},
    'power': {'min': 0, 'max': 10000, 'unit': 'W', 'alert_high': 5000, 'alert_low': 0},
    'pressure': {'min': 800, 'max': 1200, 'unit': 'hPa', 'alert_high': 1050, 'alert_low': 950},
    'light': {'min': 0, 'max': 100000, 'unit': 'lux', 'alert_high': 80000, 'alert_low': 100},
    'distance': {'min': 0, 'max': 500, 'unit': 'cm', 'alert_high': 400, 'alert_low': 5}
}

SIMULATED_DEVICES = {
    'temp_sensor_1': {'type': 'temperature', 'location': 'Room 1', 'base_value': 22},
    'temp_sensor_2': {'type': 'temperature', 'location': 'Room 2', 'base_value': 24},
    'humidity_sensor_1': {'type': 'humidity', 'location': 'Room 1', 'base_value': 45},
    'voltage_monitor_1': {'type': 'voltage', 'location': 'Main Panel', 'base_value': 220},
    'current_monitor_1': {'type': 'current', 'location': 'Main Panel', 'base_value': 15},
    'power_meter_1': {'type': 'power', 'location': 'Building', 'base_value': 3000}
}

def process_sensor_data(sensor_id, value, sensor_type=None):
    if sensor_type is None:
        if sensor_id in SIMULATED_DEVICES:
            sensor_type = SIMULATED_DEVICES[sensor_id]['type']
        else:
            sensor_type = 'generic'
    
    threshold = SENSOR_THRESHOLDS.get(sensor_type, {})
    unit = threshold.get('unit', 'units')
    
    alert = 0
    alert_message = None
    
    if threshold:
        if value >= threshold.get('alert_high', float('inf')):
            alert = 1
            alert_message = f"HIGH ALERT: {sensor_id} value {value} exceeds threshold {threshold['alert_high']}"
        elif value <= threshold.get('alert_low', float('-inf')):
            alert = 1
            alert_message = f"LOW ALERT: {sensor_id} value {value} below threshold {threshold['alert_low']}"
    
    save_iot_reading(sensor_id, value, unit, alert)
    
    result = {
        'sensor_id': sensor_id,
        'value': value,
        'unit': unit,
        'sensor_type': sensor_type,
        'timestamp': datetime.now().isoformat(),
        'alert': alert,
        'alert_message': alert_message,
        'status': 'recorded'
    }
    
    return result

def get_sensor_history(sensor_id=None, limit=100):
    readings = get_iot_readings(sensor_id, limit)
    
    history = []
    for reading in readings:
        history.append({
            'id': reading['id'],
            'sensor': reading['sensor'],
            'value': reading['value'],
            'unit': reading['unit'],
            'alert': reading['alert'],
            'timestamp': reading['timestamp']
        })
    
    return history

def simulate_sensor_reading(sensor_id=None):
    if sensor_id and sensor_id in SIMULATED_DEVICES:
        device = SIMULATED_DEVICES[sensor_id]
        sensor_type = device['type']
        base_value = device['base_value']
    else:
        devices = list(SIMULATED_DEVICES.keys())
        sensor_id = random.choice(devices)
        device = SIMULATED_DEVICES[sensor_id]
        sensor_type = device['type']
        base_value = device['base_value']
    
    threshold = SENSOR_THRESHOLDS.get(sensor_type, {})
    
    variation = base_value * 0.1
    value = base_value + random.uniform(-variation, variation)
    
    if random.random() < 0.05:
        if random.random() < 0.5:
            value = threshold.get('alert_high', base_value * 2) * 1.1
        else:
            value = threshold.get('alert_low', 0) * 0.9
    
    value = round(value, 2)
    
    return process_sensor_data(sensor_id, value, sensor_type)

def simulate_batch_readings(num_readings=10, interval_seconds=1):
    readings = []
    
    for _ in range(num_readings):
        for sensor_id in SIMULATED_DEVICES.keys():
            reading = simulate_sensor_reading(sensor_id)
            readings.append(reading)
    
    return readings

def get_device_status():
    status = []
    
    for device_id, device_info in SIMULATED_DEVICES.items():
        history = get_sensor_history(device_id, limit=1)
        
        device_status = {
            'device_id': device_id,
            'type': device_info['type'],
            'location': device_info['location'],
            'last_reading': history[0] if history else None,
            'status': 'online' if history else 'no_data'
        }
        status.append(device_status)
    
    return status

def check_alerts(sensor_id=None):
    readings = get_iot_readings(sensor_id, limit=100)
    
    alerts = []
    for reading in readings:
        if reading['alert']:
            alerts.append({
                'sensor': reading['sensor'],
                'value': reading['value'],
                'unit': reading['unit'],
                'timestamp': reading['timestamp'],
                'severity': 'high' if abs(reading['value']) > SENSOR_THRESHOLDS.get(
                    SIMULATED_DEVICES.get(reading['sensor'], {}).get('type', ''), {}
                ).get('alert_high', float('inf')) * 1.2 else 'medium'
            })
    
    return alerts

def get_statistics(sensor_id, hours=24):
    readings = get_iot_readings(sensor_id, limit=1000)
    
    if not readings:
        return {'error': 'No data available'}
    
    values = [r['value'] for r in readings]
    
    import numpy as np
    values_array = np.array(values)
    
    stats = {
        'sensor_id': sensor_id,
        'period_hours': hours,
        'num_readings': len(values),
        'min': float(np.min(values_array)),
        'max': float(np.max(values_array)),
        'mean': float(np.mean(values_array)),
        'std': float(np.std(values_array)),
        'median': float(np.median(values_array))
    }
    
    return stats

def export_sensor_data(sensor_id=None, format='json'):
    readings = get_sensor_history(sensor_id, limit=1000)
    
    if format == 'json':
        return readings
    elif format == 'csv':
        if not readings:
            return "No data"
        
        headers = ['id', 'sensor', 'value', 'unit', 'alert', 'timestamp']
        csv_lines = [','.join(headers)]
        
        for reading in readings:
            row = [str(reading.get(h, '')) for h in headers]
            csv_lines.append(','.join(row))
        
        return '\n'.join(csv_lines)
    
    return readings

def get_sensor_thresholds():
    return SENSOR_THRESHOLDS

def get_available_devices():
    return SIMULATED_DEVICES
