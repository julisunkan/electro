import numpy as np
import math
from database import save_calculation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

def panel_sizing(daily_energy_kwh, peak_sun_hours, system_efficiency=0.8, panel_wattage=400):
    warnings = []
    
    required_daily_production = daily_energy_kwh / system_efficiency
    
    required_capacity_kw = required_daily_production / peak_sun_hours
    
    num_panels = math.ceil((required_capacity_kw * 1000) / panel_wattage)
    
    actual_capacity_kw = (num_panels * panel_wattage) / 1000
    actual_daily_production = actual_capacity_kw * peak_sun_hours * system_efficiency
    
    typical_panel_area = 2.0
    total_area = num_panels * typical_panel_area
    
    result = {
        'daily_energy_required_kwh': daily_energy_kwh,
        'peak_sun_hours': peak_sun_hours,
        'system_efficiency': system_efficiency,
        'panel_wattage': panel_wattage,
        'required_capacity_kw': round(required_capacity_kw, 2),
        'num_panels': num_panels,
        'actual_capacity_kw': round(actual_capacity_kw, 2),
        'estimated_daily_production_kwh': round(actual_daily_production, 2),
        'total_array_area_m2': round(total_area, 1),
        'excess_capacity_percent': round((actual_daily_production / daily_energy_kwh - 1) * 100, 1)
    }
    
    if peak_sun_hours < 3:
        warnings.append("Low peak sun hours - consider location or seasonal variations")
    if num_panels > 50:
        warnings.append("Large array - consider structural and inverter requirements")
    if system_efficiency < 0.7:
        warnings.append("Low system efficiency - check for shading or equipment issues")
    
    save_calculation('panel_sizing',
        {'daily_energy': daily_energy_kwh, 'sun_hours': peak_sun_hours, 'panel_wattage': panel_wattage},
        result, '; '.join(warnings))
    
    return result, warnings

def battery_sizing(daily_energy_kwh, autonomy_days, depth_of_discharge=0.8, battery_voltage=48, battery_efficiency=0.9):
    warnings = []
    
    total_energy_needed = daily_energy_kwh * autonomy_days
    
    usable_capacity = total_energy_needed / battery_efficiency
    
    total_capacity = usable_capacity / depth_of_discharge
    
    capacity_ah = (total_capacity * 1000) / battery_voltage
    
    result = {
        'daily_energy_kwh': daily_energy_kwh,
        'autonomy_days': autonomy_days,
        'depth_of_discharge': depth_of_discharge,
        'battery_voltage': battery_voltage,
        'battery_efficiency': battery_efficiency,
        'total_energy_storage_kwh': round(total_capacity, 2),
        'usable_capacity_kwh': round(usable_capacity, 2),
        'capacity_ah': round(capacity_ah, 1),
        'recommended_c_rate': '0.2C for longevity'
    }
    
    if autonomy_days > 5:
        warnings.append("Extended autonomy requires large battery bank - consider costs")
    if depth_of_discharge > 0.8:
        warnings.append("High DoD may reduce battery lifespan")
    if capacity_ah > 1000:
        warnings.append("Large capacity - consider parallel battery strings")
    
    save_calculation('battery_sizing',
        {'daily_energy': daily_energy_kwh, 'autonomy': autonomy_days, 'dod': depth_of_discharge},
        result, '; '.join(warnings))
    
    return result, warnings

def inverter_sizing(peak_load_w, surge_factor=1.25, continuous_factor=1.1):
    warnings = []
    
    continuous_rating = peak_load_w * continuous_factor
    surge_rating = peak_load_w * surge_factor
    
    standard_sizes = [1000, 1500, 2000, 3000, 4000, 5000, 6000, 8000, 10000]
    recommended_size = min([s for s in standard_sizes if s >= continuous_rating], default=max(standard_sizes))
    
    result = {
        'peak_load_w': peak_load_w,
        'required_continuous_w': round(continuous_rating),
        'required_surge_w': round(surge_rating),
        'recommended_inverter_w': recommended_size,
        'headroom_percent': round((recommended_size / continuous_rating - 1) * 100, 1)
    }
    
    if peak_load_w > 10000:
        warnings.append("High load - consider multiple inverters or 3-phase system")
    
    save_calculation('inverter_sizing',
        {'peak_load': peak_load_w},
        result, '; '.join(warnings))
    
    return result, warnings

