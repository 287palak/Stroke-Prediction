# -*- coding: utf-8 -*-
"""

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iDS2VL04pCY6mWFucBU4_RHObISlQ1Ds

#PRML Course Project
Topic: Stroke Prediction  
Name: Palak Singh, Sakshi Todi  
Roll no: B20EE086, B20EE088

###Importing libraries
"""

# For ML models
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
from sklearn.svm import SVC ,SVR
from sklearn.metrics import f1_score, confusion_matrix, accuracy_score, classification_report
from sklearn.model_selection import GridSearchCV
# For Data Processing
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split 
# For Data Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Miscellaneous
import os
import random
import numpy as np
import pandas as pd
import seaborn as sns

"""##Pre processing

"""

data = pd.read_csv("/content/healthcare-dataset-stroke-data.csv")
data.head()

data.info()

"""##Descriptive data analysis"""

# Drop the id column
data.drop(columns=['id'], inplace=True)

#bmi has null values which are being replaced by meanvalues of the data
data['bmi'] = data['bmi'].fillna(data['bmi'].mean())

#continous data
data.describe()[1:][['age','avg_glucose_level','bmi']]

#normalizing the numerical attributes
# Create a new column for normalized age
data['age_norm']=(data['age']-data['age'].min())/(data['age'].max()-data['age'].min())

# Create a new column for normalized avg glucose level
data['avg_glucose_level_norm']=(data['avg_glucose_level']-data['avg_glucose_level'].min())/(data['avg_glucose_level'].max()-data['avg_glucose_level'].min())

# Create a new column for normalized bmi
data['bmi_norm']=(data['bmi']-data['bmi'].min())/(data['bmi'].max()-data['bmi'].min())

data.head()

# Discretize with respective equal-width bin
data['age_binned'] = pd.cut(data['age'], np.arange(0, 91, 5))
data['avg_glucose_level_binned'] = pd.cut(data['avg_glucose_level'], np.arange(0, 301, 10))
data['bmi_binned'] = pd.cut(data['bmi'], np.arange(0, 101, 5))

data.head()

#categorical data
columns=['gender','work_type','smoking_status','ever_married']
for i in columns:
    print("Total no of unique keys in", i, data[i].nunique())

data.gender.unique()

data.work_type.unique()

data.smoking_status.unique()

fig = make_subplots(
    rows=4, cols=2, subplot_titles=("gender", "hypertension","heart_disease","ever_married","work_type", "Residence_type",'smoking_status', 'stroke'),
    specs=[[{"type": "domain"}, {"type": "domain"}],
           [{"type": "domain"}, {"type": "domain"}],
           [{"type": "domain"}, {"type": "domain"}],
           [{"type": "domain"}, {"type": "domain"}]],
)


colours = ['#4285f4', '#ea4335', '#fbbc05', '#34a853']

fig.add_trace(go.Pie(labels=np.array(data['gender'].value_counts().index),
                     values=[x for x in data['gender'].value_counts()],
                     textinfo='label+percent', rotation=-45, hole=.35,
                     marker_colors=colours),
              row=1, col=1)

fig.add_trace(go.Pie(labels=np.array(data['hypertension'].value_counts().index),
                     values=[x for x in data['hypertension'].value_counts()],
                     textinfo='label+percent', hole=.35,
                     marker_colors=colours),
              row=1, col=2)

fig.add_trace(go.Pie(labels=np.array(data['heart_disease'].value_counts().index),
                     values=[x for x in data['heart_disease'].value_counts()],
                     textinfo='label+percent', rotation=-45, hole=.35,
                     marker_colors=colours),
              row=2, col=1)

fig.add_trace(go.Pie(labels=np.array(data['ever_married'].value_counts().index),
                     values=[x for x in data['ever_married'].value_counts()],
                     textinfo='label+percent', rotation=-45, hole=.35,
                     marker_colors=colours),
              row=2, col=2)

fig.add_trace(go.Pie(labels=np.array(data['work_type'].value_counts().index),
                     values=[x for x in data['work_type'].value_counts()],
                     textinfo='label+percent', hole=.35,
                     marker_colors=colours),
              row=3, col=1)

