from database import save_calculation

FAULT_RULES = {
    'no_power': {
        'symptoms': ['device_not_working', 'no_lights', 'no_display'],
        'causes': [
            {'cause': 'Power supply failure', 'priority': 1, 'checks': ['Check power cable', 'Test outlet', 'Check fuse']},
            {'cause': 'Blown fuse', 'priority': 2, 'checks': ['Inspect fuse visually', 'Test fuse continuity']},
            {'cause': 'Faulty power switch', 'priority': 3, 'checks': ['Test switch continuity', 'Check switch connections']},
            {'cause': 'Damaged power cord', 'priority': 4, 'checks': ['Inspect cord for damage', 'Test cord continuity']}
        ]
    },
    'overheating': {
        'symptoms': ['hot_to_touch', 'thermal_shutdown', 'burning_smell'],
        'causes': [
            {'cause': 'Blocked ventilation', 'priority': 1, 'checks': ['Clean vents', 'Ensure airflow clearance']},
            {'cause': 'Failed cooling fan', 'priority': 2, 'checks': ['Check fan rotation', 'Test fan motor']},
            {'cause': 'Thermal paste degradation', 'priority': 3, 'checks': ['Reapply thermal compound']},
            {'cause': 'Component overload', 'priority': 4, 'checks': ['Check load levels', 'Verify component ratings']}
        ]
    },
    'intermittent_operation': {
        'symptoms': ['random_shutdowns', 'flickering', 'erratic_behavior'],
        'causes': [
            {'cause': 'Loose connections', 'priority': 1, 'checks': ['Check all connectors', 'Reseat components']},
            {'cause': 'Dry solder joints', 'priority': 2, 'checks': ['Inspect PCB joints', 'Reflow suspicious joints']},
            {'cause': 'Failing capacitors', 'priority': 3, 'checks': ['Visual inspection for bulging', 'ESR testing']},
            {'cause': 'Power supply ripple', 'priority': 4, 'checks': ['Measure output ripple', 'Check filter caps']}
        ]
    },
    'no_output': {
        'symptoms': ['no_signal', 'no_response', 'open_circuit'],
        'causes': [
            {'cause': 'Open circuit', 'priority': 1, 'checks': ['Continuity test', 'Trace signal path']},
            {'cause': 'Failed output stage', 'priority': 2, 'checks': ['Test output transistors', 'Check driver circuit']},
            {'cause': 'Protection circuit triggered', 'priority': 3, 'checks': ['Check protection status', 'Verify load conditions']},
            {'cause': 'Control circuit failure', 'priority': 4, 'checks': ['Check control signals', 'Test IC functionality']}
        ]
    },
    'excessive_noise': {
        'symptoms': ['buzzing', 'humming', 'crackling', 'interference'],
        'causes': [
            {'cause': 'Ground loop', 'priority': 1, 'checks': ['Check grounding', 'Use ground loop isolator']},
            {'cause': 'EMI/RFI interference', 'priority': 2, 'checks': ['Add shielding', 'Use ferrite cores']},
            {'cause': 'Failing filter capacitors', 'priority': 3, 'checks': ['Test capacitor ESR', 'Replace filters']},
            {'cause': 'Poor cable shielding', 'priority': 4, 'checks': ['Use shielded cables', 'Check connections']}
        ]
    },
    'low_efficiency': {
        'symptoms': ['high_power_consumption', 'excessive_heat', 'poor_performance'],
        'causes': [
            {'cause': 'Component degradation', 'priority': 1, 'checks': ['Test component parameters', 'Compare to specifications']},
            {'cause': 'Incorrect biasing', 'priority': 2, 'checks': ['Measure bias points', 'Adjust as needed']},
            {'cause': 'Parasitic losses', 'priority': 3, 'checks': ['Check for leakage', 'Inspect insulation']},
            {'cause': 'Design issues', 'priority': 4, 'checks': ['Review circuit design', 'Consider redesign']}
        ]
    },
    'voltage_issues': {
        'symptoms': ['low_voltage', 'high_voltage', 'voltage_fluctuation'],
        'causes': [
            {'cause': 'Regulator failure', 'priority': 1, 'checks': ['Test regulator output', 'Check input voltage']},
            {'cause': 'Excessive load', 'priority': 2, 'checks': ['Measure current draw', 'Reduce load']},
            {'cause': 'Failing transformer', 'priority': 3, 'checks': ['Test transformer ratios', 'Check windings']},
            {'cause': 'Filter capacitor failure', 'priority': 4, 'checks': ['Test capacitor values', 'Replace if needed']}
        ]
    }
}