def system_losses(panel_capacity_kw, soiling=0.02, shading=0.03, wiring=0.02, inverter_loss=0.04, temperature=0.05, mismatch=0.02):
    total_derate = 1 - (soiling + shading + wiring + inverter_loss + temperature + mismatch)
    effective_capacity = panel_capacity_kw * total_derate
    
    losses_breakdown = {
        'soiling': soiling * 100,
        'shading': shading * 100,
        'wiring': wiring * 100,
        'inverter': inverter_loss * 100,
        'temperature': temperature * 100,
        'mismatch': mismatch * 100,
        'total_losses_percent': (1 - total_derate) * 100
    }
    
    result = {
        'panel_capacity_kw': panel_capacity_kw,
        'derate_factor': round(total_derate, 3),
        'effective_capacity_kw': round(effective_capacity, 2),
        'losses_breakdown': losses_breakdown,
        'annual_energy_loss_kwh': round(panel_capacity_kw * (1 - total_derate) * 4.5 * 365, 1)
    }
    
    return result

def roi_analysis(system_cost, annual_production_kwh, electricity_rate, annual_degradation=0.005, incentives=0, years=25):
    warnings = []
    
    cumulative_savings = 0
    yearly_data = []
    payback_year = None
    
    for year in range(1, years + 1):
        degraded_production = annual_production_kwh * ((1 - annual_degradation) ** (year - 1))
        yearly_savings = degraded_production * electricity_rate
        cumulative_savings += yearly_savings
        
        yearly_data.append({
            'year': year,
            'production_kwh': round(degraded_production, 1),
            'savings': round(yearly_savings, 2),
            'cumulative_savings': round(cumulative_savings, 2)
        })
        
        if payback_year is None and cumulative_savings >= (system_cost - incentives):
            payback_year = year
    
    net_savings = cumulative_savings - (system_cost - incentives)
    roi_percent = (net_savings / (system_cost - incentives)) * 100 if system_cost > incentives else 0
    
    result = {
        'system_cost': system_cost,
        'incentives': incentives,
        'net_cost': system_cost - incentives,
        'annual_production_kwh': annual_production_kwh,
        'electricity_rate': electricity_rate,
        'payback_years': payback_year,
        'total_savings_25yr': round(cumulative_savings, 2),
        'net_savings': round(net_savings, 2),
        'roi_percent': round(roi_percent, 1),
        'yearly_breakdown': yearly_data[:5]
    }
    
    if payback_year is None or payback_year > 15:
        warnings.append("Long payback period - review system cost or electricity rates")
    
    save_calculation('roi_analysis',
        {'system_cost': system_cost, 'annual_production': annual_production_kwh},
        result, '; '.join(warnings))
    
    return result, warnings

def compare_systems(systems):
    comparison = []
    
    for i, sys in enumerate(systems):
        panel_result, _ = panel_sizing(
            sys.get('daily_energy', 30),
            sys.get('sun_hours', 4.5),
            sys.get('efficiency', 0.8),
            sys.get('panel_wattage', 400)
        )
        
        comparison.append({
            'system_id': i + 1,
            'name': sys.get('name', f'System {i+1}'),
            'num_panels': panel_result['num_panels'],
            'capacity_kw': panel_result['actual_capacity_kw'],
            'daily_production': panel_result['estimated_daily_production_kwh'],
            'area_m2': panel_result['total_array_area_m2']
        })
    
    return comparison

def generate_solar_report(system_data, filename='solar_report.pdf'):
    filepath = os.path.join('static', 'plots', filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("Solar System Design Report", styles['Title']))
    elements.append(Spacer(1, 20))
    
    elements.append(Paragraph("System Specifications", styles['Heading2']))
    
    specs_data = [
        ['Parameter', 'Value'],
        ['Daily Energy Requirement', f"{system_data.get('daily_energy_kwh', 'N/A')} kWh"],
        ['Peak Sun Hours', f"{system_data.get('peak_sun_hours', 'N/A')} hours"],
        ['System Efficiency', f"{system_data.get('system_efficiency', 'N/A') * 100}%"],
        ['Number of Panels', str(system_data.get('num_panels', 'N/A'))],
        ['Total Capacity', f"{system_data.get('actual_capacity_kw', 'N/A')} kW"],
    ]
    
    table = Table(specs_data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    
    elements.append(Spacer(1, 20))
    
    if system_data.get('warnings'):
        elements.append(Paragraph("Warnings and Recommendations", styles['Heading2']))
        for warning in system_data.get('warnings', []):
            elements.append(Paragraph(f"• {warning}", styles['Normal']))
    
    doc.build(elements)
    return filepath
