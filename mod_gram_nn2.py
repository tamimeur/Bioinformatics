#import grn_feedfwd as ffn
import parse_input
import bandpass_simple3 as lab
import time
import numpy as np
from matplotlib import pyplot as plt
from keras.utils import np_utils
import keras.callbacks as cb
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop, SGD
from keras.datasets import mnist
from keras.layers import Merge
import random


class LossHistory(cb.Callback):
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        batch_loss = logs.get('loss')
        self.losses.append(batch_loss)


np.random.seed(1337)
X_train = []
Y_train = []

X_test = []
Y_test = []

def format_data(char_data, des):
	#global NN_inputs
	global X_train
	global Y_train
	
	inducer_conc = char_data[0]
	res_conc = char_data[1]

	inputs = [0]*len(des)

	#parts_in_list = []
	nnindex = 0
	for part in des:
		inputs[nnindex] = (T.index(part)) + 1
		nnindex += 1

	for inducer in inducer_conc:
		new_list = list(inputs)
		new_list.append(inducer)
		X_train.append(new_list)

	for val in res_conc:
		Y_train.append([val])

	return X_train, Y_train

############# GENERATE LANGUAGE ############

#The Grammar
Signals = ('s')
# T = ('p1','p2','p3','g0','g1','g2')
# NN_inputs = ['p1','p2','p3','g0','g1','g2']
T = ('p1','p3','g0','g1')
#NN_inputs = ['p3','g0']
NN_inputs = []
print "Neural N in struct = ", NN_inputs

#Productions
P = [ ('Design',           ['R']),                  \
('Design',          ['R','C']),                     \
#('Design',          ['C','C','R']),                 \
('C',               ['Prom', 'Gene']),              \
('R',               ['Prom', 'g0']),                \
('Prom',            ['p1']),                        \
#('Prom',            ['p2']),                        \
('Prom',            ['p3']),                        \
('Gene',            ['g1']),                        \
('Gene',            ['g2'])                         ]

language = parse_input.getLanguage(P,T)

print "Language = ", language
print "Num Designs = ", len(language)
# pred_design = ['p3','g2','p2','g1','p1','g0']
# language.remove(pred_design)
print "Language = ", language
print "Num Designs = ", len(language)
print "Longest design ", max(language, key=len)

############# GENERATE SINGLE CAS N.N. MODEL ############
start_time = time.time()
#num_inputs = len(T) + len(Signals)
#num_inputs = len(max(language, key=len)) + len(Signals)
num_inputs = 3
#num_hidden = num_inputs + (num_inputs/2)
num_hidden = 2
print 'num inputs = ', num_inputs
print 'num hidden units = ', num_hidden
print 'Compiling Model ... '
submodel = Sequential()
#model.add(Dense(num_hidden, input_dim=num_inputs)) #, init='zero'))
submodel.add(Dense(num_hidden, input_dim=num_inputs)) #, init='zero'))
submodel.add(Activation('sigmoid'))
submodel.add(Dropout(0.3))
submodel.add(Dense(1))
submodel.add(Activation('linear'))

rms = RMSprop()
#model.compile(loss='sparse_categorical_crossentropy', optimizer=rms)
sgd = SGD(lr=0.01)
#submodel.trainable = False
# model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
submodel.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
print 'Model compiled in {0} seconds'.format(time.time() - start_time)

print submodel.get_config()
############# RUN AGENT ############
#cur_design = ['p1','g0']

############# SINGLE-CAS FORMAT DATA ############

X_train = []
Y_train = []
sublanguage = [['p3','g0'],['p1','g0']]
cur_design = ['p3','g0']
sublanguage.remove(cur_design)
language.remove(cur_design)
#testi = 0
#cur_char_data = lab.get_data(cur_design, testi)
#X_train, Y_train = format_data(cur_char_data, cur_design)

testi = 0
langsize = int(len(sublanguage))
while testi<langsize:
	#print "Training with design ", cur_design
	cur_char_data = lab.get_data(cur_design, testi)
	X_train, Y_train = format_data(cur_char_data, cur_design)
	cur_design = random.choice(sublanguage)
	sublanguage.remove(cur_design)
	language.remove(cur_design)
	testi += 1


spliti = 0
for data in X_train:
	if spliti%2 == 0:
		X_test.append(data)
		X_train.remove(data)
	spliti += 1

spliti = 0
for out in Y_train:
	if spliti%2 == 0:
		Y_test.append(out)
		Y_train.remove(out)
	spliti += 1
print "TRAINING DATA X: ", X_train
print "Y: ", Y_train

##################### TRAIN SINGLE CAS MODEL #######################
submodel.fit(X_train, Y_train, nb_epoch=5000, batch_size=5, verbose=0)
pred_goal_beh = submodel.predict(X_test)
print "MODEL PREDICTS FOR GOALD DES ", pred_goal_beh
print "Tru output is ", Y_test

