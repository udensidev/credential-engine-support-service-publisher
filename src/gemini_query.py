import os
import json
import google.generativeai as genai
import time
import re
from google.api_core.exceptions import ResourceExhausted
from google.generativeai.types import GenerateContentResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY')
ORG_ID = os.getenv('ORGANIZATION_IDENTIFIER')

# Configure Google Gemini 
genai.configure(api_key=API_KEY)

def gemini_query_api(text, retries=3, initial_delay=1):
    """
    Queries the Google Gemini API to generate a CTDL JSON structure based on the provided text.

    This function uses the Google Gemini API to generate content based on a predefined prompt. 
    It attempts to extract a JSON structure from the API response. If the API rate limit is exceeded, 
    the function will retry the request with exponential backoff.

    Parameters:
    text (str): The input text to be used in the prompt for the Google Gemini API.
    retries (int, optional): The number of times to retry the request in case of a rate limit error. Default is 3.
    initial_delay (int, optional): The initial delay in seconds before retrying the request. 
    The delay will be doubled with each retry. Default is 1.

    Returns:
    str: A JSON string extracted from the API response.

    Raises:
    ValueError: If no JSON structure is found in the API response.
    ResourceExhausted: If the API rate limit is exceeded and all retries fail.

    Example:
    >>> text = "Generate a CTDL JSON structure for a support service."
    >>> json_string = gemini_query_api(text)
    >>> print(json_string)
    {{
    "PublishForOrganizationIdentifier": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c",
	"DefaultLanguage": "en-US",
    "SupportServices": [{{
            "CTID": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c",
            "Name": "My Support Service One",
            "Description": "This is some text that describes my Support Service.",
            "OwnedBy": [{{
                    "CTID": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c"
                }}
            ],
            "InLanguage": [
                "en-US"
            ],
            "LifeCycleStatusType": "Active",
            "AvailableAt": [{{
                    "Name": "Office of Student Financial Aid",
                    "Address1": "One University Plaza",
                    "City": "Springfield",
                    "AddressRegion": "IL",
                    "PostalCode": "62703",
                    "Country": "United States"
                }}
            ],
            "SupportServiceType": [
                "support:Counseling",
                "support:BenefitsSupport",
                "support:CareerAdvising",
                "support:PeerService"
            ]
            ...
            
        }}   
    ]    
    }}
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    #model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""You are a helpful assistant that specializes in generating structured data in the CTDL (Credential Transparency Description Language) format. 
    Your task is to extract support service information from text and structure it in JSON format.
    For the support services you find in {text}, return in JSON format. 

    Here's an example:
    
    {{
    	{{
        "PublishForOrganizationIdentifier": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c",
    	"DefaultLanguage": "en-US",
        "SupportServices": [{{
                "CTID": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c",
                "Name": "My Support Service One",
                "Description": "This is some text that describes my Support Service.",
                "OwnedBy": [{{
                        "CTID": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c"
                    }}
                ],
                "InLanguage": [
                    "en-US"
                ],
                "LifeCycleStatusType": "Active",
                "AvailableAt": [{{
                        "Name": "Office of Student Financial Aid",
                        "Address1": "One University Plaza",
                        "City": "Springfield",
                        "AddressRegion": "IL",
                        "PostalCode": "62703",
                        "Country": "United States"
                    }}
                ],
                "SupportServiceType": [
                    "support:Counseling",
                    "support:BenefitsSupport",
                    "support:CareerAdvising",
                    "support:PeerService"
                ]
            }}, 
            {{
                "CTID": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c",
                "Name": "My Support Service Two",
                "Description": "This is some text that describes my Support Service.",
                "OwnedBy": [{{
                        "CTID": "ce-3508747f-4ca5-412f-bd38-6b0fb2d1132c"
                    }}
                ],
                "InLanguage": [
                    "en-US"
                ],
                "LifeCycleStatusType": "Active",
                "AccommodationType": [
                    "accommodation:PhysicalAccessibility",
                    "accommodation:AccessibleHousing",
                    "accommodation:AccessibleParking",
                    "accommodation:AccessibleRestroom",
                    "accommodation:AdjustableLighting",
                    "accommodation:AdjustableWorkstations",
                    "accommodation:AlternativeFormats",
                    "accommodation:AssistiveTechnology",
                    "accommodation:AudioCaptioning",
                    "accommodation:CaptioningAndTranscripts",
                    "accommodation:ClearSignage",
                    "accommodation:ColorBlindness",
                    "accommodation:Communication",
                    "accommodation:DietaryAccommodation",
                    "accommodation:FacilityAccommodation",
                    "accommodation:FlexibleSchedule",
                    "accommodation:HearingLoops",
                    "accommodation:MultipleLanguage",
                    "accommodation:PhysicalAccessibility",
                    "accommodation:PlainLanguage",
                    "accommodation:ResourceAndServiceAccommodation",
                    "accommodation:ScreenReader",
                    "accommodation:Sensory",
                    "accommodation:ServiceAnimal",
                    "accommodation:TactileSignage"
                ],
                "SupportServiceType": [
                    "support:AssistiveTechnologySupport",
                    "support:AudiologicalHealthCare",
                    "support:NeurodivergenceService",
                    "support:TestAssistance",
                    "support:Transportation"
                ]
            }}
        ]
    }}
    }}

    When categorizing SupportServiceType values, use these predefined categories:

    support:AcademicAdvising, support:AssistiveTechnologySupport, support:AudiologicalHealthCare, 
    support:BehavioralService, support:BenefitsSupport, support:CareerAdvising, support:CareerAssessment, 
    support:CareerExploration, support:CaseManagement, support:ChildcareSupport, support:ClothingAssistance, support:ComputerHub, 
    support:Counseling, support:CrisisSupport, support:DiversityEquityInclusion, support:EquipmentProvision, support:FinancialLiteracy, 
    support:HealthCare, support:ImmigrationAssistance, support:InternetAccess, support:JobPlacement, support:LearningResourceProvision, 
    support:LegalService, support:MentalHealthCounseling, support:Mentoring, support:Networking, support:NeurodivergenceService, 
    support:NoteTakingAssistance, support:PeerService, support:PersonalAssistance, support:PostalAddress, support:PsychologicalService, 
    support:PublicBenefitsCaseManagement, support:ReaderService, support:Rehabilitation, support:ResidentialLiving, support:RespiteCare, 
    support:SignLanguage, support:SkillMapping, support:StudySkills, support:SubstanceAbusePrevention, support:SupportCoordination, 
    support:SupportedWork, support:TalentMarketplaceSignaling, support:TechnologyLending, support:TestAssistance, support:Translation, 
    support:Transportation, support:Tutoring, support:VisionService. 

    If applicable, also define AccommodationType for accessibility features using these predefined categories:

    accommodation:PhysicalAccessibility, accommodation:AccessibleHousing, accommodation:AccessibleParking, accommodation:AccessibleRestroom, 
    accommodation:AdjustableLighting, accommodation:AdjustableWorkstations, accommodation:AlternativeFormats, accommodation:AssistiveTechnology, 
    accommodation:AudioCaptioning, accommodation:CaptioningAndTranscripts, accommodation:ClearSignage, accommodation:ColorBlindness, 
    accommodation:Communication, accommodation:DietaryAccommodation, accommodation:FacilityAccommodation, accommodation:FlexibleSchedule, 
    accommodation:HearingLoops, accommodation:MultipleLanguage, accommodation:PhysicalAccessibility, accommodation:PlainLanguage, 
    accommodation:ResourceAndServiceAccommodation, accommodation:ScreenReader, accommodation:Sensory, accommodation:ServiceAnimal, 
    accommodation:TactileSignage 

    Key Guidelines:
        1.  Keep the PublishForOrganizationIdentifier consistent and unchanged for all services ({ORG_ID}).
        2.  Generate a unique UUID–follow the UUID4 format–for each service and use it as the CTID, prefixing it with "ce-" (e.g., "ce-84365aea-57a5-4b5a-8c1c-eae95d7a8c9b").
        3.  Use "en-US" as the DefaultLanguage for all services.
    	4.	If the same service is repeated in the input text, ensure it appears only once in the output.
    	5.	Summarize each support service’s purpose or benefit in a short, clear description.
    	6.	Specify the location for each service with the "AvailableAt" field and EXACTLY follow the schema provided. If a service has no address, omit the field from the output.
    	7.	Ensure the JSON is well-organized, follows the provided schema, and is free from formatting errors.
        8.	Include accommodation types for services that offer accessibility features. 
        9.  SupportServiceType and AccommodationType are mutually exclusive categories. Do NOT categorize a support service as an accommodation type, and do NOT categorize an accommodation type as a support service.
        10. Only use values for SupportServiceType and AccommodationType that EXACTLY match the predefined categories provided above. Do NOT use synonyms, paraphrases, or related terms. 
        11. If a value does not match any of the predefined categories for either SupportServiceType or AccommodationType, you MUST omit it entirely. Do NOT attempt to create new categories.

    """ 
    for i in range(retries):
        try:
            delay = initial_delay * (2 ** i)
            print(f"Attempting request. Delay: {delay} seconds...")
            time.sleep(delay) 
            print(f"prompt: {prompt}") 
            
            response = model.generate_content(prompt)
            print(f"response: {response}")
            print(f"response text: {response.text}")
            
            json_string = re.sub(r"```(?:json)?", "", response.text).strip()
            return json_string
        
        except ResourceExhausted as e:
            if i < retries - 1:
                print(f"Rate limit exceeded. Retrying...")
                time.sleep(delay)
            else:
                print("Max retries reached. Please try again later.")
                raise e  # Reraise if all retries fail 

