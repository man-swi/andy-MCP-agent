import re
from bs4 import BeautifulSoup
import html


# def parse_readable_content(content):
#     import re
    
#     # Extract job listings and important information
#     readable_text = []
    
#     # Remove CSS/JavaScript content
#     content = re.sub(r'@[^{]+{[^}]+}', '', content)
    
#     # Remove HTML tags but keep their content
#     content = re.sub(r'<[^>]+>', ' ', content)
    
#     # Remove special characters and entities
#     content = re.sub(r'&[a-zA-Z]+;|&#?[a-zA-Z0-9]+;', ' ', content)
    
#     # Remove multiple spaces, newlines and tabs
#     content = re.sub(r'\s+', ' ', content)
    
#     # Remove technical terms and file paths
#     content = re.sub(r'filepath:.*?\.(?:woff2|css|js|png|jpg)', '', content)
    
#     # Remove CSS class names and IDs
#     content = re.sub(r'[.#][a-zA-Z0-9-_]+', '', content)
    
#     # Remove non-ASCII characters
#     content = re.sub(r'[^\x00-\x7F]+', '', content)
    
#     # Clean up any remaining special formatting
#     content = content.replace('*', '').strip()
    
#     # Split into lines and remove empty ones
#     lines = [line.strip() for line in content.split('\n') if line.strip()]
    
#     return '\n'.join(lines)



# def extract_readable_text(content):
#     import re
    
#     # Remove CSS style definitions
#     content = re.sub(r'\{[^}]*\}', '', content)
    
#     # Remove HTML-like formatting
#     content = re.sub(r'[a-z]+\{.*?\}', '', content)
    
#     # Remove measurements and units
#     content = re.sub(r'\d+px|\d+em|\d+%', '', content)
    
#     # Remove HTML tags and attributes
#     content = re.sub(r'<[^>]+>', '', content)
#     content = re.sub(r'[a-z-]+\s*:', '', content)
    
#     # Remove special characters and formatting
#     content = re.sub(r'["\']|!important', '', content)
    
#     # Remove CSS properties and values
#     content = re.sub(r'(?:margin|padding|font|line|border|background|color|width|height|display)[^;]+;', '', content)
    
#     # Remove multiple spaces and clean up
#     content = re.sub(r'\s+', ' ', content)
    
#     # Keep only alphanumeric text and basic punctuation
#     content = re.sub(r'[^a-zA-Z0-9\s:|@.-]', '', content)
    
#     # Final cleanup of extra spaces
#     content = ' '.join(content.split())
    
#     return content

# Example usage:
# cleaned_text = extract_readable_text(content)
# print(cleaned_text)


# from textinput import text, text_2


