from flask import Flask, session, request, redirect, url_for, render_template, flash
from application.Models import*
from sqlalchemy import or_
from main import app
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

@app.route("/")
def main():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
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

@app.route("/registerSponsor", methods=['GET', 'POST'])
def registerSponsor():
    if request.method == 'POST':
        sponsor = Sponsor(
            fullname=request.form['fullname'],
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password'],
        )
        db.session.add(sponsor)
        db.session.commit()
        return redirect(url_for('spolog'))
    return render_template("registerSponsor.html")

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
        for user in U:
            ads[user.id]=UserProduct.query.filter(UserProduct.userID==user.id, UserProduct.status.in_(['Accepted','Completed'])).count()
            flagCount=User.query.filter_by(flag=True).count()
        ads=len(ads)
        
        
        return render_template("admin.html",user=user,users=users,products=products,sponsors=sponsors,ads=ads,flagCount=flagCount)
    
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
        productID = request.form.get('productID')
        if productID:
            product = Product.query.get(productID)
            if request.form.get('flag'):
                product.flag = True
            elif request.form.get('unflag'):
                product.flag = False
        sponsorID = request.form.get('sponsorID')
        if sponsorID:
            sponsor = Sponsor.query.get(sponsorID)
            if request.form.get('flag'):
                sponsor.flag = True
            elif request.form.get('unflag'):
                sponsor.flag = False
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
    requested = UserProduct.query.filter_by(status='Waiting').count()
    
    # Ad Status Distribution Pie Chart
    labels1 = ['Accepted', 'Pending', 'Completed', 'Rejected', 'Requested']
    values1 = [accepted, pending, completed, rejected, requested]
    explode = [0.2, 0.1, 0.3, 0, 0.1]
    axs[0, 0].pie(values1, labels=labels1, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
    axs[0, 0].set_title('Ad Status Distribution', pad=30)
    axs[0, 0].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Total Users Pie Chart
    influencers = User.query.count()
    sponsors = Sponsor.query.count()
    labels2 = ['Influencers', 'Sponsors']
    values2 = [influencers, sponsors]
    explode = [0.1, 0.2]
    axs[0, 1].pie(values2, labels=labels2, autopct='%1.1f%%', startangle=260, explode=explode, shadow=True)
    axs[0, 1].set_title('Total Users', pad=30)
    axs[0, 1].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Influencers Followers Pie Chart
    influ = User.query.all()
    names = [user.fullname for user in influ]
    followers = [user.followers for user in influ]
    axs[1, 0].pie(followers, labels=names, autopct='%1.1f%%', startangle=140, shadow=True)
    axs[1, 0].set_title('Influencers Reach/Followers', pad=30)
    axs[1, 0].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Products and Their Prices Bar Chart
    products = Product.query.all()
    price = [product.price for product in products]
    pname = [product.name for product in products]
    axs[1, 1].bar(pname, price, color="blueviolet", width=0.1)
    axs[1, 1].set_xlabel('Products')
    axs[1, 1].set_ylabel('Price')
    axs[1, 1].set_title('Products and Their Prices',pad=30)

    # Flagged vs Public vs Private Accounts Stacked Bar Chart
    cat = ['Public', 'Private', 'Flagged']
    public = [User.query.filter_by(visibility='Public').count(), Sponsor.query.count(), Product.query.filter_by(visibility='Public').count()]
    private = [User.query.filter_by(visibility='Private').count(), 0, Product.query.filter_by(visibility='Private').count()]
    flagged = [User.query.filter_by(flag=True).count(), Sponsor.query.filter_by(flag=True).count(), Product.query.filter_by(flag=True).count()]
    public = np.array(public)
    private = np.array(private)
    flagged = np.array(flagged)
    axs[2, 0].bar(cat, public, width=0.3, label='Public', color='red')
    axs[2, 0].bar(cat, private, bottom=public, width=0.3, label='Private', color='violet')
    axs[2, 0].bar(cat, flagged, bottom=public+private, width=0.3, label='Flagged', color='hotpink')
    axs[2, 0].set_xlabel('Categorization')
    axs[2, 0].set_ylabel('No. of Users')
    axs[2, 0].set_title('All Users Accounts Status',pad=30)
    axs[2, 0].legend()

    # Completed vs Active Ads Pie Chart
    label3 = ['Completed', 'Active']
    values3 = [completed, accepted]
    axs[2, 1].pie(values3, labels=label3, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
    axs[2, 1].set_title('Completed vs Active Ads', pad=30)
    axs[2, 1].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')

    plt.tight_layout(pad=3.0)

    path = os.path.join(app.root_path, 'static', 'Stats.png')
    plt.savefig(path, bbox_inches='tight')
    plt.clf()

    return render_template("adminStat.html")


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
        requested = UserProduct.query.filter_by(userID=user.id,status='Waiting').count()
        
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
        if (values2):
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
            axs[2, 0].set_ylabel('Budget')
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
            axs[2,1].set_title('Products and Their Prices',pad=30)
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
                    userproduct=UserProduct(userID=userID, productID=adID, status='Requested')
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
    search=request.args.get('search','').strip() #sets default to empty
    search='%'+search+'%'
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
        
        if not products and not influencers:
            flash('Warning!! No matching results found', 'warning')
            products=Product.query.all()  
            influencers=User.query.all() 
    
    #to extract the status of the products
    userID = session['userID']
    pd=UserProduct.query.filter_by(userID=userID).all()
    Status={up.productID: up.status for up in pd}
    
    return render_template('findInflu.html', products=products, Status=Status, influencers=influencers)

@app.route('/searchSpo', methods=['GET'])
def searchSpo():
    search=request.args.get('search','').strip() #sets default to empty
    search='%'+search+'%'
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
        if not products and not influencers:
            flash('Warning!! No matching results found', 'warning')
            products=Product.query.all()  
            influencers=User.query.all()  
                
    else:
        products=Product.query.all()
        influencers=User.query.all()

    return render_template('findspo.html', products=products, influencers=influencers)

@app.route('/findspo', methods=['GET','POST'])
def findspo():
    if 'sponsorID' in session:
        sponsorID=session['sponsorID']
        sponsor = Sponsor.query.get(sponsorID)
        users=User.query.all()
        products=Product.query.all()
        influencers=User.query.all()
        
        SponsorProducts=Product.query.filter_by(sponsor_id=sponsorID).all()
        
        #Status=db.session.query(Product, UserProduct.status).join(UserProduct, Product.id == UserProduct.productID).all()
        influencers=User.query.all()
        
        
        if request.method=='POST':
            prd=request.form.get('prdID')
            influID=request.form.get('influID')
            if influID:
                influencer = User.query.get(influID)
                product=Product.query.get(prd)
                currentInflu = UserProduct.query.filter_by(productID=prd, userID=influID).first() #checks if there is an existing user for same product
                if not currentInflu:
                    user_product = UserProduct(productID=prd, userID=influencer.id)
                    db.session.add(user_product)
                    db.session.commit()
                else:
                    flash(f'{influencer.fullname} is already assigned to the product {product.name}', 'warning')
                    
        
        return render_template('findspo.html',sponsorID=sponsorID,username=sponsor.username,users=users,products=products, SponsorProducts=SponsorProducts,influencers=influencers)




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

@app.route("/spolog", methods=['POST', 'GET'])
def spolog():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sponsor = Sponsor.query.filter_by(email=email, password=password).first()
        if sponsor:
            session['sponsorID'] = sponsor.id
            return redirect(url_for('sponsor',username=sponsor.username))
        else:
            return 'Invalid Details!!!'
    return render_template("spolog.html")

@app.route('/Influencer/<username>', methods=['GET', 'POST'])
def dashboard(username):
    if 'userID' in session:
        userID = session['userID']
        user = User.query.get(userID)
        if user and username:
            if request.method == 'POST':
                adID = request.form.get('adID')
                stat = request.form.get('status')
                
                up=UserProduct.query.filter_by(productID=adID,userID=userID).first() 
                if up:
                    up.status=stat
                db.session.commit()
                                    
            usrprd=UserProduct.query.filter_by(userID=userID).all()
            prdID=[a.productID for a in usrprd]
            products=Product.query.filter(Product.id.in_(prdID)).all()
            
            Status={up.productID: up.status for up in usrprd}
            progress={up.productID: up.progress for up in usrprd}
            return render_template('influpg.html', username=username,fullname=user.fullname,user=user,products=products,Status=Status,progress=progress)
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
                up.CompletedAd = completed
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

@app.route('/ad/<int:adID>/edit', methods=['POST','GET'])
def editAd(adID):
    if 'sponsorID' in session:
        ad=Product.query.get_or_404(adID)
        if request.method=='POST':
            ad.name=request.form.get('name')
            ad.description=request.form.get('description')
            ad.price=request.form.get('price')
            ad.start = datetime.strptime(request.form['start'], '%Y-%m-%d').date()
            ad.end = datetime.strptime(request.form['end'], '%Y-%m-%d').date()
            ad.Ads=request.form.get('Ads')
            ad.visibility=request.form.get('visibility')
            db.session.commit()
            
            return redirect(url_for('adDetail', adID=ad.id))
            

        return render_template('editAD.html', ad=ad)
            

@app.route('/sponsor/<username>', methods=['GET', 'POST'])
def sponsor(username):
    if 'sponsorID' in session:
        sponsorID = session['sponsorID']
        sponsor = Sponsor.query.get(sponsorID)
        if sponsor and sponsor.username==username:
            products=Product.query.filter_by(sponsor_id=sponsorID).all()
            Status={}
            progress={}
            for product in products:
                usrprd=UserProduct.query.filter_by(productID=product.id).all()
                for up in usrprd:
                    Status[product.id]=up.status
                    progress[product.id]=up.progress
                    
            if request.method == 'POST':
                adID = request.form.get('adID')
                stat = request.form.get('status')
                up=UserProduct.query.filter_by(productID=adID).first() 
                if up:
                    up.status=stat
                    db.session.commit()
                    
                    return redirect(url_for('sponsor', username=sponsor.username))
                 
            return render_template('sponsor.html',fullname=sponsor.fullname, username=sponsor.username, email=sponsor.email, Status=Status,products=products,progress=progress)
    return redirect(url_for('main'))

@app.route('/logout')
def logout():
    session.clear()  
    return redirect(url_for('main'))


@app.route('/campaigns', methods=['GET','POST'])
def campaigns():
    sponsor_id = session.get('sponsorID')
    sponsor = Sponsor.query.get(sponsor_id)
    ads = Product.query.filter_by(sponsor_id=sponsor_id).all()

    if request.method=='POST':
        name=request.form['name']
        description=request.form['description']
        price=request.form['price']
        start = datetime.strptime(request.form['start'], '%Y-%m-%d').date()
        end = datetime.strptime(request.form['end'], '%Y-%m-%d').date()
        sponsorID=session.get('sponsorID')
        Ads=request.form['Ads']
        visibility=request.form['visibility']
        
        if sponsorID:
            add=Product(name=name,description=description,price=price,start=start,end=end,sponsor_id=sponsorID, Ads=Ads, visibility=visibility)
            db.session.add(add)
            db.session.commit()
            return redirect(url_for('campaigns'))
    return render_template('campaigns.html', ads=ads, username=sponsor.username)

@app.route('/ad/<int:adID>', methods=['GET', 'POST'])
def adDetail(adID):
    sponsorID=session['sponsorID']
    sponsor=Sponsor.query.get(sponsorID)
    ad = Product.query.get(adID)
    if not ad:
        return 'error, ad not found'
    users = User.query.all()
    if request.method == 'POST':
        influencer_id = request.form.get('influencerID')
        if influencer_id:
            influencer = User.query.get(influencer_id)
            currentInflu = UserProduct.query.filter_by(productID=adID, userID=influencer_id).first() #checks if there is an existing user for same product
            if not currentInflu:
                user_product = UserProduct(productID=ad.id, userID=influencer.id)
                db.session.add(user_product)
                db.session.commit()
        deleteAD=request.form.get('deleteAD')
        if deleteAD and ad and ad.sponsor_id==session.get('sponsorID'):
            db.session.delete(ad)
            db.session.commit()
            
            return redirect(url_for('campaigns'))
        influAD=request.form.get('influAD')
        influID=request.form.get('influID')
        up=UserProduct.query.filter_by(productID=ad.id,userID=influID).first()
        if influAD and up:
            db.session.delete(up)
            db.session.commit()
            return redirect(url_for('adDetail',adID=ad.id))
    
    up = UserProduct.query.filter_by(productID=adID).all()
    status = {up.userID: up.status for up in up}
    progress={up.userID: up.progress for up in up}
    influIDs =[i.userID for i in UserProduct.query.filter_by(productID=adID).all()]
    influ= User.query.filter(User.id.in_(influIDs)).all()
    
    return render_template('adDetail.html', username=sponsor.username, ad=ad, users=users, influ=influ,status=status,progress=progress )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
