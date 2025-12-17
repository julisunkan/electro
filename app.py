from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import json
import io
import csv
from datetime import datetime

from database import init_db, get_calculations
from modules.calculator import (
    ohms_law, rc_circuit, rl_circuit, rlc_circuit, filter_design,
    amplifier_gain, tolerance_analysis, power_rating_check, voltage_divider,
    series_resistance, parallel_resistance, convert_unit, ENGINEERING_CONSTANTS, UNIT_PREFIXES
)
from modules.circuit_analysis import (
    dc_analysis, ac_analysis, frequency_response, efficiency_analysis,
    comparative_analysis, generate_conclusion
)
from modules.signal_processing import (
    generate_signal, compute_fft, add_noise, bandwidth_analysis,
    filter_signal, signal_statistics
)
from modules.antenna_rf import (
    frequency_to_wavelength, wavelength_to_frequency, dipole_antenna,
    yagi_antenna, impedance_matching, link_budget, get_rf_constants, get_band_info
)
from modules.solar_energy import (
    panel_sizing, battery_sizing, inverter_sizing, system_losses,
    roi_analysis, compare_systems, generate_solar_report
)
from modules.energy_analyzer import (
    analyze_csv, detect_peaks, calculate_efficiency, cost_estimation,
    comparative_analysis as energy_comparison, generate_recommendations, get_historical_data
)
from modules.fault_diagnosis import (
    diagnose_fault, get_repair_steps, get_component_tests,
    generate_diagnosis_report, get_all_symptoms, get_fault_types
)
from modules.iot_api import (
    process_sensor_data, get_sensor_history, simulate_sensor_reading,
    simulate_batch_readings, get_device_status, check_alerts,
    get_statistics, export_sensor_data, get_sensor_thresholds, get_available_devices
)
from modules.virtual_lab import (
    run_rc_transient, run_rlc_resonance, run_diode_characteristics,
    run_amplifier_gain, run_experiment_with_tolerance, generate_lab_report,
    get_experiment_list, get_experiment_theory
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'electrohub-secret-key')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculator')
def calculator():
    return render_template('calculator.html', constants=ENGINEERING_CONSTANTS, prefixes=UNIT_PREFIXES)

@app.route('/circuit')
def circuit():
    return render_template('circuit.html')

@app.route('/signal')
def signal_page():
    return render_template('signal.html')

@app.route('/antenna')
def antenna():
    return render_template('antenna.html', rf_constants=get_rf_constants())

@app.route('/solar')
def solar():
    return render_template('solar.html')

@app.route('/energy')
def energy():
    return render_template('energy.html')

@app.route('/iot')
def iot():
    return render_template('iot.html', devices=get_available_devices(), thresholds=get_sensor_thresholds())

@app.route('/lab')
def lab():
    return render_template('lab.html', experiments=get_experiment_list())

