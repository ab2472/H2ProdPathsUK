# -*- coding: utf-8 -*-

"""
Created on Wed Jun 21 14:19:05 2023

@author: ab2472
"""


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import seaborn as sb
import pandas as pd
import pickle
import matplotlib.ticker as mtick
import os
import statsmodels.api as sm
import scipy.stats 


""" define colours and markers"""

dict_colours =  {'Offshore Wind Floating, Offshore, Tanker':'#fabebe', 
                 'Offshore Wind Fixed, Offshore, Tanker':'#911eb4', 
                 'UKCS, Offshore, Tanker':'#4363d8', 
                 'Offshore Wind Floating, Offshore, Pipeline':'#bcf60c', 
                 'Offshore Wind Fixed, Offshore, Pipeline':'#f032e6', 
                 'UKCS, Onshore':'#800000', 
                 'Grid (2030), Onshore':'#808000' , 
                 'UKCS, Offshore, Pipeline':'#808080', 
                 'Imported LNG, Onshore':'#db744f', 
                 'Grid (Current Intensity), Onshore':'#3cb44b', 
                 'Power Station - NG with CCS, Onshore':'#ffe119', 
                 'Offshore Wind Floating, Onshore':'#000075', 
                 'Offshore Wind Fixed, Onshore':'#f58231', 
                 'Solar (PV), Onshore':'#21d9cc', 
                 'Nuclear, Onshore':'#e6beff', 
                 'Onshore Wind, Onshore':'#008080'}

dict_markers =  {'Offshore Wind Floating, Offshore, Tanker':'o', 
                'Offshore Wind Fixed, Offshore, Tanker':'v', 
                'UKCS, Offshore, Tanker':'^', 
                'Offshore Wind Floating, Offshore, Pipeline':'<', 
                'Offshore Wind Fixed, Offshore, Pipeline':'>', 
                'UKCS, Onshore':'*', 
                'Grid (2030), Onshore':'P', 
                'UKCS, Offshore, Pipeline':'s', 
                'Imported LNG, Onshore':'X', 
                'Grid (Current Intensity), Onshore':'H', 
                'Power Station - NG with CCS, Onshore':'o', 
                'Offshore Wind Floating, Onshore':'v', 
                'Offshore Wind Fixed, Onshore':'^', 
                'Solar (PV), Onshore':'<', 
                'Nuclear, Onshore':'>', 
                'Onshore Wind, Onshore':'s'}

""" define graph plots""" 

def legend_without_duplicate_labels(ax):
   #creates a legend without duplicate labels
   handles, labels = ax.get_legend_handles_labels()
   unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
   ax.legend(*zip(*unique),fontsize = 8,ncol = 1,bbox_to_anchor=(1,1))  

def remove_anomalies(dataframe):
    listtemp=[]
    for name, group in dataframe.groupby('ID',as_index=True):
        lowerco2e = group['CO2e'].quantile(0.01)*0.9
        upperco2e = group['CO2e'].quantile(0.99)*1.1
        lower = group['Energy In'].quantile(0.01)*0.9
        upper = group['Energy In'].quantile(0.99)*1.1
        group.drop(group[group['CO2e']>upperco2e].index,inplace=True)
        group.drop(group[group['CO2e']<lowerco2e].index,inplace=True)
        group.drop(group[group['Energy In']>upper].index,inplace=True)
        group.drop(group[group['Energy In']<lower].index,inplace=True)
        listtemp.append(group)
    df_byID=pd.concat(listtemp)
    return df_byID

def remove_UC_ammonia(listroutes):
    list_results = []
    for route in listroutes:
        if route.T_infra.ID in ('UCNHTFuel Oil','UCNHTNH3'):
            pass
        else:
            list_results.append(route)
    return list_results

