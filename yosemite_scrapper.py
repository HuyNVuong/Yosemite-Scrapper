from datetime import datetime
from datetime import UTC
import json
import sys
from urllib.parse import quote

import requests


def _get_user_agent():
  template = '{}.{}.{}-{}-{} ({})'
  fields = tuple(sys.version_info) + (sys.platform,)
  return template.format(*fields)


_GET_HEADERS = {
    'Accept': 'application/json',
    'User-Agent': _get_user_agent(),
}

_POST_HEADERS = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'User-Agent': _get_user_agent(),
}

_SLACK_WEBHOOK_URL = 'URL'


def _get(url, **kwargs):
  http_response = requests.get(url, headers=_GET_HEADERS, **kwargs)
  http_response.raise_for_status()

  try:
    response = json.loads(http_response.text)

    return response
  except json.JSONDecodeError:
    return http_response


def _post(url: str, payload=None, custom_headers=None, **kwargs):
  data = json.dumps(payload) if payload else None
  headers = custom_headers if custom_headers else _POST_HEADERS
  http_response = requests.post(url, headers=headers, data=data, **kwargs)
  http_response.raise_for_status()

  try:
    response = json.loads(http_response.text)

    return response
  except json.JSONDecodeError:
    return http_response


id_to_campsite_name = {
    232447: 'Upper Pines',
    232449: 'North Pines',
    232450: 'Lower Pines',
}


def check_campsite(campsite_id):
  utc_now = datetime.now(UTC)
  # Looks for campsite of the current month, and 3 months after it
  for month in range(utc_now.month, utc_now.month + 4):
    first_of_month = utc_now.replace(
        month=month, day=1, hour=0, minute=0, second=0, microsecond=0
    ) if month <= 12 else  utc_now.replace(
        year = utc_now.year + 1, month=month % 12, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    start_date_url_query = quote(
        f'{first_of_month.isoformat().replace("+00:00", ".000Z")}'
    )

    url = f'https://www.recreation.gov/api/camps/availability/campground/{campsite_id}/month?start_date={start_date_url_query}'

    results = _get(url)
    for day in range(1, 32):
      date = (
          f'2024-{month}-{day}T00:00:00Z'
          if day >= 10
          else f'2024-{month}-0{day}T00:00:00Z'
      )
      for campsite_url_id in results['campsites']:
        if (
            results['campsites'][campsite_url_id]['availabilities'].get(date)
            == 'Available'
        ):
          campsite_url = (
              f'https://www.recreation.gov/camping/campsites/{campsite_url_id}'
          )

          message = (
              f'Site {id_to_campsite_name[campsite_id]} is available on'
              f' {month}-{day if day >= 10 else f"0{day}"} at site'
              f' {results["campsites"][campsite_url_id]["site"]} and can be'
              f' reserved via {campsite_url}'
          )
          print(message)
          _post(_SLACK_WEBHOOK_URL, {'text': message})


if __name__ == '__main__':
  check_campsite('232447')
