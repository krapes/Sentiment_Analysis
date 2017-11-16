# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 23:35:08 2017

@author: KRapes

Supervised learning
"""

import exploring
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import  AdaBoostClassifier
import Gaussian_hyperpara_selection
import time
import random


def print_messages(df):
    try:
        cgroups = range(2)
        for cgroup in cgroups:
            print("Messages from group {}".format(cgroup))
            for message in df.groupby('prediction').get_group(cgroup).text.head(5):
                print(message)
            print("")
    except:
        print("Only one group")

def save_messages(df):
    df = df[['text', 'prediction']]
    for i in range(2):
        exploring.save_obj(df.groupby('prediction').get_group(i), 'Group_' + str(i))
    

df = exploring.prepare_df_labeled()     
df_training = df[df.cluster != -1]
df = df[df.cluster == -1]

X_train, X_test, y_train, y_test = train_test_split(list(df_training.features),
                                                    list(df_training.cluster),
                                                    test_size=0.5)

best = {'score': 0, 'parameters': {}}
best_overall = {'score': 0 , 'clf': None}
names = ["NerualNet", "DecisionTree", "AdaBoost", "GaussianProcess"]

parameters_SVC = {"hidden_layer_sizes": [25, 500], "alpha": [0,1.0]}
parameters_DT = {"max_depth": [3, 100], "min_samples_split": [2, 20],"min_samples_leaf": [1, 20]}
parameters_Ada = {"n_estimators": [25, 100],"learning_rate": [0,1.0] }
parameters_Gauss = {}

parameters = [parameters_SVC, parameters_DT, parameters_Ada, parameters_Gauss]

clfs = [MLPClassifier( max_iter=500),
        DecisionTreeClassifier(),
        AdaBoostClassifier(),
        GaussianProcessClassifier(1.0 * RBF(1.0))]


def run_clf(clf, **kwargs):
    clf.set_params(**kwargs)
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    return score


for name, parameters, clf in zip(names, parameters, clfs):
    start = time.time()
    findings = {}
    best = {'score': 0}
    for _ in range(200):
        try:
            kwargs = Gaussian_hyperpara_selection.next_values(parameters, findings)
            # A random value is added to increase resolution and avoid lost combinations because of similar scores
            score = run_clf(clf, **kwargs) + random.random()/1000
            findings[score] = kwargs
            if score > best['score']:
                best['score'] = score
                best['parameters'] = findings[max(findings)]
                best['clf'] = clf
            if (time.time() - start) > 5:
                start = time.time()
                print("BREAK FOR TIME")
                break
        except:
            break
                                                                                     
    print("Best Score for the {} classifier:   {}".format(name, round(run_clf(clf, **best['parameters']),2)))
    if best['score'] > best_overall['score']:
        best_overall['score'] = best['score']
        best_overall['clf'] = best['clf']
        
print(best_overall)
predictions = clf.predict(list(df.features))
df['prediction'] = predictions
print_messages(df)
save_messages(df)


#os.remove('df.pkl')
#os.remove('vocabulary.pkl')