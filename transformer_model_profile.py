# -*- coding: utf-8 -*-
"""Transformer_model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12impz0p1O5wB0uNeqdPWv2gwnIGYnCCj
"""

#imports
#$ git clone https://github.com/dmis-lab/biobert.git
#$ cd biobert; pip install -r requirements.txt
!pip install transformers
#!pip3 install torch torchvision
!pip install texthero -U
import texthero as hero
import pandas as pd

df = pd.read_csv("Penn_State_Posts_test_data.csv")

df = df[0:17200]
col = ['body_anonymised', 'Category: body_anonymised']
data = df[col]
col_profile = ['profile_bio_anonymised', 'Category: profile_bio_anonymised']
profile_data = df[col_profile]

data.dropna(inplace=True)
profile_data.dropna(inplace=True)

data['Category: body_anonymised'].unique()
profile_data['Category: profile_bio_anonymised'].unique()

data['body_anonymised'] = data['body_anonymised'].astype(str)
profile_data['profile_bio_anonymised'] = profile_data['profile_bio_anonymised'].astype(str)

import seaborn as sns
sns.set_style('whitegrid')
import matplotlib.pyplot as plt

sns.countplot(data['Category: body_anonymised'])
plt.title('Label Count')
plt.xticks(rotation = 90)
data['Category: body_anonymised'].value_counts()

sns.countplot(profile_data['Category: profile_bio_anonymised'])
plt.title('Label Count')
plt.xticks(rotation = 90)
profile_data['Category: profile_bio_anonymised'].value_counts()

data['clean_text'] = hero.clean(data['body_anonymised'])
profile_data['clean_text'] = profile_data['Category: profile_bio_anonymised']

data['clean_text_length'] = data['clean_text'].apply(lambda x: len(x))
profile_data['clean_text_length'] = profile_data['clean_text'].apply(lambda x: len(x))

#StopwordRemoval
from nltk.corpus import stopwords

STOPWORDS = set(stopwords.words('english'))
def remove_stopwords(body_anonymised):
    return " ".join([word for word in str(body_anonymised).split() if word not in STOPWORDS])

df["body_anonymised"] = df["body_anonymised"].apply(lambda body_anonymised: remove_stopwords(body_anonymised))

def remove_stopwords(profile_bio_anonymised):
    return " ".join([word for word in str(profile_bio_anonymised).split() if word not in STOPWORDS])

df["profile_bio_anonymised"] = df["profile_bio_anonymised"].apply(lambda profile_bio_anonymised: remove_stopwords(profile_bio_anonymised))

#create list of words
words_to_remove = ['x', 'n', 'hope', 'would', 'like', 'hi', "n'","'"]

#thank and thanks, treatment and treatments, 
def remove_words(text):
    text = text.replace('thanks','thank')
    text = text.replace('treatments','treatment')
    text = " ".join([word for word in text.split() if word not in words_to_remove])
    return text

data['clean_text'] = data['clean_text'].apply(lambda x: remove_words(x))
profile_data['clean_text'] = profile_data['clean_text'].apply(lambda x: remove_words(x))

# Lemmatizer
import nltk
nltk.download('wordnet')
wn = nltk.WordNetLemmatizer()

def lemmatizer(text):
    text= [wn.lemmatize(word) for word in text.split()]
    text = ' '.join(text)
    return text

data['clean_lem'] = data['clean_text'].apply(lambda x: lemmatizer(x))
profile_data['clean_lem'] = profile_data['clean_text'].apply(lambda x: lemmatizer(x))

data.head()

#from transformers import AutoTokenizer, AutoModel
#tokenizer = AutoTokenizer.from_pretrained("dmis-lab/biobert-v1.1")
#model = AutoModel.from_pretrained("dmis-lab/biobert-v1.1")
#tokens = tokenizer("body_anonymised")

import numpy as np
from sklearn import preprocessing
#classes = ['stage 1A', 'stage 1B/2/3A(Resectable)', 'stage 3A/3B(Unresectable)', 'stage 3B/4', 'unknown']
#unique_classes = np.unique(classes)
#unique_classes
#array(['stage 1A', 'stage 1B/2/3A(Resectable)', 'stage 3A/3B(Unresectable)', 'stage 3B/4', 'unknown'], dtype='<U6')
#class_map = {cls: idx for idx, cls in enumerate(unique_classes)}
#class_map
#{'stage 1A': 0, 'stage 1B/2/3A(Resectable)': 1, 'stage 3A/3B(Unresectable)': 2, 'stage 3B/4': 3, 'unknown': 4}

#Encode target labels with numerical values
le = preprocessing.LabelEncoder()
data['Category: body_anonymised'] = data['Category: body_anonymised'].astype(str)
data['label_int'] = le.fit_transform(data['Category: body_anonymised'])

le2 = preprocessing.LabelEncoder()
profile_data['Category: profile_bio_anonymised'] = profile_data['Category: profile_bio_anonymised'].astype(str)
profile_data['label_int'] = le.fit_transform(profile_data['Category: profile_bio_anonymised'])

#!pip install biobert-embedding==0.1.2 torch==1.2.0 -f https://download.pytorch.org/whl/torch_stable.html
#from biobert_embedding.embedding import BiobertEmbedding
import torch
from transformers import AutoTokenizer, AutoModel, AutoModelForSequenceClassification
from transformers import BertTokenizerFast, BertForSequenceClassification
from transformers import Trainer, TrainingArguments

