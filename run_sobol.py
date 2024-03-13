
from SALib.analyze import sobol
from SALib.sample import saltelli
from SALib import ProblemSpec
from pathway_build import *
import pickle

def save_data(list1,filename):
    with open(os.getcwd()+'\\sobolresultsfile\\'+filename,'wb') as outp:
        pickle.dump(list1,outp,-1)
        
        
"Create dictionary of form route num:[list route IDs]"
def getlistofroutepaths(dfs):
    runmodel(150, 1,dfs)
    ids_dict = {}
    legend_dict={}
    x=0
    for route in routeoptions._routeoptions:
        objs_list = route.route_path()
        objs_list.append(route.E_infra)
        ids_list = []
        for obj in objs_list:
            #returns the unique IDs in order of: h2 infra, h2 prod, tvector, tinfra, esource
            ids_list.append(obj.ID)
        if route.T_infra.location == "Offshore":
            text = ", "+route.T_infra.infratype
        else:
            text=''
        legend_dict[x] = route.E_infra.ID+", "+route.T_infra.location+text
        ids_dict[x] = ids_list
        x+=1
    return ids_dict,legend_dict

"""Retreive list of variables and their bounds"""
def createvariablelist(montecarlodf,pathway):
    montecarlodf2 = montecarlodf.copy()
    montecarlodf2.rename(columns={'Process ID':'ProcessID'},inplace=True)
    listsobol = montecarlodf2[montecarlodf2.ProcessID.isin(pathway)]
    listvars = []
    bounds = []
    for name,group in listsobol.groupby('Stage'):
        for variable1 in group['Variable'].unique():
            bounds.append([group.loc[group['Variable']==variable1]['Low'].values[0],group.loc[group['Variable']==variable1]['High'].values[0]])
            listvars.append(name+' '+variable1)
    return listvars,bounds