def gemini_query_but(text, retries=3, initial_delay=1):
    """
    Queries the Google Gemini API to generate a CTDL JSON structure based on the provided text.

    This function uses the Google Gemini API to generate content based on a predefined prompt. It attempts to extract a JSON structure from the API response. If the API rate limit is exceeded, the function will retry the request with exponential backoff.

    Parameters:
    text (str): The input text to be used in the prompt for the Google Gemini API.
    retries (int, optional): The number of times to retry the request in case of a rate limit error. Default is 3.
    initial_delay (int, optional): The initial delay in seconds before retrying the request. The delay will be doubled with each retry. Default is 1.

    Returns:
    str: A JSON string extracted from the API response.

    Raises:
    ValueError: If no JSON structure is found in the API response.
    ResourceExhausted: If the API rate limit is exceeded and all retries fail.

    Example:
    >>> text = "Generate a CTDL JSON structure for a support service."
    >>> json_string = gemini_query_api(text)
    >>> print(json_string)
	{
        "ExternalIdentifier": "example-id",
        "ResourceName": "Example Support Service",
        "Description": "This is an example support service.",
        ...
    }
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    #model = genai.GenerativeModel("gemini-1.5-flash")
    
    prompt = f"""You are a helpful assistant that specializes in generating data in structed JSON format. 
    Your task is to extract support service information from text and structure it in JSON format.
    For the support services you find in {text}, return in JSON format. 
    
    Here's an example:

    {{
    "ExternalIdentifier": "Provide a unique (external) identifier from your system for the SupportService that is used for your customers or for internal processes within your system. This identifier will be used on future uploads to ensure duplicate SupportServices are not created. SAMPLE: uiuc_ss_01",
    "ResourceName": "Use the official name of the resource. SAMPLE: This is the official name.",
    "Description": "Use the description that is commonly used or already available on the website.",
    "SubjectWebpage": "The main, public webpage about this SupportService.",
    "LifeCycleStatusType": "Active",
    "Language": "english",
    "AccommodationType": "Type of modification to facilitate equal access for people to a physical location, resource, or service. Select from the existing enumeration of such types. SAMPLE: AccessibleHousing | AccessibleParking",
    "SupportServiceType": "Types of support services offered by an agent; select from an existing enumeration of such types.. Select from the existing enumeration of such types. SAMPLE: AcademicAdvising | AssistiveTechnologySupport | CrisisSupport | DiversityEquityInclusion | EquipmentProvision",
    "DeliveryType": "Type of means by which a learning opportunity or assessment is delivered to assessment seekers and by which they interact; select from an existing enumeration of such types. SAMPLE: BlendedDelivery | In-Person | OnlineOnly | Variable Site",
    "Keywords": "Keywords (not whole sentences) that will help others find this SupportService in searches. SAMPLE: first keyword | another keyword | some text",
    "OfferedBy": "Indicate organization(s) that offer this SupportService. If the owning organization also offers the SupportService, just provide: same as owner (Recommended). Otherwise (or as well) enter the CTID or the Name and Webpage (separated by a tilde ~) of the organization(s) that offer this SupportService. NOTE: if an existing organization is NOT found for the provided Name and Webpage, a new reference organization will be created. Ensure the proper name and Webpage are provided if the organization is believed to already exist. SAMPLE: same as owner | organization name ~ https://organizationsite.com",
    "ConditionProfile": [{{
        "ExternalIdentifier": "A unique (external) identifier used to identify a condition profile especially when there are multiple. SAMPLE: cp01",
        "Description": "A description of the requirements for this condition.",
        "SubjectWebpage": "Webpage or online document that describes the conditions required for this credential. SAMPLE: http://credreg.net/ctdl/terms/processStandards",
        "AudienceType": "Current students",
        "ConditionItems": "A pipe-separated list of conditions that must be met to earn the credential. SAMPLE: Driver's License | English Proficiency",
        "SubmissionOfItems": "A pipe-separated list of URLs to information that must be submitted to earn the SupportService. SAMPLE: https://example.com/item1 | https://example.com/item2",
        "SubmissionOfDescription": "A description of the items that must be submitted to earn this SupportService. SAMPLE: The seeker must submit proof of a high school diploma..."
    }}],
    "FinancialAssistance": [{{
        "ExternalIdentifier": "A unique (external) identifier from the partner system. Used to identify a Financial Assistance profile especially when there are multiple, and for updates. Must be unique. While not required, it is recommended to always include an external identifier otherwise problems will occur if a second financial profile is added. SAMPLE: fap_1",
        "Name": "The name of this Financial Assistance profile. SAMPLE: Financial Assistance for Veterans.",
        "Description": "A description of the Financial Assistance profile for this SupportService. SAMPLE: The Financial Assistance for this SupportService include...",
        "SubjectWebpage": "Webpage or online document that describes the details for this profile. SAMPLE: http://example.com/financialAssistance",
        "Type": "A pipe-separated list of Financial Assistance type. SAMPLE: Pell Grant | State or Local Loan",
        "Value": "The financial assistance value related properties with parts separated by a tilde(~). SAMPLE: Tilde separated properties.<br>1000~USD~optional description"
    }}],
    "Cost": [{{
        "ExternalIdentifier": "A unique (external) identifier from the partner system. Used to identify a cost profile especially when there are multiple, and for updates. Must be unique. SAMPLE: cost_1",
        "Description": "A description of the cost profile for this SupportService. SAMPLE: The costs for this SupportService include...",
        "DetailsUrl": "Webpage or online document that describes the cost details for this profile. SAMPLE: http://example.com/costDetails",
        "CurrencyType": "USD",
        "TypesList": "A pipe-separated list of pairs of cost type and price separated by a tilde. SAMPLE: tuition~1299.99 | application~150.00"
    }}]
    }}

    When categorizing SupportServiceType values, use these predefined categories:

    AcademicAdvising, AssistiveTechnologySupport, AudiologicalHealthCare, 
    BehavioralService, BenefitsSupport, CareerAdvising, CareerAssessment, 
    CareerExploration, CaseManagement, ChildcareSupport, ClothingAssistance, ComputerHub, 
    Counseling, CrisisSupport, DiversityEquityInclusion, EquipmentProvision, FinancialLiteracy, 
    HealthCare, ImmigrationAssistance, InternetAccess, JobPlacement, LearningResourceProvision, 
    LegalService, MentalHealthCounseling, Mentoring, Networking, NeurodivergenceService, 
    NoteTakingAssistance, PeerService, PersonalAssistance, PostalAddress, PsychologicalService, 
    PublicBenefitsCaseManagement, ReaderService, Rehabilitation, ResidentialLiving, RespiteCare, 
    SignLanguage, SkillMapping, StudySkills, SubstanceAbusePrevention, SupportCoordination, 
    SupportedWork, TalentMarketplaceSignaling, TechnologyLending, TestAssistance, Translation, 
    Transportation, Tutoring, VisionService. 

    If applicable, also define AccommodationType for accessibility features using these predefined categories:

    PhysicalAccessibility, AccessibleHousing, AccessibleParking, AccessibleRestroom, 
    AdjustableLighting, AdjustableWorkstations, AlternativeFormats, AssistiveTechnology, 
    AudioCaptioning, CaptioningAndTranscripts, ClearSignage, ColorBlindness, 
    Communication, DietaryAccommodation, FacilityAccommodation, FlexibleSchedule, 
    HearingLoops, MultipleLanguage, PhysicalAccessibility, PlainLanguage, 
    ResourceAndServiceAccommodation, ScreenReader, Sensory, ServiceAnimal, 
    TactileSignage 

    Key Guidelines:
        1.  The external identifier for each SupportService must follow this format: uiuc_ss_01, where "uiuc" is the institution abbreviation and "ss" is the support service code. The number should be unique for each service.
    	2.	If the same service is repeated in the input text, ensure it appears only once in the output.
    	3.	Summarize each support service’s purpose or benefit in a short, clear description.
    	4.	Ensure the JSON is well-organized, follows the provided schema, and is free from formatting errors.
        5.	Include accommodation types for services that offer accessibility features. 
        6.  SupportServiceType and AccommodationType are mutually exclusive categories. Do NOT categorize a support service as an accommodation type, and do NOT categorize an accommodation type as a support service.
        7.  Only use values for SupportServiceType and AccommodationType that EXACTLY match the predefined categories provided above. Do NOT use synonyms, paraphrases, or related terms. 
        8.  If a value does not match any of the predefined categories for either SupportServiceType or AccommodationType, you MUST omit it entirely. Do NOT attempt to create new categories like NoteTakingAssistance, TestAssistance, or Transportation.
        9.  The external identifier for each SupportService must be unique. If you encounter a duplicate external identifier, please adjust the identifier to make it unique.
        10. If you encounter a field that is not applicable to a particular service, leave it as a blank space.
        11. The delivery type for each service can not be In-Person and OnlineOnly at the same time. If a service is offered both in-person and online, select the appropriate delivery type: BlendedDelivery or Variable Site.

    """ 
    for i in range(retries):
        try:
            delay = initial_delay * (2 ** i)
            print(f"Attempting request. Delay: {delay} seconds...")
            time.sleep(delay) 
            print(f"prompt: {prompt}") 
            response = model.generate_content(prompt)
            print(f"response: {response}")
            print(f"response text: {response.text}")
            json_string = re.sub(r"```(?:json)?", "", response.text).strip()
            return json_string
        
        except ResourceExhausted as e:
            if i < retries - 1:
                print(f"Rate limit exceeded. Retrying...")
                time.sleep(delay)
            else:
                print("Max retries reached. Please try again later.")
                raise e  # Reraise if all retries fail 

def save_ctdl_to_json(data, filepath):
    """
    Saves the CTDL JSON data to a specified file.

    This function takes the data generated by the Google Gemini API and saves it to a JSON file.
    It attempts to parse the data as JSON and writes it to the specified file path.
    If the data is an instance of GenerateContentResponse, it extracts the text attribute.
    If the data is not valid JSON, it raises an appropriate error.

    Parameters:
    data (str or GenerateContentResponse): The data to be saved. This can be a JSON string or an instance of GenerateContentResponse.
    filepath (str): The path to the file where the JSON data will be saved.

    Raises:
    json.JSONDecodeError: If the data cannot be parsed as valid JSON.
    AttributeError: If the data object does not have a 'text' attribute when it is expected to.

    Example:
    >>> data = '{"ExternalIdentifier": "example-id", "ResourceName": "Example Support Service"}'
    >>> save_ctdl_to_json(data, 'path/to/file.json')
    CTDL structure saved successfully'.
    """
    
    try:
        if isinstance(data, GenerateContentResponse):
            json_string = data.text
        else:
            json_string = data

        # Attempt to parse Gemini's response
        parsed_data = json.loads(json_string)
        
        with open(filepath, "w") as json_file:
            json.dump(parsed_data, json_file, indent=2)
        print("CTDL structure saved successfully.")
    except json.JSONDecodeError:
        print("Error: Could not parse the response as valid JSON. The output from Gemini may be invalid.")
    except AttributeError:
        print("Error: The data object does not have a 'text' attribute. Make sure you're passing the correct object.")