def parse_readable_content(content):
    import re
    
    # First preserve URLs
    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', content)
    unwanted_extensions = ('.png', '.html')
    urls = [url[:100] for url in urls if not url.lower().endswith(unwanted_extensions)][:2]

    # Original cleaning steps
    # Remove all HTML tags but keep their content
    content = re.sub(r'<[^>]+>', ' ', content)
    # Remove CSS class names and IDs (e.g., .class, #id)
    content = re.sub(r'[.#][a-zA-Z0-9-_]+', '', content)
    # Remove non-ASCII characters
    content = re.sub(r'[^\x00-\x7F]+', '', content)

    # Remove CSS/JavaScript content (e.g., @media, @font-face blocks)
    content = re.sub(r'@[^{]+{[^}]+}', '', content)
    content = re.sub(r'=[^\s=]+?=', '', content)
    
    # Remove HTML entities (e.g., &nbsp;, &#123;)
    content = re.sub(r'&[a-zA-Z]+;|&#?[a-zA-Z0-9]+;', ' ', content)
    # Replace multiple whitespace (spaces, tabs, newlines) with a single space
    content = re.sub(r'\s+', ' ', content)
    # Remove file paths for certain file types (woff2, css, js, png, jpg)
    content = re.sub(r'filepath:.*?\.(?:woff2|css|js|png|jpg)', '', content)
    # Remove asterisks and strip leading/trailing whitespace
    content = content.replace('*', '').strip()
    
    # Changes 2
    # Remove CSS style blocks (e.g., { ... })
    content = re.sub(r'\{[^}]*\}', '', content)
    # Remove CSS selectors with blocks (e.g., body{...})
    content = re.sub(r'[a-z]+\{.*?\}', '', content)
    # Remove CSS measurements and units (e.g., 12px, 2em, 50%)
    content = re.sub(r'\d+px|\d+em|\d+%', '', content)
    # Remove CSS property names (e.g., color:, font-size:)
    content = re.sub(r'[a-z-]+\s*:', '', content)
    # Remove quotes and '!important' from CSS
    content = re.sub(r'["\']|!important', '', content)
    # Remove specific CSS properties and their values
    content = re.sub(r'(?:margin|padding|font|line|border|background|color|width|height|display)[^;]+;', '', content)
    # Remove CSS/JavaScript content
    content = re.sub(r'@[^{]+{[^}]+}', '', content)

    # Remove class attributes
    content = re.sub(r'\sclass=".*?"', '', content)

    content = re.sub(r'\n{3,}', '', content)

    

    # Add preserved URLs back
    if urls:
        content =   content[:1650] + "\nPreserved Links:\n" + " \n ".join(urls) + "\n\n" 
    
    # lines = [line.strip() for line in content.split('\n') if line.strip()]
    # return '\n'.join(lines)
    return content

def extract_readable_text(content):
    import re
    
    # First preserve URLs
    urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', content)
    
    # Original cleaning steps
    content = re.sub(r'\{[^}]*\}', '', content)
    content = re.sub(r'[a-z]+\{.*?\}', '', content)
    content = re.sub(r'\d+px|\d+em|\d+%', '', content)
    # content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'[a-z-]+\s*:', '', content)
    content = re.sub(r'["\']|!important', '', content)
    content = re.sub(r'(?:margin|padding|font|line|border|background|color|width|height|display)[^;]+;', '', content)
    # content = re.sub(r'\s+', ' ', content)
    
    # Modified character preservation to include URL-safe characters
    content = re.sub(r'[^a-zA-Z0-9\s:|@./-]', '', content)

    content = re.sub(r'\n{3,}', '', content)
    content = ' '.join(content.split())
    
    # Add preserved URLs back
    if urls:
        content = content + "\n\nPreserved Links:\n" + "\n".join(urls)
    

    # Changes 1
    # Remove CSS/JavaScript content
    content = re.sub(r'@[^{]+{[^}]+}', '', content)
  

    return content[:1750]


# Example usage:
# cleaned_content = parse_readable_content(text_2)
# cleaned_content_2 = extract_readable_text(cleaned_content)
# # print(cleaned_content_2)


# def clean_job_description(text: str) -> str:
#     """
#     Converts HTML/messy text input into clean, human-readable text.
#     Args:
#         text (str): Input text containing job description, could be HTML or plain text
#     Returns:
#         str: Cleaned and formatted text
#     """
#     import re
#     from bs4 import BeautifulSoup

#     # If text contains HTML, clean it using BeautifulSoup
#     if "<" in text and ">" in text:
#         soup = BeautifulSoup(text, 'html.parser')
#         # Get text content
#         text = soup.get_text(separator=' ', strip=True)

#     # Remove extra whitespace and normalize spacing
#     text = re.sub(r'\s+', ' ', text)
    
#     # Remove email tracking pixels and other common email artifacts
#     text = re.sub(r'This message was sent to.*?Privacy Policy', '', text)
#     text = re.sub(r'Copyright © .*?LLC\.', '', text)
    
#     # Remove URLs
#     text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
#     # Remove common email footer content
#     text = re.sub(r'Unsubscribe|Manage settings|Privacy Policy', '', text)
    
#     # Split into paragraphs for readability
#     paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
#     # Join paragraphs with double newline for readability
#     clean_text = '\n\n'.join(paragraphs)
    
#     return clean_text.strip()


