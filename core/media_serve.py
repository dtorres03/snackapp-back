import os
import re
import mimetypes
from django.http import StreamingHttpResponse, HttpResponse, Http404

def ranged_file_response(request, path, document_root=None):
    """
    Returns a FileResponse with HTTP Range request support, which is 
    required by iOS (AVPlayer) to play videos.
    """
    file_path = os.path.join(document_root, path)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise Http404("Archivo no encontrado")
        
    size = os.path.getsize(file_path)
    content_type, _ = mimetypes.guess_type(file_path)
    content_type = content_type or 'application/octet-stream'
    
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_match = re.match(r'bytes=(?P<start>\d+)-(?P<stop>\d*)', range_header, re.I) if range_header else None
    
    if range_match:
        start = int(range_match.group('start'))
        stop = range_match.group('stop')
        stop = int(stop) if stop else size - 1
        
        if start >= size or stop >= size or start > stop:
            response = HttpResponse(status=416)
            response['Content-Range'] = f'bytes */{size}'
            return response
            
        length = stop - start + 1
        
        def file_iterator(file_path, offset, bytes_to_read):
            with open(file_path, 'rb') as f:
                f.seek(offset)
                bytes_remaining = bytes_to_read
                while bytes_remaining > 0:
                    chunk_size = min(8192, bytes_remaining)
                    data = f.read(chunk_size)
                    if not data:
                        break
                    bytes_remaining -= len(data)
                    yield data
                    
        response = StreamingHttpResponse(file_iterator(file_path, start, length), status=206, content_type=content_type)
        response['Content-Range'] = f'bytes {start}-{stop}/{size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
    else:
        def file_iterator(file_path):
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(8192)
                    if not data:
                        break
                    yield data
                    
        response = StreamingHttpResponse(file_iterator(file_path), content_type=content_type)
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(size)
        
    return response
