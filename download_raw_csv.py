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
    host_name = "thaiyal.aalam.cloud"  # Replace with actual host
    auth_token = "6183aac438e14e17b7188e833c07a7f8#1765174691.3604994#;N8e6dl6M0dvElFjcmAehEJBK1yoHXuj9Cwzh1aCs2pSDhG218h1pzZGK+GKEnM/rVwcJAT0wn17bIHWvDlR3RJUcOGRLRNHBIUMqVZYNjytjkT0+6gMtw/p4tP95lfXswgbk9d75u5QCR71fslJ2KnIHyyXjFxaIkbMaLQuND04="  
    output_file = "beelittle.csv"
    
    download_raw_csv(host_name, auth_token, output_file)
