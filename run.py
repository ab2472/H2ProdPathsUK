# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 14:29:02 2023

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
from pathway_build import *
import textwrap
from plot_sobol import *
""" define colours and markers"""

dict_colours_simple =  {'Offshore Wind Floating, Offshore, Tanker':'#D52C2C', 
                 'Offshore Wind Fixed, Offshore, Tanker':'#274e13', 
                 'UKCS, Offshore, Tanker':'#0d4e80', 
                 'Offshore Wind Floating, Offshore, Pipeline':'#F77F7F', 
                 'Offshore Wind Fixed, Offshore, Pipeline':'#468c22', 
                 'UKCS, Onshore':'#a3cef0', 
                 'Grid (2030), Onshore':'#B5B5B5' , 
                 'UKCS, Offshore, Pipeline':'#0272c7', 
                 'Imported LNG, Onshore':'#44A3AC', 
                 'Grid (Current Intensity), Onshore':'#636363', 
                 'Power Station - NG with CCS, Onshore':'#0D0D0D', 
                 'Offshore Wind Floating, Onshore':'#F9C0C0', 
                 'Offshore Wind Fixed, Onshore':'#8cd965', 
                 'Solar (PV), Onshore':'#ffd966', 
                 'Nuclear, Onshore':'#e6beff', 
                 'Onshore Wind, Onshore':'#b8f361'}

dict_colours = {'Grid (2030), Onshore':'#B5B5B5',
         'Grid (Current Intensity), Onshore':'#636363',
         'Imported LNG, Onshore,AHL': '#44A3AC',
         'Imported LNG, Onshore,SHL': '#32747A',
         'Imported LNG, Onshore,SLL': '#1D4448',
         'Nuclear, Onshore':'#e6beff',
         'Offshore Wind Fixed, Offshore, Pipeline':'#468c22',
         'Offshore Wind Fixed, Offshore, Tanker': '#274e13',
         'Offshore Wind Fixed, Onshore': '#8cd965',
         'Offshore Wind Floating, Offshore, Pipeline':'#F77F7F',
         'Offshore Wind Floating, Offshore, Tanker':'#D52C2C',
         'Offshore Wind Floating, Onshore':'#F9C0C0',
         'Onshore Wind, Onshore':'#b8f361',
         'Power Station - NG with CCS, Onshore':'#0D0D0D',
         'Solar (PV), Onshore':'#ffd966',
         'UKCS, Offshore, Pipeline,AHF':'#0272c7',
         'UKCS, Offshore, Pipeline,SHF':'#4e2cf5',
         'UKCS, Offshore, Pipeline,SLF':'#0943e3',
         'UKCS, Offshore, Tanker,AHF':'#0d4e80',
         'UKCS, Offshore, Tanker,SHF':'#2e1b8c',
         'UKCS, Offshore, Tanker,SLF':'#00003f', 
         'UKCS, Onshore,AHL':'#a3cef0',
         'UKCS, Onshore,SHL':'#8872f7',
         'UKCS, Onshore,SLL':'#5e7dd1'}

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

def loadmcdata(name):   
    with open(os.getcwd()+'\\Pickle Results\\'+name,'rb') as inp:
        return pickle.load(inp)

""" define graph plots""" 

def legend_without_duplicate_labels(ax):
   #creates a legend without duplicate labels
   handles, labels = ax.get_legend_handles_labels()
   unique = [(h, l) for i, (h, l) in enumerate(zip(handles, labels)) if l not in labels[:i]]
   ax.legend(*zip(*unique),fontsize = 8,ncol = 1,bbox_to_anchor=(1,1))  

def remove_UC_ammonia(listroutes):
    list_results = []
    for route in listroutes:
        if route.T_infra.ID in ('UCNHTFuel Oil','UCNHTNH3'):
            pass
        else:
            list_results.append(route)
    return list_results
  
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
    colours = sb.color_palette("flare", 4)
    coloursx = sb.color_palette("crest", 4)
    colours1 = [colours[1],colours[0],colours[2],colours[3]]
    colours2 = [coloursx[1],coloursx[0],coloursx[2],coloursx[3]]
    fig,ax = plt.subplots(2,2,sharey=True,figsize=(10,10))
    for axes in (ax[0,0],ax[0,1],ax[1,0],ax[1,1]):
        axes.grid()
    LC_CO2e.plot.barh(stacked=True,color=colours1,ax=ax[0,1],legend=False,title='B. Lifecycle Component',edgecolor='white',width=0.8)
    S_CO2e.plot.barh(stacked=True,color=colours2,ax=ax[0,0],legend=False,title='A. Pathway Stage',edgecolor='white',width=0.8)
    LC_Energy.plot.barh(stacked=True,color=colours1,ax=ax[1,1],legend=False,title='B. Lifecycle Component',edgecolor='white',width=0.8)
    S_Energy.plot.barh(stacked=True,color=colours2,ax=ax[1,0],legend=False,title='A. Pathway Stage',edgecolor='white',width=0.8)
    ax[0,0].set_xlabel('Percent of Total')
    for axes in (ax[0,0],ax[0,1],ax[1,0],ax[1,1]):
        axes.xaxis.set_major_formatter('{x:.0f}%')
        axes.spines['right'].set_visible(False)
        axes.spines['top'].set_visible(False)
        
    ax[0,1].set_xlabel('Percent of Total')
    plt.subplots_adjust(wspace=0.1,hspace=0.2)
    plt.savefig(os.getcwd()+'\\Figures\\'+filename+'.svg', format='svg',dpi=1000)
    plt.show()
       