fig.add_trace(go.Pie(labels=np.array(data['Residence_type'].value_counts().index),
                     values=[x for x in data['Residence_type'].value_counts()],
                     textinfo='label+percent', hole=.35,
                     marker_colors=colours),
              row=3, col=2)

fig.add_trace(go.Pie(labels=np.array(data['smoking_status'].value_counts().index),
                     values=[x for x in data['smoking_status'].value_counts()],
                     textinfo='label+percent', rotation=-45, hole=.35,
                     marker_colors=colours),
              row=4, col=1)

fig.add_trace(go.Pie(labels=np.array(data['stroke'].value_counts().index),
                     values=[x for x in data['stroke'].value_counts()],
                     rotation=-45, textinfo='label+percent', hole=.35,
                     marker_colors=colours),
              row=4, col=2)

fig.update_layout(height=2000, font=dict(size=14), showlegend=False)

fig.show()

fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12, 10))
data.plot(kind="hist", y="age", bins=70, color="b", ax=axes[0][0])
data.plot(kind="hist", y="bmi", bins=100, color="r", ax=axes[0][1])
data.plot(kind="hist", y="heart_disease", bins=6, color="g", ax=axes[1][0])
data.plot(kind="hist", y="avg_glucose_level", bins=100, color="orange", ax=axes[1][1])
plt.show()

"""##exploratory data analysis"""

# Create the correlation heatmap
heatmap = sns.heatmap(data[['age_norm', 'avg_glucose_level_norm', 'bmi_norm']].corr(), vmin=-1, vmax=1, annot=True)
heatmap.set_title('Correlation Heatmap')

def get_stacked_bar_chart(column):
    # Get the count of records by column and stroke    
    df_pct = data.groupby([column, 'stroke'])['age'].count()
    # Create proper DataFrame's format
    df_pct = df_pct.unstack()    
    return df_pct.plot.bar(stacked=True, figsize=(6,6), width=1);

def get_100_percent_stacked_bar_chart(column, width = 0.5):
    # Get the count of records by column and stroke
    df_breakdown = data.groupby([column, 'stroke'])['age'].count()
    # Get the count of records by gender
    df_total = data.groupby([column])['age'].count()
    # Get the percentage for 100% stacked bar chart
    df_pct = df_breakdown / df_total * 100
    # Create proper DataFrame's format
    df_pct = df_pct.unstack()
    return df_pct.plot.bar(stacked=True, figsize=(6,6), width=width);

get_stacked_bar_chart(data['age_binned'])
get_100_percent_stacked_bar_chart(data['age_binned'], width = 1)

get_stacked_bar_chart(data['bmi_binned'])
get_100_percent_stacked_bar_chart(data['bmi_binned'], width = 1)

get_stacked_bar_chart(data['avg_glucose_level_binned'])
get_100_percent_stacked_bar_chart(data['avg_glucose_level_binned'], width = 0.9)

get_100_percent_stacked_bar_chart(data['hypertension'])
get_100_percent_stacked_bar_chart(data['heart_disease'])
get_100_percent_stacked_bar_chart(data['gender'])
get_100_percent_stacked_bar_chart(data['Residence_type'])

get_100_percent_stacked_bar_chart(data['work_type'])
data.groupby(['work_type'])[['age']].agg(['count', 'mean'])

get_100_percent_stacked_bar_chart(data['ever_married'])
data.groupby(['ever_married'])[['age']].agg(['count', 'mean'])

"""##data cleaning"""

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
data['gender'] = le.fit_transform(data['gender'])
data['ever_married'] = le.fit_transform(data['ever_married'])
data['work_type'] = le.fit_transform(data['work_type'])
data['Residence_type'] = le.fit_transform(data['Residence_type'])
data['smoking_status'] = le.fit_transform(data['smoking_status'])

'''data = pd.get_dummies(data, columns=['gender', 'ever_married', 'work_type', 'Residence_type','smoking_status'],drop_first=True)'''

