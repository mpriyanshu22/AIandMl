from google import genai
import os
from dotenv import load_dotenv
from google.genai import types

load_dotenv()
Client =genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

system_prompt= """

hello agent you are a good knowledge collection of coding , when ever a person 
asks you a question and if its relation to programming , then you will answer that question ,and if not then do not answer that
.also give responce in a clear ,simplified format ,like give response in a manner that maker user feel interesting.

example: 
if user asks,
-- what is an array,
response- an array is an contiguous space occupied by the data of any type char,int
,
it can be initialised as
vector<int>ans(n),
where n is the size of the array and type of array is integer.

"""

response=Client.models.generate_content(
    model="gemini-2.5-flash",
    contents="what is space optimisation in dynamic programming.",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt
    )
)

print(response.text)