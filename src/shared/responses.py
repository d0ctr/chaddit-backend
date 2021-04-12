from flask import request, Response, json

def custom_response(response, status_code):
  if status_code in [200, 201]:
    if isinstance(response, list):
      offset = request.args.get('offset', default = 0, type = int)
      limit = request.args.get('limit', default = 20, type = int)
      if limit == 0:
        response = response[offset:]
      else:
        response = response[offset:offset + limit]
      response = [item for item in response if item.get('active') == True]
    else:
      if response.get('active') == False:
        response = {'error': 'No instance found'}
        status_code = 404
  return Response(
    mimetype = 'application/json',
    response = json.dumps(response),
    status = status_code
  )