COMPONENT_TESTS = {
    'resistor': [
        'Measure resistance with multimeter',
        'Compare to marked value and tolerance',
        'Check for discoloration or burning'
    ],
    'capacitor': [
        'Visual inspection for bulging or leakage',
        'Measure capacitance with meter',
        'ESR test for electrolytic types',
        'Check for shorts'
    ],
    'inductor': [
        'Measure DC resistance',
        'Test for shorts between windings',
        'Check inductance value'
    ],
    'diode': [
        'Forward voltage drop test',
        'Reverse leakage test',
        'Check for shorts'
    ],
    'transistor': [
        'Test junction voltages',
        'Check for shorts between terminals',
        'Measure hFE if applicable'
    ],
    'ic': [
        'Check power supply pins',
        'Verify input/output signals',
        'Compare to datasheet specifications',
        'Check for overheating'
    ],
    'transformer': [
        'Test primary and secondary resistance',
        'Check turns ratio',
        'Test for inter-winding shorts',
        'Measure output under load'
    ],
    'relay': [
        'Test coil resistance',
        'Verify contact operation',
        'Check contact resistance',
        'Test with/without energizing'
    ]
}

def diagnose_fault(symptoms):
    matches = []
    
    for fault_type, data in FAULT_RULES.items():
        symptom_matches = set(symptoms) & set(data['symptoms'])
        if symptom_matches:
            match_score = len(symptom_matches) / len(data['symptoms'])
            matches.append({
                'fault_type': fault_type,
                'match_score': match_score,
                'matched_symptoms': list(symptom_matches),
                'causes': data['causes']
            })
    
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    if matches:
        top_match = matches[0]
        diagnosis = {
            'primary_fault': top_match['fault_type'],
            'confidence': round(top_match['match_score'] * 100, 1),
            'matched_symptoms': top_match['matched_symptoms'],
            'probable_causes': top_match['causes'],
            'alternative_faults': matches[1:3] if len(matches) > 1 else []
        }
    else:
        diagnosis = {
            'primary_fault': 'Unknown',
            'confidence': 0,
            'matched_symptoms': [],
            'probable_causes': [],
            'message': 'No matching fault patterns found. Consider detailed inspection.'
        }
    
    save_calculation('fault_diagnosis',
        {'symptoms': symptoms},
        {'diagnosis': diagnosis['primary_fault'], 'confidence': diagnosis.get('confidence', 0)},
        '')
    
    return diagnosis

def get_repair_steps(fault_type, cause_index=0):
    if fault_type in FAULT_RULES:
        causes = FAULT_RULES[fault_type]['causes']
        if 0 <= cause_index < len(causes):
            cause = causes[cause_index]
            return {
                'cause': cause['cause'],
                'priority': cause['priority'],
                'repair_steps': cause['checks'],
                'safety_note': 'Always disconnect power before performing repairs'
            }
    return {'error': 'Fault type or cause not found'}

def get_component_tests(component_type):
    component = component_type.lower()
    if component in COMPONENT_TESTS:
        return {
            'component': component,
            'tests': COMPONENT_TESTS[component]
        }
    return {'error': f'No test procedures for {component_type}'}

def generate_diagnosis_report(symptoms, diagnosis):
    report = {
        'title': 'Fault Diagnosis Report',
        'input_symptoms': symptoms,
        'diagnosis': diagnosis
    }
    
    conclusions = []
    
    if diagnosis.get('confidence', 0) > 70:
        conclusions.append(f"High confidence diagnosis: {diagnosis.get('primary_fault', 'Unknown')}")
    elif diagnosis.get('confidence', 0) > 40:
        conclusions.append(f"Moderate confidence diagnosis: {diagnosis.get('primary_fault', 'Unknown')}")
        conclusions.append("Additional testing recommended to confirm")
    else:
        conclusions.append("Low confidence diagnosis - multiple potential causes")
        conclusions.append("Systematic troubleshooting approach recommended")
    
    if diagnosis.get('probable_causes'):
        top_cause = diagnosis['probable_causes'][0]
        conclusions.append(f"Most likely cause: {top_cause['cause']}")
        conclusions.append(f"First steps: {', '.join(top_cause['checks'][:2])}")
    
    report['conclusions'] = conclusions
    report['recommendations'] = [
        "Follow repair steps in priority order",
        "Document all findings during troubleshooting",
        "Verify fix before returning to service"
    ]
    
    return report

def get_all_symptoms():
    all_symptoms = set()
    for data in FAULT_RULES.values():
        all_symptoms.update(data['symptoms'])
    return sorted(list(all_symptoms))

def get_fault_types():
    return list(FAULT_RULES.keys())
