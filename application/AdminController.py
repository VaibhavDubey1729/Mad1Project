from flask import Flask, session, request, redirect, url_for, render_template, flash
from application.Models import*
from sqlalchemy import or_
from main import app
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

@app.route("/adminlog", methods=['POST', 'GET'])
def adminlog():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=password).first()
        if user and user.id==1:
            session['userID'] = user.id
            return redirect(url_for('admin'))
        else:
            return 'Invalid Details!!!'
    return render_template("adminlog.html")

@app.route("/admin")
def admin():
    if 'userID' in session:
        userID=session['userID']
        user=User.query.get(userID)
        U=User.query.all()
        users=User.query.count()
        products=Product.query.count()
        sponsors=Sponsor.query.count()
        ads={}
        flagCount={}
        complete={}
        for user in U:
            ads[user.id]=UserProduct.query.filter(UserProduct.userID==user.id, UserProduct.status.in_(['Accepted'])).count()
            complete[user.id]=UserProduct.query.filter(UserProduct.userID==user.id, UserProduct.status.in_(['Completed'])).count()
            flagCount=User.query.filter_by(flag=True).count()+Sponsor.query.filter_by(flag=True).count()
        ads=len(ads)
        complete=len(complete)
        
        
        return render_template("admin.html",user=user,users=users,products=products,sponsors=sponsors,ads=ads,flagCount=flagCount,complete=complete)
    
@app.route('/admin/Influencers',methods=['POST','GET'])
def adminInflu():
    users=User.query.all()
    ads={}
    flagCount={}
    for user in users:
        ads[user.id]=UserProduct.query.filter_by(userID=user.id, status='Accepted').count()
        flagCount[user.id]=User.query.filter_by(id=user.id).count()
    if request.method=='POST':
        userID=request.form.get('userID')
        if userID:
            user=User.query.get(userID)
            if request.form.get('flag'):
                user.flag=True
            elif request.form.get('unflag'):
                user.flag=False
            elif request.form.get('delete'):
                db.session.delete(user)
                
            db.session.commit()
        
        return redirect(url_for('adminInflu'))
            
        
    return render_template("adminInflu.html",users=users,ads=ads,flagCount=flagCount)

@app.route('/admin/Sponsors', methods=['POST','GET'])
def adminSpo():
    sponsors=Sponsor.query.all()
    camps={}
    active={}
    budget={}
    for sponsor in sponsors:
        camps[sponsor.id]=Product.query.filter_by(sponsor_id=sponsor.id).count()
        active[sponsor.id]=UserProduct.query.join(Product).filter(
            Product.sponsor_id==sponsor.id, UserProduct.status=='Accepted').count()
        products=Product.query.filter_by(sponsor_id=sponsor.id).all()
        budget[sponsor.id]=sum(product.price for product in products)
        
    if request.method=='POST':
        sponsorID=request.form.get('sponsorID')
        if sponsorID:
            sponsor=Sponsor.query.get(sponsorID)
            if request.form.get('flag'):
                sponsor.flag=True
            elif request.form.get('unflag'):
                sponsor.flag=False
            elif request.form.get('delete'):
                db.session.delete(sponsor)
            db.session.commit()
        
        return redirect(url_for('adminSpo'))
    
    return render_template("adminSpo.html",sponsors=sponsors, camps=camps,active=active,budget=budget)

@app.route('/admin/Campaigns',methods=['GET','POST'])
def adminCamp():
    products=Product.query.all()
    ads={}
    accepted={}
    sponsor={}
    progress={}
    for product in products:
        ads[product.id]=UserProduct.query.filter_by(productID=product.id).count()
        accepted[product.id]=UserProduct.query.filter(UserProduct.productID==product.id, UserProduct.status.in_(['Accepted','Completed'])).count()
        sp=Sponsor.query.get(product.sponsor_id)
        sponsor[product.id]=sp.fullname
        pg=UserProduct.query.filter_by(productID=product.id).first()
        progress[product.id]=pg.progress if pg else 0
        
    if request.method=='POST':
        productID=request.form.get('productID')
        if productID:
            product=Product.query.get(productID)
            if request.form.get('flag'):
                product.flag=True
            elif request.form.get('unflag'):
                product.flag=False
            elif request.form.get('delete'):
                db.session.delete(product)
            db.session.commit()
        
        return redirect(url_for('adminCamp'))
    
    return render_template("adminCamp.html",products=products,ads=ads,accepted=accepted,sponsor=sponsor,progress=progress)


