import requests,json,sqlite3,sys,win10toast


# Create a connection to the database
conn = sqlite3.connect('jokes.sqlite3')

cur = conn.cursor()
print(cur, type(cur))

cur.execute('''CREATE TABLE IF NOT EXISTS jokes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    jokeID INTEGER,
                    category VARCHAR,
                    joke TEXT,
                    setup TEXT,
                    delivery TEXT,
                    nsfw BOOLEAN,
                    religious BOOLEAN,
                    political BOOLEAN,
                    racist BOOLEAN,
                    sexist BOOLEAN,
                    explicit BOOLEAN);''')
#ცხრილში jokes მოცემულია ხუმრობის ავტომატურად მინიჭებული ID მის APIდან აღებულ IDსთან ერთად, რადგან შევძლოთ ცხრილში ერთნაირი ხუმრობების დამატების თავიდან არიდება
#მოცემულია ხუმრობის კატეგორია
#თუ ხუმრობის ტიპია single, მოცემულია ხუმრობის ტექსტი, ხოლო twopartისშემთხვევაში, მოცემულია setup როგორც ხუმრობის დასაწყისი (უმეტეს შემთხვევაში კითხვის სახით) და delivery, ანუ პასუხი
#ამ 3 მონაცემს დათმობილი აქვს მაქსიმალური შესაძლო ადგილი
#ყველა სხვა მონაცემი არის ხუმრობის ქვეკატეგორია.

conn.commit()

api="https://v2.jokeapi.dev/joke/Any"

res=requests.get(api)
if res.status_code>=500:
    print("server error")
    sys.exit()

response_date=res.headers['Date']
res=json.loads(res.text)
print(f"{res['joke']} \n{res['category']}") if res['type']=='single' else print(f"{res['setup']} \n{res['delivery']} \n{res['category']}")

def construct_tup(obj:dict):
    tup=(obj['id'], obj['category'])
    if obj["type"]=="single":
        tup+=(obj['joke'],"-----","-----")
    else:
        tup+=("-----",obj['setup'],obj['delivery'])
    tup+=(obj['flags']['nsfw'],obj['flags']['religious'],obj['flags']['political'],obj['flags']['racist'],obj['flags']['sexist'],obj['flags']['explicit'])

    updfile(obj)

    return tup

def updfile(obj):
    with open("lastjoke.json","w") as file:
        json.dump(obj,file,indent=4)

def popToast():
    toast=win10toast.ToastNotifier()
    toast.show_toast("joke",f"category: {res['category']}")
    #როგორც მივხვდი, მოდულს ბევრი პრობლემა აქვს და ბოლოს გამოტანილი ერორიც მოდულის ბრალია. ამას წერენ ფორუმეზეც. 


def insert(tup):
    joke_id = tup[0]
    cur.execute("SELECT jokeID FROM jokes WHERE jokeID=?", (joke_id,))
    result = cur.fetchone()
    
    if result is None:  # jokeID doesn't exist in the table
        query = "INSERT INTO jokes (jokeID, category, joke, setup, delivery, nsfw, religious, political, racist, sexist, explicit) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cur.execute(query, tup)
        conn.commit()
        popToast()
    else:
        print("this joke already exists in the table.")
        popToast()

insert(construct_tup(res))

conn.close()