def figure5(df_byID,colours = dict_colours,markers = dict_markers,filename='Figure1'):
    
    fig, ax = plt.subplots(2,2,gridspec_kw={'width_ratios': [4, 1],'height_ratios':[1,4]},figsize=(12,10))
    labels=[]

    for name,group in sorted(df_byID.groupby('Legend'),key=lambda k: len(k[1]), reverse=True):
        #sort by length of group so that largest sets are plotted first
        ax[1,0].scatter(group['Energy In'],group['CO2e'],
                        marker='.',s=40,alpha=0.04,
                        facecolors=dict_colours[name],
                        linewidth =0.5,edgecolors='none')
        sb.kdeplot(data=group,y="CO2e",ax=ax[1,1],
                   color=colours[name],fill = True,legend=False)
        sb.kdeplot(data=group,x="Energy In",
                   ax=ax[0,0],color=colours[name],fill = True,legend=False)
        labels.append(name)
    #plot the mean values
    for name,group in sorted(df_byID.groupby('Legend'),key=lambda k: len(k[1]), reverse=True):
        ax[1,0].scatter(group.groupby('ID', as_index=True)['Energy In'].mean(),
                        group.groupby('ID', as_index=True)['CO2e'].mean(),
                        marker=markers[name],s=25,label = name,color=colours[name],
                        edgecolors="black",linewidth =0.5)

    ax[1,0].axhline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
    ax[1,0].axhline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
    ax[1,0].axhline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
    #ax[1,0].axhline(1,label = "IEA Net Zero by 2050 Roadmap, 2050 max", color = "green",linestyle='dashed',alpha=1,linewidth =1)
    ax[1,0].set_xlabel('Energy Return On Investment (Energy Delivered/Energy In)')
    ax[1,0].set_ylim(bottom=0)
    ax[1,0].set_ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082)')
    
    ax[0,0].set_xlim(ax[1,0].get_xlim())
    ax[1,1].set_ylim(ax[1,0].get_ylim())

    fig.delaxes(ax[0,1])
    for axes in (ax[1,1],ax[0,0]):
        axes.axis('off')

    plt.subplots_adjust(wspace=0.0,hspace=0.0)
    plt.savefig(os.getcwd()+'\\Figures\\figure_5.png', format='png',dpi=600)
    plt.show() 
    
