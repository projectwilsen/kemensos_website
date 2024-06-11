import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

import os
from dotenv import load_dotenv
load_dotenv()
from supabase.client import Client, create_client
import cloudscraper


groq_api_key = os.getenv("GROQ_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

supabase_client = create_client(supabase_url, supabase_key)
model = ChatGroq(temperature=0, model_name="llama3-70b-8192", groq_api_key = groq_api_key)

print("start ini pake yang etl")

def process_berita(text):
    template = """
        Tentukan apakah judul berita {text} berikut ini berkaitan dengan bencana alam di Indonesia
        Output: 
        - 'yes' jika judul berkaitan dengan bencana alam
        - 'no' jika judul tidak berkaitan dengan bencana alam
        Do not add any explanations, reasoning or preambles.
        """
    prompt_process_berita = ChatPromptTemplate.from_template(template = template)
    output_parser = StrOutputParser()

    chain_process_berita = prompt_process_berita | model | output_parser

    result = chain_process_berita.invoke({"text": text})
    return result

def remove_specific_words(text, words_to_remove):
    pattern = r'\b(?:' + '|'.join(map(re.escape, words_to_remove)) + r')\b'
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text

try:
    url = 'https://www.cnnindonesia.com/nasional/peristiwa'  
    print(url)
    scraper = cloudscraper.create_scraper()
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = scraper.get(url, headers=headers)
    webpage_content = response.content

    print(response)
    print(webpage_content)

    soup = BeautifulSoup(webpage_content, 'html.parser')

    articles = soup.find_all('article')
    print(articles)
    title = []
    url = []
    for article in articles:
        try:
            a_tag = article.find('a', href=True)
            url.append(a_tag['href'])

            h2_tag = article.find('h2')
            h2_text = h2_tag.get_text(strip=True)
            title.append(h2_text)
        except:
            print('fail')

    data = {
        'title': title,
        'url': url
    }

    df = pd.DataFrame(data)

    df['result'] = df['title'].map(process_berita)

    filtered_df = df[df['result'] == 'yes'].drop_duplicates()

    class News(BaseModel):
        jenis_bencana : str = Field(description="Ekstrak jenis bencana alam seperti: gempa, tanah longsor, banjir")
        lokasi: str = Field(description="Ekstrak letak bencana")
        hari: str = Field(description="Ekstrak hari kejadian bencana")
        tanggal: str = Field(description="Ekstrak tanggal kejadian bencana")
        jam: str = Field(description="Ekstrak jam kejadian bencana")
        estimasi_masyarakat_terdampak: int = Field(description="""Ekstrak jumlah estimasi masyarakat yang terdampak dari bencana tersebut, jika tidak ada return 0 """)

    parser = JsonOutputParser(pydantic_object=News)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n. Do not add preambles and explanation",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    chain_extract_berita = prompt | model | parser

    for index, row in filtered_df.iterrows():
        url = row['url']
        print(url)

    response = requests.get(url)
    webpage_content = response.content

    soup = BeautifulSoup(webpage_content, 'html.parser')

    p = soup.find_all('p')
    all_text = ' '.join([soup.get_text(strip=True) for soup in p])

    words_to_remove = ['ADVERTISEMENT SCROLL TO CONTINUE WITH CONTENT', 'ADVERTISEMENT']

    result = remove_specific_words(all_text, words_to_remove)
    print(result)

    try:
        extracted_data = chain_extract_berita.invoke({"query": result})
        extracted_data['url'] = row['url']
        extracted_data['sumber'] = 'CNN Indonesia'

        pattern = r'/(\d{14})-'
        match = re.search(pattern, url)

        if match:
            date_time_str = match.group(1)
            extracted_data['published_date'] = pd.Timestamp(date_time_str).strftime("%Y%m%d_%H%M%S")
            supabase_client.table('berita').upsert(extracted_data,  returning="minimal", on_conflict="url").execute()
        else:
            print("No match found.")

        print(extracted_data)

    except:
        print("fail to parse")

except Exception as e:
    print(e)