data.columns

data.drop(columns=['age', 'heart_disease', 'avg_glucose_level', 'bmi',
       'age_binned', 'avg_glucose_level_binned', 'bmi_binned'], inplace=True)

'''data.drop(columns=['age_binned', 'avg_glucose_level_binned', 'bmi_binned'], inplace=True)'''

data.head()

data.shape

"""##data division

"""

from sklearn.feature_selection import SelectKBest, f_classif

classifier = SelectKBest(score_func=f_classif,k=5)
fits = classifier.fit(data.drop('stroke',axis=1),data['stroke'])
x=pd.DataFrame(fits.scores_)
columns = pd.DataFrame(data.drop('stroke',axis=1).columns)
fscores = pd.concat([columns,x],axis=1)
fscores.columns = ['Attribute','Score']
fscores.sort_values(by='Score',ascending=False)

cols=fscores[fscores['Score']>50]['Attribute']
print(cols)

x_train,x_test,y_train,y_test=train_test_split(data[cols],data['stroke'],random_state=1255,test_size=0.25)
#Splitting data
x_train.shape,x_test.shape,y_train.shape,y_test.shape
# Shape of data

"""As we know, our dataset is imbalanced. So to balance our data we have used SMOTE method. It will populate our data with records similar to our minor class. Usually, we perform this on the whole dataset but as we have very fewer records of minor class I am applying it on both train and test data. Earlier I tried doing it by just resampling data of the training dataset but it didn’t perform that well so I tried this approach and got a good result."""

from imblearn.over_sampling import SMOTE
smote=SMOTE()
x_train,y_train=smote.fit_resample(x_train,y_train)
x_test,y_test=smote.fit_resample(x_test,y_test)

print(x_train.shape,y_train.shape,x_test.shape,y_test.shape)

"""#Models"""

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

"""##1.XGB"""

xgc=XGBClassifier(objective='binary:logistic',n_estimators=1000,max_depth=5,learning_rate=0.001,n_jobs=-1)
xgc.fit(x_train,y_train)
predict=xgc.predict(x_test)
print('Accuracy --> ',accuracy_score(predict,y_test))
print('F1 Score --> ',f1_score(predict,y_test))
print('Classification Report  --> \n',classification_report(predict,y_test))

