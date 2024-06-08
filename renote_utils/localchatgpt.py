import ollama
# from input_file_generator import convert_ipynb_to_py, find_code_in_response

def localChat(msg):
  response = ollama.chat(
      model='llama3',
      messages=[{'role': 'user', 'content': msg}]
  )

  return response['message']['content']
