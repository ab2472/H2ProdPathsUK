# -*- coding: utf-8 -*-
"""
Created on Fri Dec 15 14:29:02 2023

@author: ab2472
"""

"""Overall Run File"""

from pathway_build import *
import pandas as pd
from plots import *
import pickle
import numpy as np
#from run_model_sobol import *
#from run_model import *

def loadmcdata(name):   
    with open(os.getcwd()+'\\Pickle Results\\'+name,'rb') as inp:
        return pickle.load(inp)
    
    
""" Function to save the mean results by pathway or groups according to columns defined"""
def clean_savemeanstd(results,ammonia=True,legendforplots = 'Legend', save=True,filename = 'summary_results_'+datetime.today().strftime("%d%m%Y")):
    #create empty list so that can add routes including or not including UC ammonia
    list_results = []
    #test if want UC ammonia to be included
    if ammonia == True:
        list_results = results
    else:
        #remove UC from set of results for plots
        list_results = remove_UC_ammonia(results)
            
    #create list to hold dictionaries of route information so that can convert to df
    d = []
    for route in list_results:
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
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
                 'Legend':route.E_infra.ID+", "+route.T_infra.location+text}
        d.append(dict2)
    df_byID=pd.DataFrame(d)
    #remove results judged to be anomalous (more than 10% different than the 99th percentile of the pathway), defined in plot
    df_byID=remove_anomalies(df_byID)
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
        else:
            print("ID",name,
                  "Average CO2e",group['CO2e'].mean(),
                  "Standard deviation CO2e",group['CO2e'].std(),
                  "Energy",group['Energy In'].mean(),
                  "Standard deviation Energy",group['Energy In'].std(),
                  "Yield",group['yield'].mean(),
                  "Yield",group['tinfratypeyeild'].mean(),
                  "Yield",group['tvectortypeyeild'].mean(),
                  "2.5%", group['CO2e'].quantile(0.05),
                  "97.5%", group['CO2e'].quantile(0.95))
    
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

"""Create Figures for Paper - move to plot"""
def createfigures6_9(model):
    for prod in ('Alkaline','PEM','ATR','lowsmr','highsmr'):
        impactofoffshore_infra(model,prodmethod = prod)
        impactofoffshore_infra(model,prodmethod = prod,variable='Energy In')
    impactofoffshore_tvector(model,electrometh1 = 'PEM',smrmeth='ATR')
    impactofoffshore_tvector(model,electrometh1 = 'PEM',smrmeth='ATR',variable='Energy In')
    impactofoffshore_tvector(model,electrometh1 = 'Alkaline',smrmeth='highsmr')
    impactofoffshore_tvector(model,electrometh1 = 'Alkaline',smrmeth='highsmr',variable='Energy In')
    impactofoffshore_tvector(model,electrometh1 = 'Alkaline',smrmeth='lowsmr')
    impactofoffshore_tvector(model,electrometh1 = 'Alkaline',smrmeth='lowsmr',variable='Energy In')
    combinedplot(basemodel1,'Legend')

"""Create Distance Figures (and run data if needed)"""    
def distancefigure(run,bounds=False):
    models = {}
    for distance in range (10,770,20):
        if run == True:
            h2prod = h2prod_uncertainty_df.loc[h2prod_uncertainty_df['Process ID'].isin(['CPF','DPF','AHF'])].copy()
            h2infra = h2infra_uncertainty_df.loc[h2infra_uncertainty_df['Process ID'].isin(['LRPI','DPFI','LRTI'])].copy()
            energysource = energysource_uncertainty_df.loc[energysource_uncertainty_df['Process ID'].isin(['Offshore Wind Fixed','UKCS'])].copy()
            dfs_fordistance2 = [tinfra_uncertainty_df,tvector_uncertainty_df,h2prod,h2infra,energysource]
            models[distance] = clean_savemeanstd(runmodel(distance,500,dfs_fordistance2))
        else:
            models[distance] = clean_savemeanstd(loadmcdata('Distance_'+str(distance)+'_Num_Iterations_50_12032024.pkl'))
    distanceplot(models,'UKCS','AHF','LRTI', bounds=bounds)
    distanceplot(models,'Offshore Wind Fixed','DPF','DPFI',bounds=bounds)
    distanceplot(models,'Offshore Wind Fixed','CPF','LRPI',bounds=bounds)
    
basemodel = runmodel(150, 1500,dfs,printvalues=True)
results = clean_savemeanstd(basemodel)
figure5(results)
createfigures6_9(basemodel)
distancefigure(True,bounds=True)




