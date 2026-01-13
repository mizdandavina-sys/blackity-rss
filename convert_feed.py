import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import format_datetime

# 1. SETTINGS
ATOM_URL = "https://blackity.store/blogs/news.atom"
OUTPUT_FILE = "feed.xml"

def atom_to_rss():
    print(f"Fetching Atom feed from: {ATOM_URL}")
    
    # We use a 'Chrome' browser identity to avoid the 403 Forbidden error
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/atom+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    try:
        req = urllib.request.Request(ATOM_URL, headers=headers)
        with urllib.request.urlopen(req) as response:
            atom_data = response.read()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        # If it still fails, we'll print the error but not crash the whole action
        exit(1)

    try:
        root = ET.fromstring(atom_data)
    except ET.ParseError as e:
        print(f"Could not parse XML. The site might be showing a captcha or block page. Error: {e}")
        exit(1)

    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    # Create RSS 2.0
    rss = ET.Element('rss', {'version': '2.0', 'xmlns:content': 'http://purl.org/rss/1.0/modules/content/'})
    channel = ET.SubElement(rss, 'channel')

    # Channel Info
    title_elem = root.find('atom:title', ns)
    ET.SubElement(channel, 'title').text = title_elem.text if title_elem is not None else "Blackity Store"
    ET.SubElement(channel, 'link').text = "https://blackity.store/blogs/news"
    ET.SubElement(channel, 'description').text = "Latest news and updates from Blackity Store"

    # Process Entries
    for entry in root.findall('atom:entry', ns):
        item = ET.SubElement(channel, 'item')
        
        # Title
        entry_title = entry.find('atom:title', ns)
        ET.SubElement(item, 'title').text = entry_title.text if entry_title is not None else "No Title"
        
        # Link & GUID
        entry_link = entry.find("atom:link[@rel='alternate']", ns)
        if entry_link is not None:
            link_href = entry_link.attrib['href']
            ET.SubElement(item, 'link').text = link_href
            ET.SubElement(item, 'guid', {'isPermaLink': 'true'}).text = link_href
        
        # Description
        content = entry.find('atom:content', ns)
        summary = entry.find('atom:summary', ns)
        desc_text = ""
        if content is not None and content.text:
            desc_text = content.text
        elif summary is not None and summary.text:
            desc_text = summary.text
        ET.SubElement(item, 'description').text = desc_text

        # Date
        published = entry.find('atom:published', ns) or entry.find('atom:updated', ns)
        if published is not None and published.text:
            try:
                dt = datetime.fromisoformat(published.text.replace('Z', '+00:00'))
                ET.SubElement(item, 'pubDate').text = format_datetime(dt)
            except:
                ET.SubElement(item, 'pubDate').text = published.text

    # Write File
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
    print(f"Success! {OUTPUT_FILE} generated.")

if __name__ == "__main__":
    atom_to_rss()
