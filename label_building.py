# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 20:55:25 2017

@author: KRapes
Polling Supervised Learnt Algorthims to build labels
"""

import pandas as pd
import numpy as np
import exploring
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.ensemble import  AdaBoostClassifier
import random
from collections import Counter






df_labeled = pd.read_pickle('labeled.pkl')
for _ in range(100):
    df, features_master = exploring.preprocess_data()
    df["cluster"] = -1.0
    df_orgional = df.copy()
    
    df_ml = pd.read_pickle('machine_labeled.pkl')
    #df_ml = df_ml[df_ml.index == 0]
    print("Machine Labeled Messages Size: {}".format(len(df_ml[df_ml.cluster != -1])))
    
    for label in [df_labeled]:
        for i, row in label.iterrows():
            if row.text in list(df_orgional.text):
                idx = df_orgional.index[df['text'] == row.text]
                df_orgional.set_value(idx,'cluster', row.cluster)

    df_train =  df_orgional[df_orgional.cluster != -1]       
        
    X_trainO, X_testO, y_trainO, y_testO = train_test_split(list(df_train.features),
                                                        list(df_train.cluster),
                                                        test_size=0.75,
                                                        random_state=42)

    for label in [df_labeled, df_ml]:
        for i, row in label.iterrows():
            if row.text in list(df.text):
                idx = df.index[df['text'] == row.text]
                df.set_value(idx,'cluster', row.cluster)
    
    df_train =  df[df.cluster != -1]       
    df = df[df.cluster == -1]
    
    X_train, X_test, y_train, y_test = train_test_split(list(df_train.features),
                                                        list(df_train.cluster),
                                                        test_size=0.33,
                                                        random_state=42)
    
    names = ["Linear SVM",  "Neural Net", "AdaBoost"]
    
    classifiers = [
        SVC(kernel="linear", C=0.025),
        MLPClassifier(alpha=1),
        AdaBoostClassifier()]
    
    
    
    for name, clf in zip(names, classifiers):
            clf.fit(X_train, y_train)
            score = clf.score(X_test, y_test)
            print("Score for {} was {}".format(name, round(score,2)))
    for name, clf in zip(names, classifiers):
        score = clf.score(X_testO, y_testO)
        print("The real score for {} was {}".format(name, round(score,2)))
    
    indexes = random.sample(range(len(df)), int(len(df)*.75))       
    for i in indexes:
        message = df.iloc[i].features
        predictions = []
        for name, clf in zip(names, classifiers):
            predictions.append(clf.predict([message])[0])
        #prediction = Counter(predictions).most_common(1)[0][0]
        
        keys = list(Counter(predictions))
        if len(keys) <= 1:
            df.set_value(i,'cluster', keys[0])
    
    
    print(df.groupby('cluster').count())
    
    try:
        #df_mlp = pd.read_pickle('machine_labeled.pkl')
        df_ml = pd.concat([df, df_ml], axis=0, join='outer', ignore_index=True)
        df_ml = df_ml.drop_duplicates(subset='text', keep="first")
        df_ml.to_pickle('machine_labeled.pkl')
    except:
        df.to_pickle('machine_labeled.pkl')

try:
    cgroups = range(2)
    for cgroup in cgroups:
        print("Messages from group {}".format(cgroup))
        for message in df.groupby('cluster').get_group(cgroup).text.head(20):
            print(message)
        print("")
except:
    print("Only one group")
    
    


names = ["Linear SVM",  "Neural Net", "AdaBoost"]

classifiers = [
    SVC(kernel="linear", C=0.025),
    MLPClassifier(alpha=1),
    AdaBoostClassifier()]




        