# vim:ts=4:sw=4:expandtab
'''HTTP/1.1 implementation of client and server.
'''
import sys, socket
import urllib
from collections import defaultdict

from diesel import up, until, until_eol, bytes, ConnectionClosed

status_strings = {
    100 : "Continue",
    101 : "Switching Protocols",
    200 : "OK",
    201 : "Created",
    202 : "Accepted",
    203 : "Non-Authoritative Information",
    204 : "No Content",
    205 : "Reset Content",
    206 : "Partial Content",
    300 : "Multiple Choices",
    301 : "Moved Permanently",
    302 : "Found",
    303 : "See Other",
    304 : "Not Modified",
    305 : "Use Proxy",
    307 : "Temporary Redirect",
    400 : "Bad Request",
    401 : "Unauthorized",
    402 : "Payment Required",
    403 : "Forbidden",
    404 : "Not Found",
    405 : "Method Not Allowed",
    406 : "Not Acceptable",
    407 : "Proxy Authentication Required",
    408 : "Request Time-out",
    409 : "Conflict",
    410 : "Gone",
    411 : "Length Required",
    412 : "Precondition Failed",
    413 : "Request Entity Too Large",
    414 : "Request-URI Too Large",
    415 : "Unsupported Media Type",
    416 : "Requested range not satisfiable",
    417 : "Expectation Failed",
    500 : "Internal Server Error",
    501 : "Not Implemented",
    502 : "Bad Gateway",
    503 : "Service Unavailable",
    504 : "Gateway Time-out",
    505 : "HTTP Version not supported",
}

def parse_request_line(line):
    '''Given a request line, split it into 
    (method, url, protocol).
    '''
    items = line.split(' ')
    items[0] = items[0].upper()
    if len(items) == 2:
        return tuple(items) + ('0.9',)
    items[1] = urllib.unquote(items[1])
    items[2] = items[2].split('/')[-1].strip()
    return tuple(items)

class HttpHeaders(object):
    '''Support common operations on HTTP headers.

    Parsing, modifying, formatting, etc.
    '''
    def __init__(self):
        self._headers = defaultdict(list)
        self.link()

    def add(self, k, v):
        self._headers[k.lower()].append(str(v).strip())

    def remove(self, k):
        if k.lower() in self._headers:
            del self._headers[k.lower()]

    def set(self, k, v):
        self._headers[k.lower()] = [str(v).strip()]

    def format(self):
        s = []
        for h, vs in self._headers.iteritems():
            for v in vs:
                s.append('%s: %s' % (h.title(), v))
        return '\r\n'.join(s)
    
    def link(self):
        self.items = self._headers.items
        self.keys = self._headers.keys
        self.values = self._headers.values
        self.itervalues = self._headers.itervalues
        self.iteritems = self._headers.iteritems

    def parse(self, rawInput):
        ws = ' \t'
        heads = {}
        curhead = None
        curbuf = []
        for line in rawInput.splitlines():
            if not line.strip():
                continue
            if line[0] in ws:
                curbuf.append(line.strip())
            else:
                if curhead:
                    heads.setdefault(curhead, []).append(' '.join(curbuf))
                name, body = map(str.strip, line.split(':', 1))
                curhead = name.lower()
                curbuf = [body]
        if curhead:
            heads.setdefault(curhead, []).append(' '.join(curbuf))
        self._headers = heads
        self.link()

    def __contains__(self, k):
        return k.lower() in self._headers

    def __getitem__(self, k):
        return self._headers[k.lower()]

    def get(self, k, d=None):
        return self._headers.get(k.lower(), d)

    def get_one(self, k, d=None):
        return self.get(k, [d])[0]

    def __iter__(self):
        return self._headers

    def __str__(self):
        return self.format()

class HttpRequest(object):
    '''Structure representing an HTTP request.
    '''
    def __init__(self, method, url, version, remote_addr=None):
        self.method = method
        self.url = url
        self.version = version
        self.headers = None
        self.body = None
        self.remote_addr = remote_addr
        
    def format(self):    
        '''Format the request line for the wire.
        '''
        return '%s %s HTTP/%s' % (self.method, self.url, self.version)
        
class HttpClose(Exception): pass    

