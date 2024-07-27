import os
import io
import requests
import warnings
import astropy.units as u
from PIL import Image
from urllib.parse import urlencode
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from astropy.utils.exceptions import AstropyWarning

image_folder = "images"


def fetch_pulsar_coordinates(pulsar_name):
    warnings.simplefilter("ignore", AstropyWarning)

    result = Simbad.query_object(pulsar_name)
    if result is None or len(result) == 0:
        raise ValueError("Pulsar not found in SIMBAD database.")
    coordinates = SkyCoord(
        ra=result["RA"], dec=result["DEC"], unit=(u.hourangle, u.deg)
    )
    return coordinates


def list_pulsars(options):
    pulsars = []
    conditions = []

    if "max_dec" in options and options["max_dec"] is not None:
        conditions.append(f"DecJ+%3C+{options['max_dec']}")
    if "min_dec" in options and options["min_dec"] is not None:
        conditions.append(f"DecJ+%3E+{options['min_dec']}")
    if "max_gb" in options and options["max_gb"] is not None:
        conditions.append(f"GB+%3C+{options['max_gb']}")
    if "min_gb" in options and options["min_gb"] is not None:
        conditions.append(f"GB+%3E+{options['min_gb']}")
    if "min_year" in options and options["min_year"] is not None:
        conditions.append(f"Date%3E{options['min_year']}")
    if "max_error" in options and options["max_error"] is not None:
        conditions.append(f"error%28DecJ%29+%3C+{options['max_error']}")

    condition_string = "+%26%26+".join(conditions)

    if "pulsar_name" in options and options["pulsar_name"] != "":
        condition_string += f"+&&+pulsar_names=+{options['pulsar_name']}"

    url = f"https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=2.1.1&Name=Name&sort_attr=jname&sort_order=asc&condition={condition_string}&state=query&table_bottom.x=45&table_bottom.y=2"
    response = requests.get(url).text
    list = response.split("<pre>")[1].split("</pre>")[0]

    for line in list.split("\n"):
        if line.strip() and line[:3] != "---":
            try:
                pulsars.append(line[6:].split(" ")[0])
            except:
                pass

    pulsars.pop(0)

    return pulsars


def save_pulsar(pulsar_name, hips, fov=1):
    pulsar_name = "PSR " + pulsar_name
    try:
        coordinates = fetch_pulsar_coordinates(pulsar_name)

        details = {
            "Name": pulsar_name,
            "RA": coordinates.ra.deg[0],
            "DEC": coordinates.dec.deg[0],
            "GLON": coordinates.galactic.l.deg[0],
            "GLAT": coordinates.galactic.b.deg[0],
        }

        image_path = os.path.join(
            image_folder,
            f"{pulsar_name.replace('PSR ', '')}_{hips.replace('/', '-')}.jpg",
        )

        # Prepare API request
        query_params = {
            "hips": hips,
            "format": "jpg",
            "ra": coordinates.ra.deg[0],
            "dec": coordinates.dec.deg[0],
            "fov": (int(fov) * u.arcmin).to(u.deg).value,
            "width": 500,
            "height": 500,
        }

        url = f"http://alasky.u-strasbg.fr/hips-image-services/hips2fits?{urlencode(query_params)}"
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        # Save the image
        os.makedirs(image_folder, exist_ok=True)

        # Check if the response content is pure white
        image = Image.open(io.BytesIO(response.content))
        if image.getextrema() == ((255, 255), (255, 255), (255, 255)):
            print(f"Skipping pure white image: {image_path}")
            return

        with open(image_path, "wb") as f:
            f.write(response.content)

    except Exception as e:
        debug = True
        if debug:
            print(f"Failed to download image: {e}")


def load_pulsar(pulsar_name, hips):
    image_path = os.path.join(
        image_folder,
        f"{pulsar_name.replace('PSR ', '')}_{hips.replace('/', '-')}.jpg",
    )
    details = {}

    try:
        coordinates = fetch_pulsar_coordinates(pulsar_name)

        details = {
            "Name": pulsar_name,
            "RA": coordinates.ra.deg[0],
            "DEC": coordinates.dec.deg[0],
            "GLON": coordinates.galactic.l.deg[0],
            "GLAT": coordinates.galactic.b.deg[0],
        }

    except Exception as e:
        debug = False
        if debug:
            print(f"Failed to download image: {e}")

    if os.path.exists(image_path):
        image = Image.open(image_path)
        return image, details
    else:
        return None
