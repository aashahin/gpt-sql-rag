import sys
from langchain_openai import ChatOpenAI
from langchain.chains import create_sql_query_chain
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_community.utilities import SQLDatabase
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Must set the environment variable OPENAI_API_KEY to your OpenAI API key

# Initialize the database connection
db = SQLDatabase.from_uri("postgresql://username:password@localhost:5432/database_name")

# Initialize the language model
llm = ChatOpenAI(model="gpt-3.5-turbo-16k-0613")

# Set up tools and chains
execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db)

# Create a prompt template for generating answers
answer_prompt = PromptTemplate.from_template(
    """
    Instruction for Chatbot Response:

Task:
   - Provide the user with the correct information based on the SQL result.
   - Correct any mistakes in the SQL query or result if necessary.
   - Clarify the user's question if it is unclear.

Correcting Information:
- If the SQL result appears incorrect, correct it and respond with the right information.
- If the user's question is unclear or incorrect, clarify it.
- If the SQL query is incorrect, correct it to provide the right information.
- If errors are found in the SQL query or result, reattempt the query to provide the correct information.


Exclusions:
- Do not mention or include any SQL queries or syntax errors or corrections or any technical details in the response.
- Avoid displaying any sensitive information such as passwords from the SQL result.
- Avoid mentioning any technical details or jargon in the answer.

Instructions:
  - Reattempt more than once if the response is incorrect.

Utilize Products Table:
- products table and ['prices', 'translations_products', 'attributes', 'translations_attributes', 'dimensions', 'reviews'] tables are related to the products table by the 'productId' column you can use them to answer the user's question.

Response as Markdown:
- Provide the response in Markdown format.

Question: {question}
SQL Query: {query}
SQL Result: {result}
Answer: """
)

# Define the processing chain
chain = (
        RunnablePassthrough.assign(query=write_query)
        .assign(result=itemgetter("query") | execute_query)
        | answer_prompt
        | llm
        | StrOutputParser()
)


# Function to get a response based on the user's question
def get_response(prompt):
    return chain.invoke({"question": prompt})


# Prompt the user for input from the terminal
if __name__ == "__main__":
    question = sys.argv[1]
    response = get_response(question)
    print(response)
