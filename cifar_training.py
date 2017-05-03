import tensorflow as tf
import numpy as np
import cifar # Contains inference(),loss(),training()
import data_helpers # Helper functions to fetch CIFAR data
import os

MAX_STEPS = 125*1000
BATCH_SIZE = 128

def generate_batch(dataset_images,dataset_labels):
    batch = np.random.choice(dataset_images.shape[0], BATCH_SIZE)
    images_batch = dataset_images[batch]
    label_batch = dataset_labels[batch]
    return images_batch,label_batch

def evaluate_batch(sess,accuracy,cifar_dataset,image_pl,label_pl,training):
    # Inputs:
        # sess : Current session
        # accuracy : op defined for computing the accuracy
        # cifar_dataset : Dataset containing all images
        # images_batch : Tensor containing images in the current batch
        # label_batch : Tensor containing label in the current batch
        # image_pl : Placeholder tensor for images
        # label_pl : Placeholder tensor for label
    # Returns:
        # prediction : fraction of correctly predicated labels

    if training:
        dataset_images = cifar_dataset['images_train']
        dataset_labels = cifar_dataset['labels_train']
    else:
        dataset_images = cifar_dataset['images_test']
        dataset_labels = cifar_dataset['labels_test']

    num_examples = dataset_images.shape[0]
    steps_per_epoch = num_examples/BATCH_SIZE
    true_count = 0
    for x in range(steps_per_epoch):
        # Generate batch
        images_batch,label_batch = generate_batch(dataset_images,dataset_labels)
        true_count += sess.run(accuracy,feed_dict = {image_pl: images_batch,label_pl:label_batch})
    prediction = float(true_count)/num_examples
    print 'Num exaples = %d True count = %d Precision = %.04f'%(num_examples,true_count,prediction)
    return prediction

# Top level training function
def run_training():

    with tf.Graph().as_default():
        cifar_dataset = data_helpers.load_data() # Loads training images/label + test images/label
        image = tf.placeholder(tf.float32,[None,3072])
        label = tf.placeholder(tf.int64,[None])


        # Construct the graph
        out,regularizer = cifar.inference(image)

        # Add op for loss
        loss = cifar.loss(out,regularizer,label)

        # Add op for optimization for each training step
        train_step = cifar.create_train_step(loss)

        # Add op for evaluating training accuracy
        accuracy = cifar.evaluate(out,label)

        # Now that all the ops are defined, run the training
        init = tf.global_variables_initializer()

        # Create a "saver" to save weights and biases
        saver = tf.train.Saver()

        # Create session
        sess = tf.Session()
        sess.run(init)

        for i in range(MAX_STEPS):
            # Generate batch
            images_batch,label_batch = generate_batch(cifar_dataset['images_train'],cifar_dataset['labels_train'])
            # Execute the train step
            sess.run(train_step,feed_dict = {image:images_batch,label:label_batch})
            if i%1000 == 0:
                train_accuracy = evaluate_batch(sess,accuracy,cifar_dataset,image,label,training = True) #evaluate model with training data
                print('Iteration '+str(i)+' training accuracy: '+str(train_accuracy))
                test_accuracy = evaluate_batch(sess,accuracy,cifar_dataset,image,label,training = False) #evaluate model with test data
                print('Iteration '+str(i)+' test accuracy: '+str(test_accuracy))
            if i == MAX_STEPS-1:
                # Now that training is complete, save the checkpoint file
                file_path = os.path.join(os.getcwd(),"model.cpkt")
                saver.save(sess,file_path,global_step = i)



def main(_):
    run_training()

if __name__ == '__main__':
    tf.app.run(main=main)



