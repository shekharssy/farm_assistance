#Import necessary packages
import flask
from flask import render_template
import logging
import pickle
import pandas as pd
from datetime import datetime
import random
import json
import requests
from flask import request
from flask_cors import CORS
import sys

app = flask.Flask(__name__)
CORS(app)
#Setting log for flask app
logging.basicConfig(filename = 'FlaskApp.log',level = logging.INFO)
crop_name = ""

#API to return the recommended crop
@app.route('/crop_predict',methods = ['GET','POST'])
def PredictCrop():
    try:
        user_api="a63eabe6f13509c1a830f1c4238d7a03"
        # location=input("enter the city")
        location=request.form["Location"]
        api_link="https://api.openweathermap.org/data/2.5/weather?q="+location+"&appid="+user_api
        api_data_comp=requests.get(api_link)
        api_data=api_data_comp.json()
        temp=math.floor((api_data['main']['temp']) -273.15)
        hum=(api_data['main']['humidity'])
    except:
        temp,hum=30,22
    try:
        random.seed(datetime.now())
        global N,P,K,ph
        first = request.form["nitrogen"]
        print(first, file=sys.stderr)
        try:
            N = float(request.form["nitrogen"])
            P = float(request.form["phosphorous"])
            K = float(request.form["pottasium"])
            ph = float(request.form["ph"])
            
            rainfall = float(request.form["rainfall"])
#             hum = float(request.form["humidity"])
#             temp = float(request.form["temperature"])
            
            soilType=request.form["soil_type"]
        except:
            N,P,K,ph,rainfall,soilType = 2,44,60,5.5,150,"sandy"
        a = {}
        a['N'] = N
        a['P'] = P 
        a['K'] = K
        a['temperature']= temp
        a['humidity'] = hum
        a['ph'] = ph
        a['rainfall'] = rainfall

        a['red']=0
        a['sandy']=0
        a['clayey']=0
        a['black']=0
        a['loamy']=0
        if(soilType=='red'):
            a['red']=1
        elif (soilType=='sandy'):
            a['sandy']=1
        elif (soilType=='clayey'):
            a['clayey']=1
        elif (soilType=='black'):
            a['black']=1
        else:
            a['loamy']=1
        

        new_df = pd.DataFrame(a, columns = ['N','P','K','temperature','humidity','ph','rainfall','black','clayey','loamy','red','sandy'],index = [0])
        #print(new_df)
        NB_pkl_filename = 'RandForest.pkl'
        NB_pkl = open(NB_pkl_filename, 'rb')
        NB_model = pickle.load(NB_pkl)
        global crop_name
        crop_name = NB_model.predict(new_df)[0]
        # df = pd.read_csv('Datasets/FertilizerData.csv')
        # temp1 = df[df['Crop']==crop_name]['soil_moisture']
        # soil_moisture = temp1.iloc[0]
        crop_name = crop_name.title()
        response = {'crop': str(crop_name)}
        response = json.dumps(response)
        return render_template('crop_res.html', response=crop_name)
    except Exception as e:
        return "Caught err "+str(e)
        
@app.route('/fertilizer_predict',methods = ['GET','POST'])
def FertRecommend():
    global crop_name
    try:
        # df = pd.read_csv('Datasets/FertilizerData.csv')
        fert = pd.read_csv('Datasets/Fertilizer.csv')
        cp1=request.form["crop"]
        cp=cp1.capitalize()
        # return render_template('fert_res.html', response=cp)
        N=fert.loc[fert['Crop']==cp].iloc[0][2]
        P=fert.loc[fert['Crop']==cp].iloc[0][3]
        K=fert.loc[fert['Crop']==cp].iloc[0][4]
        
        nr = float(request.form["nitrogen"])
        pr = float(request.form["phosphorous"])
        kr = float(request.form["pottasium"])       
    except:
        nr = 180
        pr = 70
        kr = 40
    # global N,P,K
    n = nr - N
    p = pr - P
    k = kr - K
    
    temp2 = {abs(n) : "N",abs(p) : "P", abs(k) :"K"}
    b={}
    b['N']=n
    b['P']=p
    b['K']=k
    new_df1 = pd.DataFrame(b, columns = ['N','P','K'], index=[0])
    NB_pk_filename = 'svm_fert.pkl'
    NB_pkl = open(NB_pk_filename, 'rb')
    svm_model = pickle.load(NB_pkl)
    global fert_name
    
    fert_name = svm_model.predict(new_df1)[0]

   
    return render_template('fert_res.html', response=fert_name)    



@app.route('/',methods=['GET'])
def hello():
    return render_template('index.html')
    # return "Super Awesome code is running in the background!!"
@app.route('/crop')
def crop_pred():
    return render_template('crop.html')

@app.route('/fertilizer')
def fert_pred():
    return render_template('fertilizer.html')

# app.run(port = 3000,host = "127.0.0.1")
# app = flask.Flask(__name__)
if __name__== '__main__':
    app.run(debug=True)

