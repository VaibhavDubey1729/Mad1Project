from flask import Flask, session, request, redirect, url_for, render_template, flash
from application.Models import*
from sqlalchemy import or_
from main import app
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os


@app.route("/influlog", methods=['POST', 'GET'])
def influlog():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['userID'] = user.id
            return redirect(url_for('dashboard',username=user.username))
        else:
            return 'Invalid Details!!!'
    return render_template("influlog.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        existingUser=User.query.filter_by(username=request.form['username']).first()
        if existingUser:
            return "Username Already exists"
        existingMail=User.query.filter_by(email=request.form['email']).first()
        if existingMail:
            return "E-mail Already exists"
        user = User(
            fullname=request.form['fullname'],
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password'],
        )
        
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('influlog'))
    return render_template("register.html")


@app.route('/Influencer/<username>/Stats')
def InfluStats(username):
    if 'userID' in session:
        userID=session['userID']
        user=User.query.get(userID)
        
        def func(pct, values):
            abs = int(pct / 100.*np.sum(values))
            return "{:.1f}%\n({:d})".format(pct, abs)
        
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(14, 14))
        
        #Data for Ads Status
        accepted = UserProduct.query.filter_by(userID=user.id,status='Accepted').count() 
        pending = UserProduct.query.filter_by(userID=user.id,status='Pending').count()
        rejected = UserProduct.query.filter_by(userID=user.id,status='Rejected').count()
        completed = UserProduct.query.filter_by(userID=user.id,status='Completed').count()
        requested = UserProduct.query.filter_by(userID=user.id,status='Requested').count()
        
        labels1 = ['Accepted', 'Pending', 'Completed', 'Rejected', 'Requested']
        values1 = [accepted, pending, completed, rejected, requested]
        explode = [0.2, 0.1, 0.3, 0, 0.1]
        #to check if the data exists
        if any(values1): 
            axs[0, 0].pie(values1, labels=labels1, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
            axs[0, 0].set_title('Ads Status', pad=30)
            axs[0, 0].legend(title='Labels', bbox_to_anchor=(1.2, 1), loc='upper left')
        else:
            axs[0,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[0, 0].set_title('Ads Status', pad=30)
        
        #Data for Ads Interactions
        ads = UserProduct.query.filter(UserProduct.userID==user.id,UserProduct.status.in_(['Pending','Accepted','Rejected','Requested','Completed'])).count()
        camps=Product.query.count()
        labels2 = ['Engaged Ads', 'Total Campaigns']
        values2 = [ads, camps]
        explode = [0.2, 0.1]
        if any(values2):
            axs[0, 1].pie(values2, labels=labels2, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
            axs[0, 1].set_title('Ads Interactions', pad=30)
            axs[0, 1].legend(title='Labels', bbox_to_anchor=(1.3, 1), loc='upper left')
        else:
            axs[0,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[0, 1].set_title('Ads Interactions', pad=30)
        
        #Data for Completed Ads and Active Ads
        label3=['Completed Ads','Active Ads']
        values3=[completed,accepted]
        if any(values3): 
            axs[1, 0].pie(values3, labels=label3, autopct='%1.1f%%', startangle=120, explode=explode, shadow=True)
            axs[1, 0].set_title('Completed Vs Active Ads', pad=30)
            axs[1, 0].legend(title='Labels', bbox_to_anchor=(1.2, 1), loc='upper left')
        else:
            axs[1,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[1, 0].set_title('Completed Vs Active Ads', pad=30)
        
        #Data for possible Revenue generation from all the campaigns
        rev=sum(product.price for product in Product.query.all())
        revpos=sum(Product.query.get(up.productID).price for up in UserProduct.query.filter_by(userID=userID).all() if up.productID)
        revgen = sum(Product.query.get(up.productID).price for up in UserProduct.query.filter_by(userID=userID, status='Completed').all() if up.productID)
        label4=['Revenue Generated','Possible Revenue', 'Budget for All Campaigns']
        values4=[revgen,revpos,rev]
        if any(values4): 
            axs[1, 1].bar(label4,values4, width=0.2)
            axs[1, 1].set_title('Completed Vs Active Ads', pad=30)
        else:
            axs[1,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[1,1].set_title('Revenue Sharing', pad=30)
            
        # Products and Their Prices Bar Chart
        up=UserProduct.query.filter_by(userID=userID).all()
        prdid=[up.productID for up in up]
        assigned=Product.query.filter(Product.id.in_(prdid)).all()
        
        price = [product.price for product in assigned]
        pname = [product.name for product in assigned]
        if (price):
            axs[2, 0].bar(pname, price, color="blueviolet", width=0.1)
            axs[2, 0].set_xlabel('Products')
            axs[2, 0].set_ylabel('Budget(Rs)')
            axs[2, 0].set_title('Products and Their Prices',pad=30)
        else:
            axs[2,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[2, 0].set_title('Products and Their Prices',pad=30)
        
        #Data for Ads Prgress
        prds = UserProduct.query.filter(UserProduct.status.in_(['Accepted', 'Completed']),UserProduct.userID == userID).all()
        
        pname=[Product.query.get(up.productID).name for up in prds if Product.query.get(up.productID)]
        progress=[up.progress for up in prds]
        
        if (progress):        
            axs[2,1].bar(pname, progress, color="blueviolet", width=0.1)
            axs[2,1].set_xlabel('Products')
            axs[2,1].set_ylabel('Complition(%)')
            axs[2, 1].set_ylim(0,100)
            axs[2,1].set_title('Products Complition(%)',pad=30)
        else:
            axs[2,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[2,1].set_title('Products and Their Prices',pad=30)
        
        plt.tight_layout(pad=4.0)
        
        file=f'Stats+{user.id}+{user.username}.png'
        path = os.path.join(app.root_path, 'static', file)
        plt.savefig(path, bbox_inches='tight')
        plt.clf()
        
        return render_template('influstats.html', user=user,username=user.username, plot=url_for('static',filename=file))


@app.route('/findInflu', methods=['GET','POST'])
def findInflu():
    if 'userID' in session:
        userID = session['userID']
        user = User.query.get(userID) 
        products=Product.query.all()
        influencers=User.query.all()
        
        pd=UserProduct.query.filter_by(userID=userID).all()
        Status={up.productID: up.status for up in pd}
        
        #to extract all the products that aren't assigned to anyone yet
        a=db.session.query(UserProduct.productID).distinct()
        pna=Product.query.filter(Product.id.not_in(a)).all()
        
        
        if request.method =="POST":
            adID = request.form.get('adID')
            influID = request.form.get('influID')
            req = request.form.get('request')
            stat = request.form.get('status')
            flag=request.form.get('Flag')
            up=UserProduct.query.filter_by(productID=adID,userID=userID).first() 
            if up:
                up.status=stat
                db.session.commit()
            if req=='Request':
                currentReq=UserProduct.query.filter_by(userID=userID, productID=adID).first()
                if currentReq:
                    pass
                else:
                    userproduct=UserProduct(userID=userID, productID=adID, status='Requested', budget=Product.query.get(adID).price)
                    
                    db.session.add(userproduct)
                    db.session.commit()
                    
            if flag=='FlagAD':
                prd=Product.query.get(adID)
                prd.flagCount+=1
                flash(f'Reported!! The Product ({prd.name}) has been reported', 'warning')
            if flag=='FlagInflu':
                influ=User.query.get(influID)
                influ.flagCount+=1
                flash(f'Reported!! The User ({influ.fullname}) has been reported', 'warning')
            db.session.commit()
                
                    
            return redirect(url_for('findInflu'))
            
            
        return render_template('findInflu.html',username=user.username,fullname=user.fullname,Status=Status, products=products, influencers=influencers)


@app.route('/search', methods=['GET'])
def search():
    input=request.args.get('search','').strip() #sets default to empty
    category = request.args.get('category', '')
    search='%'+input+'%'
    if search:
        products=Product.query.join(Sponsor).filter(
            Product.name.like(search) |
            Product.description.like(search) |
            Product.price.like(search) |
            Sponsor.fullname.like(search)
            ).all()
        influencers = User.query.filter(
            or_(
                User.fullname.like(search),
                User.username.like(search)
            )
        ).all()
    if category:
        products=Product.query.filter(
            Product.category.like(category)
        ).all()
        influencers=User.query.filter(
            User.category.like(category)
        ).all()
        
    if not products and not influencers:
        flash('Warning!! No matching results found', 'warning')
        products=Product.query.all()  
        influencers=User.query.all() 

    #to extract the status of the products
    userID = session['userID']
    pd=UserProduct.query.filter_by(userID=userID).all()
    Status={up.productID: up.status for up in pd}
    
    return render_template('findInflu.html', products=products, Status=Status, influencers=influencers)


@app.route('/Influencer/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'userID' in session:
        userID = session['userID']
        user = User.query.get(userID)
        if user and username:
            if request.method == 'POST':
                adID = request.form.get('adID')
                stat = request.form.get('status')
                budget=request.form.get('Budget')
                up=UserProduct.query.filter_by(productID=adID,userID=userID).first()
                if up:
                    if budget:
                        up.budget=budget
                        up.status='Negotiation'
                    else:
                        pd=Product.query.filter_by(id=adID).first()
                        up.budget=pd.price
                        up.status=stat
                    db.session.commit()
                                    
            usrprd=UserProduct.query.filter_by(userID=userID).all()
            prdID=[a.productID for a in usrprd]
            products=Product.query.filter(Product.id.in_(prdID)).all()
            
            Status={up.productID: up.status for up in usrprd}
            progress={up.productID: up.progress for up in usrprd}
            budget={up.productID: up.budget for up in usrprd}
            return render_template('influpg.html', username=username,fullname=user.fullname,user=user,products=products,Status=Status,progress=progress, budget=budget)
    return redirect(url_for('main'))

@app.route('/progress', methods=['GET','POST'])
def progress():
    if 'userID' in session:
        userID = session['userID']
        user = User.query.get(userID)
        if request.method=='POST':
            adID=request.form.get('adID')
            completed = int(request.form.get('completed'))
            prd=Product.query.get(adID)
            up=UserProduct.query.filter_by(productID=adID,userID=userID).first() 
            if up:
                up.progress=(completed/prd.Ads)*100
                if completed == prd.Ads:
                    up.status = 'Completed'
            db.session.commit()
                
        return redirect(url_for('dashboard', username=user.username))
    

@app.route('/Influencer/<username>/<influencer>',methods=['POST','GET'])
def influencer(username,influencer):
    userID=session['userID']
    user=User.query.get(userID)
    inf=User.query.filter_by(username=influencer).all()
    for i in inf:
        influID=i.id
    influ=User.query.get(influID)
    if request.method=='POST':
        if request.form.get('flag'):
            influ.flagCount+=1
        if request.form.get('follow'):
            influ.followers+=1
        if request.form.get('unfollow'):
            influ.followers-=1
        db.session.commit()
        
        return redirect(url_for('influencer',username=username,influencer=influencer))
    
    return render_template('influencer.html',influ=influ, user=user,username=username,influencer=influencer)    

@app.route('/setting/<username>', methods=['POST','GET'])
def settingInflu(username):
    if 'userID' in session:
        userID = session['userID']
        user = User.query.get(userID)
        username=user.username
        if request.method=='POST':
            user.fullname=request.form['fullname']
            user.username=request.form['username']
            user.bio=request.form['bio']
            user.category=request.form['category']
            user.niche=request.form['niche']
            user.visibility=request.form['visibility']
            db.session.commit()
            
    return render_template('settinginflu.html', username=username, user=user)


