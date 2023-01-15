from flask import Flask, request, render_template, redirect, session ,flash
import pymongo 
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId


myclient = pymongo.MongoClient("mongodb://localhost:27017")
db = myclient["mydatabase"]
user_table = db["user"]
tour_table = db["tour"]
payment_table = db["payment"]
review_table = db["review"]

app = Flask(__name__)

app.secret_key = 'super secret key'

img = False

@app.route('/', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home ():
    tours = list(tour_table.find())
    reviews=list(review_table.find())
    count=0
    img= True
    return render_template("index.html", **locals())

@app.route('/about', methods=['GET', "POST"])
def about ():
   
    return render_template("about.html", **locals())

@app.route('/contract', methods=['GET', "POST"])
def contract ():
   
    return render_template("contract.html", **locals())

@app.route('/review', methods=['GET', "POST"])
def review ():
    msg=""
   
        
    if request.method == "POST":

        name = request.form["name"]
        place=  request.form["place"]
        comment = request.form["comment"]
        date = request.form["date"]
        
        
        place = db.payment.find_one({"tourname": place})
        if  place is not None:
            if name != place["username"] :
                msg = "No records were found"
                return render_template("review.html", **locals())
            else:
                review_table.insert_one(dict(request.form))
                msg= "Data has been Inserted"
                return render_template("review.html", **locals())
        
           
        msg= "No place were found"
        return render_template("review.html", **locals())
            
    reviews=list(review_table.find())
    return render_template("review.html", **locals())
   


@app.route('/event', methods=['GET', "POST"])
def event ():
   
    return render_template("event.html", **locals())


@app.route('/admin-login', methods=['GET', "POST"])
def admin_login ():
    if request.method =="POST":
        form_data =request.form
        email = form_data["email"]
        password = form_data["password"]
        user = db.user.find_one({"email": email})
        msg=" "
        if user is None:
            msg = "User doesn't exist"
            return render_template("admin-login.html", **locals())
        else:
            if password!= user["password"]:
                msg = "Password did not match"
                return render_template("admin-login.html", **locals())

            else:
                msg = "Login Successful!"   
                return render_template("admin-panel.html", **locals())


   
    return render_template("admin-login.html", **locals())

@app.route('/logout', methods=['GET', "POST"])
def logout():
    # remove the username from the session if it's there
    session.pop('email', None)
    session.clear()
    return render_template("admin-login.html", **locals())


@app.route('/insert_tour', methods=['GET', "POST"])
def insert_tour ():

     msg=""
     if request.method == "POST":
        
        
        image = request.files["image"]
        
        # mongo.save_file(image.image, image)

        tourname = request.form["tourname"]
        cardtext = request.form["cardtext"]
        date= request.form["date"]
        seat= request.form["seat"]
        duration = request.form["duration"]
        price = request.form["price"]
        # tempname = request.files['image']['tempname']
        
        name = db.tour.find_one({"tourname": tourname})
        if name is not None:
            msg = "Tour already exist"
            return render_template("insert_tourdetails.html", **locals())
        else:
            tour_table.insert_one(dict(request.form))
            msg= "Data has been Inserted"
        
       
        return render_template("insert_tourdetails.html", **locals())

     return render_template("insert_tourdetails.html", **locals())


@app.route("/tour_history",methods=['GET','POST'])
def history():
    tours =list(tour_table.find())
    return render_template("tour_history.html",**locals())

@app.route("/tour_details/<id>",methods=['GET','POST'])
def details(id):

    tours=list(tour_table.find())

    for tour in tours:
        if str(tour['_id']) == id:
            id = tour['_id']
            tourname = tour['tourname']
            cardtext = tour["cardtext"]
            date= tour["date"]
            seat= tour["seat"]
            duration = tour["duration"]
            price = tour["price"]
            return render_template("event.html",**locals())

    return render_template("event.html",**locals())


@app.route("/edit/<id>",methods=['GET','POST'])
def edit(id):

    msg = " "

    if request.method=='POST':
        tourname = request.form["tourname"]
        cardtext = request.form["cardtext"]
        date= request.form["date"]
        seat= request.form["seat"]
        duration = request.form["duration"]
        price = request.form["price"]
        filter = {'_id': ObjectId(id)}
        newvalues = {"$set": {'tourname': tourname, 'cardtext':cardtext,'date': date, 'seat': seat, 'duration': duration, 'price': price}}
        tour = tour_table.update_one(filter,newvalues)
        msg="Updated successfully"
    else:
        tours=list(tour_table.find())
        for tour in tours:
            if str(tour['_id']) == id:
                id = tour['_id']
                tourname = tour['tourname']
                cardtext = tour["cardtext"]
                date= tour["date"]
                seat= tour["seat"]
                duration = tour["duration"]
                price = tour["price"]
                return render_template("edit_tour.html",**locals())

    return render_template("edit_tour.html",**locals())



    

@app.route("/delete/<id>",methods=['GET','POST'])
def delete(id):
    
    tour = tour_table.delete_one({"_id":ObjectId(id)})

    return redirect("/tour_history")


@app.route('/payment/<id>', methods=['GET', "POST"])
def payment(id):
    msg=""

    tours=list(tour_table.find())

    for tour in tours:
        if str(tour['_id']) == id:
            tourname = tour['tourname']
            id = tour['_id']

            if request.method == "POST":
                tourname = tour['tourname']
                id = tour['_id']
                username = request.form["username"]
                email= request.form["email"]
                phone= request.form["phone"]
                amount= request.form["amount"]
                transaction_id = request.form["transaction_id"]
                t_size = request.form["t_size"]
                tran_id= db.payment.find_one({"transaction_id": transaction_id})
                emal = db.payment.find_one({"email": email})
                phn = db.payment.find_one({"phone": phone})

                if tran_id is None:
                        payment_table.insert_one({"tourname": tourname, "username": username, "email": email, "phone": phone,
                                                "amount": amount, "transaction_id": transaction_id, "t_size":t_size})
                        msg= "Payment Successful"
                        return render_template("payment.html", **locals())
                else:
                     msg= "Transaction ID Already exist "
                     return render_template("payment.html", **locals())

            return render_template("payment.html", **locals())    

        
@app.route('/view_payment', methods=['GET', "POST"])
def view_payment(): 
    
    payments =list(payment_table.find())

    return render_template("view_payment.html", **locals())    
    
@app.route('/view_review', methods=['GET', "POST"])
def view_review(): 
    
    reviews =list(review_table.find())

    return render_template("view_review.html", **locals())  




if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5002)
    #serve(app, host='127.0.0.1', port=5002)
    #serve(app, host='0.0.0.0', port=80)