def distanceplot(models,einfra,h2prodid,h2infraid,bounds=True):
    fig, ax = plt.subplots(figsize = (9,4))
    distances = []
    #get the list of tinfra by looking at one of the models
    df = models[10].loc[(models[10]['Einfra']==einfra)&
                        (models[10]['h2 prod']==h2prodid)&
                        (models[10]['h2 infra']==h2infraid)]
    list_tinfra = df['tinfra'].unique()
    colours_list = sb.color_palette("hls", len(list_tinfra))
    colours={}
    legend_labels = {'LHTLH2LH2E':'Liquified Hydrogen Tanker (LH2)',
                    'LHTMDOLH2E':'Liquified Hydrogen Tanker (MDO)',
                    'PHRECH2E':'Repurposed Pipeline',
                    'PHNECH2E':'New Pipeline',
                    'LOHCTFuel OilLOE':'LOHC Tanker (Fuel Oil)',
                    'NHTNH3NH3E':'Ammonia Tanker (NH3)',
                    'NHTFuel OilNH3E':'Ammonia Tanker (Fuel Oil)',
                    'LHTLH2LH2NG':'Liquified Hydrogen Tanker (LH2)',
                    'LHTMDOLH2NG':'Liquified Hydrogen Tanker (MDO)',
                    'PHRNGCH2NG':'Repurposed Pipeline',
                    'PHNNGCH2NG':'New Pipeline',
                    'LOHCTFuel OilLONG':'LOHC Tanker (Fuel Oil)',
                    'NHTNH3NH3NG':'Ammonia Tanker (NH3)',
                    'NHTFuel OilNH3NG':'Ammonia Tanker (Fuel Oil)'}
    for infra,colour in zip(legend_labels.values(),colours_list):
        colours[infra] = colour 
       
    for name in list_tinfra:
        distances = []
        mean = []
        lowSD = []
        highSD = []
        for distance in models:
            df = models[distance].loc[(models[distance]['Einfra']==einfra)&
                                      (models[distance]['h2 prod']==h2prodid)&
                                      (models[distance]['h2 infra']==h2infraid)&
                                      (models[distance]['tinfra']==name)]
            distances.append(distance)
            mean.append(df['CO2e'].mean())
            lowSD.append(df['CO2e'].quantile(0.05))
            highSD.append(df['CO2e'].quantile(0.95))
        label = legend_labels[name]
        
        ax.scatter(distances, mean,marker='.',s=10,color = colours[label],alpha=0.2)
        z = np.polyfit(distances, mean, 1)
        p = np.poly1d(z)
        ax.plot(distances,p(distances),"-",color = colours[label],lw=1,label=label)
        if bounds == True:
            z = np.polyfit(distances, lowSD, 1)
            p = np.poly1d(z)
            #ax.plot(distances,p(distances),":",color = colours[name],lw=0.5)
            z = np.polyfit(distances, highSD, 1)
            p = np.poly1d(z)
            #ax.plot(distances,p(distances),":",color = colours[name],lw=0.5)
            ax.fill_between(distances, lowSD, highSD, alpha=0.1, edgecolor=colours[label], facecolor=colours[label])
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    #ax.fill_between(distances, 0, 2, alpha=0.1, edgecolor=None, facecolor='blue')
    plt.xlabel('Distance from shore (km)')
    plt.ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082e)')
    plt.xlim(left=10,right=730)
    titles = {'CPF':'A. Centralised PEM Electrolysis, Fixed Offshore Wind','DPF':'B. Decentralised PEM Electrolysis, Fixed Offshore Wind','AHF':'C. Centralised Autothermal Reforming with CCS, Natural Gas (UKCS)'}
    plt.title(titles[h2prodid])
    if h2prodid in ('CPF','DPF') and bounds == False:
        plt.ylim(bottom=1.5,top=5)
    fig.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\SI_fig13_'+h2prodid+'_distanceplot.tiff',format='tiff',dpi=1000)
    plt.show()

def distancefigure(run,bounds=False):
    models = {}
    for distance in range (10,770,20):
        if run == True:
            h2prod = h2prod_uncertainty_df.loc[h2prod_uncertainty_df['Process ID'].isin(['CPF','DPF','AHF'])].copy()
            h2infra = h2infra_uncertainty_df.loc[h2infra_uncertainty_df['Process ID'].isin(['LRPI','DPFI','LRTI'])].copy()
            energysource = energysource_uncertainty_df.loc[energysource_uncertainty_df['Process ID'].isin(['Offshore Wind Fixed','UKCS'])].copy()
            dfs_fordistance2 = [tinfra_uncertainty_df,tvector_uncertainty_df,h2prod,h2infra,energysource]
            models[distance] = clean_savemeanstd(runmodel(distance,500,dfs_fordistance2),False)
        else:
            models[distance] = clean_savemeanstd(loadmcdata('Distance_'+str(distance)+'_Num_Iterations_500_06092024.pkl'),False)
    distanceplot(models,'UKCS','AHF','LRTI', bounds=bounds)
    distanceplot(models,'Offshore Wind Fixed','DPF','DPFI',bounds=bounds)
    distanceplot(models,'Offshore Wind Fixed','CPF','LRPI',bounds=bounds)

