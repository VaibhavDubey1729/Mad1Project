from flask import Flask, session, request, redirect, url_for, render_template, flash
from application.Models import*
from sqlalchemy import or_
from main import app
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import os

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
        category=request.form['category']
        niche=request.form['niche']
        
        if sponsorID:
            add=Product(name=name,description=description,price=price,start=start,end=end,sponsor_id=sponsorID, Ads=Ads, visibility=visibility, category=category,niche=niche)
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
        budget=request.form.get('Budget')
        newbudget=0
        if budget:
            newbudget=budget
        else:
            newbudget=ad.price
        if influencer_id:
            influencer = User.query.get(influencer_id)
            currentInflu = UserProduct.query.filter_by(productID=adID, userID=influencer_id).first() #checks if there is an existing user for same product
            if not currentInflu:
                user_product = UserProduct(productID=ad.id, userID=influencer.id,budget=newbudget)
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
    budget={up.userID: up.budget for up in up}
    influIDs =[i.userID for i in UserProduct.query.filter_by(productID=adID).all()]
    influ= User.query.filter(User.id.in_(influIDs)).all()
    
    
    #Creating Useful Statistics for a Particular Ad
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))
    
    # Data for Ad Status
    accepted = UserProduct.query.filter_by(productID=adID,status='Accepted').count()
    pending = UserProduct.query.filter_by(productID=adID,status='Pending').count()
    rejected = UserProduct.query.filter_by(productID=adID,status='Rejected').count()
    completed = UserProduct.query.filter_by(productID=adID,status='Completed').count()
    requested = UserProduct.query.filter_by(productID=adID,status='Requested').count()
    
    # Ad Status Distribution Pie Chart
    labels1 = ['Accepted', 'Pending', 'Completed', 'Rejected', 'Requested']
    values1 = [accepted, pending, completed, rejected, requested]
    explode = [0.2, 0.1, 0.3, 0, 0.1]
    
    if any(values1):
        axs[0].pie(values1, labels=labels1, autopct='%1.1f%%', startangle=140, explode=explode, shadow=True)
        axs[0].set_title('Ad Status', pad=30)
        axs[0].legend(title='Labels', bbox_to_anchor=(1.05, 1), loc='upper left')
    else:
        axs[0].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[0].set_title('Ad Status', pad=30)
        
    influIDs=[up.userID for up in UserProduct.query.filter_by(productID=adID).all()]
    iName=[User.query.get(influID).username for influID in influIDs]
    iprogress=[UserProduct.query.filter_by(productID=adID, userID=influID).first().progress for influID in influIDs] 
    
    if (iprogress):
        axs[1].bar(iName,iprogress, color='red',width=0.4)
        axs[ 1].set_xlabel('Influencer')
        axs[ 1].set_ylabel('Progress(%)')
        axs[ 1].set_title('Ad Progress')
        axs[ 1].set_ylim(0, 100)
    else:
        axs[1].text(0.5,0.5, 'No Data Available',horizontalalignment='center', verticalalignment='center', fontsize=12)
        axs[1].set_title('Ad Progress')

    plt.tight_layout(pad=3.0)

    file=f'Stats+{ad.id}+{ad.name}.png'
    path = os.path.join(app.root_path, 'static', file)
    plt.savefig(path, bbox_inches='tight')
    plt.clf()
    
    
    return render_template('adDetail.html', username=sponsor.username, ad=ad, users=users, influ=influ,status=status,progress=progress, budget=budget,plot=url_for('static',filename=file))