class HttpServer(object):
    '''An HTTP/1.1 implementation or a server.
    '''
    def __init__(self, request_handler):
        '''`request_handler` is a callable that takes
        an HttpRequest object and generates a response.
        '''
        self.request_handler = request_handler

    BODY_CHUNKED, BODY_CL, BODY_NONE = range(3)

    def check_for_http_body(self, heads):
        if heads.get_one('Transfer-Encoding') == 'chunked':
            return self.BODY_CHUNKED
        elif 'Content-Length' in heads:
            return self.BODY_CL
        return self.BODY_NONE

    def __call__(self, addr):
        '''Since an instance of HttpServer is passed to the Service
        class (with appropriate request_handler established during
        initialization), this __call__ method is what's actually
        invoked by diesel.

        This is our generator, this is our protocol handler.

        It does protocol work, then calls the request_handler, 
        looking for HttpClose if necessary.
        '''
        while True:
            chunks = []
            try:
                header_line = yield until_eol()
            except ConnectionClosed:
                break

            method, url, version = parse_request_line(header_line)    
            req = HttpRequest(method, url, version, remote_addr=addr)

            header_block = yield until('\r\n\r\n')

            heads = HttpHeaders()
            heads.parse(header_block)
            req.headers = heads

            if req.version >= '1.1' and heads.get_one('Expect') == '100-continue':
                yield 'HTTP/1.1 100 Continue\r\n\r\n'

            more_mode = self.check_for_http_body(heads)

            if more_mode is self.BODY_NONE:
                req.body = None

            elif more_mode is self.BODY_CL:
                req.body = yield bytes(int(heads['Content-Length']))

            elif more_mode is self.BODY_CHUNKED:
                req.body = handle_chunks(heads)

            leave_loop = False
            try:
                yield self.request_handler(req)
            except HttpClose:
                leave_loop = True
            if leave_loop:
                break

def http_response(req, code, heads, body):
    '''A "macro", which can be called by `request_handler` callables
    that are passed to an HttpServer.  Takes care of the nasty business
    of formatting a response for you, as well as connection handling
    on Keep-Alive vs. not.
    '''
    if req.version <= '1.0' and req.headers.get_one('Connection', '') != 'keep-alive':
        close = True
    elif req.headers.get_one('Connection') == 'close' or  \
        heads.get_one('Connection') == 'close':
        close = True
    else:
        close = False
        heads.set('Connection', 'keep-alive')
    yield '''HTTP/%s %s %s\r\n%s\r\n\r\n''' % (
    req.version, code, status_strings.get(code, "Unknown Status"), 
    heads.format())
    if body:
        yield body
    if close:
        raise HttpClose()

from diesel import Client, call, response

def handle_chunks(headers):
    '''Generic chunk handling code, used by both client
    and server.

    Modifies the passed-in HttpHeaders instance.
    '''
    chunks = []
    while True:
        chunk_head = yield until_eol()
        if ';' in chunk_head:
            # we don't support any chunk extensions
            chunk_head = chunk_head[:chunk_head.find(';')]
        size = int(chunk_head, 16)
        if size == 0:
            break
        else:
            chunks.append((yield bytes(size)))
            _ = yield bytes(2) # ignore trailing CRLF

    while True:
        trailer = yield until_eol()
        if trailer.strip():
            headers.add(*tuple(trailer.split(':', 1)))
        else:
            body = ''.join(chunks)
            headers.set('Content-Length', len(body))
            headers.remove('Transfer-Encoding')
            yield up(body)
            break

class HttpClient(Client):
    '''An HttpClient instance that issues 1.1 requests,
    including keep-alive behavior.

    Does not support sending chunks, yet... body must
    be a string.
    '''
    @call
    def request(self, method, path, headers, body=None):
        '''Issues a `method` request to `path` on the
        connected server.  Sends along `headers`, and
        body.

        Very low level--you must set "host" yourself,
        for example.  It will set Content-Length, 
        however.
        '''
        req = HttpRequest(method, path, '1.1')
        
        if body:
            headers.set('Content-Length', len(body))
        
        yield '%s\r\n%s\r\n\r\n' % (req.format(), 
        headers.format())

        if body:    
            yield body

        resp_line = yield until_eol()
        version, code, status = resp_line.split(None, 2)
        code = int(code)

        header_block = yield until('\r\n\r\n')
        heads = HttpHeaders()
        heads.parse(header_block)

        if heads.get_one('Transfer-Encoding') == 'chunked':
            body = yield handle_chunks(heads)
        else:
            cl = int(heads.get_one('Content-Length', 0))
            if cl:
                body = yield bytes(cl)
            else:
                body = None

        if version < '1.0' or heads.get_one('Connection') == 'close':
            self.close()
        yield response((code, heads, body))