def SI_fig5_6(df_byID,colours = dict_colours,markers = dict_markers,filename='Figure1'):
    # gridspec inside gridspec
    
    fig,axsLeft = plt.subplots(2,2,figsize=[11,10],gridspec_kw={'width_ratios': [4,0.5],'height_ratios':[0.5,4],'wspace': 0, 'hspace': 0},layout='tight')
    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):
        #sort by length of group so that largest sets are plotted first
        axsLeft[1,0].scatter(group['Energy In'],group['CO2e'],marker='.',s=20,alpha=0.1,facecolors='None',linewidth =0.5,edgecolors=dict_colours[name])
        sb.kdeplot(data=group,y="CO2e",ax=axsLeft[1,1],color=dict_colours[name],fill = True,legend=False)
        sb.kdeplot(data=group,x="Energy In",ax=axsLeft[0,0],color=dict_colours[name],fill = True,legend=False)

    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):
        axsLeft[1,0].scatter(group.groupby('ID', as_index=True)['Energy In'].mean(),group.groupby('ID', as_index=True)['CO2e'].mean(),marker=markers[group['Legend'].unique()[0]],
            s=25,label = name,color=dict_colours[name],edgecolors="black",linewidth =0.5)

    axsLeft[1,0].axhline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
    axsLeft[1,0].axhline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
    axsLeft[1,0].axhline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
    for axes in (axsLeft[1,1],axsLeft[0,0]):
        axes.axis('off')

    axsLeft[1,0].set_xlabel('Energy Return On Investment (Energy Delivered/Energy In)')
    axsLeft[1,0].set_ylim(bottom=0)
    axsLeft[1,0].set_ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082)')
    axsLeft[1,1].set_ylim(axsLeft[1,0].get_ylim())
    axsLeft[0,1].remove()

    plt.savefig(os.getcwd()+'\\Figures\\SI_Fig5a.tiff', format='tiff',dpi=1200)
    plt.show()

    fig,axsRight = plt.subplots(2, 2, figsize=[11,10],sharex=True,sharey=True,gridspec_kw={'wspace': 0.05, 'hspace': 0.05},layout='tight')

    axes={'Offshore Wind Floating, Offshore, Tanker':axsRight[0,1], 
          'Offshore Wind Fixed, Offshore, Tanker':axsRight[0,1], 
          'UKCS, Offshore, Tanker':axsRight[1,1], 
          'Offshore Wind Floating, Offshore, Pipeline':axsRight[0,1], 
          'Offshore Wind Fixed, Offshore, Pipeline':axsRight[0,1], 
          'UKCS, Onshore':axsRight[1,0], 
          'Grid (2030), Onshore':axsRight[0,0], 
          'UKCS, Offshore, Pipeline':axsRight[1,1], 
          'Imported LNG, Onshore':axsRight[1,0], 
          'Grid (Current Intensity), Onshore':axsRight[0,0], 
          'Power Station - NG with CCS, Onshore':axsRight[0,0], 
          'Offshore Wind Floating, Onshore':axsRight[0,0], 
          'Offshore Wind Fixed, Onshore':axsRight[0,0], 
          'Solar (PV), Onshore':axsRight[0,0], 
          'Nuclear, Onshore':axsRight[0,0], 
          'Onshore Wind, Onshore':axsRight[0,0]}

    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):
        #sort by length of group so that largest sets are plotted first
        axes[group['Legend'].unique()[0]].scatter(group['Energy In'],group['CO2e'],marker='.',facecolors='None',linewidth =0.5,edgecolors=dict_colours[name],s=10,alpha=0.1)
    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):    
        axes[group['Legend'].unique()[0]].scatter(group.groupby('ID', as_index=True)['Energy In'].mean(),group.groupby('ID', as_index=True)['CO2e'].mean(),
            s=10,label = name,color=dict_colours[name],edgecolors="black",linewidth =0.5,marker=markers[group['Legend'].unique()[0]])

    for ax in axes.values():
        ax.axhline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
        ax.axhline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
        ax.axhline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
        ax.set_ylim(bottom=0)
        #ax.legend()

    axsRight[1,1].set_xlabel('Energy Return On Investment \n(Energy Delivered/Energy In)')
    axsRight[0,0].set_ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082)')
    axsRight[1,0].set_xlabel('Energy Return On Investment \n(Energy Delivered/Energy In)')
    axsRight[1,0].set_ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082)')

    plt.savefig(os.getcwd()+'\\Figures\\SI_Fig5b.tiff', format='tiff',dpi=1200)
    plt.show()

def figure_5_paper(df_byID,colours = dict_colours,markers = dict_markers,filename='Figure1'):

    # gridspec inside gridspec
    fig, ax = plt.subplots(figsize=[10,9],layout='tight')
    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):
        #sort by length of group so that largest sets are plotted first
        ax.scatter(group['Energy In'],group['CO2e'],marker='.',s=20,alpha=0.1,facecolors='None',linewidth =0.5,edgecolors=dict_colours[name])

    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):

        ax.scatter(group.groupby('ID', as_index=True)['Energy In'].mean(),group.groupby('ID', as_index=True)['CO2e'].mean(),marker=markers[group['Legend'].unique()[0]],
            s=25,label = name,color=dict_colours[name],edgecolors="black",linewidth =0.5)

    ax.axhline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
    ax.axhline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
    ax.axhline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)

    ax.set_xlabel('Energy Return On Investment (Energy Delivered/Energy In)')
    ax.set_ylim(bottom=0)
    ax.set_ylabel('Emissions Intensity (kg CO\u2082e/kg H\u2082)')
    plt.savefig(os.getcwd()+'\\Figures\\figure_5_new2.tiff', format='tiff',dpi=1000)
    plt.show()
    