from sklearn.model_selection import RandomizedSearchCV
params1={ "learning_rate": [0.001,0.01,0.02,0.03,0.04,0.05,0.10,0.15, 0.20, 0.25, 0.30, 0.40,0.6,0.7,0.8,0.9,0.99 ],
        "max_depth":[3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], 
        "min_child_weight":[0.06,1,2,3,4,5,6,7,8,9], 
        "gamma":[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
        "colsample_bytree":[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
         "n_estimators": [80, 100, 120]}
classifier1=XGBClassifier()
random_search1=RandomizedSearchCV(classifier1,param_distributions=params1,n_iter=5,scoring='roc_auc',n_jobs=-1,cv=5,verbose=3)
random_search1.fit(x_train,y_train)
random_search1.best_estimator_

model1_new = XGBClassifier(colsample_bytree=0.9, gamma=0.6, learning_rate=0.25, max_depth=13,
              min_child_weight=0.06, n_estimators=80)
model1_new.fit(x_train,y_train)
y_pre3 = model1_new.predict(x_test)

as1 = accuracy_score(y_pre3,y_test)
f1 = f1_score(y_pre3,y_test)
cf = classification_report(y_pre3,y_test)

print("accuracy score:", accuracy_score(y_pre3,y_test))
print("f1_score:" ,f1_score(y_pre3,y_test))
print('Classification Report  --> \n',classification_report(y_pre3,y_test))

"""##2.decision tree"""

DTC = DecisionTreeClassifier()
DTC.fit(x_train, y_train)
y_pred = DTC.predict(x_test)

print('Accuracy --> ',accuracy_score(y_pred,y_test))
print('F1 Score --> ',f1_score(y_pred,y_test))
print('Classification Report  --> \n',classification_report(y_pred,y_test))

"""###DTC with gridsearchcv"""

model_comparison = {}

'''parameters = {'max_depth': [11,12,13,14,15,16,17,18,17,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]}'''
parameters = {'criterion':["gini","entropy"], 'max_depth': [None,1,2,3,4,5,6], 'min_samples_split':[2,4,6,8,10], 'min_samples_leaf':[1,2,3,4,5,6], 'max_leaf_nodes': [None,1,2,3,4,5]}
Tree_model = DecisionTreeClassifier()
clf = GridSearchCV(Tree_model, parameters)
print("Searching for best hyperparameters ...")
clf.fit(x_train, y_train)
print(f'Best Hyperparameters: {clf.best_params_}')

y_pred = clf.predict(x_test)
model_comparison['DecisionTreeClassifier'] = [accuracy_score(y_test,y_pred), f1_score(y_test,y_pred, average='weighted')]
print('\n')
print(classification_report(y_test,y_pred, zero_division=1, digits=3))

DTC_new = DecisionTreeClassifier(criterion= 'entropy', max_depth= None, max_leaf_nodes= None, min_samples_leaf= 1, min_samples_split= 2)
DTC_new.fit(x_train, y_train)
y_pred = DTC_new.predict(x_test)

as2 = accuracy_score(y_pred,y_test)
f2 = f1_score(y_pred,y_test)
cf2 = classification_report(y_pred,y_test)

print('Accuracy --> ',accuracy_score(y_pred,y_test))
print('F1 Score --> ',f1_score(y_pred,y_test))
print('Classification Report  --> \n',classification_report(y_pred,y_test))

"""##3. Naive Bayes"""

clf = BernoulliNB()
clf = clf.fit(x_train,y_train)
y_pred2 = clf.predict(x_test)
print('Accuracy --> ',accuracy_score(y_pred2,y_test))
print('F1 Score --> ',f1_score(y_pred2,y_test))
print('Classification Report  --> \n',classification_report(y_pred2,y_test))

params2={ 'fit_prior':[True,False],'alpha':[0.01,0.1,0.9,1,1.5]}
classifier2=BernoulliNB()
random_search2=RandomizedSearchCV(classifier2,param_distributions=params2,n_iter=5,scoring='roc_auc',n_jobs=-1,cv=5,verbose=3)
random_search2.fit(x_train,y_train)
random_search2.best_estimator_

model4_new = BernoulliNB(alpha=0.1,fit_prior=False)
model4_new.fit(x_train,y_train)
y_pre4 = model4_new.predict(x_test)


as3 = accuracy_score(y_pre4,y_test)
f3 = f1_score(y_pre4,y_test)
cf3 = classification_report(y_pre4,y_test)

print("accuracy score:", accuracy_score(y_pre4,y_test))
print("f1_score:" ,f1_score(y_pre4,y_test))
print('Classification Report  --> \n',classification_report(y_pre4,y_test))

"""##4. Random Forest Classifier"""

from sklearn.ensemble import RandomForestClassifier as rfc
model1 = rfc()
model1.fit(x_train,y_train)
y_pred3 = model1.predict(x_test)
print('Accuracy --> ',accuracy_score(y_pred3,y_test))
print('F1 Score --> ',f1_score(y_pred3,y_test))
print('Classification Report  --> \n',classification_report(y_pred3,y_test))

'''parameters = {'max_depth': [11,12,13,14,15,16,17,18,17,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50]}'''
'''params2 = {'n_estimators': [80,100,120,140,160,180,200,220], 'max_depth':[None,2,3,6,8,10,12,14,16,18,20,22,24],'min_samples_split':[2,4,6,8,10], 'min_samples_leaf':[1,2,3,4,5,6],'max_samples':[None,0,1,2] }'''
params2 = { 'max_depth':[None,2,3,6,8,10,12,14,16,18,20,22,24],'min_samples_split':[2,4,6,8,10] }
model1 = rfc()
clf = GridSearchCV(model1, params2)
print("Searching for best hyperparameters ...")
clf.fit(x_train, y_train)
print(f'Best Hyperparameters: {clf.best_params_}')

y_pred = clf.predict(x_test)
model_comparison['DecisionTreeClassifier'] = [accuracy_score(y_test,y_pred), f1_score(y_test,y_pred, average='weighted')]
print('\n')
print(classification_report(y_test,y_pred, zero_division=1, digits=3))

model5_new =rfc(max_depth= 22, min_samples_split= 4)
model5_new.fit(x_train,y_train)
y_pre5 = model4_new.predict(x_test)


as5 = accuracy_score(y_pre5,y_test)
f5 = f1_score(y_pre5,y_test)
cf5 = classification_report(y_pre5,y_test)

print("accuracy score:", accuracy_score(y_pre5,y_test))
print("f1_score:" ,f1_score(y_pre5,y_test))
print('Classification Report  --> \n',classification_report(y_pre5,y_test))

"""##5.Light GBM"""

import lightgbm as lgb
model4 = lgb.LGBMClassifier()
model4.fit(x_train,y_train)
y_pred4 = model4.predict(x_test)
print('Accuracy --> ',accuracy_score(y_pred4,y_test))
print('F1 Score --> ',f1_score(y_pred4,y_test))
print('Classification Report  --> \n',classification_report(y_pred4,y_test))

params3={ "learning_rate": [None,0.001,0.01,0.02,0.03,0.04,0.05,0.10,0.15, 0.20, 0.25, 0.30, 0.40,0.6,0.7,0.8,0.9,0.99 ],
        "max_depth":[None,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], 
        "min_child_weight":[None,0.06,1,2,3,4,5,6,7,8,9], 
        "gamma":[None,0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
        "colsample_bytree":[None,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9],
         "n_estimators": [None,80, 100, 120]}
classifier3=lgb.LGBMClassifier()
random_search3=RandomizedSearchCV(classifier3,param_distributions=params3,n_iter=5,scoring='roc_auc',n_jobs=-1,cv=5,verbose=3)
random_search3.fit(x_train,y_train)
random_search3.best_estimator_

model5_new = lgb.LGBMClassifier(colsample_bytree=None, gamma=0.7, learning_rate=0.3,
               max_depth=11, min_child_weight=6, n_estimators=120)
model5_new.fit(x_train,y_train)
y_pre6 = model5_new.predict(x_test)

as6 = accuracy_score(y_pre6,y_test)
f6 = f1_score(y_pre6,y_test)
cf6 = classification_report(y_pre6,y_test)

print("accuracy score:", accuracy_score(y_pre6,y_test))
print("f1_score:" ,f1_score(y_pre6,y_test))
print('Classification Report  --> \n',classification_report(y_pre6,y_test))

"""#Evaluation of different models

###comparing different models
"""

Models = ['XGBoost Classifier','Decision Tree Classifier','Naive Bayes Classifier','Random Forest Classifier','LGBM Classifier']
ascore = [as1, as2, as3, as5,as6]
fscore = [f1, f2, f3, f5, f6]

plt.figure(figsize = (10, 5))
plt.title('Comparing Models based on Accuracy')
ax = plt.scatter(x = Models, y = ascore)
plt.xlabel('Models')
plt.ylabel('MSE')
plt.plot( Models,  ascore)

plt.figure(figsize = (10, 5))
plt.title('Comparing Models based on F1 score')
ax = plt.scatter(x = Models, y = fscore)
plt.xlabel('Models')
plt.ylabel('MSE')
plt.plot( Models,  fscore)

from sklearn.metrics import roc_curve
from sklearn import metrics

"""###model evaluation"""

#xgb
metrics.plot_roc_curve(model1_new, x_test, y_test)

#DTC
metrics.plot_roc_curve(DTC_new, x_test, y_test)

#naives bayes
metrics.plot_roc_curve(model4_new, x_test, y_test)

#random forest
metrics.plot_roc_curve(model5_new, x_test, y_test)

#lgbm
metrics.plot_roc_curve(model5_new, x_test, y_test)