def func(esourceCO2e,esourceefficiency,esourceproductioncf,
                 h2infralt,h2infraee,h2inframe,h2infraeen,
                 h2prodpr,h2prodlt,h2prodee,h2prodpe,h2prodme,h2prodmekm,h2prodpen,
                 h2prodh2,tinfrapr,tinfracf,tinfralt,tinfray,tinfraee,
                 tvectorpr,tvectorcf,tvectorlt,tvectory,tvectorpe,tvectormekm,tvectorpen,tvectorhe,pathway,variable='CO2e'):
    routeoptions._routeoptions =[]
    tvector._tvectors = []
    h2infra._h2infras = []
    tinfra._tinfras = []
    h2prod._h2prods = []
    energysource._energysources = []
    
    distance=150
    tinfra_dict = tinfra_uncertainty_df.loc[tinfra_uncertainty_df['Process ID']==pathway[3]].to_dict(orient='records')[0]
    tvector_dict = tvector_uncertainty_df.loc[tvector_uncertainty_df['Process ID']==pathway[2]].to_dict(orient='records')[0]
    h2prod_dict = h2prod_uncertainty_df.loc[h2prod_uncertainty_df['Process ID']==pathway[1]].to_dict(orient='records')[0]
    h2infra_dict = h2infra_uncertainty_df.loc[h2infra_uncertainty_df['Process ID']==pathway[0]].to_dict(orient='records')[0]
    esource_dict = energysource_uncertainty_df.loc[energysource_uncertainty_df['Process ID']==pathway[4]].to_dict(orient='records')[0]

    #input h2prod
    a = energy(h2prod_dict['Process ID'], 
               {"Unassigned":(h2prod_dict["Maintenance Energy"]+h2prod_dict["Maintenance Energy (/km)"]*distance)},
               {h2prod_dict["Energy Type"]:(h2prodpen+h2prod_dict["Process Energy (/km)"]*distance)},
               {"Unassigned":(h2prod_dict["Embodied Energy"]+h2prod_dict["Embodied Energy (/km)"]*distance)})
    b = CO2e_inputs(h2prod_dict['Process ID'], 
                    h2prodme+h2prodmekm*distance, 
                    h2prodpe+h2prod_dict["Process Emissions (/km)"]*distance, 
                    h2prodee+h2prod_dict["Embodied Emissions (/km)"]*distance)
    h2prod(h2prod_dict['Process ID'], h2prod_dict["Production Location"], 
           h2prod_dict["Infrastructure Type"], 
           h2prod_dict["Energy Type"], 
           h2prodlt, 
           h2prodpr, 
           esourceproductioncf, 
           h2prod_dict["Yield"], 
           a, 
           b, 
           h2prodh2,
           1)
    
    #input tinfra
    a = energy(tinfra_dict['Process ID'], 
               {"Unassigned":tinfra_dict["Maintenance Energy"]+tinfra_dict["Maintenance Energy (/km)"]*distance},
               {tinfra_dict["Energy Type"]:tinfra_dict["Process Energy"]+tinfra_dict["Process Energy (/km)"]*distance},
               {"Unassigned":tinfra_dict["Embodied Energy"]+tinfra_dict["Embodied Energy (/km)"]*distance})
    b = CO2e_inputs(tinfra_dict['Process ID'], 
                    tinfra_dict["Maintenance Emissions"]+tinfra_dict["Maintenance Emissions (/km)"]*distance, 
                    tinfra_dict["Process Emissions"]+tinfra_dict["Process Emissions (/km)"]*distance, 
                    tinfraee+tinfra_dict["Embodied Emissions (/km)"]*distance)
    tinfra(tinfra_dict['Process ID'], 
           tinfra_dict["Production Location"], 
           tinfra_dict["Transmission Vector"], 
           tinfra_dict["Energy Type"],
           tinfralt, 
           tinfrapr, 
           tinfracf, 
           tinfray, 
           a, 
           b, 
           tinfra_dict["Hydrogen Emissions"],
           1,
           tinfra_dict["Infra Type"])

    #input tvector
    a = energy(tvector_dict['Process ID'], 
               {"Unassigned":(tvector_dict["Maintenance Energy"]+tvector_dict["Maintenance Energy (/km)"]*distance)},
               {tvector_dict["Energy Type"]:(tvectorpen+tvector_dict["Process Energy (/km)"]*distance)},
               {"Unassigned":(tvector_dict["Embodied Energy"]+tvector_dict["Embodied Energy (/km)"]*distance)})
    b = CO2e_inputs(tvector_dict['Process ID'], 
                    tvector_dict["Maintenance Emissions"]+tvectormekm*distance, 
                    tvectorpe+tvector_dict["Process Emissions (/km)"]*distance, 
                    tvector_dict["Embodied Emissions"]+tvector_dict["Embodied Emissions (/km)"]*distance)
    tvector(tvector_dict['Process ID'], 
            tvector_dict["Production Location"], 
            tvector_dict["Transmission Vector"], 
            tvector_dict["Energy Type"],
            tvectorlt, 
            tvectorpr, 
            tvectorcf, 
            tvectory, 
            a, 
            b, 
            tvectorhe,
            1)

    #input h2infra
    a = energy(h2infra_dict['Process ID'], 
               {"Unassigned":(h2infra_dict["Maintenance Energy"]+h2infra_dict["Maintenance Energy (/km)"]*distance)},
               {h2infra_dict["Energy Type"]:(h2infra_dict["Process Energy"]+h2infra_dict["Process Energy (/km)"]*distance)},
               {"Unassigned":(h2infraeen+h2infra_dict["Embodied Energy (/km)"]*distance)})
    b = CO2e_inputs(h2infra_dict['Process ID'], 
                    h2inframe+h2infra_dict["Maintenance Emissions (/km)"]*distance, 
                    h2infra_dict["Process Emissions"]+h2infra_dict["Process Emissions (/km)"]*distance, 
                    h2infraee+h2infra_dict["Embodied Emissions (/km)"]*distance)
    h2infra(h2infra_dict['Process ID'], 
            h2infra_dict["Production Location"], 
            h2infra_dict["Infrastructure Type"], 
            h2infra_dict["Energy Type"], 
            h2infralt, 
            h2infra_dict["Production Rate (kg/yr)"], 
            h2infra_dict["Capacity Factor"], 
            h2infra_dict["Yield"], 
            a, 
            b, 
            None, 
            h2infra_dict["Hydrogen Emissions"],
            1)

    #input energy
    energysource(esource_dict['Process ID'], 
                 esource_dict["Location"], 
                 esource_dict["Energy Type"], 
                 esourceCO2e, 
                 esourceefficiency,
                 1,
                 esource_dict["Production CF"])
    
    routeoptions(1, 'sobol', h2prod._h2prods[0].e_type, None, None, None, None, h2prod._h2prods[0], h2infra._h2infras[0], energysource._energysources[0], tvector._tvectors[0], tinfra._tinfras[0], distance, None)
    
    routeoptions._routeoptions[0].set_capacities()
    routeoptions._routeoptions[0].set_hydrogen_emissions()
    routeoptions._routeoptions[0].route_energy()
    routeoptions._routeoptions[0].set_route_CO2e()
    if variable == 'CO2e':
        return routeoptions._routeoptions[0].CO2e
    elif variable == 'Energy':
        return routeoptions._routeoptions[0].energy_in

""" Wrap pathway creation function for sobol analysis, variables must be in the correct order"""
def wrapped_CO2e(X,func=func):
    N, D = X.shape
    results = np.empty(N)
    for i in range(N):
        esourceCO2e,esourceefficiency,esourceproductioncf,h2infralt,h2infraee,h2inframe,h2infraeen, h2prodpr,h2prodlt,h2prodee,h2prodpe,h2prodme,h2prodmekm,h2prodpen,h2prodh2,tinfrapr,tinfracf,tinfralt,tinfray,tinfraee,tvectorpr,tvectorcf,tvectorlt,tvectory,tvectorpe,tvectormekm,tvectorpen,tvectorhe = X[i, :]
        #func defined in sobol_def, creates pathway selected for the iteration and returns CO2e or Energy depending on variable chosen
        results[i] = func(esourceCO2e,esourceefficiency,esourceproductioncf,
                         h2infralt,h2infraee,h2inframe,h2infraeen,
                         h2prodpr,h2prodlt,h2prodee,h2prodpe,h2prodme,h2prodmekm,h2prodpen,
                         h2prodh2,tinfrapr,tinfracf,tinfralt,tinfray,tinfraee,
                         tvectorpr,tvectorcf,tvectorlt,tvectory,tvectorpe,tvectormekm,tvectorpen,tvectorhe,pathway,'CO2e')

    return results