def SI_transmissionvector_plot(model):
    d=[]
    for route in model: 
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.h2_prod.ID in ('AHF','AHL','SHF','SHL','SLL','SLF'):
            text2=text+ ","+route.h2_prod.ID
        else:
            text2=text
        if route.h2_prod.ID in ('AHF','AHL'):
            prodmethod = 'ATR'
        elif route.h2_prod.ID in ('CPF','CPL','DPF','DPL'):
            prodmethod = 'PEM'
        elif route.h2_prod.ID in ('CAF','CAL','DAF','DAL'):
            prodmethod = 'Alkaline'
        elif route.h2_prod.ID in ('SLL','SLF'):
            prodmethod = 'lowsmr'
        elif route.h2_prod.ID in ('SHF','SHL'):
            prodmethod = 'highsmr'
        if route.E_infra.ID in ('Offshore Wind Floating','Offshore Wind Fixed','UKCS') and route.T_infra.ID not in ('UCNHTNH3','UCNHTFuel Oil'):
            dict2 = {'ID':route.ID,
                     'H2 Prod':prodmethod,
                     'Esource':route.E_infra.ID,
                     'T Infra':route.T_infra.infratype,
                     'T Infra ID':route.T_infra.ID,
                     'Route Path':route.route_path(),
                     'Num':route.name,
                     'Location':route.h2_infra.location,
                     'CO2e':route.CO2e,
                     'Energy In':route.energy_in,
                     'EInfra':route.E_infra.ID,
                     'H2Infra':route.h2_infra.ID,
                     'Legend':route.E_infra.ID+", "+route.T_infra.location+text,
                     'Colour':route.E_infra.ID+", "+route.T_infra.location+text2}
            d.append(dict2)
    df_byID=pd.DataFrame(d)
    dict_labels = {'PHRE':'Offshore, Repurposed Pipeline',
                'PHRNG':'Offshore, Repurposed Pipeline',
                'PHNE':'Offshore, New Pipeline',
                'PHNNG':'Offshore, New Pipeline',
                'PNNG':'Onshore, Pipeline',
                'CE':'Onshore, Cable',
                'LHTLH2':'Offshore, Liquid Hydrogen Tanker (LH2)',
                'LHTMDO':'Offshore, Liquid Hydrogen Tanker (MDO)',
                'NHTNH3':'Offshore, Ammonia Tanker (NH3)',
                'UCNHTNH3':'Offshore, Ammonia Tanker (NH3)',
                'NHTFuel Oil':'Offshore, Ammonia Tanker (Fuel Oil)',
                'UCNHTFuel Oil':'Offshore, Ammonia Tanker (Fuel Oil)',
                'LOHCTFuel Oil':'Offshore, Liquid Organic Hydrogen Carrier (Fuel Oil)'}
    df_byID['T Infra ID'] = df_byID['T Infra ID'].map(dict_labels)
    titles =['Offshore Wind Fixed, Alkaline','Offshore Wind Fixed, PEM','Offshore Wind Floating, Alkaline','Offshore Wind Floating, PEM',
        'Natural Gas, ATR','Natural Gas, SMR with High CCS','Natural Gas, SMR with Low CCS']
    
    #plot CO2e emissions
    fig, ax = plt.subplots(4, 2, figsize=(12, 18),layout='tight')
    axes = [ax[0,0],ax[0,1],ax[1,0],ax[1,1],ax[2,0],ax[2,1],ax[3,0]]
    x=0
    basevalue=[]
    new_legend_labels = ['Tanker','Pipeline','Onshore']
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        title = titles[x]
        order = group.groupby('T Infra ID')['CO2e'].mean().sort_values().index
        sb.barplot(ax=axes[x],data = group,y='T Infra ID',x='CO2e',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
        axes[x].set_title(title)
        axes[x].set_yticklabels(axes[x].get_yticklabels(), wrap=True, rotation=0, ha='right',fontsize=11)
        axes[x].axvline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
        axes[x].axvline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
        axes[x].axvline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
        basevalue.append(group.loc[group['Location'] == 'Onshore']['CO2e'].mean())
        x+=1

    x=0
    ax[3,1].remove()
    #set xlim to largest value so that all plots are on same scale (sharex doesn't allow the axis labels to be plotted)
    axlim = axes[-1].get_xlim()
    for ax1 in axes:
        ax1.set_xlim(axlim)
        ax1.tick_params(axis='x',labelbottom=True)
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2 = ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue[x])/basevalue[x]*100,(mx-basevalue[x])/basevalue[x]*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.set_xlabel('Comparison to Onshore Emissions Intensity (%)')
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2.xaxis.grid(alpha=0.5)
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, new_legend_labels)
        ax1.legend().remove()
        x+=1

    ax[0,1].tick_params(axis='both',left=False,labelleft=False)
    ax[0,1].set_xlabel('kg CO\u2082e/kg H\u2082')
    ax[1,1].tick_params(axis='y',left=False,labelleft=False)
    ax[2,1].tick_params(axis='y',left=False,labelleft=False)
    ax[3,1].tick_params(axis='y',left=False,labelleft=False)
    ax[0,1].set_ylabel('')
    ax[1,1].set_ylabel('')
    ax[2,1].set_ylabel('')
    plt.subplots_adjust(wspace=0.5,hspace=1)
    plt.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\figure_8_S12.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    plt.show()

    #plot Energy Intensity
    fig, ax = plt.subplots(4, 2, figsize=(12, 18),layout='tight')
    axes = [ax[0,0],ax[0,1],ax[1,0],ax[1,1],ax[2,0],ax[2,1],ax[3,0]]
    x=0
    basevalue=[]
    new_legend_labels = ['Tanker','Pipeline','Onshore']
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        title = titles[x]
        order = group.groupby('T Infra ID')['Energy In'].mean().sort_values().index
        sb.barplot(ax=axes[x],data = group,y='T Infra ID',x='Energy In',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
        axes[x].set_title(title)
        axes[x].set_yticklabels(axes[x].get_yticklabels(), wrap=True, rotation=0, ha='right',fontsize=11)
        basevalue.append(group.loc[group['Location'] == 'Onshore']['Energy In'].mean())
        x+=1

    x=0
    ax[3,1].remove()
    #set xlim to largest value so that all plots are on same scale (sharex doesn't allow the axis labels to be plotted)
    axlim = axes[-1].get_xlim()
    for ax1 in axes:
        ax1.set_xlim(axlim)
        ax1.tick_params(axis='x',labelbottom=True)
        ax2 = ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue[x])/basevalue[x]*100,(mx-basevalue[x])/basevalue[x]*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.set_xlabel('Comparison to Onshore Energy Intensity (%)')
        ax1.set_xlabel('kWh/kg H\u2082')
        ax2.xaxis.grid(alpha=0.5)
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, new_legend_labels)
        ax1.legend().remove()
        x+=1

    #ax[0,0].tick_params(axis='x', bottom=False)
    ax[0,1].tick_params(axis='both',left=False,labelleft=False)
    ax[1,1].tick_params(axis='y',left=False,labelleft=False)
    ax[2,1].tick_params(axis='y',left=False,labelleft=False)
    ax[3,1].tick_params(axis='y',left=False,labelleft=False)
    ax[0,1].set_ylabel('')
    ax[1,1].set_ylabel('')
    ax[2,1].set_ylabel('')
    plt.subplots_adjust(wspace=0.5,hspace=1)
    plt.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\figure_9_SI2.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    plt.show()
   
