import csv
import json

def json_file_to_csv(json_filepath, output_filename):
    """
    Converts a JSON file to a CSV file.

    This function reads a JSON file containing support service data, extracts the relevant fields,
    and writes them to a CSV file. The CSV file will contain headers corresponding to the fields in the Bulk Upload Template.

    Parameters:
    json_filepath (str): The path to the JSON file to be converted.
    output_filename (str): The path to the output CSV file.

    Example:
    >>> json_filepath = "path/to/input.json"
    >>> output_filename = "path/to/output.csv"
    >>> json_file_to_csv(json_filepath, output_filename)
    Bulk Upload Template has been created successfully!
    """

    # Read the JSON file
    with open(json_filepath, "r", encoding="utf-8") as file:
        ctdl_json = json.load(file)  # Load JSON data
        
    if isinstance(ctdl_json, dict):
        ctdl_json = [ctdl_json]
    
    # Define CSV headers
    headers = [
        "External Identifier", "Resource Name", "Description", "Subject Webpage",
        "Life Cycle Status Type", "Language", "Accommodation Type", 
        "Support Service Type", "Delivery Type", "Keywords", "Offered By"
    ]

    # Open CSV file for writing
    with open(output_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the header row

        for service in ctdl_json:
            row = [
                service.get("ExternalIdentifier", ""),
                service.get("ResourceName", ""),
                service.get("Description", ""),
                service.get("SubjectWebpage", ""),
                service.get("LifeCycleStatusType", ""),
                service.get("Language", ""),
                service.get("AccommodationType", ""),
                service.get("SupportServiceType", ""),
                service.get("DeliveryType", ""),
                service.get("Keywords", ""),
                service.get("OfferedBy", "")
            ]
            writer.writerow(row)
    print("Bulk Upload Template has been created successfully!")