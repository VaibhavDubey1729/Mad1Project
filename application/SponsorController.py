from flask import Flask, session, request, redirect, url_for, render_template, flash
from application.Models import*
from sqlalchemy import or_
from main import app
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

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

@app.route("/registerSponsor", methods=['GET', 'POST'])
def registerSponsor():
    if request.method == 'POST':
        existingUser=Sponsor.query.filter_by(username=request.form['username']).first()
        if existingUser:
            return "Username Already exists"
        existingMail=Sponsor.query.filter_by(email=request.form['email']).first()
        if existingMail:
            return "E-mail Already exists"
        
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

@app.route('/Sponsor/<username>/Stats')
def spoStats(username):
    if 'sponsorID' in session:
        sponsorID=session['sponsorID']
        sponsor=Sponsor.query.get(sponsorID)
        
        #Data for Ads Status
        products=Product.query.filter_by(sponsor_id=sponsorID).all()
        accepted={}
        pending={}
        rejected={}
        completed={}
        requested={}
        
        for product in products:
            accepted[product.id] = UserProduct.query.filter_by(productID=product.id,status='Accepted').count() or 0
            pending[product.id] = UserProduct.query.filter_by(productID=product.id,status='Pending').count() or 0
            rejected[product.id] = UserProduct.query.filter_by(productID=product.id,status='Rejected').count() or 0
            completed[product.id] = UserProduct.query.filter_by(productID=product.id,status='Completed').count() or 0
            requested[product.id] = UserProduct.query.filter_by(productID=product.id,status='Requested').count() or 0
        
            

        accepted = sum(accepted.values())
        pending= sum(pending.values())
        rejected = sum(rejected.values())
        completed = sum(completed.values())
        requested = sum(requested.values())
        # Ad Status Distribution Pie Chart
        labels1 = ['Accepted', 'Pending', 'Completed', 'Rejected', 'Requested']
        values1 = [accepted, pending, completed, rejected, requested]
        explode = [0.2, 0.1, 0.3, 0, 0.1]
        
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(15, 15))

        if any(values1):
            axs[0, 0].pie(values1, labels=labels1, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
            axs[0, 0].set_title('Ad Status Distribution', pad=30)
            axs[0, 0].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
        else:
            axs[0,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[0, 0].set_title('Ad Status Distribution', pad=30)
        
       
        
        products = Product.query.filter_by(sponsor_id=sponsor.id).all()        
        price = [product.price for product in products]
        pname = [product.name for product in products]
        
        if any(price):
            axs[0, 1].bar(pname, price, color="blueviolet", width=0.1)
            axs[0, 1].set_xlabel('Products')
            axs[0, 1].set_ylabel('Price(Rs)')
            axs[0, 1].set_title('Products and Their Prices',pad=30)
        else:
            axs[0,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[0, 1].set_title('Products and Their Prices',pad=30)


        progress=[UserProduct.query.filter_by(productID=product.id).first().progress for product in products  if UserProduct.query.filter_by(productID=product.id).first()]
        upname=[product.name for product in products if UserProduct.query.filter_by(productID=product.id).first()]
        
        if any(progress):
            axs[1, 0].bar(upname, progress, color="red", width=0.1)
            axs[1, 0].set_xlabel('Products')
            axs[1, 0].set_ylabel('Progress(%)')
            axs[1, 0].set_ylim(0,100)
            axs[1, 0].set_title('Products and their Progress(%)',pad=30)
        else:
            axs[1,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[1,0].set_title('Products and their Progress(%)',pad=30)
        
        ads=[product.Ads for product in products if UserProduct.query.filter_by(productID=product.id).first()]
        if any(ads):
            axs[1, 1].bar(upname, ads, color="violet", width=0.1)
            axs[1, 1].set_xlabel('Products')
            axs[1, 1].set_ylabel('No. of Ads')
            axs[1, 1].set_title('Products and No. of Ads',pad=30)
        else:
            axs[1,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[1,1].set_title('Products and No. of Ads',pad=30)
         #Campaign Budget vs Negotiated Budget
        pprice=[UserProduct.query.filter_by(productID=product.id).first().budget for product in products  if UserProduct.query.filter_by(productID=product.id).first()]
        nprice = [product.price for product in products if UserProduct.query.filter_by(productID=product.id).first()]
        if any(nprice):
            axs[2, 0].bar(upname, pprice, color="violet", width=0.1,label='Negotiated Budget')
            axs[2, 0].bar(upname, nprice, color="red", width=0.1,label='Campaign Budget')
            axs[2, 0].set_xlabel('Products')
            axs[2, 0].set_ylabel('No. of Ads')
            axs[2, 0].set_title('Original Budget vs Negotiated Budget',pad=30)
            axs[2, 0].legend()
        else:
            axs[2,0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[2,0].set_title('Original Budget vs Negotiated Budget',pad=30)
        
        public=Product.query.filter_by(sponsor_id=sponsorID,visibility='Public').count()
        private=Product.query.filter_by(sponsor_id=sponsorID,visibility='Private').count()
        visibility=[public,private]
        lables=['Public','Private']
        explode1=[0.2,0.3]
        
        if (public or private):
            axs[2, 1].pie(visibility, labels=lables, autopct='%1.1f%%', startangle=140, explode=explode1, shadow=True)
            axs[2, 1].set_title('Public vs Private Campaigns',pad=30)
        else:
            axs[2,1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
            axs[2,1].set_title('Original Budget vs Negotiated Budget',pad=30)
        plt.tight_layout(pad=4.0)
        
        file=f'Stats+Sponsor+{sponsor.id}+{sponsor.username}.png'
        path = os.path.join(app.root_path, 'static', file)
        plt.savefig(path, bbox_inches='tight')
        plt.clf()
    
    
    return render_template('spoStats.html', username=username,plot=url_for('static',filename=file))


@app.route('/searchSpo', methods=['GET'])
def searchSpo():
    input=request.args.get('search','').strip() #sets default to empty
    category = request.args.get('category', '')
    search='%'+input+'%'
    if search:
        products=Product.query.join(Sponsor).filter(
            Product.name.like(search) |
            Product.description.like(search) |
            Product.price.like(search) |
            Product.category.like(search) |
            Sponsor.fullname.like(search)
            ).all()
        influencers = User.query.filter(
            or_(
                User.fullname.like(search),
                User.username.like(search),
                User.category.like(search)
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

@app.route('/sponsor/<username>', methods=['GET', 'POST'])
def sponsor(username):
    if 'sponsorID' in session:
        sponsorID = session['sponsorID']
        sponsor = Sponsor.query.get(sponsorID)
        if sponsor and sponsor.username==username:
            products=Product.query.filter_by(sponsor_id=sponsorID).all()
            Status={}
            progress={}
            budget={}
            for product in products:
                usrprd=UserProduct.query.filter_by(productID=product.id).all()
                for up in usrprd:
                    budget[product.id]=up.budget
                    Status[product.id]=up.status
                    progress[product.id]=up.progress
                    
            if request.method == 'POST':
                adID = request.form.get('adID')
                stat = request.form.get('status')
                up=UserProduct.query.filter_by(productID=adID).first() 
                if up:
                    if stat=='Resend':
                        up.status='Pending'
                    else:
                        up.status=stat
                db.session.commit()
                    
                return redirect(url_for('sponsor', username=sponsor.username))
                 
            return render_template('sponsor.html',fullname=sponsor.fullname, username=sponsor.username, email=sponsor.email, Status=Status,products=products,progress=progress, budget=budget)
    return redirect(url_for('main'))

