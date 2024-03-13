"""Class definition, including class functions that lead to the estimation of emissions and energy intensity"""


class stage():
    #class template for each of the pathway stages
    def __init__(self,ID,location,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num):
        self.ID = ID
        self.num = num
        self.capacity = capacity
        self.capacity_factor = capacity_factor
        self.lifetime = lifetime
        self._yield = _yield
        self.location = location
        self.e_type = e_type
        self.E_inputs = E_inputs
        self.CO2e = CO2e 
        self.H2_emissions = H2_emissions
    
    def _CO2e_kgH2_ex_energy(self):
        #function calculates the CO2e inputs per kg hydrogen/hydrogen equivalent
        annual_prod = self.capacity*self.capacity_factor
        emb = self.CO2e.Embodied/(annual_prod*self.lifetime)
        Process = self.CO2e.Process
        OM = self.CO2e.OM/annual_prod
        total = {"emb_kgCO2e":emb,"process_kgCO2e":Process,"OM_kgCO2e":OM,"Total":Process + emb + OM}
        return total
    
    def _energy_kgH2(self,E_infra):
        #calculate the energy requirements of a stage by energy type
        annual_prod = self.capacity*self.capacity_factor
        emb_kWh = {}
        pro_kWh = {}
        OM_kWh = {}
        Total_kWh = {}
        #calc values per kWh by energy type and add to dictionary
        for energy_type in self.E_inputs.Embodied:
            #scale values by the annual production and expected lifetime of assets
            emb_kWh[energy_type] = self.E_inputs.Embodied[energy_type]/(annual_prod*self.lifetime)
            
        for energy_type in self.E_inputs.Process:
            #no changes needed, already per kWh, assign to energy source if the same energy type
            if energy_type in (E_infra.e_type,"Both"):
                pro_kWh[E_infra.ID] = self.E_inputs.Process[energy_type]   
            else:
                pro_kWh[energy_type] = self.E_inputs.Process[energy_type]
                
        for energy_key in self.E_inputs.OM:
                OM_kWh[energy_key] = self.E_inputs.OM[energy_key]/annual_prod
                
        for item in [emb_kWh,pro_kWh,OM_kWh]:
            #iterate through all to find the total by energy source
            for energy_key in item:
                if energy_key in Total_kWh.keys():
                    Total_kWh[energy_key] = Total_kWh[energy_key] + item[energy_key]
                else:
                    Total_kWh[energy_key] = item[energy_key]

        #return the energy use by lifecycle stage or in total
        Lifecycle_inputs = {'emb_kWh':emb_kWh,'process_kWh':pro_kWh,'OM_kWh':OM_kWh,"Total":Total_kWh}
        
        return Lifecycle_inputs    

class energysource():
    #class to hold the primary energy source options (not based on template)
    _energysources = []
    def __init__(self,ID,location,e_type,CO2e,efficiency,num,prod_cf):
        self.ID = ID
        self.num = num
        self.location = location
        self.e_type = e_type
        self.CO2e = CO2e
        self.efficiency = efficiency 
        #production CF is related to the energy source so include the limits here. 
        self.prod_cf = prod_cf   
        self._energysources.append(self)
        
class energy():
    #class for each stage to hold energy details in, annual energy = kWh/yr, process energy = kWh/kg H2, embodied energy = kWh
    def __init__(self,ID,OM,Process,Embodied):
        self.ID = ID
        self.OM = OM
        self.Process = Process
        self.Embodied =  Embodied

class CO2e_inputs():
    #class for each stage to hold emissions details in, annual emissions = kg CO2e/yr, process emissions = kg CO2e/kg H2, embodied emissions = kg CO2e
    def __init__(self,ID,OM,Process,Embodied):
        self.ID = ID
        self.OM = OM
        self.Process = Process
        self.Embodied =  Embodied
        
class h2infra(stage):
    #class to hold h2 infra options
    _h2infras = []
    def __init__(self,ID,location,h2infratype,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,tdist,H2_emissions,num):
        super().__init__(ID,location,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num)
        self.h2infratype = h2infratype
        self._h2infras.append(self)
        
class h2prod(stage):
    #class to hold hydrogen production method options
    _h2prods = []
    def __init__(self,ID,location,h2infratype,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num):
        super().__init__(ID,location,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num)
        self.h2infratype=h2infratype
        self._h2prods.append(self)
        
class tinfra(stage):
    #class to hold transmission infrastructure options
    _tinfras = []
    def __init__(self,ID,location,tvector,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num,infratype):
        super().__init__(ID,location,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num)
        self.tvector = tvector
        self.infratype = infratype
        self._tinfras.append(self)   
        
class tvector(stage):
    #class to hold transmission vector options
    _tvectors = []
    def __init__(self,ID,location,tvector,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num):
        super().__init__(ID,location,e_type,lifetime,capacity,capacity_factor,_yield,E_inputs,CO2e,H2_emissions,num)
        self.tvector = tvector
        self._tvectors.append(self)

