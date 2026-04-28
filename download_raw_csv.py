import requests
import sys

def download_raw_csv(host_name, auth_token, output_file):
    """
    Download raw CSV response from the Aalam API and save to file
    """
    url = f"https://{host_name}/aalam/stock/items?download&fields=id,name,type,code,sale_price,sale_discount,sale_discount_pr,sale_discount_mode,stock,is_public,properties"
    headers = {"X-Auth-Token": auth_token}
    
    try:
        print(f"Downloading from: {url}")
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Save raw response to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print(f"✓ Successfully saved to {output_file}")
        print(f"  File size: {len(response.text)} bytes")
        print(f"  Rows: {len(response.text.splitlines())}")
        
    except requests.RequestException as e:
        print(f"✗ Error downloading: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Example usage
    host_name = "paavay.aalam.cloud"  # Replace with actual host
    auth_token = "80139a6e84fe42a18e5a1c481217a976#1775123576.2215948#;Sge5tCrDLPmrs/r9DNHt0wfOKj6CW1rLUDHXhrsuAs84t5XsD0UiZUSmQ3IqxZziCBbJIlNXfmUqy3vPMwd8NO3UaFZT/3m9JLWnYQAvNuFvlX6Jk2ZTH1TBBwrDbz787jPeKNmtzuv5+sgtFAGRe6OHR8o3GWUs/ZxrjuoUqTM="  
    output_file = "paavay.csv"
    
    download_raw_csv(host_name, auth_token, output_file)