def wrapped_energy(X,func=func):
    N, D = X.shape
    results = np.empty(N)
    for i in range(N):
        esourceCO2e,esourceefficiency,esourceproductioncf,h2infralt,h2infraee,h2inframe,h2infraeen, h2prodpr,h2prodlt,h2prodee,h2prodpe,h2prodme,h2prodmekm,h2prodpen,h2prodh2,tinfrapr,tinfracf,tinfralt,tinfray,tinfraee,tvectorpr,tvectorcf,tvectorlt,tvectory,tvectorpe,tvectormekm,tvectorpen,tvectorhe = X[i, :]
        #func defined in sobol_def, creates pathway selected for the iteration and returns CO2e or Energy depending on variable chosen
        results[i] = func(esourceCO2e,esourceefficiency,esourceproductioncf,
                         h2infralt,h2infraee,h2inframe,h2infraeen,
                         h2prodpr,h2prodlt,h2prodee,h2prodpe,h2prodme,h2prodmekm,h2prodpen,
                         h2prodh2,tinfrapr,tinfracf,tinfralt,tinfray,tinfraee,
                         tvectorpr,tvectorcf,tvectorlt,tvectory,tvectorpe,tvectormekm,tvectorpen,tvectorhe,pathway,'Energy')

    return results


dfs_sobol=[]
ids_dict,legend_dict = getlistofroutepaths(dfs)

for x in range(len(ids_dict)):
    pathway=ids_dict[x]
    listvars,bounds =createvariablelist(monte_carlo_df,ids_dict[x])
    sp_energy = ProblemSpec({
        'names': listvars,
        'bounds': bounds,
        })
    (
     sp_CO2e.sample_sobol(2**10,calc_second_order=False)
     .evaluate(wrapped_energy)
     .analyze_sobol(calc_second_order=False)
     )
    total_Si, first_Si = sp_CO2e.to_df()
    sobol_results = sp_CO2e.to_df()
    print(sp_energy)
    
    df_sobol = total_Si.rename(columns={'ST':x})
    df_sobol.drop(['ST_conf'],axis=1,inplace=True)
    df_transposed = df_sobol.T
    df_transposed['Energy Source'] = ids_dict[x][4]
    df_transposed['H2 Prod Infra'] = ids_dict[x][0]
    df_transposed['H2 Prod Method'] = ids_dict[x][1]
    df_transposed['T vector'] = ids_dict[x][2]
    df_transposed['T Infra'] = ids_dict[x][3]
    df_transposed['Legend'] = legend_dict[x]
        
    dfs_sobol.append(df_transposed)
    
combined_sobol_df = pd.concat(dfs_sobol,axis=0, ignore_index=True)   
save_data(dfs_sobol,'Dataframes_Sobol_offshore_CO2e.pkl')
combined_sobol_df.to_csv('Sobolcombineddfs_all_CO2e.csv')


dfs_sobol=[]
ids_dict,legend_dict = getlistofroutepaths(dfs)

for x in range(len(ids_dict)):
    pathway=ids_dict[x]
    listvars,bounds =createvariablelist(monte_carlo_df,ids_dict[x])
    sp_energy = ProblemSpec({
        'names': listvars,
        'bounds': bounds,
        })
    (
     sp_energy.sample_sobol(2**10,calc_second_order=False)
     .evaluate(wrapped_energy)
     .analyze_sobol(calc_second_order=False)
     )
    total_Si, first_Si = sp_energy.to_df()
    sobol_results = sp_energy.to_df()
    print(sp_energy)
    
    df_sobol = total_Si.rename(columns={'ST':x})
    df_sobol.drop(['ST_conf'],axis=1,inplace=True)
    df_transposed = df_sobol.T
    df_transposed['Energy Source'] = ids_dict[x][4]
    df_transposed['H2 Prod Infra'] = ids_dict[x][0]
    df_transposed['H2 Prod Method'] = ids_dict[x][1]
    df_transposed['T vector'] = ids_dict[x][2]
    df_transposed['T Infra'] = ids_dict[x][3]
    df_transposed['Legend'] = legend_dict[x]
        
    dfs_sobol.append(df_transposed)
    
combined_sobol_df_energy = pd.concat(dfs_sobol,axis=0, ignore_index=True)   
save_data(dfs_sobol,'Dataframes_Sobol_offshore_Energy.pkl')
combined_sobol_df_energy.to_csv('Sobolcombineddfs_all_Energy.csv')



