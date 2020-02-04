import imaplib
import email
from bs4 import BeautifulSoup
import re
from datetime import datetime
from pymongo import MongoClient
from DBConnection import client
from ScrapeImg import scrapeimg


m = imaplib.IMAP4_SSL('imap.outlook.com',993)
m.login('youremail@outlook.com', 'yourpassword')

m.select('Inbox')

resp, items = m.search(None, 'FROM', '"sender_email@outlook.com"')
items = items[0].split()
#print(items)

for emailid in items:
    resp, data = m.fetch(emailid, "(RFC822)")
    email_body = data[0][1]
    mail = email.message_from_bytes(email_body)
    #print(mail)

    #Check email content type
    #'multipart' : contains HTML and text in email
    #'digest': automated generated email
    #In this case, the email is both

    if mail.get_content_maintype() != 'multipart':
    #if mail.get_content_type() == 'text/plain':
        continue

    #Retrieve email subject
    subject = ""
    date = ""

    if mail["subject"] is not None:
        subject = mail["subject"]
        date = mail["Date"]
        #print("DD " + date)
        #date = datetime.strptime(mail["Date"], "%a, %d %b %Y %H:%M:%S %z")
        print("Email subject: " + subject)
        print("Date: "+ str(date))
    #print("["+ mail["From"]+"] :" + subject)

    for payload in mail.get_payload():

        body = payload.get_payload()
        soup = BeautifulSoup(body, 'html.parser')

        #print(soup.prettify())
        title = soup.find(name='table', attrs={'class': '3D"MsoNormalTable"', 'id': '3D"templateBody"'})

        if title is not None:
            title = title.find('p').text.replace('=','')
            print("Title: "+ str(title))


        content = soup.find(name='p', attrs={'style': '3D"margin-top:7.5pt;line-height:140%;float:left"'})

        if content is not None:
            delay = content.findAll(name= 'b')[0].text
            delay = int(str(delay).replace(' minit',''))
            

            distance = content.findAll(name='b')[1].text
            distance = float(str(distance).replace(' km',''))
            

            speed = content.findAll(name='b')[2].text
            speed = float(str(speed).replace(' km/j',''))
            

            traffic = content.findAll(name='b')[3].text
            traffic = int(str(traffic).replace('% perlahan dari biasa',''))/100
           

        #To ways to construct image Url:
        #1) Construct manually from tag attributes
        #2) If the url header is known & CONSTANT, (eg: www.whatever.com/), hard code the header
        #and append to list index (imgList[4])

        image = soup.find(name='table',attrs={'class':'3D"MsoNormalTable"','id':'3D"templateColumns"'})

        if image is not None:
            img = image.find(name='img')
            head = img['src'].replace('3D"','').replace('=','')
            imgList = list(img.attrs)
            #Choice 1:
            url = head + imgList[3] + "/" + imgList[4].replace('"','')
            #Choice 2:
            #url = 'http://livemap-image.waze.com/'+ imgList[4].replace('"','')

            #print(url)
            #Scrape image here:
            scrapeimg(url).getImage()

            
    #Compose output to a dictionary
    result = {'Subject': subject, 'Date': date, 'Title': title, 'Delay (minutes)': delay, 'Distance (km)': distance, 'Speed (km/h)': speed, 'Traffic rate (%)' : traffic}

    #print(struct)

    #insert struct into MongoDB
    coll = client['yourCollectionName']
    coll.insert_one(result)


