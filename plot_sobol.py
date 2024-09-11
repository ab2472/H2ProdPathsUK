
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import pickle
import os
import textwrap

labels_forplot = {'Energy Source CO2e': 'Energy Source: Emissions Factor',
                'Energy Source Production CF':'Hydrogen Production: Load Factor',
                'H2 infra Liftime (yrs)':'Hydrogen Infrastructure: Lifetime',
                'H2 infra Embodied Emissions':'Hydrogen Infrastructure: Embodied Emissions',
                'H2 prod Production Rate (kg/yr)':'Hydrogen Production: Capacity',
                'H2 prod Embodied Emissons':'Hydrogen Production: Embodied Emissions',
                'H2 prod Process Emissions':'Hydrogen Production: Process Emissions',
                'H2 prod Process Energy':'Hydrogen Production: Process Energy',
                'H2 prod Hydrogen Emissions':'Hydrogen Production: Hydrogen Emissions',
                'Tinfra Yield':'Transmission Infrastructure: Yield',
                'Tvector Yield':'Transmission Vector: Yield',
                'Tvector Process Emissions':'Transmission Vector: Process Emissions',
                'Tvector Hydrogen Emissions':'Transmission Vector: Hydrogen Emissions',
                }

def importantvariables(combined_df):
    cols = [col for col in combined_df.select_dtypes(include='number').columns]
    important_cols = [col for col in cols if combined_df[col].max() > 0.05]
    return important_cols


def plot(dataframe,variable,dict_colours_simple):
    fig, axs = plt.subplots(3,3,figsize=(12,11),sharex=True,sharey=True,layout='tight')
    axes=[axs[1,0],axs[2,0],axs[0,0],axs[1,1],axs[2,1],axs[0,1],axs[1,2],axs[2,2],axs[0,2]]#,axs[0,1],axs[1,1],axs[2,1],axs[0,2],axs[1,2],axs[2,2]]
    gridnum=0
    titlelabels=['D','G','A','E','H','B','F','I','C']
    for col in dataframe.select_dtypes(include='number').columns:
        #print(col)
        if col not in importantvariables(dataframe):
            #print(col)
            dataframe.drop(col,axis=1,inplace=True)
    x=0
    for name,group in dataframe.groupby('Legend'):
        #print(name)
        if group['Energy Source'].unique()[0] in ('UKCS', 'Offshore Wind Fixed','Offshore Wind Floating'):
            group = pd.melt(group,id_vars = ['H2 Prod Infra','H2 Prod Method','T vector','T Infra','Energy Source','Legend'],value_vars=importantvariables(dataframe),var_name='Variable',value_name='Sobol Index (St)')
            group['Variable'] = group['Variable'].map(labels_forplot)
            if x<1:
                order = group.groupby('Variable')['Sobol Index (St)'].median().sort_values(ascending=False).index
            sb.boxplot(y=group['Variable'],x=group['Sobol Index (St)'],order=order,width = 0.6,color=dict_colours_simple[name],whis=[5,95],linewidth=1,ax=axes[gridnum],showfliers=False)
            #axes[gridnum].set_yticks(axes[gridnum].get_yticks(),[textwrap.fill(label,15) for label in cols],fontsize=14)
            axes[gridnum].tick_params(labelrotation=0)
            wrapped_title = textwrap.fill(titlelabels[gridnum] + ': ' + str(name), width=30)
            axes[gridnum].set_title(wrapped_title)
            #y_labels = [textwrap.fill(label.get_text(), 30) for label in axes[gridnum].get_yticklabels()]
            #print(y_labels)
            #axes[gridnum].set_yticklabels(y_labels)
            axes[gridnum].set_xlabel('Sobol Index (St)',fontsize=9)
            axes[gridnum].set_ylabel('')
            #axes[gridnum].yaxis.set_ticklabels('')
            axes[gridnum].xaxis.set_tick_params(which='both', labelbottom=True)
            gridnum+=1
            x+=1

    fig.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\Sobol_Offshore'+variable+'.tiff',format='tiff',dpi=1000,bbox_inches='tight',)
    plt.show()

def plotonshore(dataframe,variable,dict_colours_simple):
    fig, axs = plt.subplots(1,3,figsize=(12,2),sharex=True,sharey=True)
    axes=[axs[0],axs[1],axs[2]]
    gridnum=0
    titlelabels=['A','B','C','D','E','F','G','H','I']
    mask = dataframe['Legend'].isin(['Offshore Wind Floating, Onshore','Offshore Wind Fixed, Onshore','UKCS, Onshore'])
    dataframe = dataframe[mask]
    for col in dataframe.select_dtypes(include='number').columns:
        #print(col)
        if col not in importantvariables(dataframe):
            #print(col)
            dataframe.drop(col,axis=1,inplace=True)
            
    for name,group in dataframe.groupby('Legend'):
        #print(name)
        if group['Energy Source'].unique()[0] in ('UKCS', 'Offshore Wind Fixed','Offshore Wind Floating'):
            group = pd.melt(group,id_vars = ['H2 Prod Infra','H2 Prod Method','T vector','T Infra','Energy Source','Legend'],value_vars=importantvariables(dataframe),var_name='Variable',value_name='Sobol Index (St)')
            group['Variable'] = group['Variable'].map(labels_forplot)
            sb.boxplot(y=group['Variable'],x=group['Sobol Index (St)'],width = 0.6,color=dict_colours_simple[name],whis=[5,95],linewidth=1,ax=axes[gridnum],showfliers=False)
            #axes[gridnum].set_yticks(axes[gridnum].get_yticks(),[textwrap.fill(label,15) for label in cols],fontsize=14)
            axes[gridnum].tick_params(labelrotation=0)
            axes[gridnum].set_title(titlelabels[gridnum]+': '+str(name),wrap=True)
            axes[gridnum].set_xlabel('Sobol Index (St)',fontsize=9,wrap=True)
            axes[gridnum].set_ylabel('')
            axes[gridnum].xaxis.set_tick_params(which='both', labelbottom=True)
            gridnum+=1
    fig.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\Sobol_Onshore'+variable+'.tiff',format='tiff',dpi=1000,bbox_inches='tight',)
    plt.show()
    plot(df_all_paths,variable)


