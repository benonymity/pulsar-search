import unittest
from pulsars import fetch_pulsar_coordinates, list_pulsars, load_pulsar, save_pulsar
from astropy.coordinates import SkyCoord
import os
from PIL import Image


class TestPulsarFunctions(unittest.TestCase):
    def setUp(self):
        # Common setup for the tests
        self.known_pulsar = "PSR J1821-0331"
        self.invalid_pulsar = "Invalid Pulsar Name"
        self.hips = "CDS/P/VPHAS/DR4/Halpha"

    def test_fetch_pulsar_coordinates_with_known_pulsar(self):
        # Ensure coordinates are fetched correctly for a known pulsar
        coordinates = fetch_pulsar_coordinates(self.known_pulsar)
        self.assertIsInstance(coordinates, SkyCoord)
        self.assertEqual(coordinates.ra.deg, 275.43625)
        self.assertEqual(coordinates.dec.deg[0], -3.5201944444444444)

    def test_fetch_pulsar_coordinates_with_invalid_pulsar_raises_error(self):
        # Test that fetching coordinates with an invalid pulsar name raises an error
        with self.assertRaises(ValueError) as context:
            fetch_pulsar_coordinates(self.invalid_pulsar)
        self.assertEqual(str(context.exception), "Pulsar not found in SIMBAD database.")

    def test_list_pulsars_returns_non_empty_list_of_strings(self):
        # Ensure listing pulsars returns a non-empty list of strings
        options = {
            "max_dec": "0",
            "min_dec": "-90",
            "max_gb": "5",
            "min_gb": "-5",
            "min_year": "2012",
            "max_error": "1",
        }
        pulsars = list_pulsars(options)
        self.assertIsInstance(pulsars, list)
        self.assertTrue(len(pulsars) > 0)
        self.assertTrue(all(isinstance(pulsar, str) for pulsar in pulsars))

    def test_load_pulsar_returns_correct_types(self):
        # Ensure that pulsar details and image are returned correctly
        save_pulsar(self.known_pulsar, self.hips)
        result = load_pulsar(self.known_pulsar, self.hips)
        self.assertIsInstance(result, tuple)
        image, details = result
        self.assertIsInstance(details, dict)
        self.assertIsInstance(image, Image.Image)
        self.assertEqual(details["Name"], self.known_pulsar)
        self.assertTrue(
            os.path.exists(
                f"images/{self.known_pulsar.replace('PSR ', '')}_{self.hips.replace('/', '-')}.jpg"
            )
        )
        image.close()


if __name__ == "__main__":
    unittest.main()