@app.route('/admin/Reports', methods=['GET', 'POST'])
def adminReport():
    # Fetch users who are flagged or have a flag count greater than 0
    users = User.query.filter((User.flagCount > 0) | (User.flag == True)).all()
    ads = {}
    flagCount = {}
    
    # Fetch only flagged products
    products = Product.query.filter((Product.flagCount > 0) | (Product.flag == True)).all()
    ad = {}
    accepted = {}
    spo = {}
    progress = {}
    
    # Fetch only flagged sponsors
    sponsors = Sponsor.query.filter((Sponsor.flagCount > 0) | (Sponsor.flag == True)).all()
    camps = {}
    active = {}
    budget = {}
    
    for sponsor in sponsors:
        camps[sponsor.id] = Product.query.filter_by(sponsor_id=sponsor.id).count()
        active[sponsor.id] = UserProduct.query.join(Product).filter(
            Product.sponsor_id == sponsor.id, UserProduct.status == 'Accepted').count()
        products = Product.query.filter_by(sponsor_id=sponsor.id).filter(
            (Product.flagCount > 0) | (Product.flag == True)).all()  # Filter only flagged products
        budget[sponsor.id] = sum(product.price for product in products)
        
    for user in users:
        ads[user.id] = UserProduct.query.filter_by(userID=user.id, status='Accepted').count()
        flagCount[user.id] = User.query.filter_by(id=user.id).count()
        
    for product in products:
        ad[product.id] = UserProduct.query.filter_by(productID=product.id).count()
        accepted[product.id] = UserProduct.query.filter(
            UserProduct.productID == product.id,
            UserProduct.status.in_(['Accepted', 'Completed'])
        ).count()
        sp = Sponsor.query.get(product.sponsor_id)
        spo[product.id] = sp.fullname if sp else 'Unknown'
        pg = UserProduct.query.filter_by(productID=product.id).first()
        progress[product.id] = pg.progress if pg else 0
        
    if request.method == 'POST':
        userID = request.form.get('userID')
        if userID:
            user = User.query.get(userID)
            if request.form.get('flag'):
                user.flag = True
            elif request.form.get('unflag'):
                user.flagCount = 0  # Resetting the Flag Count as soon as the user gets unflagged
                user.flag = False
            elif request.form.get('delete'):
                db.session.delete(user)
        productID = request.form.get('productID')
        if productID:
            product = Product.query.get(productID)
            if request.form.get('flag'):
                product.flag = True
            elif request.form.get('unflag'):
                product.flag = False
            elif request.form.get('delete'):
                db.session.delete(product)
        sponsorID = request.form.get('sponsorID')
        if sponsorID:
            sponsor = Sponsor.query.get(sponsorID)
            if request.form.get('flag'):
                sponsor.flag = True
            elif request.form.get('unflag'):
                sponsor.flag = False
            elif request.form.get('delete'):
                db.session.delete(sponsor)
        db.session.commit()
        
        return redirect(url_for('adminReport'))
            
    return render_template("adminReport.html", users=users, ads=ads, flagCount=flagCount, products=products, ad=ad, accepted=accepted, sponsor=spo, progress=progress, sponsors=sponsors, camps=camps, active=active, budget=budget)

