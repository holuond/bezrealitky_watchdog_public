import datetime
import json
import logging
import os
import pprint

import pytz
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from shapely.geometry import Point, Polygon

from bezrealitky_watchdog.graphql_queries import fetch_advert, fetch_advert_markers
from bezrealitky_watchdog.s3 import download_dict_from_s3, upload_dict_to_s3

logger = logging.getLogger(__name__)


def run():
    base_advert_url = "https://www.bezrealitky.cz/nemovitosti-byty-domy/"

    # ========== QUERY ADVERT MARKERS ==================
    response_advert_markers = fetch_advert_markers()

    # ========== FILTER TO UNSEEN ONLY =================
    advert_markers = filter_out_seen_advert_markers(response_advert_markers)
    if not advert_markers:
        exit(0)
    for am in advert_markers:
        am['uri'] = base_advert_url + am['uri']
    logger.info(pprint.pformat(advert_markers))

    # ========== CUSTOM FILTER BY LOCATION =============
    # TODO configure this according to your needs
    polygon = Polygon([
        # https://en.mapy.cz/s/malojepato
        (50.134046, 14.515442), (50.124472, 14.506516), (50.135587, 14.485916), (50.129204, 14.438194), (50.110934, 14.430298), (50.110383, 14.376568),
        (50.099484, 14.351505), (50.092986, 14.35099), (50.094308, 14.396481), (50.090013, 14.382061), (50.087259, 14.399742), (50.078887, 14.394936),
        (50.072388, 14.36541), (50.060488, 14.370216), (50.052883, 14.334683), (50.053875, 14.305157), (50.039544, 14.296917), (50.039654, 14.337257),
        (50.052662, 14.386524), (50.044754, 14.412237), (50.053765, 14.427723), (50.039654, 14.444374), (50.028959, 14.488148), (50.035244, 14.498791),
        (50.045387, 14.468578), (50.058173, 14.443001), (50.068091, 14.451069), (50.066327, 14.45742), (50.064345, 14.515785), (50.077676, 14.510292),
        (50.085497, 14.462227), (50.097391, 14.495873), (50.104658, 14.495873), (50.123482, 14.526085)])

    advert_markers = [am for am in advert_markers if polygon.contains(Point(am['gps']['lat'], am['gps']['lng']))]
    logger.info(f'Leaving {len(advert_markers)} advert markers after location filtering.')
    if not advert_markers:
        exit(0)

    if len(advert_markers) > 20:
        msg = (f'There are {len(advert_markers)} advert markers before querying details per advert. There might be a misconfiguration. '
               f'Aborting to avoid too many requests to the API server. If this is the first run of the watchdog, increase this limit if needed.')
        logger.warning(msg)
        send_dict_by_email({'msg': msg})
        exit(1)

    # ========== QUERY ADVERT DETAILS ==================
    adverts = [fetch_advert(am['id']) for am in advert_markers]

    # Improve fetched data content/format
    for advert in adverts:
        advert['uri'] = base_advert_url + advert['uri']
        advert['availableFrom'] = datetime.datetime.fromtimestamp(advert['availableFrom'], tz=pytz.timezone('Europe/Prague')).strftime('%Y-%m-%d %H:%M:%S')

    # ========== SEND ALERT ============================
    result_dict = {'msg': f'Found {len(adverts)} new adverts.'} | {'adverts': adverts}
    logger.info(pprint.pformat(result_dict))
    send_dict_by_email(result_dict)


def send_dict_by_email(_dict):
    logger.info('Sending email.')
    sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))

    html_content = f"<html><body><pre>{json.dumps(_dict, indent=4)}</pre></body></html>"
    message = Mail(from_email=os.getenv('FROM_EMAIL'),
                   to_emails=os.getenv('TO_EMAIL'),
                   subject='Bezrealitky Watchdog',
                   html_content=html_content)
    response = sg.send(message)

    logger.info("Received response:\n" + pprint.pformat({"status_code": response.status_code, "body": response.body}))
    return response


def filter_out_seen_advert_markers(advert_markers):
    bucket_name = os.getenv('BUCKET_NAME')
    seen_advert_markers_file_key = ("seen_advert_markers.json")

    # Read state
    seen_advert_markers = download_dict_from_s3(bucket_name, seen_advert_markers_file_key)['markers']
    if seen_advert_markers is None:
        seen_advert_markers = []
        upload_dict_to_s3({'markers': seen_advert_markers}, bucket_name, seen_advert_markers_file_key)

    # Filter out already seen adverts
    seen_advert_marker_ids = [am['id'] for am in seen_advert_markers]
    unseen_advert_markers = [am for am in advert_markers if am['id'] not in seen_advert_marker_ids]
    logger.info(f'Found {len(unseen_advert_markers)} new advert markers.')
    if not unseen_advert_markers:
        return unseen_advert_markers

    # Update state
    upload_dict_to_s3({'markers': seen_advert_markers + unseen_advert_markers}, bucket_name, seen_advert_markers_file_key)
    return unseen_advert_markers
