# Melatih CNN sederhana di MNIST dan menyimpan model ke ./models/mnist_cnn.h5

import os
import tensorflow as tf
from tensorflow.keras import layers, models


def build_model(input_shape=(28, 28, 1), num_classes=10):
    model = models.Sequential([
        layers.Input(shape=input_shape),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    return model


def main():
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

    # Normalisasi ke [0,1] dan reshape ke (28,28,1)
    x_train = (x_train.astype('float32') / 255.0)[..., None]
    x_test = (x_test.astype('float32') / 255.0)[..., None]

    model = build_model()
    model.summary()

    model.fit(
        x_train, y_train,
        validation_split=0.1,
        epochs=6,
        batch_size=128,
        verbose=2
    )

    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
    print(f"Test accuracy: {test_acc:.4f}")

    os.makedirs('models', exist_ok=True)
    model_path = 'models/mnist_cnn.h5'
    model.save(model_path)
    print(f"Saved model to {model_path}")


if __name__ == '__main__':
    main()