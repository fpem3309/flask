import openai
from flask import Flask, render_template, request, redirect
from flask_restx import Api, Resource, reqparse
import requests

from openai import OpenAI
client = OpenAI(api_key=API_KEY)

app = Flask(__name__)

@app.route('/', methods=['GET'])
def main():
  return render_template('index.html')

@app.route('/data', methods=['GET'])
def get_data():
    response = requests.get('https://asia-northeast3-ketchup-e6dc3.cloudfunctions.net/data')
    return response.json()

@app.route('/sentence', methods=['GET'])
def get_sentence():
    response = requests.get('https://asia-northeast3-ketchup-e6dc3.cloudfunctions.net/data/sentence')
    return response.json()



@app.route('/gpt', methods=['POST'])
def get_gpt_test():
  system_text = request.form.get('system_text')
  user_text = request.form.get('user_text')
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={ "type": "json_object" },
    messages=[
      {"role": "system", "content": system_text},
      {"role": "user", "content": user_text},
    ]
  )
  answer = completion.choices[0].message
  print(answer)
  return answer.content



def find_similar(target_item, items):
  prompt = (
    f"Given the Korean or English word '{target_item}', which of the following English words is the most similar? "
    f"The options are: {', '.join(items)}."
    f"Output format: similar word")

  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {"role":"system", "content":"You are a helpful assistant."},
      {"role":"user","content":prompt}
    ]
  )



  match_item = response.choices[0].message.content
  return match_item

@app.route('/gpt-prop', methods=['POST'])
def get_gpt_prop():
  system_text = request.form.get('system_text')
  user_text = request.form.get('user_text')
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {"role": "system", "content": system_text},
      {"role": "user", "content": user_text},
    ]
  )
  answer = completion.choices[0].message
  response = requests.get('https://asia-northeast3-ketchup-e6dc3.cloudfunctions.net/ai/'+answer.content)
  a = response.json()

  item_list=[]
  for i in a: item_list.append(i['ch_name'])
  for i in range(len(item_list)): print(item_list[i])


  match_item = find_similar(user_text, item_list)
  print("매치 : "+ match_item)

  result_url = "https://asia-northeast3-ketchup-e6dc3.cloudfunctions.net/ai/img?collection="+answer.content+"&name="+match_item
  return result_url



@app.route('/gpt-img', methods=['POST'])
def get_gpt_test2():
  user_text = request.form.get('user_text')
  img_url = request.form.get('img_url')
  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
      {
        "role": "user",
        "content": [
          {"type": "text", "text": user_text},
          {
            "type": "image_url",
            "image_url": {
              "url": img_url,
            },
          },
        ],
      }
    ],
    max_tokens=300,
  )
  answer = completion.choices[0].message
  print(answer)
  return answer.content




# Swagger UI 설정
api = Api(app, version='1.0', title='API 문서', description='Swagger 문서', doc="/docs")
get_api = api.namespace('test', description='조회 API')

@get_api.route('/', methods=['GET'])
class Test(Resource):
  def get():
    return 'Hello, World!'


if __name__ == '__main__':
  app.run()