import gzip

from flask import abort, request, send_file

from services.thumbnails import image_path, prepare_thumbnail


def init_http_response(app):
    @app.get('/media/thumbnail/<int:width>/<path:filename>')
    def thumbnail(width, filename):
        if width not in (160, 480, 960):
            abort(404)
        source = image_path('/static/' + filename)
        if not source:
            abort(404)
        response = send_file(prepare_thumbnail(source, width), mimetype='image/webp', conditional=True, max_age=86400)
        return response

    # 静态资源可以缓存，接口数据每次重新获取。
    @app.after_request
    def deliver(response):
        if (request.path.startswith(('/assets/', '/static/assets/'))
                and response.status_code in (200, 304) and response.mimetype != 'text/html'):
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
        elif request.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        if response.mimetype not in ('application/json', 'application/javascript', 'text/javascript', 'text/css', 'text/html'):
            return response
        response.vary.add('Accept-Encoding')
        if (request.method != 'GET' or response.status_code != 200
                or request.accept_encodings['gzip'] <= 0
                or 'Content-Encoding' in response.headers or 'Range' in request.headers):
            return response
        response.direct_passthrough = False
        body = response.get_data()
        if len(body) < 1024:
            return response
        compressed = gzip.compress(body, compresslevel=5, mtime=0)
        if len(compressed) >= len(body):
            return response
        response.set_data(compressed)
        response.headers['Content-Encoding'] = 'gzip'
        response.headers.pop('ETag', None)
        return response