# the model to train, base uncased BERT
#model_name = "google/bert_uncased_L-12_H-768_A-12"
#model_name = "dmis-lab/biobert-v1.1"
#model_name = "allenai/scibert_scivocab_uncased"

# max sequence length for each input
max_length = 512

data.head()

#Bert
#Load Tokenizer
#tokenizer = BertTokenizerFast.from_pretrained(model_name, do_lower_case=True, use_fast = True)

#Loading pretrained model and specify number of labels
#model = BertForSequenceClassification.from_pretrained(model_name, num_labels = 5)

#BioBert
#tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=True, use_fast = True)
#model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels = 5)

#SciBert
#tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=True, use_fast = True)

#model = BertForSequenceClassification.from_pretrained(model_name, num_labels = 5)

# Our data should be a list
body_text = list(data['body_anonymised'])
labels = list(data['label_int'])

profile_bio = list(profile_data['profile_bio_anonymised'])
labels2 = list(profile_data['label_int'])

# split into training & testing set
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(body_text, labels, test_size=0.3)

X_train, X_test, y_train, y_test = train_test_split(profile_bio, labels2, test_size=0.3)

# Tokenizing X_train and X_test
#Look up stride(n_stride or docstride) - more context for overflowed text
X_train_tokenized = tokenizer(X_train,
                              padding=True,
                              truncation=True,
                              max_length=max_length)

X_test_tokenized = tokenizer(X_test,
                              padding=True,
                              truncation=True,
                              max_length=max_length)

#testing different keys
X_train_tokenized['attention_mask'][0][0:10]

X_train_tokenized['input_ids'][0][0:10]

#Transforming dataset into torch tensors
#self default class, 
class CancerDataset(torch.utils.data.Dataset): 
  def __init__(self, encodings, labels):
    self.encodings = encodings
    self.labels = labels
  
  def __len__(self):
    return len(self.encodings['input_ids'])

  def __getitem__(self, idx):
    item = {key:torch.tensor(val[idx]) for key,val in self.encodings.items()}
    item['labels'] = torch.tensor(self.labels[idx])
    return item

#pass in encodings and pass in training labels
#converting x train and x test into torch tensors to load into model
train_dataset = CancerDataset(X_train_tokenized, y_train)
test_dataset = CancerDataset(X_test_tokenized, y_test)

#train_dataset[2]

#training arguments
#56, 64 batch size, epoch between 2-6(most impact), learning rate 1e-4 to 1e-5
#output directory, evaluation at the end of each epoch, batch size, number of epochs, 
args = TrainingArguments(
    output_dir="output",
    overwrite_output_dir =True,
    evaluation_strategy="epoch",
    eval_steps=1,
    per_device_train_batch_size=32,
    per_device_eval_batch_size=32,
    num_train_epochs=4,
    save_steps=1,
    save_strategy="epoch",
    learning_rate=5e-5,
    seed=0,
    )

#Passing model, arguments, train and test data into trainer
trainer = Trainer(model=model,
                  args=args,
                  train_dataset=train_dataset,
                  eval_dataset=test_dataset
                  )

#Train model
trainer.train()

# Model predictions
y_pred=trainer.predict(test_dataset)

#y_pred

from sklearn.metrics import classification_report, confusion_matrix

#softmax probabilties
#argmax looks for the highest probability and returns index
y_pred_fix = np.argmax(y_pred[0], axis = 1)

#looking at first 5 values
y_pred_fix[0:5]

#Print classification report and confusion matrix 
print(classification_report(y_test,y_pred_fix))
print(confusion_matrix(y_test,y_pred_fix))

# Commented out IPython magic to ensure Python compatibility.
#plotting confusion matrix
# %matplotlib inline  
import itertools

cm = confusion_matrix(y_true=y_test, y_pred=y_pred_fix)

def plot_confusion_matrix(cm, classes, 
                          normalize=False, 
                          title='Confusion matrix', 
                          cmap=plt.cm.Blues):


  plt.imshow(cm, interpolation='nearest', cmap=cmap)
  plt.title(title)
  plt.colorbar()
  tick_marks = np.arange(len(classes))
  plt.xticks(tick_marks, classes, rotation=-90)
  plt.yticks(tick_marks, classes)

  if normalize:
    cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
    print("Normalized confusion matrix")
  else:
    print(cm)

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
      plt.text(j, i, cm[i, j],
             horizontalalignment="center",
             color="white" if cm[i, j] > thresh else "black")
    
    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label', rotation=-90 )
    plt.figure(figsize= (60,60))

cm_plot_labels = ['stage 1A', 'stage 1B/2/3A(Resectable)', 'stage 3A/3B(Unresectable)', 'stage 3B/4', 'unknown']
plot_confusion_matrix(cm=cm, classes=cm_plot_labels, title='Confusion Matrix')

#SciBERT transformer

#Load pretrained model/tokenizer
#model_class, tokenizer_class, pretrained_weights = (ppb.BertModel, ppb.BertTokenizer, 'bert-base-uncased')

# Load pretrained model/tokenizer
#tokenizer = tokenizer_class.from_pretrained(pretrained_weights)
#model = model_class.from_pretrained(pretrained_weights)
