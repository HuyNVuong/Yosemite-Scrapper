from yosemite_scrapper import check_campsite

import os
from flask import Flask

app = Flask(__name__)

@app.route('/tasks/PollRecreationGovForSite/<int:site_id>', methods=['GET'])
def poll_recreation_gov_for_updates(site_id):
  try:
    check_campsite(site_id)

    return 'Recreation.gov polled successfully', 200
  except Exception:

    return 'Internal server error', 500

if __name__ == '__main__':
  # Get the configured host name in GCP, otherwise fall back to localhost
  host = os.environ.get('HOST_NAME', '127.0.0.1')
  port = os.environ.get('PORT', '8080')
  app.run(host=host, port=port, debug=True)
