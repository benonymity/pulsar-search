# Pulsar Search

<div align="center">
 <img src="pulsar.png" width="300px">
</div>

This is a simple GUI I whipped up to make searching for [pulsar bowshocks](https://arxiv.org/abs/2309.13809) easier. It downloads a bunch of sky surveys using [Aladin](https://aladin.cds.unistra.fr/aladin.gml) and [HIPS](https://alasky.cds.unistra.fr/hips-image-services/hips2fits#endpoint), then runs image analysis to predict which are most likely to have interesting visual attributes then displays them for examination. It's compatible with 5 useful surveys right now, but could be modified to use more!

## Installation

To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/benonymity/pulsar-search.git
   ```
2. Install the required Python packages:
   ```bash
   pip3 install -r requirements.txt
   ```

## Usage

### Running the GUI

To start the pulsar image searcher, run:

```bash
python3 gui.py
```

You'll have to select the parameters of the images you want, then download them! You should see a progress bar, and when it is complete then you can click on "Sort" to sort the images.

## Contributing

Feel free to contribute with a pull request if you see anything that I've messed up or that can be improved! Or open an issue in the tracker so I can fix it when I have some time.

### Testing

Though there are only four tests, I've been convinced about how important testing is, so if you are messing with the pulsar module, execute the following command to run the unit tests:

```bash
python -m unittest test.py
```

Enjoy!