@app.route('/admin/Statistics')
def adminStat():
    
    fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(12, 12))
    
     # Data for Ad Status
    accepted = UserProduct.query.filter_by(status='Accepted').count()
    pending = UserProduct.query.filter_by(status='Pending').count()
    rejected = UserProduct.query.filter_by(status='Rejected').count()
    completed = UserProduct.query.filter_by(status='Completed').count()
    requested = UserProduct.query.filter_by(status='Requested').count()
    
    # Ad Status Distribution Pie Chart
    labels1 = ['Accepted', 'Pending', 'Completed', 'Rejected', 'Requested']
    values1 = [accepted, pending, completed, rejected, requested]
    explode = [0.2, 0.1, 0.3, 0, 0.1]
    
    if any(values1):
        axs[0, 0].pie(values1, labels=labels1, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
        axs[0, 0].set_title('Ad Status Distribution', pad=30)
        axs[0, 0].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        axs[0,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[0, 0].set_title('Ad Status Distribution', pad=30)

    # Total Users Pie Chart
    influencers = User.query.count()
    sponsors = Sponsor.query.count()
    labels2 = ['Influencers', 'Sponsors']
    values2 = [influencers, sponsors]
    explode = [0.1, 0.2]
    if any(values2):
        axs[0, 1].pie(values2, labels=labels2, autopct='%1.1f%%', startangle=260, explode=explode, shadow=True)
        axs[0, 1].set_title('Total Users', pad=30)
        axs[0, 1].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        axs[0,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[0, 1].set_title('Total Users', pad=30)

    # Influencers Followers Pie Chart
    influ = User.query.all()
    names = [user.fullname for user in influ]
    followers = [user.followers for user in influ]
    if any(followers):
        axs[1, 0].pie(followers, labels=names, autopct='%1.1f%%', startangle=140, shadow=True)
        axs[1, 0].set_title('Influencers Reach/Followers', pad=30)
        axs[1, 0].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        axs[1,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[1, 0].set_title('Influencers Reach/Followers', pad=30)
    
    # Products and Their Prices Bar Chart
    products = Product.query.all()
    price = [product.price for product in products]
    pname = [product.name for product in products]
    if any(price):
        axs[1, 1].bar(pname, price, color="blueviolet", width=0.1)
        axs[1, 1].set_xlabel('Products')
        axs[1, 1].set_ylabel('Price')
        axs[1, 1].set_title('Products and Their Prices',pad=30)
    else:
        axs[1,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[1, 1].set_title('Products and Their Prices',pad=30)

    # Flagged vs Public vs Private Accounts Stacked Bar Chart
    cat = ['Public', 'Private', 'Flagged']
    public = [User.query.filter_by(visibility='Public').count(), Sponsor.query.count(), Product.query.filter_by(visibility='Public').count()]
    private = [User.query.filter_by(visibility='Private').count(), 0, Product.query.filter_by(visibility='Private').count()]
    flagged = [User.query.filter_by(flag=True).count(), Sponsor.query.filter_by(flag=True).count(), Product.query.filter_by(flag=True).count()]
    public = np.array(public)
    private = np.array(private)
    flagged = np.array(flagged)
    
    if np.any(public) or np.any(private) or np.any(flagged):
        axs[2, 0].bar(cat, public, width=0.3, label='Public', color='red')
        axs[2, 0].bar(cat, private, bottom=public, width=0.3, label='Private', color='violet')
        axs[2, 0].bar(cat, flagged, bottom=public + private, width=0.3, label='Flagged', color='hotpink')
        axs[2, 0].set_xlabel('Categorization')
        axs[2, 0].set_ylabel('No. of Users')
        axs[2, 0].set_title('All Users Accounts Status', pad=30)
        axs[2, 0].legend()
    else:
        axs[2, 0].text(0.5, 0.5, 'No Data Available', horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[2, 0].set_title('All Users Accounts Status', pad=30)

    # Completed vs Active Ads Pie Chart
    label3 = ['Completed', 'Active']
    values3 = [completed, accepted]
    if any(values3):
        axs[2, 1].pie(values3, labels=label3, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
        axs[2, 1].set_title('Completed vs Active Ads', pad=30)
        axs[2, 1].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        axs[2,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[2, 1].set_title('Completed vs Active Ads', pad=30)

    plt.tight_layout(pad=3.0)

    path = os.path.join(app.root_path, 'static', 'Stats.png')
    plt.savefig(path, bbox_inches='tight')
    plt.clf()

    return render_template("adminStat.html")