print "Weights = ", submodel.get_weights()
submodel.save_weights("submod.h5")

############## FREEZE SINGLE CAS MODEL - MAKE UNTRAINABLE ##########
#submodel.trainable = False
frzsubmodel = Sequential()
frzin = Dense(num_hidden, input_dim=num_inputs)
frzsubmodel.add(frzin)
frzin2 = Activation('sigmoid')
frzsubmodel.add(frzin2)
frzin3 = Dropout(0.3)
frzsubmodel.add(frzin3)
frzin.trainable = False
frzin2.trainable = False
frzin3.trainable = False
frzout = Dense(1)
frzsubmodel.add(frzout)
frzout2 = Activation('linear')
frzsubmodel.add(frzout2)
frzout.trainable = False
frzout2.trainable = False

frzsubmodel.load_weights("submod.h5")
#frzsubmodel.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
#print 'Model compiled in {0} seconds'.format(time.time() - start_time)

# print submodel.get_config()
print "\nFROZEN MODEL: "
print frzsubmodel.get_config()
# print "\n"
# print submodel.get_weights()
print "\n"
print frzsubmodel.get_weights()

#######Just a test to make sure it wouldnt update the weights######
#frzsubmodel.fit(X_train, Y_train, nb_epoch=5000, batch_size=5, verbose=1)
#print frzsubmodel.get_weights()

############## GENERATE DOUBLE CAS MERGED MODEL ####################
cas2model = Sequential()
#model.add(Dense(num_hidden, input_dim=num_inputs)) #, init='zero'))
cas2model.add(Dense(2, input_dim=2)) #, init='zero'))
cas2model.add(Activation('sigmoid'))
cas2model.add(Dropout(0.3))
cas2model.add(Dense(1))
cas2model.add(Activation('linear'))

#merged = Merge([frzsubmodel, cas2model], mode='concat', concat_axis=-1)
merged = Merge([frzsubmodel, cas2model], mode='sum')
fin_model = Sequential()
fin_model.add(merged)
fin_model.add(Dense(2, activation='sigmoid'))
fin_model.add(Dropout(0.5))
fin_model.add(Dense(1, activation='linear'))
# final_out = Dense(1, activation='linear')(merged_vector)
# fin_model = Model(input = [], output = final_out)
fin_model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
print "FINAL MODEL YO: "
print fin_model.get_config()
print "\n"
print fin_model.get_weights()

################ FORMAT DOUBLE CAS DATA ############################
X_train = []
Y_train = []

print "Remaining designs for training: ", language

testi = 1
langsize = int(len(language))
cur_design = random.choice(language)
language.remove(cur_design)
while testi<langsize:
	#print "Training with design ", cur_design
	cur_char_data = lab.get_data(cur_design, testi)
	X_train, Y_train = format_data(cur_char_data, cur_design)
	cur_design = random.choice(language)
	language.remove(cur_design)
	testi += 1
print "Pre split training data: ", X_train, Y_train

cas1_train = []
cas2_train = []
cas1_test = []
cas2_test = []
Y_test = []
for data in X_train:
	cas1_in = list([data[0],data[1],data[4]])
	cas1_train.append(cas1_in)
	#cas2_in = list([data[2],data[3],data[4]])
	cas2_in = list([data[2],data[3]])
	cas2_train.append(cas2_in)

print "cas1_train: ", cas1_train
print "cas2_train: ", cas2_train

spliti = 0
for data in cas1_train:
	if spliti%2 == 0:
		cas1_test.append(data)
		cas1_train.remove(data)
	spliti += 1

spliti = 0
for data in cas2_train:
	if spliti%2 == 0:
		cas2_test.append(data)
		cas2_train.remove(data)
	spliti += 1

spliti = 0
for out in Y_train:
	if spliti%2 == 0:
		Y_test.append(out)
		Y_train.remove(out)
	spliti += 1
print "TRAINING DATA X: ", cas1_train, cas2_train
print "Y: ", Y_train

##################### TRAIN DOUBLE CAS MODEL #######################
cas1_train = np.array(cas1_train)
cas2_train = np.array(cas2_train)
cas1_test = np.array(cas1_test)
cas2_test = np.array(cas2_test)

fin_model.fit([cas1_train, cas2_train], Y_train, nb_epoch=5000, batch_size=5, verbose=0)
finpred_goal_beh = fin_model.predict([cas1_test,cas2_test])
print "MODEL PREDICTS FOR GOALD DES ", finpred_goal_beh
print "Tru output is ", Y_test
print "Config:"
print fin_model.get_config()
print "Weigts:"
print fin_model.get_weights()