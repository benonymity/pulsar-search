import os
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
    max_dec = options["max_dec"]
    min_dec = options["min_dec"]
    max_gb = options["max_gb"]
    min_gb = options["min_gb"]
    min_date = options["min_year"]
    max_error = options["max_error"]
    url = f"https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=2.1.1&Name=Name&sort_attr=jname&sort_order=asc&condition=DecJ+%3C+{max_dec}+%26%26+DecJ+%3E+{min_dec}+%26%26+GB+%3C+{max_gb}+%26%26+GB+%3E+{min_gb}+%26%26+Date%3E{min_date}+%26%26+error%28DecJ%29+%3C+{max_error}&state=query&table_bottom.x=45&table_bottom.y=2"
    response = requests.get(url).text
    list = response.split("<pre>")[1].split("</pre>")[0]

    for line in list.split("\n"):
        if line.strip() and line[:3] != "---":
            try:
                pulsars.append(line[6:].split(" ")[0])
            except:
                pass

    pulsars.pop(0)
    pulsars.pop(0)

    return pulsars


def save_pulsar(pulsar_name, hips):
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

        if not os.path.exists(image_path):
            # Prepare API request
            query_params = {
                "hips": hips,
                "format": "jpg",
                "ra": coordinates.ra.deg[0],
                "dec": coordinates.dec.deg[0],
                "fov": (1 * u.arcmin).to(u.deg).value,
                "width": 500,
                "height": 500,
            }

            url = f"http://alasky.u-strasbg.fr/hips-image-services/hips2fits?{urlencode(query_params)}"
            response = requests.get(url)
            response.raise_for_status()  # Raises an HTTPError for bad responses

            # Save the image
            os.makedirs(image_folder, exist_ok=True)
            with open(image_path, "wb") as f:
                f.write(response.content)

    except Exception as e:
        debug = False
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
