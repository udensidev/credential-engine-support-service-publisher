import json
import requests


def validate_json(input_file, output_file):
    """Filters JSON data based on allowed values for support services and checks for valid URLs. 
    
    This function reads a JSON file, filters the data based on allowed values for specific keys,
    and checks if the 'SubjectWebpage' URL is valid. The filtered data is then written to a new JSON file.
    
    Args:
        input_file (str): Path to the input JSON file.
        output_file (str): Path to the output JSON file where filtered data will be saved.
    """
    
    keys_to_filter = ['SupportServiceType', 'AccommodationType']
    allowed_values = {
        'SupportServiceType': ['AcademicAdvising', 'AssistiveTechnologySupport', 'AudiologicalHealthCare', 
        'BehavioralService', 'BenefitsSupport', 'CareerAdvising', 'CareerAssessment', 
        'CareerExploration', 'CaseManagement', 'ChildcareSupport', 'ClothingAssistance', 'ComputerHub', 
        'Counseling', 'CrisisSupport', 'DiversityEquityInclusion', 'EquipmentProvision', 'FinancialLiteracy', 
        'HealthCare', 'ImmigrationAssistance', 'InternetAccess', 'JobPlacement', 'LearningResourceProvision', 
        'LegalService', 'MentalHealthCounseling', 'Mentoring', 'Networking', 'NeurodivergenceService', 
        'NoteTakingAssistance', 'PeerService', 'PersonalAssistance', 'PostalAddress', 'PsychologicalService', 
        'PublicBenefitsCaseManagement', 'ReaderService', 'Rehabilitation', 'ResidentialLiving', 'RespiteCare', 
        'SignLanguage', 'SkillMapping', 'StudySkills', 'SubstanceAbusePrevention', 'SupportCoordination', 
        'SupportedWork', 'TalentMarketplaceSignaling', 'TechnologyLending', 'TestAssistance', 'Translation', 
        'Transportation', 'Tutoring', 'VisionService'],
        
        'AccommodationType': ['PhysicalAccessibility', 'AccessibleHousing', 'AccessibleParking', 'AccessibleRestroom', 
        'AdjustableLighting', 'AdjustableWorkstations', 'AlternativeFormats', 'AssistiveTechnology', 
        'AudioCaptioning', 'CaptioningAndTranscripts', 'ClearSignage', 'ColorBlindness', 
        'Communication', 'DietaryAccommodation',' FacilityAccommodation', 'FlexibleSchedule', 
        'HearingLoops', 'MultipleLanguage', 'PhysicalAccessibility', 'PlainLanguage', 
        'ResourceAndServiceAccommodation', 'ScreenReader', 'Sensory', 'ServiceAnimal', 
        'TactileSignage']
    }
    required_key = 'SubjectWebpage'
    
    def is_valid_url(url): # Check if the URL is valid and reachable
        try:
            response = requests.head(url, allow_redirects=True)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    filtered_data = []
    for item in data:
        subject_webpage = item.get(required_key)
        if not subject_webpage or not is_valid_url(subject_webpage):
            continue  # Skip this item if the webpage is invalid or missing

        new_item = item.copy()
        for key in keys_to_filter:
            if key in new_item and isinstance(new_item[key], str):
                values = [v.strip() for v in new_item[key].split('|')]
                valid_values = [v for v in values if v in allowed_values.get(key, [])]
                new_item[key] = ' | '.join(valid_values)
            else:
                values = []
        filtered_data.append(new_item)
    
    with open(output_file, 'w') as f:
        json.dump(filtered_data, f, indent=2)

    print(f"Filtered data written to 'filtered_output.json' with {len(filtered_data)} valid entries.")