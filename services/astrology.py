import os
import tempfile
from datetime import datetime, timezone
from skyfield.api import Loader, Topos
from skyfield import almanac

SIGN_NAMES = [
    'Овен', 'Телец', 'Близнецы', 'Рак', 'Лев', 'Дева',
    'Весы', 'Скорпион', 'Стрелец', 'Козерог', 'Водолей', 'Рыбы'
]

PLANETS = ['sun', 'moon', 'mercury', 'venus', 'mars',
           'jupiter barycenter', 'saturn barycenter',
           'uranus barycenter', 'neptune barycenter']
PLANET_NAMES_RU = {
    'sun': 'Солнце', 'moon': 'Луна', 'mercury': 'Меркурий',
    'venus': 'Венера', 'mars': 'Марс', 'jupiter barycenter': 'Юпитер',
    'saturn barycenter': 'Сатурн', 'uranus barycenter': 'Уран',
    'neptune barycenter': 'Нептун',
}

ASPECT_ORBS = {
    0: ('Соединение', 8),
    60: ('Секстиль', 6),
    90: ('Квадратура', 6),
    120: ('Тригон', 6),
    180: ('Оппозиция', 8),
}

_EPHEMERIS = None
_SKYFIELD_DIR = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), 'skyfield-data')
_LOADER = None


def _get_loader():
    global _LOADER
    if _LOADER is None:
        os.makedirs(_SKYFIELD_DIR, exist_ok=True)
        _LOADER = Loader(_SKYFIELD_DIR)
        _LOADER.verbose = False
    return _LOADER


def _get_ephemeris():
    global _EPHEMERIS
    if _EPHEMERIS is None:
        _EPHEMERIS = _get_loader()('de421.bsp')
    return _EPHEMERIS


def calculate_chart(birth_date: str, birth_time: str, lat: float, lon: float, tz: int = 3):
    day, month, year = map(int, birth_date.split('.'))
    hour, minute = map(int, birth_time.split(':'))

    utc_hour = hour - tz
    dt = datetime(year, month, day, utc_hour, minute, tzinfo=timezone.utc)

    try:
        return _calc_with_skyfield(dt, lat, lon)
    except Exception:
        return _fallback_chart(dt)


def _calc_with_skyfield(dt, lat, lon):
    eph = _get_ephemeris()
    ts = _get_loader().timescale()
    t = ts.from_datetime(dt)
    earth = eph['earth']

    planets = {}
    for pl in PLANETS:
        body = eph[pl]
        apparent = earth.at(t).observe(body).apparent()
        ecl_lat, ecl_lon, ecl_dist = apparent.ecliptic_latlon()
        lon_deg = ecl_lon.degrees % 360
        sign_num = int(lon_deg / 30)
        degree = lon_deg % 30
        planets[PLANET_NAMES_RU[pl]] = {
            'sign': SIGN_NAMES[sign_num],
            'degree': round(degree, 2),
            'longitude': round(lon_deg, 2)
        }

    observer = Topos(latitude_degrees=lat, longitude_degrees=lon)
    sun_app = earth.at(t).observe(eph['sun']).apparent()
    ecl_lat, ecl_lon, ecl_dist = sun_app.ecliptic_latlon()
    asc_lon = (ecl_lon.degrees + 90) % 360
    asc_sign = int(asc_lon / 30)
    asc_deg = asc_lon % 30

    aspects = []
    pl_list = list(PLANET_NAMES_RU.keys())
    for i in range(len(pl_list)):
        for j in range(i + 1, len(pl_list)):
            lon1 = planets[PLANET_NAMES_RU[pl_list[i]]]['longitude']
            lon2 = planets[PLANET_NAMES_RU[pl_list[j]]]['longitude']
            diff = abs(lon1 - lon2) % 360
            diff = min(diff, 360 - diff)
            for angle, (name, orb) in ASPECT_ORBS.items():
                if abs(diff - angle) <= orb:
                    aspects.append(
                        f"{PLANET_NAMES_RU[pl_list[i]]} {name} {PLANET_NAMES_RU[pl_list[j]]} ({round(diff, 1)}°)")
                    break

    return {
        'ascendant': f"{SIGN_NAMES[asc_sign]} {round(asc_deg, 2)}°",
        'planets': planets,
        'aspects': aspects,
    }


def _fallback_chart(dt):
    approx_lon = (dt.timestamp() / 3600 / 24 * 360) % 360
    sun_sign = int(approx_lon / 30)
    planets = {
        'Солнце': {'sign': SIGN_NAMES[sun_sign], 'degree': round(approx_lon % 30, 2), 'longitude': round(approx_lon, 2)},
    }
    return {
        'ascendant': f"{SIGN_NAMES[int((dt.month * 30) % 360 / 30)]} 15.0°",
        'planets': planets,
        'aspects': [],
        '_note': 'Не удалось загрузить эфемериды. Установите skyfield с de421.bsp.',
    }
