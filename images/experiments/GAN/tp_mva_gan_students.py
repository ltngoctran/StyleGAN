

import pdb
import matplotlib.pyplot as plt
import sys
import numpy as np
import pickle
import copy
import os

import tensorflow as tf
#config = tf.ConfigProto()
# #config.gpu_options.allow_growth = True
# config.gpu_options.per_process_gpu_memory_fraction = 0.3
# session = tf.Session(config=config)


from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten, Dropout, BatchNormalization, Activation, ZeroPadding2D
from keras.layers.advanced_activations import LeakyReLU
from keras.layers.convolutional import UpSampling2D, Conv2D, Conv2DTranspose
from keras.models import Sequential, Model, load_model
from keras.optimizers import Adam
from keras import backend as K
#from keras.backend.tensorflow_backend import set_session

class GAN():
	def __init__(self,dataset_name='mnist',load_model_name=''):
		
		optimizer = Adam(0.0002, 0.5)
		if (load_model_name == ''):
			X_train = self.load_gan_data(dataset_name)

			# default parameters for mnist 
			self.img_rows = X_train.shape[1]
			self.img_cols = X_train.shape[2]
			self.img_channels = X_train.shape[3]
			self.img_shape = (self.img_rows, self.img_cols, self.img_channels)
			self.z_dim = 32
			self.iter_count = 0
			self.dataset_name = dataset_name
			self.model_file = 'GAN_models/'+self.dataset_name+'_gan_model.pickle'#

			# Build and compile the discriminator and discriminator loss
			self.discriminator = self.build_discriminator()
			# set discriminator loss
			# BEGIN INSERT CODE
			self.discriminator.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])
			# END INSERT CODE 

			# Build the generator
			self.generator = self.build_generator()

		else:
			#load gan class and models (generator, discriminator and stacked model)
			self.load_gan_model(load_model_name)

		# Create the stacked model
		#first, create the random vector z in the latent space
		z = Input(shape=(self.z_dim,))
		#create generated (fake) image
		img = self.generator(z)

		#indicate that for the stacked model, the weights are not trained
		self.discriminator.trainable = False

		# The discriminator takes generated images as input and gives a probability of whether it is a true or
		#false image
		p_true = self.discriminator(img)

		# The combined model  (stacked generator and discriminator)
		# In this model, we train the generator only
		self.stacked_gen_disc = Model(z, p_true)

		# loss
		# START INSERT CODE HERE
		generator_loss = K.mean(K.log(1 - p_true))
		# END INSERT CODE HERE
		self.stacked_gen_disc.add_loss(generator_loss)
		self.stacked_gen_disc.compile(optimizer=optimizer)

	def build_generator(self):

		z_rand = Input(shape=(self.z_dim,))

		# START INSERT CODE HERE
		x = Dense(256)(z_rand)
		x = LeakyReLU(alpha=0.2)(x)
		x = Dense(512)(x)
		x = LeakyReLU(alpha=0.2)(x)
		x = Dense(784)(x)
		x = Activation('tanh')(x)
		output_img = Reshape((28, 28, 1))(x)
		# END INSERT CODE HERE

		model_generator = Model(z_rand, output_img)
		model_generator.summary()

		return model_generator

	def build_discriminator(self):

		input_img = Input(shape=self.img_shape)

		x = Flatten()(input_img)
		x = Dense(512)(x)
		x = LeakyReLU(alpha=0.2)(x)
		x = Dense(256)(x)
		x = LeakyReLU(alpha=0.2)(x)
		x = Dense(1)(x)
		p_true = Activation('sigmoid')(x)
		
		model_discriminator = Model(input_img, p_true)
		model_discriminator.summary()

		return model_discriminator

	def load_gan_data(self,dataset_name):
		# Load the dataset
		if(dataset_name == 'mnist'):
			(X_train, _), (_, _) = mnist.load_data()
		elif(dataset_name == 'cifar'):
			from keras.datasets import cifar10
			(X_train, y_train), (X_test, y_test) = cifar10.load_data()
		else:
			print('Error, unknown database')

		# Rescale -1 to 1
		X_train = X_train / 127.5 - 1.
		#add a channel dimension, if need be (for mnist data)
		if(X_train.ndim ==3):
			X_train = np.expand_dims(X_train, axis=3)
		return X_train

	def save_gan_model(self, model_file):

		#save the GAN class instance
		gan_temp = GAN(self.dataset_name,'')
		gan_temp.generator = self.generator
		gan_temp.discriminator = self.discriminator
		gan_temp.stacked_gen_disc = []
		gan_temp.iter_count = self.iter_count
		with open(model_file,'wb') as file_class:
			pickle.dump(gan_temp,file_class,-1)

	def load_gan_model(self, model_file):

		#load GAN class instance
		gan_temp = pickle.load(open(model_file,"rb",-1))
		#copy parameters
		self.img_rows = gan_temp.img_rows 
		self.img_cols = gan_temp.img_cols 
		self.img_channels = gan_temp.img_channels 
		self.img_shape = gan_temp.img_shape
		self.z_dim = gan_temp.z_dim
		self.iter_count = gan_temp.iter_count
		self.model_file = gan_temp.model_file
		self.dataset_name = gan_temp.dataset_name

		#copy models
		self.generator = gan_temp.generator
		self.discriminator = gan_temp.discriminator

	def train(self, epochs, batch_size=128, sample_interval=50):
		
		k=1	#number of internal loops

		#load dataset
		X_train = self.load_gan_data(self.dataset_name)

		# Adversarial ground truths
		d_output_true = np.ones((batch_size, 1))
		d_output_false = np.zeros((batch_size, 1))

		first_iter =self.iter_count

		for epoch in range(first_iter,epochs):

			# ---------------------
			#  Train Discriminator
			# ---------------------

			# Train the discriminator
			for i in range(0,k):
				# Select a random batch of images
				idx = np.random.randint(0, X_train.shape[0], batch_size)
				imgs = X_train[idx]

				z_random = np.random.normal(0, 1, (batch_size, self.z_dim))

				# Generate a batch of new (fake) images
				gen_imgs = self.generator.predict(z_random)
				
				# START INSERT CODE
				d_loss_real = self.discriminator.train_on_batch(imgs, d_output_true)
				d_loss_fake = self.discriminator.train_on_batch(gen_imgs,d_output_false)
				# END INSERT CODE
				d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
			
			# ---------------------
			#  Train Generator
			# ---------------------

			# Select a random batch of images
			idx = np.random.randint(0, X_train.shape[0], batch_size)
			imgs = X_train[idx]

			z_random = np.random.normal(0, 1, (batch_size, self.z_dim))

			# Generate a batch of new (fake) images
			gen_imgs = self.generator.predict(z_random)
			# Generator training : try to make generated images be classified as true by the discriminator
			g_loss = self.stacked_gen_disc.train_on_batch(z_random,None)

			# increase epoch counter
			self.iter_count = self.iter_count+1
			# Plot the losses
			print("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100*d_loss[1], g_loss))

			# Save some random generated images and the models at every sample_interval iterations
			if (epoch % sample_interval == 0):
				self.sample_images('GAN_images/'+self.dataset_name+'_sample_%06d.png' % epoch)
				# self.save_gan_model(self.model_file)

	def sample_images(self, image_filename, rand_seed=30):
		np.random.seed(rand_seed)

		r, c = 5, 5
		z_random = np.random.normal(0, 1, (r * c, self.z_dim))
		gen_imgs = self.generator.predict(z_random)

		# Rescale images 0 - 1
		gen_imgs = 0.5 * gen_imgs + 0.5

		fig, axs = plt.subplots(r, c)
		cnt = 0
		for i in range(r):
			for j in range(c):
				#black and white images
				if(gen_imgs.shape[3] == 1):
					axs[i,j].imshow(gen_imgs[cnt, :,:,0], cmap='gray')
				elif(gen_imgs.shape[3] == 3):   #colour images
					axs[i,j].imshow(gen_imgs[cnt, :,:])
				else:
					print('Error, unsupported channel size. Dude, I don''t know what you want me to do.\
							I can''t handle this data. You''ve made me very sad ...')
				axs[i,j].axis('off')
				cnt += 1
		fig.savefig(image_filename)
		plt.close()


if __name__ == '__main__':

	#create the output image and model directories
	if (os.path.isdir('GAN_images')==0):
		os.mkdir('GAN_images')
	if (os.path.isdir('GAN_models')==0):
		os.mkdir('GAN_models')

	#choose dataset
	dataset_name = 'mnist'#

	#create GAN model
	#set_session(session)

	#create GAN model
	model_file = ''#'models/'+dataset_name+'_gan_model.pickle'#
	gan = GAN(dataset_name,model_file)#,
	is_training = 1

	if (is_training ==1):
		gan.train(epochs=50000, batch_size=128, sample_interval=5000)
	else:
		gan.sample_images('GAN_images/test_images.png')
