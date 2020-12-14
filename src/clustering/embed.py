import umap
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

pd.options.mode.chained_assignment = None  

class Embed(object):
    def __init__(self, dfHH, outDim = 2 , topk = None, ratio = None, inDim=None, nCluster=None):
        if ratio is not None:  dfHH = dfHH[dfHH['ra']<ratio] 
        self.ratio = ratio 
        self.dfHH = dfHH
        self.ftr = None
        self.nCluster = None
        self.kmap = None
        self.outDim = outDim
        self.matUMAP = None

        self.init(inDim, nCluster)

    def init(self, inDim, nCluster):
        ftrLen = np.where(self.dfHH.columns == "HH")[0][0]
        if inDim is not None:  assert inDim == ftrLen
        self.ftr = self.dfHH.columns[:ftrLen]
        self.nCluster = nCluster or 10

    def run(self):
        self.get_umapT()
        self.get_cluster()

    def get_umapT(self):
        umapT = umap.UMAP(n_components=self.outDim, min_dist=0.0, n_neighbors=50, random_state=926)
        self.matUMAP = umapT.fit_transform(self.dfHH[self.ftr].values)
        for i in range(self.outDim):
            self.dfHH[f'u{i+1}'] = pd.Series(self.matUMAP[:,i], index=self.dfHH.index)
        self.umapT = umapT

    def get_mapped(self, df, ftr):
        matUMAPED=self.umapT.transform(df[ftr])
        for i in range(self.outDim):   
            df[f'u{i+1}'] = pd.Series(matUMAPED[:,i], index=df.index)
        return df

    def get_cluster(self):
        self.kmap = KMeans(n_clusters=self.nCluster, n_init=30, algorithm='elkan',random_state=926)
        self.kmap.fit(self.matUMAP, sample_weight = None)
        self.dfHH[f'k{self.nCluster}'] = pd.Series(self.kmap.labels_+1, index=self.dfHH.index)

    def get_clustered(self, df, ftr):
        matKMAPED=self.kmap.transform(df[ftr])
        df[f'k{self.nCluster}'] = pd.Series(matKMAPED, index=self.dfHH.index)
        return df




# def get_freq_aug(df):
#     freq=df['freq'].values
#     df['FN']=freq/freq[-1]
#     df['FR']=df['FN'].apply(lambda x: 1+np.floor(np.log2(x)))
# #     df['RR']=1+np.floor(np.log2(freq/freq[-1]))
#     return freq

# def get_aug_pd(df,ftr,mode='FR'):
#     data=df[ftr].values   
#     freqN =df[mode].values
#     freqInt=freqN.astype('int')
#     plt.figure(figsize=(5,5))
#     _=plt.hist(freqInt,bins=freqInt[0])  
#     data_aug=data[0]
#     freq_list=[]
#     np.random.seed(112)
#     for ii, da in enumerate(data[1:]):
#         freqInt_ii=freqInt[ii]
#         freq_list+=[freqInt_ii]*freqInt_ii
#         randmat=np.random.rand(freqInt_ii,pca_comp)-0.5
#         da_aug = da+0.25*randmat
#         assert np.sum(np.round(da_aug)-da)<0.001
#         data_aug=np.vstack((data_aug,da_aug))
#     data_aug=data_aug[1:]
#     print(data_aug.shape,len(freq_list))
#     aug_pd=pd.DataFrame(data_aug, columns=list(range(pca_comp)))
#     aug_pd['freqInt']=freq_list
#     aug_pd['freq']=aug_pd['freqInt'].apply(lambda x: float(x))    
#     return aug_pd