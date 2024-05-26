import csv
import requests
i=1
url="http://188.166.211.155:8081/calories_img/"
with open('image_program.csv', 'r') as csv_file:
    reader = csv.reader(csv_file)
    next(reader)
    for row in reader:
        if row[4]==1:
            continue
        response = requests.get(url+row[1])
        with open("images/"+row[1], "wb") as f:
            f.write(response.content)
        i+=1
        if i%500 == 0:
            print(i,":",row[1])