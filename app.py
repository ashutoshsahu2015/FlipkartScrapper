from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pymongo

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    if request.method =='POST':
        searchtext = request.form['content'].replace(" ","")
        try:
            dbconnection = pymongo.MongoClient("mongodb+srv://admin:admin@cluster0.ssnj2.mongodb.net/reviewScrapper?retryWrites=true&w=majority")
            db = dbconnection["reviewScrapper"]
            reviews = db[searchtext].find({})
            if len(list(reviews)) > 0:
                reviews =db[searchtext].find({})
                return render_template('results.html',reviews = reviews)

            else:
                flipkart_url = "https://www.flipkart.com/search?q=" + searchtext
                uClient = uReq(flipkart_url)
                flipkartPage = uClient.read()
                uClient.close()

                flipkart_html =bs(flipkartPage,'html.parser')
                bigboxes = flipkart_html.findAll('div',{
                    'class' : "_2kHMtA"
                })

                #Creating a collection with Search String
                table = db[searchtext]
            
                for box in bigboxes:
                    product_url = "https://www.flipkart.com"+box.a['href']
                    product_request = requests.get(product_url)
                    product_page = bs(product_request.text,'html.parser')
                    comment_boxes = product_page.findAll('div',{
                    'class':"col _2wzgFH"
                    })

                    for comment in comment_boxes:
                        try:
                            commentHead = comment.div.find_all('p',{'class':"_2-N8zT"})[0].text
                        except:
                            commentHead = 'No comment Heading'
                        
                        try:
                            name = comment.find_all('div',{'class':"row _3n8db9"})[0].find_all('p',{'class',"_2sc7ZR _2V5EHH"})[0].text
                        
                        except:
                            name ='No Name'

                        try:
                            rating = comment.find_all('div',{'class':"_3LWZlK _1BLPMq"})[0].text
                        
                        except:
                            rating = 'No Rating'

                        try:
                            commentdesc = comment.find_all('div',{'class':"t-ZTKy"})[0].div.find_all('div',{'class':""})[0].text

                        except:
                            commentdesc = 'No comment description'
                        
                        product_details = {'Product':searchtext,'Name':name,'Rating':rating,'CommentHead':commentHead, 'Comment':commentdesc}
                        
                        x= table.insert_one(product_details)
                    reviews = table.find({})
                return render_template('results.html',reviews = reviews)


        except Exception as e:
            return e

    else:
        return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True, port =8000)