def figures_offshoreinfra(model):
    d=[]
    for route in model: 
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.h2_prod.ID in ('AHF','AHL','SHF','SHL','SLL','SLF'):
            text2=text+ ","+route.h2_prod.ID
        else:
            text2=text
        if route.h2_prod.ID in ('AHF','AHL'):
            prodmethod = 'ATR'
        elif route.h2_prod.ID in ('CPF','CPL','DPF','DPL'):
            prodmethod = 'PEM'
        elif route.h2_prod.ID in ('CAF','CAL','DAF','DAL'):
            prodmethod = 'Alkaline'
        elif route.h2_prod.ID in ('SLL','SLF'):
            prodmethod = 'lowsmr'
        elif route.h2_prod.ID in ('SHF','SHL'):
            prodmethod = 'highsmr'
        if route.E_infra.ID in ('Offshore Wind Floating','Offshore Wind Fixed') and route.T_infra.ID not in ('UCNHTNH3','UCNHTFuel Oil') and route.T_infra.ID in ('PHRE','PHRNG','PNNG','CE','LHTMDO'):
            dict2 = {'ID':route.ID,
                     'H2 Prod':prodmethod,
                     'Esource':route.E_infra.ID,
                     'T Infra':route.T_infra.infratype,
                     'T Infra ID':route.T_infra.ID,
                     'Route Path':route.route_path(),
                     'Num':route.name,
                     'Location':route.h2_infra.location,
                     'CO2e':route.CO2e,
                     'Energy In':route.energy_in,
                     'EInfra':route.E_infra.ID,
                     'H2Infra':route.h2_infra.ID,
                     'Plot':route.T_infra.ID+" "+route.h2_infra.ID,
                     'Legend':route.E_infra.ID+", "+route.T_infra.location+text,
                     'Colour':route.E_infra.ID+", "+route.T_infra.location+text2}
            d.append(dict2)
    df_byID=pd.DataFrame(d)
    dict_labels = {'CE DALI':'Onshore, Decentralised',
                'CE CALI':'Onshore, Centralised',
                'PHRE LRPI':'Offshore, Repurposed \nCentralised, Repurposed Pipeline',
                'PHRE LI':'Offshore, Centralised,\nRepurposed Pipeline',
                'LHTMDO LRPI':'Offshore, Repurposed \nCentralised, LH2 Tanker',
                'LHTMDO LI':'Offshore, Centralised,\nLH2 Tanker',
                'LHTMDO DAFI':'Offshore, Decentralised,\nLH2 Tanker',
                'PHRE DAFI':'Offshore, Decentralised,\nRepurposed Pipeline',
                'LHTMDO DPFI':'Offshore, Decentralised,\nLH2 Tanker',
                'PHRE DPFI':'Offshore, Decentralised,\nRepurposed Pipeline',
                'CE DPLI':'Onshore, Decentralised',
                'CE CPLI':'Onshore, Centralised',
                'PHRE LRTI':'Offshore, Repurposed Centralised, \nRepurposed Pipeline'}
    df_byID['Plot'] = df_byID['Plot'].map(dict_labels)
    titles =['Offshore Wind Fixed, Alkaline','Offshore Wind Fixed, PEM','Offshore Wind Floating, Alkaline','Offshore Wind Floating, PEM',
        'Natural Gas, ATR','Natural Gas, SMR with High CCS','Natural Gas, SMR with Low CCS']
    
    #plot CO2e emissions for SI
    fig, ax = plt.subplots(2, 2, figsize=(14, 10),layout='tight')
    axes = [ax[0,0],ax[0,1],ax[1,0],ax[1,1]]
    x=0
    basevalue=[]
    new_legend_labels = ['Offshore - Pipeline','Offshore - Tanker','Onshore']
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        #title = titles[x]
        order = group.groupby(['Plot'])['CO2e'].mean().sort_values().index
        sb.barplot(ax=axes[x],data = group,y='Plot',x='CO2e',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
        axes[x].set_title(name)
        axes[x].set_yticklabels(axes[x].get_yticklabels(), wrap=True, rotation=0, ha='right',fontsize=11)
        axes[x].axvline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
        #axes[x].axvline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
        #axes[x].axvline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
        basevalue.append(group.loc[group['Location'] == 'Onshore']['CO2e'].mean())
        x+=1

    x=0
    #set xlim to largest value so that all plots are on same scale (sharex doesn't allow the axis labels to be plotted)
    axlim = axes[-1].get_xlim()
    for ax1 in axes:
        ax1.set_xlim(axlim)
        ax1.tick_params(axis='x',labelbottom=True)
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2 = ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue[x])/basevalue[x]*100,(mx-basevalue[x])/basevalue[x]*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.set_xlabel('Comparison to Onshore Emissions Intensity (%)')
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2.xaxis.grid(alpha=0.5)
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, new_legend_labels)
        ax1.legend().remove()
        x+=1

    ax[0,1].tick_params(axis='both',left=False,labelleft=False)
    ax[0,1].set_xlabel('kg CO\u2082e/kg H\u2082')
    ax[1,1].tick_params(axis='y',left=False,labelleft=False)
    ax[0,1].set_ylabel('')
    ax[1,1].set_ylabel('')
    plt.subplots_adjust(wspace=0.5,hspace=1)
    plt.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\figure_10_S1.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    #plt.show()

    #plot Energy Intensity for SI
    fig, ax = plt.subplots(2, 2, figsize=(14, 10),layout='tight')
    axes = [ax[0,0],ax[0,1],ax[1,0],ax[1,1]]
    x=0
    basevalue=[]
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        title = titles[x]
        order = group.groupby('Plot')['Energy In'].mean().sort_values().index
        sb.barplot(ax=axes[x],data = group,y='Plot',x='Energy In',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
        axes[x].set_title(title)
        axes[x].set_yticklabels(axes[x].get_yticklabels(), wrap=True, rotation=0, ha='right',fontsize=11)
        basevalue.append(group.loc[group['Location'] == 'Onshore']['Energy In'].mean())
        x+=1

    x=0
    #set xlim to largest value so that all plots are on same scale (sharex doesn't allow the axis labels to be plotted)
    axlim = axes[-1].get_xlim()
    for ax1 in axes:
        ax1.set_xlim(axlim)
        ax1.tick_params(axis='x',labelbottom=True)
        ax2 = ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue[x])/basevalue[x]*100,(mx-basevalue[x])/basevalue[x]*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.set_xlabel('Comparison to Onshore Energy Intensity (%)')
        ax1.set_xlabel('kWh/kg H\u2082')
        ax2.xaxis.grid(alpha=0.5)
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, new_legend_labels)
        ax1.legend().remove()
        x+=1

    #ax[0,0].tick_params(axis='x', bottom=False)
    ax[0,1].tick_params(axis='both',left=False,labelleft=False)
    ax[1,1].tick_params(axis='y',left=False,labelleft=False)
    ax[0,1].set_ylabel('')
    ax[1,1].set_ylabel('')
    plt.subplots_adjust(wspace=0.5,hspace=1)
    plt.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\figure_11_S1_energy.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    #plt.show()

    #create single plot for paper
    x=0
    fig,ax = plt.subplots(figsize=(6, 4),layout='constrained')
    orderlabels = [2,0,1]
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        title = titles[x]
        if title == 'Offshore Wind Fixed, PEM':
            order = group.groupby('Plot')['CO2e'].mean().sort_values().index
            sb.barplot(ax=ax,data = group,y='Plot',x='CO2e',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
            ax.set_title(title)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0, ha='right',fontsize=11, linespacing=1.05)
            ax.axvline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
            #ax.axvline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
            #ax.axvline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
            basevalue=group.loc[group['Location'] == 'Onshore']['CO2e'].mean()
        x+=1
    #add second axis
    ax.tick_params(axis='x',labelbottom=True)
    ax.set_xlabel('kg CO\u2082e/kg H\u2082')
    ax2 = ax.twiny()
    mn, mx = ax.get_xlim()
    ax2.set_xlim((mn-basevalue)/basevalue*100,(mx-basevalue)/basevalue*100)
    ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
    ax2.set_xlabel('Comparison to Onshore Emissions Intensity (%)')
    ax.set_xlabel('kg CO\u2082e/kg H\u2082')
    ax2.xaxis.grid(alpha=0.5)
    handles, labels = ax.get_legend_handles_labels()
    ax2.legend([handles[idx] for idx in orderlabels],[new_legend_labels[idx] for idx in orderlabels])
    ax.legend().remove()
    ax.set_ylabel('')
    plt.savefig(os.getcwd()+'\\Figures\\figure_8_new_paper.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    plt.show()

def figure_offshorevector_paper(model):
    d=[]
    for route in model: 
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.h2_prod.ID in ('AHF','AHL','SHF','SHL','SLL','SLF'):
            text2=text+ ","+route.h2_prod.ID
        else:
            text2=text
        if route.h2_prod.ID in ('AHF','AHL'):
            prodmethod = 'ATR'
        elif route.h2_prod.ID in ('CPF','CPL','DPF','DPL'):
            prodmethod = 'PEM'
        elif route.h2_prod.ID in ('CAF','CAL','DAF','DAL'):
            prodmethod = 'Alkaline'
        elif route.h2_prod.ID in ('SLL','SLF'):
            prodmethod = 'lowsmr'
        elif route.h2_prod.ID in ('SHF','SHL'):
            prodmethod = 'highsmr'
        if route.E_infra.ID in ('Offshore Wind Fixed','UKCS') and route.T_infra.ID not in ('UCNHTNH3','UCNHTFuel Oil') and prodmethod in ('ATR','PEM'):
            dict2 = {'ID':route.ID,
                     'H2 Prod':prodmethod,
                     'Esource':route.E_infra.ID,
                     'T Infra':route.T_infra.infratype,
                     'T Infra ID':route.T_infra.ID,
                     'Route Path':route.route_path(),
                     'Num':route.name,
                     'Location':route.h2_infra.location,
                     'CO2e':route.CO2e,
                     'Energy In':route.energy_in,
                     'EInfra':route.E_infra.ID,
                     'H2Infra':route.h2_infra.ID,
                     'Legend':route.E_infra.ID+", "+route.T_infra.location+text,
                     'Colour':route.E_infra.ID+", "+route.T_infra.location+text2}
            d.append(dict2)
    df_byID=pd.DataFrame(d)
    dict_labels = {'PHRE':'Offshore, Repurposed Pipeline',
                'PHRNG':'Offshore, Repurposed Pipeline',
                'PHNE':'Offshore, New Pipeline',
                'PHNNG':'Offshore, New Pipeline',
                'PNNG':'Onshore',
                'CE':'Onshore',
                'LHTLH2':'Offshore, Liquid Hydrogen Tanker (LH2)',
                'LHTMDO':'Offshore, Liquid Hydrogen Tanker (MDO)',
                'NHTNH3':'Offshore, Ammonia Tanker (NH3)',
                'UCNHTNH3':'Offshore, Ammonia Tanker (NH3)',
                'NHTFuel Oil':'Offshore, Ammonia Tanker (Fuel Oil)',
                'UCNHTFuel Oil':'Offshore, Ammonia Tanker (Fuel Oil)',
                'LOHCTFuel Oil':'Offshore, Liquid Organic Hydrogen Carrier (Fuel Oil)'}
    df_byID['T Infra ID'] = df_byID['T Infra ID'].map(dict_labels)
    titles =['A. Offshore Wind Fixed, PEM','B. Natural Gas, ATR']
    
    #plot CO2e emissions
    fig, ax = plt.subplots(1, 2, figsize=(10, 4),sharey=True,layout='tight')
    axes = [ax[0],ax[1]]
    x=0
    basevalue=[]
    new_legend_labels = ['Tanker','Pipeline','Onshore']
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        if x < 1:
            order = group.groupby('T Infra ID')['CO2e'].mean().sort_values().index
        title = titles[x]
        sb.barplot(ax=axes[x],data = group,y='T Infra ID',x='CO2e',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
        axes[x].set_title(title)
        axes[x].set_yticklabels(order, wrap=True, rotation=0, ha='right',fontsize=9)
        axes[x].axvline(2.4,label = "Low carbon hydrogen standard",linestyle='dashed',alpha=1,linewidth =1)
        mn, mx = axes[x].get_xlim()
        if mx > 11:
            axes[x].axvline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
            axes[x].axvline(12,label = "Current Hydrogen Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
        basevalue.append(group.loc[group['Location'] == 'Onshore']['CO2e'].mean())
        x+=1

    x=0
    #set xlim to largest value so that all plots are on same scale (sharex doesn't allow the axis labels to be plotted)
    #axlim = axes[-1].get_xlim()
    for ax1 in axes:
        #ax1.set_xlim(axlim)
        ax1.tick_params(axis='x',labelbottom=True)
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2 = ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue[x])/basevalue[x]*100,(mx-basevalue[x])/basevalue[x]*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.set_xlabel('Comparison to Onshore Emissions Intensity (%)')
        ax1.set_xlabel('kg CO\u2082e/kg H\u2082')
        ax2.xaxis.grid(alpha=0.5)
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, new_legend_labels)
        ax1.legend().remove()
        x+=1

    ax[0].tick_params(axis='both',left=True,labelleft=True)
    ax[1].set_xlabel('kg CO\u2082e/kg H\u2082')
    ax[0].set_ylabel('Transmission Vector')
    #ax[0,1].set_ylabel('')
    plt.subplots_adjust(wspace=0.5,hspace=1)
    plt.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\figure_8_new_paper.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    plt.show()

    #plot Energy Intensity
    fig, ax = plt.subplots(1, 2, figsize=(10, 4),layout='tight')
    axes = [ax[0],ax[1]]
    x=0
    basevalue=[]
    new_legend_labels = ['Tanker','Pipeline','Onshore']
    for name,group in df_byID.groupby(['Esource','H2 Prod']):
        title = titles[x]
        order = group.groupby('T Infra ID')['Energy In'].mean().sort_values().index
        sb.barplot(ax=axes[x],data = group,y='T Infra ID',x='Energy In',order=order,hue='Colour',errorbar=("pi", 95), capsize=.4,palette=dict_colours)
        axes[x].set_title(title)
        axes[x].set_yticklabels(axes[x].get_yticklabels(), wrap=True, rotation=0, ha='right',fontsize=9)
        basevalue.append(group.loc[group['Location'] == 'Onshore']['Energy In'].mean())
        x+=1

    x=0
    #set xlim to largest value so that all plots are on same scale (sharex doesn't allow the axis labels to be plotted)
    axlim = axes[-1].get_xlim()
    for ax1 in axes:
        ax1.set_xlim(axlim)
        ax1.tick_params(axis='x',labelbottom=True)
        ax2 = ax1.twiny()
        mn, mx = ax1.get_xlim()
        ax2.set_xlim((mn-basevalue[x])/basevalue[x]*100,(mx-basevalue[x])/basevalue[x]*100)
        ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
        ax2.set_xlabel('Comparison to Onshore Energy Intensity (%)')
        ax1.set_xlabel('kWh/kg H\u2082')
        ax2.xaxis.grid(alpha=0.5)
        handles, labels = ax1.get_legend_handles_labels()
        ax2.legend(handles, new_legend_labels)
        ax1.legend().remove()
        x+=1

    #ax[0,0].tick_params(axis='x', bottom=False)
    ax[1].tick_params(axis='both',left=False,labelleft=False)
    #ax[0,1].set_ylabel('')

    plt.subplots_adjust(wspace=0.5,hspace=1)
    plt.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\figure_9_newpaper_energy.tiff', bbox_inches='tight',format='tiff',dpi=1000)
    plt.show()

def ammonnia_SI(model,markers=dict_markers,colours=dict_colours):
    d=[]
    for route in model:
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.h2_prod.ID in ('AHF','AHL','SHF','SHL','SLL','SLF'):
            text2=text+ ","+route.h2_prod.ID
        else:
            text2=text
        if route.h2_prod.ID in ('AHF','AHL'):
            prodmethod = 'ATR'
        elif route.h2_prod.ID in ('CPF','CPL','DPF','DPL'):
            prodmethod = 'PEM'
        elif route.h2_prod.ID in ('CAF','CAL','DAF','DAL'):
            prodmethod = 'Alkaline'
        elif route.h2_prod.ID in ('SLL','SLF'):
            prodmethod = 'lowsmr'
        elif route.h2_prod.ID in ('SHF','SHL'):
            prodmethod = 'highsmr'
        if route.T_infra.ID in ('UCNHTNH3','UCNHTFuel Oil'):
            dict2 = {'ID':route.ID,
                     'H2 Prod':prodmethod,
                     'Esource':route.E_infra.ID,
                     'T Infra':route.T_infra.infratype,
                     'T Infra ID':route.T_infra.ID,
                     'Route Path':route.route_path(),
                     'Num':route.name,
                     'Location':route.h2_infra.location,
                     'CO2e':route.CO2e,
                     'Energy In':route.energy_in,
                     'EInfra':route.E_infra.ID,
                     'H2Infra':route.h2_infra.ID,
                     'Legend':route.E_infra.ID+", "+route.T_infra.location+text,
                     'Colour':route.E_infra.ID+", "+route.T_infra.location+text2}
            d.append(dict2)
    df_byID=pd.DataFrame(d)
    #correct to per kg ammonia
    df_byID['CO2e'] = df_byID['CO2e']*3/17
    df_byID['Energy In'] = df_byID['Energy In']*3/17
    fig,axsLeft = plt.subplots(2,2,figsize=[11,10],gridspec_kw={'width_ratios': [4,0.5],'height_ratios':[0.5,4],'wspace': 0, 'hspace': 0},layout='tight')
    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):
        #sort by length of group so that largest sets are plotted first
        axsLeft[1,0].scatter(group['Energy In'],group['CO2e'],marker='.',s=20,alpha=0.1,facecolors='None',linewidth =0.5,edgecolors=dict_colours[name])
        sb.kdeplot(data=group,y="CO2e",ax=axsLeft[1,1],color=dict_colours[name],fill = True,legend=False)
        sb.kdeplot(data=group,x="Energy In",ax=axsLeft[0,0],color=dict_colours[name],fill = True,legend=False)

    for name,group in sorted(df_byID.groupby('Colour'),key=lambda k: len(k[1]), reverse=True):
        axsLeft[1,0].scatter(group.groupby('ID', as_index=True)['Energy In'].mean(),group.groupby('ID', as_index=True)['CO2e'].mean(),marker=markers[group['Legend'].unique()[0]],
            s=25,label = name,color=dict_colours[name],edgecolors="black",linewidth =0.5)

    axsLeft[1,0].axhline(0.87,label = "Low carbon ammonia standard - Japan",linestyle='dashed',alpha=1,linewidth =1)
    #axsLeft[1,0].axhline(0.203*33.3,label = "Emissions due to Combustion of Natural Gas(Energy Equivalent Basis)",color="red",linestyle='dashed',alpha=1,linewidth =1)
    axsLeft[1,0].axhline(2.4,label = "Current Ammonnia Production - Average", color ="grey",linestyle='dashed',alpha=1,linewidth =1)
    for axes in (axsLeft[1,1],axsLeft[0,0]):
        axes.axis('off')

    axsLeft[1,0].set_xlabel('Energy Return On Investment (Energy Delivered/Energy In)')
    axsLeft[1,0].set_ylim(bottom=0)
    axsLeft[1,0].set_ylabel('Emissions Intensity (kg CO\u2082e/kg NH\u2083)')
    axsLeft[1,1].set_ylim(axsLeft[1,0].get_ylim())
    axsLeft[0,1].remove()

    plt.savefig(os.getcwd()+'\\Figures\\figure_12_SI.tiff', format='tiff',dpi=1200)
    plt.show()

