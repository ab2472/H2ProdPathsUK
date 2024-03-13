
import matplotlib.pyplot as plt
import seaborn as sb
import pandas as pd
import pickle
from plots import dict_colours,dict_markers
import os

    
def importantvariables(combined_df):
    cols = [col for col in combined_df.select_dtypes(include='number').columns]
    important_cols = [col for col in cols if combined_df[col].max() > 0.05]
    return important_cols

def plot(dataframe,variable):
    fig, axs = plt.subplots(3,3,gridspec_kw={'hspace':0.3,'wspace':0.1},figsize=(20,18),sharex=True,sharey=True)
    axes=[axs[1,0],axs[2,0],axs[0,0],axs[1,1],axs[2,1],axs[0,1],axs[1,2],axs[2,2],axs[0,2]]#,axs[0,1],axs[1,1],axs[2,1],axs[0,2],axs[1,2],axs[2,2]]
    gridnum=0
    titlelabels=['D','G','A','E','H','B','F','I','C']
    for col in dataframe.select_dtypes(include='number').columns:
        #print(col)
        if col not in importantvariables(dataframe):
            #print(col)
            dataframe.drop(col,axis=1,inplace=True)
            
    for name,group in dataframe.groupby('Legend'):
        #print(name)
        if group['Energy Source'].unique()[0] in ('UKCS', 'Offshore Wind Fixed','Offshore Wind Floating'):
            group = pd.melt(group,id_vars = ['H2 Prod Infra','H2 Prod Method','T vector','T Infra','Energy Source','Legend'],value_vars=importantvariables(dataframe),var_name='Variable',value_name='Sobol Index (St)')
            sb.boxplot(y=group['Variable'],x=group['Sobol Index (St)'],width = 0.6,color=dict_colours[name],whis=[5,95],linewidth=1,ax=axes[gridnum],showfliers=False)
            #axes[gridnum].set_yticks(axes[gridnum].get_yticks(),[textwrap.fill(label,15) for label in cols],fontsize=14)
            axes[gridnum].tick_params(labelrotation=0)
            axes[gridnum].set_title(titlelabels[gridnum]+': '+str(name),size=15)
            axes[gridnum].set_xlabel('Sobol Index (St)',fontsize=13)
            axes[gridnum].set_ylabel('')
            #axes[gridnum].yaxis.set_ticklabels('')
            axes[gridnum].xaxis.set_tick_params(which='both', labelbottom=True,labelsize=12)
            gridnum+=1
          
    
    fig.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\Sobol_Offshore'+variable+'.svg',format='svg',dpi=600)
    plt.show()

def plotonshore(dataframe,variable):
    fig, axs = plt.subplots(1,3,gridspec_kw={'hspace':0.2,'wspace':0.1},figsize=(20,2),sharex=True,sharey=True)
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
            sb.boxplot(y=group['Variable'],x=group['Sobol Index (St)'],width = 0.6,color=dict_colours[name],whis=[5,95],linewidth=1,ax=axes[gridnum],showfliers=False)
            #axes[gridnum].set_yticks(axes[gridnum].get_yticks(),[textwrap.fill(label,15) for label in cols],fontsize=14)
            axes[gridnum].tick_params(labelrotation=0)
            axes[gridnum].set_title(titlelabels[gridnum]+': '+str(name),size=15)
            axes[gridnum].set_xlabel('Sobol Index (St)',fontsize=13)
            axes[gridnum].set_ylabel('')
            axes[gridnum].xaxis.set_tick_params(which='both', labelbottom=True,labelsize=12)
            gridnum+=1
    fig.tight_layout()
    plt.savefig(os.getcwd()+'\\Figures\\Sobol_Onshore'+variable+'.svg',format='svg',dpi=600)
    plt.show()

for variable in ('CO2e','Energy'):
    df_all_paths = pd.read_csv(os.getcwd()+'\\CSV Results\\Sobolcombineddfs_all_'+variable+'.csv')  
    #delete unnamed column which is the path number but is not required as path legend used to plot
    df_all_paths.drop(df_all_paths.columns[df_all_paths.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)
    plotonshore(df_all_paths,variable)
    plot(df_all_paths,variable)


