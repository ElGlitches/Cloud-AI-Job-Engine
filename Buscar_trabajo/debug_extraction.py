import requests
import json

def debug_getonbrd():
    # Search for "sap" to likely find the user's vacancy
    url = "https://www.getonbrd.com/api/v0/search/jobs?query=sap&per_page=2&expand=[\"company\",\"location_cities\",\"seniority\",\"modality\"]"
    
    print(f"Fetching: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            item = data['data'][0]
            attributes = item.get("attributes", {})
            
            print("\n--- ATTRIBUTES KEYS ---")
            print(list(attributes.keys()))
            
            print("\n--- RELATIONSHIPS (Company) ---")
            print(f"Modality (field): {attributes.get('modality')}")
            print(f"Remote: {attributes.get('remote')}")
            
            print("\n--- INCLUDED SECTION ---")
            if 'included' in data:
                print(f"Found {len(data['included'])} included items.")
                # Print first few included items to see what they are
                for inc in data['included'][:3]:
                    print(json.dumps(inc, indent=2))
            else:
                print("No 'included' section found.")

            
        else:
            print("No vacancies found for 'sap'.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_getonbrd()
