import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import format_datetime

# 1. SETTINGS
ATOM_URL = "https://blackity.store/blogs/news.atom"
OUTPUT_FILE = "feed.xml"

def atom_to_rss():
    print(f"Fetching Atom feed from: {ATOM_URL}")
    
    # Fetch content
    try:
        req = urllib.request.Request(ATOM_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            atom_data = response.read()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        exit(1) # Stop if we can't fetch

    root = ET.fromstring(atom_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}

    # Create RSS 2.0
    rss = ET.Element('rss', {'version': '2.0'})
    channel = ET.SubElement(rss, 'channel')

    # Channel Info
    title = root.find('atom:title', ns)
    ET.SubElement(channel, 'title').text = title.text if title is not None else "Blackity Store"
    ET.SubElement(channel, 'link').text = "https://blackity.store/blogs/news"
    ET.SubElement(channel, 'description').text = "Latest news and updates from Blackity Store"

    # Process Entries
    for entry in root.findall('atom:entry', ns):
        item = ET.SubElement(channel, 'item')
        
        # Title
        entry_title = entry.find('atom:title', ns)
        ET.SubElement(item, 'title').text = entry_title.text
        
        # Link & GUID
        entry_link = entry.find("atom:link[@rel='alternate']", ns)
        if entry_link is not None:
            link_href = entry_link.attrib['href']
            ET.SubElement(item, 'link').text = link_href
            ET.SubElement(item, 'guid').text = link_href
        
        # Content
        content = entry.find('atom:content', ns) or entry.find('atom:summary', ns)
        if content is not None:
            ET.SubElement(item, 'description').text = content.text

        # Date
        published = entry.find('atom:published', ns) or entry.find('atom:updated', ns)
        if published is not None:
            try:
                # Convert date format
                dt = datetime.fromisoformat(published.text.replace('Z', '+00:00'))
                ET.SubElement(item, 'pubDate').text = format_datetime(dt)
            except:
                pass # If date fails, skip it

    # Write File
    tree = ET.ElementTree(rss)
    ET.indent(tree, space="  ", level=0)
    tree.write(OUTPUT_FILE, encoding='utf-8', xml_declaration=True)
    print(f"Success! {OUTPUT_FILE} generated.")

if __name__ == "__main__":
    atom_to_rss()
