"Pathway build, and execution of emissions and energy calculations"

import numpy as np
import pickle
from class_definitions import * #NOQA
import pandas as pd
import timeit
import os
import io
from datetime import datetime


start1 = timeit.default_timer()

"""Define the input data"""
with open('Data/DataInputs.xlsx', "rb") as f:
    file_io_obj = io.BytesIO(f.read())
#xls = pd.ExcelFile('Data/uncertainty/SI_3.xlsx')
tinfra_uncertainty_df = pd.read_excel(file_io_obj,'4. Transmission Infrastructure')
tvector_uncertainty_df = pd.read_excel(file_io_obj,'5. Transmission Vector')
h2prod_uncertainty_df = pd.read_excel(file_io_obj,'2. H2 Production Methods')
h2infra_uncertainty_df = pd.read_excel(file_io_obj,'3. H2 Production Infrastructure')
energysource_uncertainty_df = pd.read_excel(file_io_obj,'1. Energy Sources')
monte_carlo_df = pd.read_excel(file_io_obj,'6. MC Bounds')

def dropna(df):
    df = df.dropna(how="all", inplace=True)

dfs = [tinfra_uncertainty_df,tvector_uncertainty_df,h2prod_uncertainty_df,h2infra_uncertainty_df,energysource_uncertainty_df]
stages=['Tinfra','Tvector','H2 prod','H2 infra','Energy Source']

for dataframe in dfs:
    dropna(dataframe) 

def randvalue_MC(proccess_ID,dataframe,MC_df_stage,y):
    #returns random value based on the bounds defined in the excel, change to being based on the same sobol
    #MC_df_stage = monte_carlo_df.loc[monte_carlo_df['obj name'] == proccess_ID].copy()
    #MC_df_stage['rand value'] = np.random.uniform(MC_df_stage['low'],MC_df_stage['high'])
    stage_values = dataframe.loc[dataframe['Process ID'] == proccess_ID].copy().set_index('Process ID')
    if y>2:
        # if it equals one, no monte carlo analysis, use base values
        MC_df_stage_temp = MC_df_stage.loc[MC_df_stage['Process ID'] == proccess_ID].copy()
        variables = MC_df_stage_temp['Variable'].unique()
        #print(variables,proccess_ID)
        for variable in variables:
            stage_values.loc[proccess_ID,variable] = MC_df_stage_temp.loc[MC_df_stage_temp['Variable'] == variable]['rand value'].values[process_id]
    return stage_values.to_dict('list')