# def clean_text_for_human_reading(text: str) -> str:
#     """
#     Cleans text to make it human readable by removing URLs, tracking codes, 
#     and other non-natural language content.
    
#     Args:
#         text (str): Input text that may contain URLs and tracking codes
#     Returns:
#         str: Clean, human-readable text
#     """
#     import re

#     # Remove URL parameters and tracking codes
#     text = re.sub(r'(?:\?|&amp;|&)[^"\s]*', '', text)
    
#     # Remove any URLs
#     text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
#     # Remove tracking pixels and IDs
#     text = re.sub(r'utm\w+=[\w-]+', '', text)
#     text = re.sub(r'guid=[\w-]+', '', text)
#     text = re.sub(r'uid=[\w-]+', '', text)
#     text = re.sub(r'jrtk[\w-]+', '', text)
    
#     # Remove file extensions and paths
#     text = re.sub(r'\.(png|jpg|gif|jpeg|pdf|html?)\b', '', text)
#     text = re.sub(r'filepath:[\\\/\w-]+', '', text)
    
#     # Remove encoded characters
#     text = re.sub(r'&\w+;', ' ', text)
    
#     # Remove numbers and special characters that aren't part of natural language
#     text = re.sub(r'\b\d{6,}\b', '', text)  # Remove long numbers
#     text = re.sub(r'[^\w\s.,!?-]', ' ', text)  # Keep basic punctuation
    
#     # Clean up whitespace
#     text = re.sub(r'\s+', ' ', text)
    
#     # Remove single letters (often remnants of parameters)
#     text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)
    
#     # Remove any lines that are just numbers or very short fragments
#     lines = [line.strip() for line in text.split('\n')]
#     lines = [line for line in lines if len(line) > 5 and not line.isdigit()]
    
#     return '\n'.join(lines).strip()

# # cleaned_content_2 = clean_job_description(cleaned_content_2)
# # cleaned_content_2 = clean_text_for_human_reading(cleaned_content_2)
# with open("cleaned_content_5.txt", "w", encoding="utf-8") as f:

#     f.write(cleaned_content_2)

# new_content = clean_email_content(content_2)
# new_content_2 = extract_readable_text(new_content)
# print("\n\nPrevious content:\n\n",new_content_2)
















# Example usage:
email_content = """
<html>
<body>
From: sender@email.com
To: recipient@email.com
Subject: Meeting update

Hello team,
Please check this link <a href="https://example.com">important document</a>.

Best regards,
John

=====
Some unwanted footer text
=====
</body>
</html>
"""

# cleaned_email = clean_email_content(email_content)
# print(cleaned_email)


""" 
Lessons\MCP-1\MCP-ENV-1 python d:/Lessons/MCP-2/Investor-Relations-Market-Intelligence/a.py
We are looking for experienced Data Engineers 610 years with strong expertise in the Number of 10 nos L Pune Work from Office Mandatory initially then Hybrid possible Python Pandas andor Polars Mandatory SQL Mandatory Azure AWS Knowledge of Airflow and web scraping Selenium will be an added advantage L Pune Candidates must be available for the in-person drive on 13th 9:00 AM to 6:00 PM or 14th September 9:00 AM to 2:00 PM Notice P Immediate to 30 days only N Only strong profiles 
with 6 years of proven experience in Data Engineering PandasPolars SQL and availability for the Pune drive will be considered. Interested candidates are requested to share their profiles along with the following Current CTC Expected CTC Notice Period Availability for the drive 13th or 14th September and preferred time Required Skills Experience Proficient in Python with deep experience using pandas or polars Strong understanding of ETL development data extraction and transformation Hands-on experience with SQL and querying large datasets Experience deploying workflows on Apache Airflow Familiar with web scraping techniques Selenium is a plus Comfortable working with various data formats and large-scale datasets Experience with Azure DevOps including pipeline configuration and automation Familiarity with pytest or equivalent test frameworks Strong communication skills and a team-first attitude. Experience with Databricks Familiarity with AWS services Working knowledge of Jenkins and advanced ADO Pipelines Regards CGI Talent Acquisition wwwinmichael-kisilenko-ceo"""
