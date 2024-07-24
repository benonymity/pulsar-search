import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout


def create_model(image_width, image_height):
    model = Sequential(
        [
            Conv2D(
                16,
                (3, 3),
                activation="relu",
                input_shape=(image_width, image_height, 3),
            ),
            MaxPooling2D(2, 2),
            Conv2D(32, (3, 3), activation="relu"),
            MaxPooling2D(2, 2),
            Conv2D(64, (3, 3), activation="relu"),
            MaxPooling2D(2, 2),
            Flatten(),
            Dense(512, activation="relu"),
            Dropout(0.5),
            Dense(1, activation="sigmoid"),  # Binary classification
        ]
    )
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model


def main():
    # Set the dimensions to which all images will be resized
    image_width, image_height = 64, 64

    datagen = ImageDataGenerator(rescale=1.0 / 255, validation_split=0.2)

    train_generator = datagen.flow_from_directory(
        "path_to_data",
        target_size=(image_width, image_height),
        batch_size=32,
        class_mode="binary",
        subset="training",
    )

    validation_generator = datagen.flow_from_directory(
        "path_to_data",
        target_size=(image_width, image_height),
        batch_size=32,
        class_mode="binary",
        subset="validation",
    )

    model = create_model(image_width, image_height)
    model.summary()

    history = model.fit(
        train_generator,
        steps_per_epoch=train_generator.n // train_generator.batch_size,
        epochs=10,
        validation_data=validation_generator,
        validation_steps=validation_generator.n // validation_generator.batch_size,
    )

    # Save the model
    model.save("pulsar_bow_shock_classifier.h5")


if __name__ == "__main__":
    main()