def openfiles(distance,y,dataframes,MC=True):
    for x in range(y):
        if MC ==True and y>1:
            MC_df_stage = monte_carlo_df.copy()
            MC_df_stage['rand value'] = np.random.uniform(MC_df_stage['Low'],MC_df_stage['High'])
            MC_df_stage.set_index('Process ID',inplace=True)
        
            for df,stage in zip(dataframes,stages):
                MC_df_stage_temp = MC_df_stage.loc[MC_df_stage['Stage'] == stage]
                variables = MC_df_stage_temp['Variable'].unique()
                df.set_index('Process ID',inplace=True)
                df['Process ID'] = df.index
                #print(variables,stage)
                for variable in variables:
                    #print(df.columns)
                    #print(MC_df_stage_temp.loc[MC_df_stage_temp['Variable'] == variable]['rand value'])
                    df[variable] = MC_df_stage_temp.loc[MC_df_stage_temp['Variable'] == variable]['rand value']
                    #print(df[variable])
        else:
            for df in dataframes:
                df.set_index('Process ID',inplace=True)
                df['Process ID'] = df.index
        
        dict1 = dataframes[0].to_dict()
        for process_id in dataframes[0]['Process ID'].unique():
            a = energy(process_id, 
                       {"Unassigned":dict1["Maintenance Energy"][process_id]+dict1["Maintenance Energy (/km)"][process_id]*distance},
                       {dict1["Energy Type"][process_id]:dict1["Process Energy"][process_id]+dict1["Process Energy (/km)"][process_id]*distance},
                       {"Unassigned":dict1["Embodied Energy"][process_id]+dict1["Embodied Energy (/km)"][process_id]*distance})
            b = CO2e_inputs(process_id, 
                            dict1["Maintenance Emissions"][process_id]+dict1["Maintenance Emissions (/km)"][process_id]*distance, 
                            dict1["Process Emissions"][process_id]+dict1["Process Emissions (/km)"][process_id]*distance, 
                            dict1["Embodied Emissions"][process_id]+dict1["Embodied Emissions (/km)"][process_id]*distance)
            tinfra(process_id, 
                   dict1["Production Location"][process_id], 
                   dict1["Transmission Vector"][process_id], 
                   dict1["Energy Type"][process_id],
                   dict1["Lifetime (yrs)"][process_id], 
                   dict1["Production Rate (kg/yr)"][process_id], 
                   dict1["Capacity Factor" ][process_id], 
                   dict1["Yield" ][process_id], 
                   a, 
                   b, 
                   dict1["Hydrogen Emissions"][process_id],
                   x+1,
                   dict1["Infra Type"][process_id])

        
        dict1 = dataframes[1].to_dict()
        for process_id in dataframes[1]['Process ID'].unique():
            a = energy(process_id, 
                       {"Unassigned":(dict1["Maintenance Energy"][process_id]+dict1["Maintenance Energy (/km)"][process_id]*distance)},
                       {dict1["Energy Type"][process_id]:(dict1["Process Energy"][process_id]+dict1["Process Energy (/km)"][process_id]*distance)},
                       {"Unassigned":(dict1["Embodied Energy"][process_id]+dict1["Embodied Energy (/km)"][process_id]*distance)})
            b = CO2e_inputs(process_id, 
                            dict1["Maintenance Emissions"][process_id]+dict1["Maintenance Emissions (/km)"][process_id]*distance, 
                            dict1["Process Emissions"][process_id]+dict1["Process Emissions (/km)"][process_id]*distance, 
                            dict1["Embodied Emissions"][process_id]+dict1["Embodied Emissions (/km)"][process_id]*distance)
            tvector(process_id, 
                    dict1["Production Location"][process_id], 
                    dict1["Transmission Vector"][process_id], 
                    dict1["Energy Type"][process_id],
                    dict1["Lifetime (yrs)"][process_id], 
                    dict1["Production Rate (kg/yr)"][process_id], 
                    dict1["Capacity Factor" ][process_id], 
                    dict1["Yield" ][process_id], 
                    a, 
                    b, 
                    dict1["Hydrogen Emissions"][process_id],
                    x+1)
            #print(dict1["Process Emissions"][process_id]+dict1["Process Emissions (/km)"][process_id]*distance)
            
        dict1 = dataframes[2].to_dict()
        
        for process_id in dataframes[2]['Process ID'].unique():
            a = energy(process_id, 
                       {"Unassigned":(dict1["Maintenance Energy"][process_id]+dict1["Maintenance Energy (/km)"][process_id]*distance)},
                       {dict1["Energy Type"][process_id]:(dict1["Process Energy"][process_id]+dict1["Process Energy (/km)"][process_id]*distance)},
                       {"Unassigned":(dict1["Embodied Energy"][process_id]+dict1["Embodied Energy (/km)"][process_id]*distance)})
            b = CO2e_inputs(process_id, 
                            dict1["Maintenance Emissions"][process_id]+dict1["Maintenance Emissions (/km)"][process_id]*distance, 
                            dict1["Process Emissions"][process_id]+dict1["Process Emissions (/km)"][process_id]*distance, 
                            dict1["Embodied Emissions"][process_id]+dict1["Embodied Emissions (/km)"][process_id]*distance)
            h2prod(process_id, dict1["Production Location"][process_id], 
                   dict1["Infrastructure Type"][process_id], 
                   dict1["Energy Type"][process_id], 
                   dict1["Lifetime (yrs)"][process_id], 
                   dict1["Production Rate (kg/yr)"][process_id], 
                   dict1["Capacity Factor"][process_id], 
                   dict1["Yield"][process_id], 
                   a, 
                   b, 
                   dict1["Hydrogen Emissions"][process_id],
                   x+1)
            
        dict1 = dataframes[3].to_dict()


        for process_id in dataframes[3]['Process ID'].unique():
            a = energy(process_id, 
                       {"Unassigned":(dict1["Maintenance Energy"][process_id]+dict1["Maintenance Energy (/km)"][process_id]*distance)},
                       {dict1["Energy Type"][process_id]:(dict1["Process Energy"][process_id]+dict1["Process Energy (/km)"][process_id]*distance)},
                       {"Unassigned":(dict1["Embodied Energy"][process_id]+dict1["Embodied Energy (/km)"][process_id]*distance)})
            b = CO2e_inputs(process_id, 
                            dict1["Maintenance Emissions"][process_id]+dict1["Maintenance Emissions (/km)"][process_id]*distance, 
                            dict1["Process Emissions"][process_id]+dict1["Process Emissions (/km)"][process_id]*distance, 
                            dict1["Embodied Emissions"][process_id]+dict1["Embodied Emissions (/km)"][process_id]*distance)
            h2infra(process_id, 
                    dict1["Production Location"][process_id], 
                    dict1["Infrastructure Type"][process_id], 
                    dict1["Energy Type"][process_id], 
                    dict1["Lifetime (yrs)"][process_id], 
                    dict1["Production Rate (kg/yr)"][process_id], 
                    dict1["Capacity Factor"][process_id], 
                    dict1["Yield"][process_id], 
                    a, 
                    b, 
                    None, 
                    dict1["Hydrogen Emissions"][process_id],
                    x+1)
            
        dict1 = dataframes[4].to_dict()


        for process_id in dataframes[4]['Process ID'].unique():
            energysource(process_id, 
                         dict1["Location"][process_id], 
                         dict1["Energy Type"][process_id], 
                         dict1["CO2e"][process_id], 
                         dict1["Efficiency"][process_id],
                         x+1,
                         dict1["Production CF"][process_id])
    print("complete")