def sobolplots():
    for variable in ('CO2e','Energy'):
        df_all_paths = pd.read_csv(os.getcwd()+'\\Sobolcombineddfs_all_'+variable+'2.csv')  
        #delete unnamed column which is the path number but is not required as path legend used to plot
        df_all_paths.drop(df_all_paths.columns[df_all_paths.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
        plotonshore(df_all_paths,variable,dict_colours_simple)
        plot(df_all_paths,variable,dict_colours_simple)
    
""" Run model and import results for plots"""

def convertresultstodataframe(results,ammonia=False,legendforplots = 'Legend', save=True,filename = 'summary_results_'+datetime.today().strftime("%d%m%Y")):
    #create empty list so that can add routes including or not including UC ammonia
    list_results = []
    #include or remove direct ammonia routes depending on the ammonia flag 
    if ammonia == True:
        list_results = results
    else:
        list_results = remove_UC_ammonia(results)
    #create list to hold dictionaries of route information so that can convert to df
    d = []
    for route in list_results:
        #create legends for plots
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        if route.h2_prod.ID in ('AHF','AHL','SHF','SHL','SLL','SLF'):
            text2=text+ ","+route.h2_prod.ID
        else:
            text2=text
        dict2 = {'ID':route.ID,
                 'Route Path':route.route_path(),
                 'Num':route.name,
                 'esource':route.E_infra.ID,
                 'Location':route.h2_prod.location,
                 'h2 infra':route.h2_infra.ID,
                 'h2 prod':route.h2_prod.ID,
                 'CO2e':route.CO2e,
                 'yield':route._yield,
                 'tinfratypeyeild':route.T_infra._yield,
                 'tvectortypeyeild':route.T_vector._yield,
                 'tinfratype':route.T_infra.tvector,
                 'tinfra':route.T_infra.ID+route.T_vector.ID,
                 'Energy In':33.3/route.energy_in,
                 'Einfra':route.E_infra.ID,
                 'Legend':route.E_infra.ID+", "+route.T_infra.location+text,
                 'Colour':route.E_infra.ID+", "+route.T_infra.location+text2}
        d.append(dict2)
    df_byID=pd.DataFrame(d)
    df_byID = df_byID.replace([np.inf, -np.inf], np.nan)
    #calculate and print standard deviations and means
    list_values = []
    print(len(df_byID['ID'].unique()))
    for name,group in df_byID.groupby('ID'):
        if group['CO2e'].max()>20:
            print(name)
        if "UKCS" in group['esource'].unique():
            print("ID",name,
                  "Average CO2e",group['CO2e'].mean(),
                  "Standard deviation CO2e",group['CO2e'].std(),
                  "Energy",group['Energy In'].mean(),
                  "Standard deviation Energy",group['Energy In'].std(),
                  "Yield",group['yield'].mean(),
                  "Yield",group['tinfratypeyeild'].mean(),
                  "Yield",group['tvectortypeyeild'].mean(),
                  "5%", group['CO2e'].quantile(0.05),
                  "95%", group['CO2e'].quantile(0.95))

    
    for name,group in df_byID.groupby(legendforplots):
        list_values.append({"ID":name,
              "Average CO2e": group['CO2e'].mean(),
              "Standard deviation CO2e":group['CO2e'].std(),
              "Energy":group['Energy In'].mean(),
              "Standard deviation Energy":group['Energy In'].std(),
              "5%": group['CO2e'].quantile(0.05),
              "95%": group['CO2e'].quantile(0.95)})

    dataframevalues=pd.DataFrame(list_values)
    #save as CSV
    if save == True:
        dataframevalues.to_csv(os.getcwd()+'\\CSV Results\\'+filename+'.csv')
    return df_byID

#run model, distance offshore (km), number of iterations, data inputs - dfs uses data input provided in data file
basemodel = run(150, 1500,dfs,printvalues=True)