@app.route('/api/calculator/ohms-law', methods=['POST'])
def api_ohms_law():
    data = request.json
    result, warnings = ohms_law(
        voltage=data.get('voltage'),
        current=data.get('current'),
        resistance=data.get('resistance')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/rc-circuit', methods=['POST'])
def api_rc_circuit():
    data = request.json
    result, warnings = rc_circuit(
        resistance=data.get('resistance'),
        capacitance=data.get('capacitance'),
        frequency=data.get('frequency')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/rl-circuit', methods=['POST'])
def api_rl_circuit():
    data = request.json
    result, warnings = rl_circuit(
        resistance=data.get('resistance'),
        inductance=data.get('inductance'),
        frequency=data.get('frequency')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/rlc-circuit', methods=['POST'])
def api_rlc_circuit():
    data = request.json
    result, warnings = rlc_circuit(
        resistance=data.get('resistance'),
        inductance=data.get('inductance'),
        capacitance=data.get('capacitance'),
        frequency=data.get('frequency')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/filter', methods=['POST'])
def api_filter():
    data = request.json
    result, warnings = filter_design(
        filter_type=data.get('filter_type'),
        cutoff_freq=data.get('cutoff_freq'),
        resistance=data.get('resistance'),
        capacitance=data.get('capacitance')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/amplifier', methods=['POST'])
def api_amplifier():
    data = request.json
    result, warnings = amplifier_gain(
        input_voltage=data.get('input_voltage'),
        output_voltage=data.get('output_voltage'),
        gain_db=data.get('gain_db'),
        gain_linear=data.get('gain_linear')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/tolerance', methods=['POST'])
def api_tolerance():
    data = request.json
    result, warnings = tolerance_analysis(
        nominal_value=data.get('nominal_value'),
        tolerance_percent=data.get('tolerance_percent')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/power-rating', methods=['POST'])
def api_power_rating():
    data = request.json
    result, warnings = power_rating_check(
        voltage=data.get('voltage'),
        current=data.get('current'),
        rated_power=data.get('rated_power'),
        derating_factor=data.get('derating_factor', 0.8)
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/voltage-divider', methods=['POST'])
def api_voltage_divider():
    data = request.json
    result, warnings = voltage_divider(
        vin=data.get('vin'),
        r1=data.get('r1'),
        r2=data.get('r2')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/calculator/unit-convert', methods=['POST'])
def api_unit_convert():
    data = request.json
    result = convert_unit(
        value=data.get('value'),
        from_prefix=data.get('from_prefix', ''),
        to_prefix=data.get('to_prefix', '')
    )
    return jsonify({'result': result})

@app.route('/api/calculator/history')
def api_calculator_history():
    history = get_calculations(limit=50)
    return jsonify([dict(row) for row in history])

@app.route('/api/circuit/dc-analysis', methods=['POST'])
def api_dc_analysis():
    data = request.json
    result, warnings = dc_analysis(
        voltage_sources=data.get('voltage_sources', []),
        current_sources=data.get('current_sources', []),
        resistances=data.get('resistances', []),
        connections=data.get('connections', {})
    )
    conclusion = generate_conclusion('dc', result, warnings)
    return jsonify({'result': result, 'warnings': warnings, 'conclusion': conclusion})

@app.route('/api/circuit/ac-analysis', methods=['POST'])
def api_ac_analysis():
    data = request.json
    result, warnings = ac_analysis(
        voltage_amplitude=data.get('voltage_amplitude'),
        frequency=data.get('frequency'),
        resistance=data.get('resistance'),
        inductance=data.get('inductance', 0),
        capacitance=data.get('capacitance', 0)
    )
    conclusion = generate_conclusion('ac', result, warnings)
    return jsonify({'result': result, 'warnings': warnings, 'conclusion': conclusion})

@app.route('/api/circuit/frequency-response', methods=['POST'])
def api_frequency_response():
    data = request.json
    result = frequency_response(
        resistance=data.get('resistance'),
        inductance=data.get('inductance'),
        capacitance=data.get('capacitance'),
        freq_start=data.get('freq_start', 1),
        freq_end=data.get('freq_end', 1e6),
        points=data.get('points', 100)
    )
    return jsonify({'result': result})

@app.route('/api/circuit/efficiency', methods=['POST'])
def api_efficiency():
    data = request.json
    result, warnings = efficiency_analysis(
        input_power=data.get('input_power'),
        output_power=data.get('output_power'),
        losses=data.get('losses')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/signal/generate', methods=['POST'])
def api_signal_generate():
    data = request.json
    result = generate_signal(
        signal_type=data.get('signal_type', 'sine'),
        frequency=data.get('frequency', 1000),
        amplitude=data.get('amplitude', 1),
        duration=data.get('duration', 0.01),
        sample_rate=data.get('sample_rate', 10000),
        phase=data.get('phase', 0),
        dc_offset=data.get('dc_offset', 0)
    )
    return jsonify({'result': result})

@app.route('/api/signal/fft', methods=['POST'])
def api_signal_fft():
    data = request.json
    result = compute_fft(
        signal_data=data.get('signal_data'),
        sample_rate=data.get('sample_rate')
    )
    return jsonify({'result': result})

@app.route('/api/signal/noise', methods=['POST'])
def api_signal_noise():
    data = request.json
    result = add_noise(
        signal_data=data.get('signal_data'),
        noise_type=data.get('noise_type', 'gaussian'),
        snr_db=data.get('snr_db', 20)
    )
    return jsonify({'result': result})

@app.route('/api/signal/bandwidth', methods=['POST'])
def api_signal_bandwidth():
    data = request.json
    result = bandwidth_analysis(
        signal_data=data.get('signal_data'),
        sample_rate=data.get('sample_rate'),
        threshold_db=data.get('threshold_db', -3)
    )
    return jsonify({'result': result})

@app.route('/api/signal/filter', methods=['POST'])
def api_signal_filter():
    data = request.json
    result = filter_signal(
        signal_data=data.get('signal_data'),
        sample_rate=data.get('sample_rate'),
        filter_type=data.get('filter_type'),
        cutoff_freq=data.get('cutoff_freq'),
        order=data.get('order', 4)
    )
    return jsonify({'result': result})

@app.route('/api/antenna/frequency-wavelength', methods=['POST'])
def api_freq_wavelength():
    data = request.json
    if data.get('frequency'):
        result = frequency_to_wavelength(data.get('frequency'))
    else:
        result = wavelength_to_frequency(data.get('wavelength'))
    return jsonify({'result': result})

@app.route('/api/antenna/dipole', methods=['POST'])
def api_dipole():
    data = request.json
    result, warnings = dipole_antenna(
        frequency=data.get('frequency'),
        wire_diameter=data.get('wire_diameter', 0.002)
    )
    band_info = get_band_info(data.get('frequency'))
    result['band_info'] = band_info
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/antenna/yagi', methods=['POST'])
def api_yagi():
    data = request.json
    result, warnings = yagi_antenna(
        frequency=data.get('frequency'),
        num_elements=data.get('num_elements', 3),
        boom_length_wavelengths=data.get('boom_length')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/antenna/impedance', methods=['POST'])
def api_impedance():
    data = request.json
    result, warnings = impedance_matching(
        source_impedance=data.get('source_impedance'),
        load_impedance=data.get('load_impedance'),
        frequency=data.get('frequency')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/antenna/link-budget', methods=['POST'])
def api_link_budget():
    data = request.json
    result, warnings = link_budget(
        tx_power_dbm=data.get('tx_power_dbm'),
        tx_gain_dbi=data.get('tx_gain_dbi'),
        rx_gain_dbi=data.get('rx_gain_dbi'),
        distance_km=data.get('distance_km'),
        frequency=data.get('frequency')
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/solar/panel-sizing', methods=['POST'])
def api_panel_sizing():
    data = request.json
    result, warnings = panel_sizing(
        daily_energy_kwh=data.get('daily_energy_kwh'),
        peak_sun_hours=data.get('peak_sun_hours'),
        system_efficiency=data.get('system_efficiency', 0.8),
        panel_wattage=data.get('panel_wattage', 400)
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/solar/battery-sizing', methods=['POST'])
def api_battery_sizing():
    data = request.json
    result, warnings = battery_sizing(
        daily_energy_kwh=data.get('daily_energy_kwh'),
        autonomy_days=data.get('autonomy_days'),
        depth_of_discharge=data.get('depth_of_discharge', 0.8),
        battery_voltage=data.get('battery_voltage', 48),
        battery_efficiency=data.get('battery_efficiency', 0.9)
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/solar/inverter-sizing', methods=['POST'])
def api_inverter_sizing():
    data = request.json
    result, warnings = inverter_sizing(
        peak_load_w=data.get('peak_load_w'),
        surge_factor=data.get('surge_factor', 1.25),
        continuous_factor=data.get('continuous_factor', 1.1)
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/solar/losses', methods=['POST'])
def api_solar_losses():
    data = request.json
    result = system_losses(
        panel_capacity_kw=data.get('panel_capacity_kw'),
        soiling=data.get('soiling', 0.02),
        shading=data.get('shading', 0.03),
        wiring=data.get('wiring', 0.02),
        inverter_loss=data.get('inverter_loss', 0.04),
        temperature=data.get('temperature', 0.05),
        mismatch=data.get('mismatch', 0.02)
    )
    return jsonify({'result': result})

@app.route('/api/solar/roi', methods=['POST'])
def api_solar_roi():
    data = request.json
    result, warnings = roi_analysis(
        system_cost=data.get('system_cost'),
        annual_production_kwh=data.get('annual_production_kwh'),
        electricity_rate=data.get('electricity_rate'),
        annual_degradation=data.get('annual_degradation', 0.005),
        incentives=data.get('incentives', 0),
        years=data.get('years', 25)
    )
    return jsonify({'result': result, 'warnings': warnings})

@app.route('/api/solar/report', methods=['POST'])
def api_solar_report():
    data = request.json
    filepath = generate_solar_report(data, f"solar_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    return jsonify({'filepath': filepath, 'message': 'Report generated successfully'})

@app.route('/api/energy/analyze', methods=['POST'])
def api_energy_analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filepath = os.path.join('static', 'plots', 'temp_upload.csv')
    file.save(filepath)
    
    cost_per_kwh = float(request.form.get('cost_per_kwh', 0.12))
    result, warnings = analyze_csv(filepath, cost_per_kwh=cost_per_kwh)
    
    os.remove(filepath)
    
    recommendations = generate_recommendations(result)
    return jsonify({'result': result, 'warnings': warnings, 'recommendations': recommendations})

@app.route('/api/energy/efficiency', methods=['POST'])
def api_energy_efficiency():
    data = request.json
    result = calculate_efficiency(
        input_energy=data.get('input_energy'),
        output_energy=data.get('output_energy'),
        standby_power=data.get('standby_power', 0),
        operating_hours=data.get('operating_hours', 24)
    )
    return jsonify({'result': result})

@app.route('/api/energy/cost', methods=['POST'])
def api_energy_cost():
    data = request.json
    result = cost_estimation(
        energy_kwh=data.get('energy_kwh'),
        rate_structure=data.get('rate_structure', 'flat'),
        flat_rate=data.get('flat_rate', 0.12),
        peak_rate=data.get('peak_rate', 0.20),
        offpeak_rate=data.get('offpeak_rate', 0.08),
        peak_percentage=data.get('peak_percentage', 0.4)
    )
    return jsonify({'result': result})

@app.route('/api/energy/history')
def api_energy_history():
    history = get_historical_data(limit=20)
    return jsonify([dict(row) for row in history])

@app.route('/api/fault/diagnose', methods=['POST'])
def api_fault_diagnose():
    data = request.json
    symptoms = data.get('symptoms', [])
    diagnosis = diagnose_fault(symptoms)
    report = generate_diagnosis_report(symptoms, diagnosis)
    return jsonify({'diagnosis': diagnosis, 'report': report})

@app.route('/api/fault/repair-steps', methods=['POST'])
def api_repair_steps():
    data = request.json
    result = get_repair_steps(
        fault_type=data.get('fault_type'),
        cause_index=data.get('cause_index', 0)
    )
    return jsonify({'result': result})

@app.route('/api/fault/component-tests', methods=['POST'])
def api_component_tests():
    data = request.json
    result = get_component_tests(data.get('component_type'))
    return jsonify({'result': result})

@app.route('/api/fault/symptoms')
def api_get_symptoms():
    return jsonify({'symptoms': get_all_symptoms(), 'fault_types': get_fault_types()})

@app.route('/api/iot/data', methods=['POST'])
def api_iot_data():
    data = request.json
    result = process_sensor_data(
        sensor_id=data.get('sensor_id'),
        value=data.get('value'),
        sensor_type=data.get('sensor_type')
    )
    return jsonify({'result': result})

@app.route('/api/iot/history')
def api_iot_history():
    sensor_id = request.args.get('sensor_id')
    limit = int(request.args.get('limit', 100))
    history = get_sensor_history(sensor_id, limit)
    return jsonify({'history': history})

@app.route('/api/iot/simulate', methods=['POST'])
def api_iot_simulate():
    data = request.json
    sensor_id = data.get('sensor_id')
    result = simulate_sensor_reading(sensor_id)
    return jsonify({'result': result})

@app.route('/api/iot/simulate-batch', methods=['POST'])
def api_iot_simulate_batch():
    data = request.json
    num_readings = data.get('num_readings', 10)
    results = simulate_batch_readings(num_readings)
    return jsonify({'results': results})

@app.route('/api/iot/status')
def api_iot_status():
    status = get_device_status()
    return jsonify({'devices': status})

@app.route('/api/iot/alerts')
def api_iot_alerts():
    sensor_id = request.args.get('sensor_id')
    alerts = check_alerts(sensor_id)
    return jsonify({'alerts': alerts})

@app.route('/api/iot/statistics')
def api_iot_statistics():
    sensor_id = request.args.get('sensor_id')
    hours = int(request.args.get('hours', 24))
    stats = get_statistics(sensor_id, hours)
    return jsonify({'statistics': stats})

@app.route('/api/iot/export')
def api_iot_export():
    sensor_id = request.args.get('sensor_id')
    format_type = request.args.get('format', 'json')
    data = export_sensor_data(sensor_id, format_type)
    
    if format_type == 'csv':
        return Response(data, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=sensor_data.csv'})
    return jsonify({'data': data})

@app.route('/api/lab/run', methods=['POST'])
def api_lab_run():
    data = request.json
    experiment = data.get('experiment')
    params = data.get('parameters', {})
    with_tolerance = data.get('with_tolerance', False)
    tolerance_percent = data.get('tolerance_percent', 5)
    
    if with_tolerance:
        result = run_experiment_with_tolerance(experiment, params, tolerance_percent)
    else:
        if experiment == 'rc_transient':
            result = run_rc_transient(**params)
        elif experiment == 'rlc_resonance':
            result = run_rlc_resonance(**params)
        elif experiment == 'diode_characteristics':
            result = run_diode_characteristics(**params)
        elif experiment == 'amplifier_gain':
            result = run_amplifier_gain(**params)
        else:
            return jsonify({'error': 'Unknown experiment'}), 400
    
    return jsonify({'result': result})

@app.route('/api/lab/report', methods=['POST'])
def api_lab_report():
    data = request.json
    filepath = generate_lab_report(data.get('result'))
    return jsonify({'filepath': filepath, 'message': 'Lab report generated successfully'})

@app.route('/api/lab/theory')
def api_lab_theory():
    experiment = request.args.get('experiment')
    theory = get_experiment_theory(experiment)
    return jsonify({'theory': theory})

@app.route('/api/constants')
def api_constants():
    return jsonify({
        'engineering_constants': ENGINEERING_CONSTANTS,
        'unit_prefixes': UNIT_PREFIXES,
        'rf_constants': get_rf_constants()
    })

@app.route('/download/<path:filename>')
def download_file(filename):
    filepath = os.path.join('static', 'plots', filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True, mimetype='application/pdf')
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/download-pdf/<path:filename>')
def download_pdf(filename):
    filepath = os.path.join('static', 'plots', filename)
    if os.path.exists(filepath):
        return send_file(
            filepath, 
            as_attachment=True, 
            download_name=filename,
            mimetype='application/pdf'
        )
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    os.makedirs('static/plots', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)