def createpathways(H2infra,H2prod,Energyinfra,Transvect,Transinfra,distance,montecarlo,**kwargs):
    linked_H2prod_infra = []
    linked_Tvector_H2=  []
    linked_all_exceptenergy =[]
    #first match production option and location
    for prod_option in H2prod:
        for h2infra_option in H2infra:
            if prod_option.num == h2infra_option.num:
                #num restricts number of pathways to number specified in monte carlo - ensures that same number of new iterations per pathway
                if prod_option.e_type == h2infra_option.e_type and prod_option.h2infratype == h2infra_option.h2infratype and prod_option.location == h2infra_option.location:
                    linked_H2prod_infra.append({"Production Option":prod_option,"Production Location":h2infra_option})
                #print(prod_option.ID)
    #next match transmission vector
    for option in linked_H2prod_infra:
        for tvector_option in Transvect:
            if option["Production Option"].location == tvector_option.location and option["Production Option"].e_type == tvector_option.e_type and tvector_option.num == option["Production Option"].num:
                linked_Tvector_H2.append({"Production Option":option["Production Option"],
                                          "Production Location":option["Production Location"],
                                          "Transmission Vector":tvector_option})
    #now match transmission infra
    for option in linked_Tvector_H2:
        for trans_option in Transinfra:
            if trans_option.e_type in (option["Transmission Vector"].e_type,"Fuel Oil","MDO","LH2","NH3","HFO") and option["Transmission Vector"].location == trans_option.location and option["Transmission Vector"].tvector == trans_option.tvector and trans_option.num == option["Transmission Vector"].num:
                linked_all_exceptenergy.append({"Production Option":option["Production Option"],
                                                "Production Location":option["Production Location"],
                                                "Transmission Vector":option["Transmission Vector"],
                                                "Transmission Infra":trans_option})
    #empty list to reuse
    linked_all = []
    n=0
    #match primary energy source
    for option in linked_all_exceptenergy:
        for energysource in Energyinfra:
            if option["Production Option"].location in (energysource.location,"Onshore") and option["Production Option"].e_type == energysource.e_type and energysource.num == option["Production Option"].num:
                if montecarlo == True: 
                    #if doing sensitivity analysis set the value of the production capacity factor to the energy source capacity factor
                    option["Production Option"].capacity_factor = energysource.prod_cf
                linked_all.append({"Production Option":option["Production Option"],
                                   "Production Location":option["Production Location"],
                                   "Transmission Vector":option["Transmission Vector"],
                                   "Transmission Infra":option["Transmission Infra"],
                                   "Energy Source":energysource})
                #add to class, set number of the pathway iteration
                n += 1
                ID = energysource.ID+"-"+option["Production Option"].ID+"-"+option["Production Location"].ID+"-"+option["Transmission Infra"].ID+"-"+option["Transmission Vector"].ID
                routeoptions(n, 
                             ID, 
                             option["Production Option"].e_type, 
                             None, 
                             None, 
                             None, 
                             None, 
                             option["Production Option"], 
                             option["Production Location"], 
                             energysource, 
                             option["Transmission Vector"], 
                             option["Transmission Infra"], 
                             distance, 
                             None)
                if option["Production Option"].num == energysource.num == option["Production Location"].num == option["Transmission Vector"].num == option["Transmission Infra"].num:
                    #check that all the pathway iterations are the same
                    pass
                else:
                    print(option["Production Option"].num,energysource.num,option["Production Location"].num,option["Transmission Vector"].num,option["Transmission Infra"].num)
                    