def stages(model,variable):
    d = []
    names = ['H2 Infra','H2 Prod','T Vector','T Infra']
    list_results = remove_UC_ammonia(model)
    for route in list_results:
        dict1 = route.set_route_CO2e()
        dict1_temp={}
        for key,name in zip(dict1.keys(),names):
            dict1_temp[name]=dict1[key]
        if route.T_infra.location == "Offshore":
            text = ","+route.T_infra.infratype
        else:
            text=''
        dict2 = {'ID':route.ID,
                 'Route Path':route.route_path(),
                 'Num':route.name,
                 'Location':route.h2_infra.location,
                 'CO2e':route.CO2e,
                 'Energy In':route.energy_in,
                 'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
        dict2 = dict2|dict1_temp
        d.append(dict2)
    df_byID=pd.DataFrame(d)
    df_byID=remove_anomalies(df_byID)
    h2infra_median = df_byID.groupby(variable,as_index=True)['H2 Infra'].mean()
    h2prod_median = df_byID.groupby(variable,as_index=True)['H2 Prod'].mean()
    tvector_median = df_byID.groupby(variable,as_index=True)['T Vector'].mean()
    tinfra_median = df_byID.groupby(variable,as_index=True)['T Infra'].mean()
    #groups = df_byID[['ID','Legend']].drop_duplicates().set_index('ID')
    LC_results = pd.concat([h2prod_median,h2infra_median,tvector_median,tinfra_median],axis=1, ignore_index=False)
    LC_results['Total'] = LC_results[names].sum(axis=1)
    for columnname in names:
        LC_results[columnname] = LC_results[columnname]/LC_results['Total']*100
    LC_results.drop('Total',axis=1,inplace=True)
    #LC_results.plot.bar(stacked=True)
    LC_results.to_csv(os.getcwd()+'\\CSV Results\\stageresults_bylegend'+variable+'.csv')
    return LC_results
    
def lifecyclestages_percent(model,variable):
    d=[]
    list_results = remove_UC_ammonia(model)
    for route in list_results:
        dict1 = route.route_CO2e_bySP()
        emb=0
        OM=0
        pro=0
        h2=0
        for stage in dict1:
            emb+=dict1[stage]["emb_kgCO2e"]
            OM+=dict1[stage]["OM_kgCO2e"]
            pro+=dict1[stage]["process_kgCO2e"]
            h2+=dict1[stage]["H2 emissions"]
        dict1_temp={'Embodied':emb,
                    'Process':pro,
                    'O&M':OM,
                    'Hydrogen Emissions':h2}
        if route.T_infra.location == "Offshore":
            text = ","+route.T_infra.infratype
        else:
            text=''
        dict2 = {'ID':route.ID,
                 'Route Path':route.route_path(),
                 'Num':route.name,
                 'Location':route.h2_infra.location,
                 'CO2e':route.CO2e,
                 'Energy In':route.energy_in,
                 'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
        dict2 = dict2|dict1_temp
        d.append(dict2)
        
    df_byID=pd.DataFrame(d)
    df_byID=remove_anomalies(df_byID)
    Embodied_median = df_byID.groupby(variable,as_index=True)['Embodied'].median()
    Process_median = df_byID.groupby(variable,as_index=True)['Process'].median()
    OM_median = df_byID.groupby(variable,as_index=True)['O&M'].median()
    HE_median = df_byID.groupby(variable,as_index=True)['Hydrogen Emissions'].median()
    #groups = df_byID[['ID','Legend']].drop_duplicates().set_index('ID')
    LC_results = pd.concat([Process_median,Embodied_median,OM_median,HE_median],axis=1, ignore_index=False)
    colnames=['Embodied','Process','O&M','Hydrogen Emissions']
    LC_results['Total']=LC_results[colnames].sum(axis=1)
    for columnname in colnames:
        LC_results[columnname] = LC_results[columnname]/LC_results['Total']*100
    LC_results.drop('Total',axis=1,inplace=True)
    LC_results.to_csv(os.getcwd()+'\\CSV Results\\lcresults_bylegend'+variable+'.csv')
    #LC_results.plot.bar(stacked=True)

    return LC_results

def lifecyclestages_energy(model,variable):
    
    d=[]
    list_results = remove_UC_ammonia(model)
    for route in list_results:
        dict1 = route.routeenergy_bystageandprocess()
        emb=0
        OM=0
        pro=0
        h2=0
        for stage in dict1:
            emb+=dict1[stage]["emb_kWh"]['Total']
            OM+=dict1[stage]["OM_kWh"]['Total']
            pro+=dict1[stage]["process_kWh"]['Total']
        dict1_temp={'Embodied':emb,
                    'Process':pro,
                    'O&M':OM}
        if route.T_infra.location == "Offshore":
            text = ","+route.T_infra.infratype
        else:
            text=''
        dict2 = {'ID':route.ID,
                 'Route Path':route.route_path(),
                 'Num':route.name,
                 'Location':route.h2_infra.location,
                 'CO2e':route.CO2e,
                 'Energy In':route.energy_in,
                 'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
        dict2 = dict2|dict1_temp
        d.append(dict2)
    df_byID=pd.DataFrame(d)
    df_byID=remove_anomalies(df_byID)
    Embodied_median = df_byID.groupby(variable,as_index=True)['Embodied'].mean()
    Process_median = df_byID.groupby(variable,as_index=True)['Process'].mean()
    OM_median = df_byID.groupby(variable,as_index=True)['O&M'].mean()
    #groups = df_byID[['ID','Legend']].drop_duplicates().set_index('ID')
    LC_results = pd.concat([Process_median,Embodied_median,OM_median],axis=1, ignore_index=False)
    LC_results['Total'] = LC_results[['Embodied','Process','O&M']].sum(axis=1)
    for columnname in ('Embodied','Process','O&M'):
        LC_results[columnname] = LC_results[columnname]/LC_results['Total']*100
    LC_results.drop('Total',axis=1,inplace=True)
    #LC_results.plot.bar(stacked=True)
    return LC_results

def stages_energy(model,variable):
    d=[]
    names = ['H2 Infra','H2 Prod','T Vector','T Infra']
    list_results = remove_UC_ammonia(model)
    for route in list_results:
        dict1 = route.routeenergy_bystageandprocess()
        dict1_temp = {}
        for n in range(len(dict1.keys())):
            dict1_temp[names[n]]=dict1[list(dict1.keys())[n]]['Total']
        if route.T_infra.location == "Offshore":
            text = ","+route.T_infra.infratype
        else:
            text=''
        dict2 = {'ID':route.ID,
                 'Route Path':route.route_path(),
                 'Num':route.name,
                 'Location':route.h2_infra.location,
                 'CO2e':route.CO2e,
                 'Energy In':route.energy_in,
                 'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
        dict2 = dict2|dict1_temp
        d.append(dict2)
    df_byID=pd.DataFrame(d)
    df_byID=remove_anomalies(df_byID)
    h2infra_median = df_byID.groupby(variable,as_index=True)['H2 Infra'].mean()
    h2prod_median = df_byID.groupby(variable,as_index=True)['H2 Prod'].mean()
    tvector_median = df_byID.groupby(variable,as_index=True)['T Vector'].mean()
    tinfra_median = df_byID.groupby(variable,as_index=True)['T Infra'].mean()
    #groups = df_byID[['ID','Legend']].drop_duplicates().set_index('ID')
    LC_results = pd.concat([h2prod_median,h2infra_median,tvector_median,tinfra_median],axis=1, ignore_index=False)
    LC_results['Total'] = LC_results[names].sum(axis=1)
    for columnname in names:
        LC_results[columnname] = LC_results[columnname]/LC_results['Total']*100
    LC_results.drop('Total',axis=1,inplace=True)

    return LC_results

def combinedplot(model,variable,filename='figure6'):
    #variable = groupby legend or ID
    LC_CO2e = lifecyclestages_percent(model,variable)
    LC_Energy = lifecyclestages_energy(model,variable)
    S_Energy = stages_energy(model,variable)
    S_CO2e = stages(model,variable)
    list1 = [LC_CO2e,LC_Energy,S_Energy,S_CO2e]
    for item in list1:
        item.sort_values(by=variable)
    colours = sb.color_palette("rocket_r", 4)
    coloursx = sb.color_palette("mako_r", 4)
    colours1 = [colours[1],colours[0],colours[2],colours[3]]
    colours2 = [coloursx[1],coloursx[0],coloursx[2],coloursx[3]]
    fig,ax = plt.subplots(2,2,sharey=True,figsize=(10,10))
    for axes in (ax[0,0],ax[0,1],ax[1,0],ax[1,1]):
        axes.grid()
    LC_CO2e.plot.barh(stacked=True,color=colours1,ax=ax[0,1],legend=False,title='Lifecycle Component',edgecolor='white',width=0.8)
    S_CO2e.plot.barh(stacked=True,color=colours2,ax=ax[0,0],legend=False,title='Pathway Stage',edgecolor='white',width=0.8)
    LC_Energy.plot.barh(stacked=True,color=colours1,ax=ax[1,1],legend=False,title='LC Energy',edgecolor='white',width=0.8)
    S_Energy.plot.barh(stacked=True,color=colours2,ax=ax[1,0],legend=False,title='Stage Energy',edgecolor='white',width=0.8)
    ax[0,0].set_xlabel('Percent of Total')
    for axes in (ax[0,0],ax[0,1],ax[1,0],ax[1,1]):
        axes.xaxis.set_major_formatter('{x:.0f}%')
    ax[0,1].set_xlabel('Percent of Total')
    plt.subplots_adjust(wspace=0.05,hspace=0.2)
    plt.savefig(os.getcwd()+'\\Figures\\'+filename+'.svg', format='svg',dpi=600)
    plt.show()

"""
def combinedplot2(model,variable,filename='fig2'):
    #variable = groupby legend or ID
    LC_CO2e = lifecyclestages_percent(model,variable)
    LC_Energy = lifecyclestages_energy(model,variable)
    S_Energy = stages_energy(model,variable)
    S_CO2e = stages(model,variable)
    list1 = [LC_CO2e,LC_Energy,S_Energy,S_CO2e]
    for item in list1:
        item.sort_values(by='Legend')
    colours = sb.color_palette("rocket_r", 4)
    coloursx = sb.color_palette("mako_r", 4)
    colours1 = [colours[1],colours[0],colours[2],colours[3]]
    colours2 = [coloursx[1],coloursx[0],coloursx[2],coloursx[3]]
    fig,ax = plt.subplots()
    ax = LC_CO2e.plot.barh(stacked=True,color=colours1,ax=ax,legend=False,title='Lifecycle Component',edgecolor='white',width=0.8)
    for c in ax.containers:
        labels = [f'{w:.2f}%' if (w := v.get_width()) > 0 else '' for v in c ]
        ax.bar_label(c,label_type='center')
    ax[0,1].set_xlabel('Percent of Total')
    plt.show()"""
    
def impactofoffshore_tvector(model,filename='fig7',electrometh1 = 'PEM',smrmeth='ATR',variable='CO2e'):
    d=[]
    if electrometh1 == 'PEM':
        prodmeth1 = 'CPL'
        prodmeth2 = 'CPF'
        h2infra1 = 'CPLI'
        h2infra2 = 'LRPI'
    elif electrometh1 == 'Alkaline':
        prodmeth1 = 'CAL'
        prodmeth2 = 'CAF'
        h2infra1 = 'CALI'
        h2infra2 = 'LRPI'
        
    if smrmeth=='ATR':
        prodmeth3 = 'AHL'
        prodmeth4 = 'AHF'
        h2infra3 = 'CNGI'
        h2infra4 = 'LRTI'
    elif smrmeth=='lowsmr':
        prodmeth3 = 'SLL'
        prodmeth4 = 'SLF'
        h2infra3 = 'CNGI'
        h2infra4 = 'LRTI'
    elif smrmeth=='highsmr':
        prodmeth3 = 'SHF'
        prodmeth4 = 'SHL'
        h2infra3 = 'CNGI'
        h2infra4 = 'LRTI'
    for route in model: 
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.E_infra.ID in ('Offshore Wind Floating','Offshore Wind Fixed','UKCS') and route.h2_prod.ID in (prodmeth3,prodmeth4,prodmeth2,prodmeth1) and route.h2_infra.ID in (h2infra1,h2infra2,h2infra3,h2infra4):
            dict2 = {'ID':route.ID,
                     'T Infra':route.T_infra.infratype,
                     'Route Path':route.route_path(),
                     'Num':route.name,
                     'Location':route.h2_infra.location,
                     'CO2e':route.CO2e,
                     'Energy In':route.energy_in,
                     'EInfra':route.E_infra.ID,
                     'H2Infra':route.h2_infra.ID,
                     'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
            d.append(dict2)
    df_byID=pd.DataFrame(d)  
    df_byID=remove_anomalies(df_byID)
    grouped = df_byID.groupby('ID', as_index=True)[variable].mean().to_frame()
    groupedmin = df_byID.groupby('ID', as_index=True)[variable].quantile(0.025).to_frame().rename(columns={variable:'Min'})
    groupedmax = df_byID.groupby('ID', as_index=True)[variable].quantile(0.975).to_frame().rename(columns={variable:'Max'})
    location = df_byID.groupby('ID',as_index=True)['Location'].first()
    tinfra = df_byID.groupby('ID',as_index=True)['T Infra'].first()
    EInfra = df_byID.groupby('ID',as_index=True)['EInfra'].first()
    legend = df_byID.groupby('ID',as_index=True)['Legend'].first()
    h2infra = df_byID.groupby('ID',as_index=True)['H2Infra'].first()
    LC_results = pd.concat([grouped,groupedmin,groupedmax,h2infra,location,EInfra,tinfra,legend],axis=1, ignore_index=False)

    for name,group in LC_results.groupby('EInfra'):
        if name in ('Offshore Wind Floating','Offshore Wind Fixed'):
            onshoreid = h2infra1
            meth = electrometh1
        elif name in ('UKCS'):
            onshoreid = h2infra3
            meth = smrmeth
        group.sort_values(by=[variable],inplace=True,ascending=False)
        basevalue = float(group.loc[group['Location'] == 'Onshore'][variable])
        errors = [[group[variable]-group['Min'], group['Max']-group[variable]]]
        fig,ax1=plt.subplots()
        colourlist= [dict_colours[legend1] for legend1 in group['Legend']]
        uniquecolours = list(dict.fromkeys(colourlist))
        group.plot.barh(y=variable,color=colourlist,xerr=errors,capsize=3,ax=ax1)
        if variable == 'CO2e':
            defaultxlim= ax1.get_xlim()
            ax1.axvline(x=2.4,linestyle='dashed')
            ax1.axvline(x=0.203*33.3,linestyle='dashed', color="red")
            ax1.axvline(x=12,linestyle='dashed',color="grey")
            ax1.set_xlim(defaultxlim)
        ax2=ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue)/basevalue*100,(mx-basevalue)/basevalue*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2.set_xlabel('Percent of Average Onshore, Centralised Emissions Intensity')
        patch1 = mpatches.Patch(color=uniquecolours[2], label='Onshore')
        patch2 = mpatches.Patch(color=uniquecolours[1], label='Offshore - Pipeline')
        patch3 = mpatches.Patch(color=uniquecolours[0], label='Offshore - Tanker')
        ax2.set_axisbelow(True)
        ax1.set_axisbelow(True)
        ax2.xaxis.grid()
        #ax1.set_ylabel('')
        ax1.tick_params(labelleft=False)
        #plt.ylabel('')        
        plt.legend(handles=[patch1,patch2,patch3],framealpha=1)
        plt.savefig(os.getcwd()+'\\Figures\\'+filename+'_'+name+meth+variable+'.svg', format='svg',dpi=600)
        plt.show()

def impactofoffshore_infra(model,prodmethod='PEM',variable = 'CO2e',filename='fig8'):
    if prodmethod=='PEM':
       prodidlist = ('CPL','CPF','DPL','DPF')
       onshoreid = 'CPLI'
    elif prodmethod == 'Alkaline':
       prodidlist = ('CAL','CAF','DAL','DAF')
       onshoreid = 'CALI' 
    elif prodmethod == 'ATR':
        prodidlist = ('AHF', 'AHL')
        onshoreid = 'CNGI'
    elif prodmethod == 'lowsmr':
        prodidlist = ('SLF', 'SLL')
        onshoreid = 'CNGI' 
    elif prodmethod == 'highsmr':
        prodidlist = ('SHF', 'SHL')
        onshoreid = 'CNGI' 
    
    d=[]
    for route in model: 
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.E_infra.ID in ('Offshore Wind Fixed','Offshore Wind Floating','UKCS') and route.h2_prod.ID in prodidlist and route.T_infra.ID in ('PHRE','PHRNG','PNNG','CE','LOHCTFuel Oil'):
            dict2 = {'ID':route.ID,
                     'T Infra':route.T_infra.infratype,
                     'Route Path':route.route_path(),
                     'Num':route.name,
                     'Location':route.h2_infra.location,
                     'CO2e':route.CO2e,
                     'Energy In':route.energy_in,
                     'EInfra':route.E_infra.ID,
                     'H2Infra':route.h2_infra.ID,
                     'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
            d.append(dict2)
    df_byID=pd.DataFrame(d)  
    df_byID=remove_anomalies(df_byID)
    grouped = df_byID.groupby('ID', as_index=True)[variable].mean().to_frame()
    groupedmin = df_byID.groupby('ID', as_index=True)[variable].quantile(0.025).to_frame().rename(columns={variable:'Min'})
    groupedmax = df_byID.groupby('ID', as_index=True)[variable].quantile(0.975).to_frame().rename(columns={variable:'Max'})
    groupedstd = df_byID.groupby('ID', as_index=True)[variable].std().to_frame().rename(columns={variable:'std'})
    location = df_byID.groupby('ID',as_index=True)['Location'].first()
    tinfra = df_byID.groupby('ID',as_index=True)['T Infra'].first()
    h2infra = df_byID.groupby('ID',as_index=True)['H2Infra'].first()
    Legend = df_byID.groupby('ID',as_index=True)['Legend'].first()
    EInfra = df_byID.groupby('ID',as_index=True)['EInfra'].first()

    LC_results = pd.concat([grouped,groupedmin,groupedstd,groupedmax,location,Legend,EInfra,tinfra,h2infra],axis=1, ignore_index=False)

    for name,group in LC_results.groupby('EInfra'):
        #print(group.loc[group['H2Infra'] == onshoreid][variable])
        basevalue = float(group.loc[group['H2Infra'] == onshoreid][variable])
        group.sort_values(by=[variable],inplace=True,ascending=False)
        errors = [[group[variable]-group['Min'],group['Max']-group[variable]]]
        #print(group[[variable,'Min','Max']],group[variable]-group['Min'],group['Max']-group[variable])
        fig,ax1=plt.subplots()
        colourlist= [dict_colours[legend1] for legend1 in group['Legend']]
        uniquecolours = list(dict.fromkeys(colourlist))
        group.plot.barh(y=variable,color=colourlist,xerr=errors,capsize=3,ax=ax1)
        ax2=ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue)/basevalue*100,(mx-basevalue)/basevalue*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        if variable == 'CO2e':
            ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        if variable == 'Energy In':
            ax1.set_xlabel('kWh/kg H\u2082')
        ax2.set_xlabel('Percent of Average Onshore, Centralised Emissions Intensity')
        patch1 = mpatches.Patch(color=uniquecolours[2], label='Onshore')
        patch2 = mpatches.Patch(color=uniquecolours[1], label='Offshore - Pipeline')
        patch3 = mpatches.Patch(color=uniquecolours[0], label='Offshore - Tanker')
        ax2.set_axisbelow(True)
        ax1.set_axisbelow(True)
        if variable == 'CO2e':
            defaultxlim= ax1.get_xlim()
            ax1.axvline(x=2.4,linestyle='dashed')
            ax1.axvline(x=0.203*33.3,linestyle='dashed', color="red")
            ax1.axvline(x=12,linestyle='dashed',color="grey")
            ax1.set_xlim(defaultxlim)
        ax2.xaxis.grid()
        #ax1.set_ylabel('')
        plt.legend(handles=[patch1,patch2,patch3],framealpha=1)
        #ax1.tick_params(labelleft=False)
        plt.savefig(os.getcwd()+'\\Figures\\'+filename+name+prodmethod+variable+'.svg', format='svg',dpi=600)
        plt.show()
        
def distanceplot(models,einfra,h2prodid,h2infraid,bounds=True):
    fig, ax = plt.subplots(figsize = (8,4))
    distances = []
    #get the list of tinfra by looking at one of the models
    df = models[10].loc[(models[10]['Einfra']==einfra)&
                        (models[10]['h2 prod']==h2prodid)&
                        (models[10]['h2 infra']==h2infraid)]
    list_tinfra = df['tinfra'].unique()
    colours_list = sb.color_palette("hls", len(list_tinfra))
    colours={}
    for infra,colour in zip(list_tinfra,colours_list):
        colours[infra] = colour    
    for name in list_tinfra:
        distances = []
        mean = []
        low = []
        high = []
        for distance in models:
            df = models[distance].loc[(models[distance]['Einfra']==einfra)&
                                      (models[distance]['h2 prod']==h2prodid)&
                                      (models[distance]['h2 infra']==h2infraid)&
                                      (models[distance]['tinfra']==name)]
            distances.append(distance)
            mean.append(df['CO2e'].mean())
            low.append(df['CO2e'].quantile(0.05))
            high.append(df['CO2e'].quantile(0.95))
        
        ax.scatter(distances, mean,marker='.',s=10,color = colours[name],alpha=0.2,label=name)
        z = np.polyfit(distances, mean, 1)
        p = np.poly1d(z)
        ax.plot(distances,p(distances),"-",color = colours[name],lw=1)
        if bounds == True:
            z = np.polyfit(distances, low, 1)
            p = np.poly1d(z)
            #ax.plot(distances,p(distances),":",color = colours[name],lw=0.5)
            z = np.polyfit(distances, high, 1)
            p = np.poly1d(z)
            #ax.plot(distances,p(distances),":",color = colours[name],lw=0.5)
            ax.fill_between(distances, low, high, alpha=0.1, edgecolor=colours[name], facecolor=colours[name])
    #ax.fill_between(distances, 0, 2, alpha=0.1, edgecolor=None, facecolor='blue')
    plt.xlabel('Distance from shore (km)')
    plt.ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082e)')
    #plt.legend()
    plt.xlim(left=10,right=750)
    titles = {'CPF':'A. Centralised PEM Electrolysis, Fixed Offshore Wind','DPF':'B. Decentralised PEM Electrolysis, Fixed Offshore Wind','AHF':'C. Centralised Autothermal Reforming with CCS, Natural Gas (UKCS)'}
    plt.title(titles[h2prodid])
    if h2prodid in ('CPF','DPF') and bounds == False:
        plt.ylim(bottom=1.5,top=3.5)
    plt.savefig(os.getcwd()+'\\Figures\\SI_fig_'+h2prodid+'_distanceplot.svg', format='svg',dpi=600)
    plt.show()
    #print(mean,low,high)
    

    

