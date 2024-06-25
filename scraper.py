import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def find_new_arl():
    url = 'https://rentry.org/firehawk52/raw'
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}. Status code: {response.status_code}")

    soup = BeautifulSoup(response.content, 'html.parser')

    arls = []

    # Find all sections under '#### Deezer ARLs'
    deezer_arls_section = soup.find('section', text='#### Deezer ARLs')
    if deezer_arls_section:
        # Find all sibling elements until the next section
        for element in deezer_arls_section.find_next_siblings():
            # Stop when encountering the next section
            if element.name and element.name.startswith('h'):
                break

            # Parse each line for ARL details
            if element.name == 'p' and '->' in element.text:
                country = None
                date_str = None
                arl = None
                thanks_to = None

                # Extract relevant information
                parts = element.text.split('|')
                if len(parts) >= 4:
                    country_part = parts[0].strip().split('->')[1].strip()
                    date_part = parts[2].strip()
                    arl_part = parts[3].strip().split('`')[0].strip()
                    if len(parts) >= 5:
                        thanks_to = parts[4].strip().split('`')[0].strip().split('-')[0].strip()

                    # Extract country
                    if '/' in country_part:
                        country = country_part.split('/')[1].strip()
                    else:
                        country = country_part

                    # Extract date
                    if '|' in date_part:
                        date_str = date_part.split('|')[0].strip()

                    # Convert date string to datetime object
                    if date_str:
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d')
                            # Calculate difference from current date
                            days_diff = (date - datetime.now()).days
                            if days_diff <= 1825:  # Less than or equal to 5 years (365 * 5)
                                arls.append({
                                    'country': country,
                                    'date': date,
                                    'arl': arl_part,
                                    'thanks_to': thanks_to
                                })
                        except ValueError:
                            pass  # Handle if date format is invalid

        # Sort ARLs by country (custom order) and then by date descending
        sorted_arls = sorted(arls, key=lambda x: (
            ['United States of America', 'Canada', 'Australia', 'Netherlands'].index(x['country'])
            if x['country'] in ['United States of America', 'Canada', 'Australia', 'Netherlands']
            else 5,  # Place other countries at the end
            x['date']
        ), reverse=True)

        return sorted_arls

    else:
        raise Exception("Section '#### Deezer ARLs' not found in the document")