def createpaths(distance,n,dataframes):
    #make sure lists are blanked from previous iterations
    routeoptions._routeoptions = []
    tvector._tvectors = []
    h2infra._h2infras = []
    tinfra._tinfras = []
    h2prod._h2prods = []
    energysource._energysources = []
    openfiles(distance,n,dataframes)
    stop1 = timeit.default_timer()
    #print('Time: ', stop1 - start1)  
    #print(len(h2infra._h2infras))
    createpathways(h2infra._h2infras,h2prod._h2prods,energysource._energysources,tvector._tvectors,tinfra._tinfras,distance,True)
    return routeoptions._routeoptions

def run():
    #make sure lists are blanked from previous iterations
    routepaths =[]
    for x in routeoptions._routeoptions:
        if x.route_coefficients() == "False":
            print("error - more than 1process_idprocess_id% yield")
            return False
        else:
            x.set_hydrogen_emissions()
            x.set_capacities()
            x.route_energy()
            x.set_route_CO2e()
            #check for duplicates by appending route path name to string
            routepaths.append(str(x.route_path()[0])+str(x.route_path()[1])+str(x.route_path()[2])+str(x.route_path()[3])+str(x.E_infra.ID))  
    if len(routepaths) == len(set(routepaths)):
        return routeoptions._routeoptions
    else:
        #print("Error: Duplicates exist") - doesn't work as names of options changed to be the same now
        pass
        return routeoptions._routeoptions

def save_data(list1,filename):
    with open(os.getcwd()+'\\Pickle Results\\'+filename,'wb') as outp:
        pickle.dump(list1,outp,-1)

def runmodel(distance,n,dataframes,**kwargs):
    createpaths(distance,n,dataframes)
    base_model = run()
    if base_model == False:
        print("Error - Duplicates")
        return False
    else:
        str1 = 'Distance_'+str(distance)+'_Num_Iterations_'+str(n)+'_'+datetime.today().strftime("%d%m%Y")+'.pkl'
        save_data(base_model,str1)
        #print(len(base_model))
        """electricity_routes=0
        NG_routes=0
        offshore=0
        onshore=0
        emin=0
        emax=100
        CO2emin = 5
        CO2emax=5
        for route in routeoptions._routeoptions:
            if route.h2_prod.location =="Onshore":
                onshore+=1
            if route.E_type == "E":
                electricity_routes +=1
            if route.E_type == "NG":
                NG_routes += 1
            if route.energy_in < emin:
                emin = route.energy_in
            if route.energy_in > emax:
                emax = route.energy_in   
            if route.CO2e < CO2emin:
                CO2emin = route.CO2e
            if route.CO2e > CO2emax:
                CO2emax = route.CO2e
    print("No. onshore routes: "+ str(onshore))
    print("No. E routes: "+ str(electricity_routes))
    print("No. NG routes: "+str( NG_routes))
    print("Min Energy: "+str(emin)+" kWh/kg H2")
    print("Max Energy: "+str(emax)+" kWh/kg H2")
    print("Min CO2e: "+str(CO2emin)+" kgCO2e/kg H2")
    print("Max CO2e: "+str(CO2emax)+" kgCO2e/kg H2")"""
    return base_model
    


