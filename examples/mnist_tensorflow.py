import os
import argparse

import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data

from mag.experiment import Experiment

mnist = input_data.read_data_sets("MNIST", one_hot=True)
Dataset = tf.data.Dataset


class MnistClassifier:

    def __init__(self, mnist, experiment):

        self.experiment = experiment
        self.config = experiment.config

        with tf.Graph().as_default() as self.graph:
            images, targets = self._create_input(mnist)
            logits = self._forward(images)
            loss = self._create_loss(logits, targets)
            self.train_op = self._create_optimizer(loss)
            accuracy = self._create_accuracy(logits, targets)
            self._create_summaries(loss, accuracy)
            self._create_summary_writers()
            self._create_initializers()
            self._create_saver()

    def _create_input(self, mnist):
        with tf.name_scope("input"):

            train_dataset = (
                Dataset
                .zip((
                    Dataset.from_tensor_slices(mnist.train.images),
                    Dataset.from_tensor_slices(mnist.train.labels)
                ))
                .shuffle(buffer_size=self.config.train._buffer_size)
                .batch(self.config.train.batch_size)
            )

            valid_dataset = (
                tf.data.Dataset
                .zip((
                    Dataset.from_tensor_slices(mnist.validation.images),
                    Dataset.from_tensor_slices(mnist.validation.labels)
                ))
                .batch(self.config.validation._batch_size)
            )

            iterator = tf.data.Iterator.from_structure(
                train_dataset.output_types,
                train_dataset.output_shapes
            )

            self.train_initializer_op = iterator.make_initializer(
                train_dataset
            )
            self.valid_initializer_op = iterator.make_initializer(
                valid_dataset
            )

            images, targets = iterator.get_next()

            return images, targets

    def _forward(self, images):
        with tf.variable_scope("forward"):

            net = images
            for layer in range(self.config.network.n_layers):
                net = tf.layers.dense(
                    net, self.config.network.hidden_units,
                    # dynamically get the activation from config
                    activation=getattr(tf.nn, self.config.network.activation)
                )
            net = tf.layers.dense(
                net, self.config._n_classes, activation=None
            )

            return net

    def _create_loss(self, logits, targets):
        with tf.name_scope("loss"):

            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
                labels=targets,
                logits=logits
            )
            # average over minibatch
            cross_entropy = tf.reduce_mean(cross_entropy, axis=0)

            return cross_entropy

    def _create_accuracy(self, logits, targets):
        with tf.name_scope("accuracy"):
            correct = tf.equal(
                tf.argmax(logits, axis=1),
                tf.argmax(targets, axis=1))
            accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))
            return accuracy

    def _create_optimizer(self, loss):
        with tf.name_scope("optimizer"):

            self.global_step = tf.Variable(
                0, trainable=False, name="global_step"
            )
            optimizer = tf.train.MomentumOptimizer(
                self.config.train.learning_rate,
                momentum=self.config.train.momentum
            )
            train_op = optimizer.minimize(loss, global_step=self.global_step)

            return train_op

    def _create_summaries(self, loss, accuracy):
        with tf.variable_scope("summaries"):
            # streaming mean helps to compute the mean across
            # all samples in the dataset
            streaming_loss, update_loss = tf.metrics.mean(loss)
            streaming_accuracy, update_accuracy = tf.metrics.mean(accuracy)

            self.update_metrics = tf.group(update_loss, update_accuracy)

            self.loss = streaming_loss
            self.accuracy = streaming_accuracy

            cross_entropy_summary = tf.summary.scalar(
                "loss",
                streaming_loss)

            accuracy_summary = tf.summary.scalar(
                "accuracy",
                streaming_accuracy)

            self.summary = tf.summary.merge([
                cross_entropy_summary, accuracy_summary])

    def _create_initializers(self):
        self.variables_initializer = tf.global_variables_initializer()
        # streaming mean requires initializing of local variables
        self.local_variables_initializer = tf.local_variables_initializer()

    def _create_summary_writers(self):

        # Experiment allows creating directories in experiment
        # directory by calling register_directory(directory_name).
        # After this call experiment has attribute `directory_name`
        # which is a path to the specified directory.
        self.experiment.register_directory("summaries")

        train_summary_path = os.path.join(self.experiment.summaries, "train")
        self.train_writer = tf.summary.FileWriter(train_summary_path)
        valid_summary_path = os.path.join(self.experiment.summaries, "valid")
        self.valid_writer = tf.summary.FileWriter(valid_summary_path)

    def _create_saver(self):
        self.experiment.register_directory("checkpoints")
        self.saver = tf.train.Saver(max_to_keep=5)

    @property
    def _checkpoint_path(self):
        return self.experiment.checkpoints

    def save(self, sess):
        self.saver.save(
            sess, os.path.join(self._checkpoint_path, "model"),
            global_step=self.global_step
        )

    def load(self, sess):
        checkpoint = tf.train.latest_checkpoint(self._checkpoint_path)
        self.saver.restore(sess, checkpoint)

    def _train_epoch(self, sess):

        sess.run(self.local_variables_initializer)
        sess.run(self.train_initializer_op)

        fetches = [self.train_op, self.update_metrics]

        while True:
            try:
                sess.run(fetches)
            except tf.errors.OutOfRangeError:
                break

        # since streaming mean is used
        # it's nessecary to save summary only in the end of epoch
        self.train_writer.add_summary(
            sess.run(self.summary), sess.run(self.global_step)
        )

    def _validation(self, sess):

        sess.run(self.local_variables_initializer)
        sess.run(self.valid_initializer_op)

        fetches = [self.update_metrics]

        while True:
            try:
                sess.run(fetches)
            except tf.errors.OutOfRangeError:
                break

        summary, loss, accuracy, global_step = sess.run([
            self.summary, self.loss, self.accuracy, self.global_step])

        self.valid_writer.add_summary(summary, global_step)

        return loss, accuracy

    def fit(self):

        with self._setup_session() as sess:
            self.variables_initializer.run()
            self.train_writer.add_graph(self.graph)

            for epoch in range(1, self.config.train.n_epochs + 1):
                self._train_epoch(sess)
                self._validation(sess)
                self.save(sess)

    def _setup_session(self):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True
        return tf.Session(graph=self.graph, config=config)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "--n_layers", type=int, default=1,
        help="Number of layers of a neural network.")
    parser.add_argument(
        "--hidden_units", type=int, default=128,
        help="Number of hidden units in each layer of a neural network.")
    parser.add_argument(
        "--activation", type=str, default="relu",
        help="Activation function used in each layer of a neural network.")
    parser.add_argument(
        "--batch_size", type=int, default=32,
        help="Minibatch size.")
    parser.add_argument(
        "--n_epochs", type=int, default=20,
        help="Number of training epochs.")
    parser.add_argument(
        "--lr", type=float, default=1e-3,
        help="Learning rate.")
    parser.add_argument(
        "--momentum", type=float, default=0.9,
        help="Momentum value used in optimizer.")

    args = parser.parse_args()

    with Experiment({
        "_n_classes": 10,
        "network": {
            "n_layers": args.n_layers,
            "hidden_units": args.hidden_units,
            "activation": args.activation
        },
        "train": {
            "batch_size": args.batch_size,
            "n_epochs": args.n_epochs,
            # to exclude the parameter from the identifier,
            # start its name from the underscore
            "_buffer_size": 128,
            "learning_rate": args.lr,
            "momentum": args.momentum
        },
        "validation": {
            "_batch_size": 128
        }
    }) as experiment:

        classifier = MnistClassifier(mnist, experiment)
        classifier.fit()

        print("Finished!")    # will be logged to a file

        identifier = experiment.config.identifier

    # Now, restore the experiment.
    # Normally you might want to specify `resume_from` argument manually,
    # typically by passing as a command line argument
    with Experiment(resume_from=identifier) as experiment:
        classifier = MnistClassifier(mnist, experiment)
        classifier.sess = classifier._setup_session()
        classifier.load(classifier.sess)

        # now the model is successfully restored and ready for usage!

        loss, accuracy = classifier._validation(classifier.sess)

        # float call is required since both loss and accuracy have
        # np.float32 type which is not json-serializable
        experiment.register_result("loss", float(loss))
        experiment.register_result("accuracy", float(accuracy))