class routeoptions():
    #class to combine whole route togethor, linked to the stage classes
    _routeoptions = []
    def __init__(self,name,ID,E_type,E_inputs,energy_in,CO2e,coefficients,h2_prod,h2_infra,E_infra,T_vector,T_infra,distance,H2_emissions):
        self._routeoptions.append(self)
        self.name = name
        self.ID = ID
        self.E_type = E_type
        self.energy_in = energy_in  
        self.CO2e = CO2e
        self.E_inputs = E_inputs
        #coefficients are the yields needed of each stage to ensure 1 kWh delivered so that can calc the energy efficiency etc of the route
        self.coefficients = coefficients
        self.h2_prod = h2_prod
        self.h2_infra = h2_infra
        self.E_infra = E_infra
        self.T_vector = T_vector
        self.T_infra = T_infra
        self.distance = distance
        self.H2_emissions = H2_emissions

    
    def route_path(self):
        return [self.h2_infra,self.h2_prod,self.T_vector,self.T_infra]
        
    def route_coefficients(self):
        #set the yields of hydrogen at each stage
        
        n4 = self.T_infra._yield
        n3 = self.T_vector._yield
        n2 = 1 #self.h2_infra._yield, assumed to be one for all infrastructure components as does not interact with the hydrogen.
        n1 = self.h2_prod._yield
        
        if self.h2_infra.location == "Offshore":
            #quant needed (in kWh) at each stage to produce 1 kg at the end for offshore production
                coefficients = {self.T_infra:1/1,self.T_vector:1/(n4),self.h2_prod:1/(n4*n3),self.h2_infra:1/(n2*n3*n4)}
                self._yield = n2*n3*n4
        elif self.h2_infra.location == "Onshore":
            #onshore production yield does not impact as only H2 production and H2 infra, set all to 1
                coefficients = {self.h2_infra:1/n2,self.h2_prod:1,self.T_infra:1,self.T_vector:1}
                self._yield = n2
        self.coefficients = coefficients
        
        
        for y in (n4,n3,n2,n1):
            if y > 1:
                #check if the yields are more than 1, which is not possible, if this occurs return value that will stop code
                print('Error, yield more than 1')
                return False
            else:
                return (n4,n3,n2,n1)

    def set_hydrogen_emissions(self):
        #set the route_coefficients
        self.route_coefficients()
        #initiate variables
        H2_emission_impact = {}
        total_CO2e = 0
        total_H2 = 0
        for stage in self.route_path():
            H2_emission_impact[stage] = stage.H2_emissions * 11.6 * self.coefficients[stage]
            total_CO2e += stage.H2_emissions * 11.6 * self.coefficients[stage]
            total_H2 += stage.H2_emissions * self.coefficients[stage]
        H2_emission_impact["Total_CO2e"] = total_CO2e
        H2_emission_impact["Total_H2"] = total_H2
        self.H2_emissions = H2_emission_impact
        return H2_emission_impact
            
    def set_capacities(self):
        #if the infrastructure capacities have not been set, default to production capacity *This does not affect process values*
        self.h2_infra.capacity = self.h2_prod.capacity
        for stage in self.route_path():
            if stage.capacity in (None,0,1):
                stage.capacity = self.h2_prod.capacity
            if stage.capacity_factor in (None,0):
                stage.capacity_factor = self.h2_prod.capacity_factor
            if stage._yield == 0 or stage._yield >1:
                #default to 1
                print("Error, yield more than 1 or equal to 0",stage.ID,stage._yield)
                stage._yield = 1
                

    def routeenergy_bystageandprocess(self):
            self.route_coefficients()
            route_energy_bySP = {}
            energy_efficiency = {}
            #create a temp dictionary of energy source ID's and efficiencies 
            for energy_source in energysource._energysources:
                energy_efficiency[energy_source.ID] = energy_source.efficiency
                
            for stage in self.route_path():
                Lifecycle_inputs = stage._energy_kgH2(self.E_infra)
                route_energy_bySP[stage] = {}
                stagetotal=0
                #Lifecycle_inputs = {'emb_kWh':emb_kWh,'process_kWh':pro_kWh,'OM_kWh':OM_kWh,"Total":total_kWh} so iterate through all except from the total 
                for process in ('emb_kWh','process_kWh','OM_kWh'):
                    route_energy_bySP[stage][process] = {}
                    processtotal = 0 
                    for energy_type,quantity in Lifecycle_inputs[process].items():
                        if energy_type in energy_efficiency.keys():        
                            #add efficiency energy production if applicable
                            route_energy_bySP[stage][process][energy_type] = (self.coefficients[stage]*quantity)/energy_efficiency[energy_type]
                            processtotal += self.coefficients[stage]*quantity/energy_efficiency[energy_type]
                        else:
                            #add to total if no energy efficiency modelled - assume to be 100% efficient
                            route_energy_bySP[stage][process][energy_type] = self.coefficients[stage]*quantity
                            processtotal += self.coefficients[stage]*quantity        
                    route_energy_bySP[stage][process]["Total"] = processtotal 
                    stagetotal += processtotal
                route_energy_bySP[stage]["Total"] = stagetotal

            return route_energy_bySP
        
    def routeenergy_bytype(self):
        #calc the route energy by type of energy used, return dictionary of total energy by type, doesn't get used, can delete?
        total_by_type = {}
        temp_dict = self.routeenergy_bystageandprocess()
        for stage in temp_dict:
            #iterate through each stage and then return dictionary of energy types and quantities for the stage
            for process in ('emb_kWh','process_kWh','OM_kWh'):
                del temp_dict[stage][process]["Total"]
                for energy_type in temp_dict[stage][process]:
                #iterate through the energy types in the stage energy and add to total
                    if energy_type in total_by_type.keys():
                        total_by_type[energy_type] = temp_dict[stage][process][energy_type] + total_by_type[energy_type]
                    else:
                        total_by_type[energy_type] = temp_dict[stage][process][energy_type]
        return total_by_type
    
    def route_energy(self):
        #define the total route efficiency using the functions previously defined.
        total_energy = 0
        for stage in self.routeenergy_bystageandprocess():
            total_energy += self.routeenergy_bystageandprocess()[stage]["Total"]
        self.energy_in = total_energy
        return total_energy
        
    def set_route_CO2e(self):
        #emissions from embodied energy use are already accounted for, as are the emissions from combustion of natural gas/CH4 during OM and Process
        #upstream emissions from NG/E are not accounted for and they need to be added based on the values for the energy source
        CO2e = 0
        CO2e_bystage = {}
        energy_efficiency = {}
        for energy_source in energysource._energysources:
            energy_efficiency[energy_source.ID] = energy_source.efficiency
        #loop through all the stages
        for stage in self.route_path():
            #add direct emissions
            CO2e_bystage[str(stage)]=stage._CO2e_kgH2_ex_energy()["Total"]*self.coefficients[stage]
            for energytype in stage._energy_kgH2(self.E_infra)["process_kWh"]:
                if energytype == self.E_infra.ID:
                    CO2e_bystage[str(stage)] = CO2e_bystage[str(stage)] +stage._energy_kgH2(self.E_infra)["process_kWh"][energytype]*self.E_infra.CO2e*self.coefficients[stage]
            for energytype in stage._energy_kgH2(self.E_infra)["OM_kWh"]:
                if energytype == self.E_infra.ID:
                    CO2e_bystage[str(stage)] = CO2e_bystage[str(stage)] +stage._energy_kgH2(self.E_infra)["OM_kWh"][energytype]*self.E_infra.CO2e*self.coefficients[stage]
            CO2e_bystage[str(stage)] = CO2e_bystage[str(stage)]+self.H2_emissions[stage] #CO2e_bystage[str(stage)] = CO2e_bystage[str(stage)] + stage.H2_emissions * 11.6 * self.coefficients[stage]
        for stage in CO2e_bystage:
            CO2e+= CO2e_bystage[stage]
        self.CO2e = CO2e
        return CO2e_bystage
    
    def route_CO2e_bySP(self):
        #split CO2e by process and stage
        CO2e_bySP ={}
        for stage in self.route_path():
            CO2e_bySP[stage] = {}
            CO2e_bySP[stage]["emb_kgCO2e"] = stage._CO2e_kgH2_ex_energy()['emb_kgCO2e']*self.coefficients[stage]
            CO2e_bySP[stage]["process_kgCO2e"] = stage._CO2e_kgH2_ex_energy()['process_kgCO2e']*self.coefficients[stage]
            CO2e_bySP[stage]["OM_kgCO2e"] = stage._CO2e_kgH2_ex_energy()['OM_kgCO2e']*self.coefficients[stage]
            CO2e_bySP[stage]["H2 emissions"] = self.H2_emissions[stage]
            for energytype in stage._energy_kgH2(self.E_infra)["process_kWh"]:
                if energytype == self.E_infra.ID:
                    CO2e_bySP[stage]["process_kgCO2e"] = CO2e_bySP[stage]["process_kgCO2e"] + stage._energy_kgH2(self.E_infra)["process_kWh"][energytype]*self.E_infra.CO2e*self.coefficients[stage]
            for energytype in stage._energy_kgH2(self.E_infra)["OM_kWh"]:
                if energytype == self.E_infra.ID:
                    CO2e_bySP[stage]["OM_kWh"] = CO2e_bySP[stage]["OM_kWh"] + stage._energy_kgH2(self.E_infra)["OM_kWh"][energytype]*self.E_infra.CO2e*self.coefficients[stage]
        return CO2e_bySP
    



