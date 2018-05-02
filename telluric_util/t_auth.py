def get_token( user, passwd ):
  """
  Given a `user` and `passwd` strings, returns the auth token for Telluric.
  In case of error it Raises an error
  """
  import requests

  url = 'https://auth.telluric.satellogic.com/api-token-auth/'
  payload = {'username': user, 'password': passwd}

  print("Getting token...")

  r = requests.post(url, data=payload)
  if r.status_code != 200:
    raise ValueError("%s: Telluric response error: %s" % (r.status_code,r.text))

  telluric_token = "JWT "+r.json()['token']

  return telluric_token
